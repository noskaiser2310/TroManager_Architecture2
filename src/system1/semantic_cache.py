"""
Semantic Cache - Tra cứu cache bằng vector similarity.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass

import asyncpg
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Một entry trong semantic cache."""
    cache_id: int
    query_text: str
    response_text: str
    similarity: float


class SemanticCache:
    """
    Quản lý semantic cache với PostgreSQL + pgvector.
    
    - Cosine similarity search
    - TTL expiration
    - Hit count tracking
    """
    
    def __init__(self, db_pool: asyncpg.Pool, embedding_dim: int = 3072):
        self.db = db_pool
        self.embedding_dim = embedding_dim
    
    async def lookup(
        self,
        query_embedding: list[float],
        threshold: float = 0.9,
    ) -> CacheEntry | None:
        """
        Tìm cache entry có similarity cao nhất.
        
        Args:
            query_embedding: Vector 768-dim
            threshold: Minimum similarity (0-1)
            
        Returns:
            CacheEntry nếu tìm thấy, None nếu không
        """
        embedding_str = self._to_pgvector(query_embedding)
        
        sql = """
        SELECT 
            cache_id,
            query_text,
            response_text,
            1 - (query_embedding <=> $1::vector) AS similarity
        FROM semantic_cache
        WHERE 1 - (query_embedding <=> $1::vector) > $2
          AND expires_at > CURRENT_TIMESTAMP
        ORDER BY query_embedding <=> $1::vector
        LIMIT 1
        """
        
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, embedding_str, threshold)
            
            if row:
                # Update hit count và last_accessed
                await self._update_access(row["cache_id"])
                return CacheEntry(
                    cache_id=row["cache_id"],
                    query_text=row["query_text"],
                    response_text=row["response_text"],
                    similarity=float(row["similarity"]),
                )
        
        return None
    
    async def save(
        self,
        query: str,
        query_embedding: list[float],
        response: str,
    ) -> int:
        """
        Lưu cache entry mới.
        
        Returns:
            cache_id của entry mới tạo
        """
        embedding_str = self._to_pgvector(query_embedding)
        
        sql = """
        INSERT INTO semantic_cache (query_text, query_embedding, response_text)
        VALUES ($1, $2::vector, $3)
        ON CONFLICT DO NOTHING
        RETURNING cache_id
        """
        
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, query, embedding_str, response)
            if row:
                logger.debug(f"Saved cache entry {row['cache_id']}: {query[:50]}")
                return row["cache_id"]
        
        return -1
    
    async def _update_access(self, cache_id: int):
        """Update last_accessed và hit_count."""
        sql = """
        UPDATE semantic_cache
        SET last_accessed = CURRENT_TIMESTAMP,
            hit_count = hit_count + 1
        WHERE cache_id = $1
        """
        async with self.db.acquire() as conn:
            await conn.execute(sql, cache_id)
    
    async def cleanup_expired(self) -> int:
        """Xóa các cache entries đã expired. Trả về số lượng đã xóa."""
        sql = "SELECT cleanup_expired_cache()"
        async with self.db.acquire() as conn:
            count = await conn.fetchval(sql)
        logger.info(f"Cleaned up {count} expired cache entries")
        return count
    
    async def get_stats(self) -> dict:
        """Lấy thống kê cache."""
        sql = """
        SELECT
            COUNT(*) AS total_entries,
            COALESCE(SUM(hit_count), 0) AS total_hits,
            COALESCE(AVG(hit_count), 0) AS avg_hits_per_entry,
            MAX(last_accessed) AS last_accessed
        FROM semantic_cache
        WHERE expires_at > CURRENT_TIMESTAMP
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql)
        return dict(row) if row else {}
    
    def _to_pgvector(self, embedding: list[float]) -> str:
        """Convert list[float] to pgvector string format."""
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        return "[" + ",".join(str(x) for x in embedding) + "]"


# ============ Cache warming ============

async def warm_cache_with_faq(cache: SemanticCache, faqs: list[dict], embedding_model):
    """
    Pre-populate cache với top FAQs.
    
    Args:
        faqs: list of {"query": str, "response": str}
    """
    logger.info(f"Warming cache with {len(faqs)} FAQs...")
    for faq in faqs:
        embedding = await embedding_model.encode(faq["query"])
        await cache.save(faq["query"], embedding, faq["response"])
    logger.info("Cache warming complete")
