"""
Memory Manager - Quản lý user embeddings (semantic memory).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import asyncpg
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Một memory entry trong user_embeddings."""
    memory_id: int
    tenant_id: int
    memory_text: str
    weight: float
    retrieval_count: int
    is_archived: bool
    created_at: datetime


class MemoryManager:
    """
    Quản lý semantic memory của users.
    
    Sử dụng PostgreSQL + pgvector cho vector storage.
    """
    
    def __init__(self, db_pool: asyncpg.Pool, embedding_model, embedding_dim: int = 3072):
        self.db = db_pool
        self.embedding = embedding_model
        self.embedding_dim = embedding_dim
    
    async def add_memory(
        self,
        tenant_id: int,
        memory_text: str,
        source: str = "persona_optimizer",
    ) -> int:
        """
        Thêm memory mới.
        
        Returns:
            memory_id
        """
        embedding = await self.embedding.encode(memory_text)
        embedding_str = self._to_pgvector(embedding)
        
        sql = """
        INSERT INTO user_embeddings (tenant_id, memory_text, embedding, source)
        VALUES ($1, $2, $3::vector, $4)
        RETURNING memory_id
        """
        async with self.db.acquire() as conn:
            memory_id = await conn.fetchval(sql, tenant_id, memory_text, embedding_str, source)
        logger.info(f"Added memory {memory_id} for tenant {tenant_id}: {memory_text[:50]}")
        return memory_id
    
    async def search_memories(
        self,
        tenant_id: int,
        query_text: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Tìm memories liên quan nhất đến query.
        
        Returns:
            list of {"memory_id": int, "memory_text": str, "similarity": float}
        """
        query_embedding = await self.embedding.encode(query_text)
        embedding_str = self._to_pgvector(query_embedding)
        
        sql = """
        SELECT
            memory_id, memory_text,
            1 - (embedding <=> $2::vector) AS similarity
        FROM user_embeddings
        WHERE tenant_id = $1
          AND is_archived = FALSE
        ORDER BY embedding <=> $2::vector
        LIMIT $3
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, embedding_str, top_k)
            
            # Update last_retrieved
            memory_ids = [row["memory_id"] for row in rows]
            if memory_ids:
                await conn.execute("""
                UPDATE user_embeddings
                SET last_retrieved = CURRENT_TIMESTAMP,
                    retrieval_count = retrieval_count + 1
                WHERE memory_id = ANY($1::int[])
                """, memory_ids)
        
        return [
            {
                "memory_id": row["memory_id"],
                "memory_text": row["memory_text"],
                "similarity": float(row["similarity"]),
            }
            for row in rows
        ]
    
    async def get_all_memories(
        self,
        tenant_id: int,
        include_archived: bool = False,
    ) -> list[Memory]:
        """Lấy tất cả memories của tenant."""
        sql = """
        SELECT memory_id, tenant_id, memory_text, weight, retrieval_count, is_archived, created_at
        FROM user_embeddings
        WHERE tenant_id = $1
        """
        if not include_archived:
            sql += " AND is_archived = FALSE"
        sql += " ORDER BY created_at DESC"
        
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id)
            return [self._row_to_memory(row) for row in rows]
    
    async def archive_memory(self, memory_id: int) -> bool:
        """Archive một memory (soft delete)."""
        sql = "UPDATE user_embeddings SET is_archived = TRUE WHERE memory_id = $1"
        async with self.db.acquire() as conn:
            result = await conn.execute(sql, memory_id)
        return result == "UPDATE 1"
    
    async def delete_memory(self, memory_id: int) -> bool:
        """Xóa cứng một memory."""
        sql = "DELETE FROM user_embeddings WHERE memory_id = $1"
        async with self.db.acquire() as conn:
            result = await conn.execute(sql, memory_id)
        return result == "DELETE 1"
    
    async def apply_decay(self, decay_rate: float = 0.95, threshold: float = 0.1):
        """
        Áp dụng decay cho memories cũ không được truy xuất.
        
        Args:
            decay_rate: Hệ số giảm (0.95 = giảm 5%)
            threshold: Weight tối thiểu trước khi archive
        """
        sql = """
        UPDATE user_embeddings
        SET weight = weight * $1
        WHERE is_archived = FALSE
          AND (last_retrieved IS NULL OR last_retrieved < CURRENT_TIMESTAMP - INTERVAL '30 days')
          AND weight > $2
        RETURNING memory_id, weight
        """
        async with self.db.acquire() as conn:
            # Apply decay first
            decayed = await conn.fetch(sql, decay_rate, threshold)
            logger.info(f"Applied decay to {len(decayed)} memories")
            
            # Archive memories with weight below threshold (including newly decayed ones)
            await conn.execute("""
            UPDATE user_embeddings
            SET is_archived = TRUE
            WHERE is_archived = FALSE
              AND weight <= $1
            """, threshold)
    
    async def regenerate_memories(
        self,
        tenant_id: int,
        behavior_summary_text: str,
    ) -> list[int]:
        """
        Regenerate memories cho tenant dựa trên behavior summary.
        Dùng bởi Persona Optimizer batch job.
        
        Args:
            tenant_id: ID khách thuê
            behavior_summary_text: Tổng hợp behavior (text)
            
        Returns:
            list of memory_ids mới tạo
        """
        # Split summary thành insights riêng biệt
        insights = [s.strip() for s in behavior_summary_text.split("\n") if s.strip()]
        
        memory_ids = []
        try:
            for insight in insights:
                mid = await self.add_memory(tenant_id, insight, source="persona_optimizer")
                memory_ids.append(mid)
            
            # Archive old memories only after successfully creating new ones
            if memory_ids:
                async with self.db.acquire() as conn:
                    await conn.execute("""
                    UPDATE user_embeddings
                    SET is_archived = TRUE
                    WHERE tenant_id = $1 AND memory_id != ALL($2::int[])
                    """, tenant_id, memory_ids)
            
            logger.info(f"Regenerated {len(memory_ids)} memories for tenant {tenant_id}")
            return memory_ids
        except Exception as e:
            logger.error(f"Failed to regenerate memories: {e}")
            raise
    
    def _row_to_memory(self, row) -> Memory:
        return Memory(
            memory_id=row["memory_id"],
            tenant_id=row["tenant_id"],
            memory_text=row["memory_text"],
            weight=float(row["weight"]),
            retrieval_count=row["retrieval_count"],
            is_archived=row["is_archived"],
            created_at=row["created_at"],
        )
    
    def _to_pgvector(self, embedding) -> str:
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        return "[" + ",".join(str(x) for x in embedding) + "]"
