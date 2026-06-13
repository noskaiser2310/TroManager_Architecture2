"""
ConversationMemory - Service lưu trữ và truy xuất lịch sử hội thoại.

Schema (đã có trong database/schema.sql):
    conversation_history(
        conversation_id, tenant_id, session_id, source,
        user_message, ai_response, system_used, iterations,
        tool_calls, latency_ms, tokens_used, cost_usd, timestamp
    )

Service này cung cấp:
- add_turn(): lưu 1 turn (user msg + AI response)
- get_recent_turns(): lấy N turn gần nhất của tenant
- get_recent_turns_for_session(): lấy turn trong cùng session
- format_for_context(): format thành text cho LLM system prompt
- cleanup_old(): xóa turn cũ (cron job)
"""

from __future__ import annotations
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Một turn hội thoại (user message + AI response)."""
    conversation_id: int
    tenant_id: int
    session_id: Optional[str]
    source: Optional[str]
    user_message: str
    ai_response: str
    system_used: Optional[str]
    iterations: int
    tool_calls: list[dict]
    timestamp: datetime

    @classmethod
    def from_row(cls, row) -> "ConversationTurn":
        return cls(
            conversation_id=row["conversation_id"],
            tenant_id=row["tenant_id"],
            session_id=str(row["session_id"]) if row["session_id"] else None,
            source=row["source"],
            user_message=row["user_message"],
            ai_response=row["ai_response"],
            system_used=row["system_used"],
            iterations=row["iterations"] or 0,
            tool_calls=row["tool_calls"] or [],
            timestamp=row["timestamp"],
        )


class ConversationMemory:
    """Service quản lý lịch sử hội thoại."""

    def __init__(self, db_pool, max_turns_per_tenant: int = 20):
        self.db = db_pool
        self.max_turns_per_tenant = max_turns_per_tenant

    @staticmethod
    def new_session_id() -> str:
        """Generate UUID mới cho session."""
        return str(uuid.uuid4())

    async def add_turn(
        self,
        tenant_id: int,
        user_message: str,
        ai_response: str,
        session_id: Optional[str] = None,
        source: Optional[str] = None,
        system_used: Optional[str] = None,
        iterations: int = 0,
        tool_calls: Optional[list[dict]] = None,
        latency_ms: int = 0,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ) -> int:
        """
        Lưu 1 turn hội thoại (user msg + AI response).

        Returns:
            conversation_id mới tạo
        """
        if not session_id:
            session_id = self.new_session_id()

        db_tenant_id = tenant_id if tenant_id and tenant_id > 0 else None

        sql = """
        INSERT INTO conversation_history (
            tenant_id, session_id, source,
            user_message, ai_response,
            system_used, iterations, tool_calls,
            latency_ms, tokens_used, cost_usd
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11)
        RETURNING conversation_id
        """
        params = [
            db_tenant_id,
            session_id,
            source,
            user_message,
            ai_response,
            system_used,
            iterations,
            json.dumps(tool_calls or []),
            latency_ms,
            tokens_used,
            cost_usd,
        ]
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, *params)
            conv_id = row["conversation_id"]
            logger.debug(
                f"ConversationMemory: saved turn {conv_id} for tenant {tenant_id} "
                f"(session={session_id[:8] if session_id else 'new'}...)"
            )
            return conv_id

    async def get_recent_turns(
        self,
        tenant_id: int,
        limit: int = 5,
    ) -> list[ConversationTurn]:
        """
        Lấy N turn gần nhất của tenant (bất kể session).

        Args:
            tenant_id: ID khách thuê
            limit: số turn tối đa (mặc định 5)

        Returns:
            List các ConversationTurn, sắp xếp theo timestamp ASC (cũ → mới)
        """
        sql = """
        SELECT * FROM conversation_history
        WHERE tenant_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, limit)
        turns = [ConversationTurn.from_row(r) for r in rows]
        turns.reverse()  # Cũ → mới
        return turns

    async def get_recent_turns_for_session(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[ConversationTurn]:
        """Lấy turn trong cùng 1 session."""
        sql = """
        SELECT * FROM conversation_history
        WHERE session_id = $1
        ORDER BY timestamp ASC
        LIMIT $2
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, session_id, limit)
        return [ConversationTurn.from_row(r) for r in rows]

    async def format_for_context(
        self,
        tenant_id: int,
        max_turns: int = 5,
    ) -> str:
        """
        Format các turn gần nhất thành text để inject vào LLM system prompt.

        Returns:
            Chuỗi text hoặc "" nếu không có history.
        """
        turns = await self.get_recent_turns(tenant_id, limit=max_turns)
        if not turns:
            return ""

        lines = ["LỊCH SỬ HỘI THOẠI GẦN ĐÂY (để tham khảo ngữ cảnh):"]
        for turn in turns:
            ts = turn.timestamp.strftime("%Y-%m-%d %H:%M")
            lines.append(f"\n[{ts}]")
            user_msg = turn.user_message.strip()
            if len(user_msg) > 200:
                user_msg = user_msg[:200] + "..."
            lines.append(f"Khách: {user_msg}")
            ai_msg = turn.ai_response.strip()
            if len(ai_msg) > 200:
                ai_msg = ai_msg[:200] + "..."
            lines.append(f"AI: {ai_msg}")
        return "\n".join(lines)

    async def cleanup_old(self, days: int = 30) -> int:
        """
        Xóa các turn cũ hơn N ngày. Chạy bởi cron job.

        Returns:
            Số turn đã xóa
        """
        sql = """
        DELETE FROM conversation_history
        WHERE timestamp < CURRENT_TIMESTAMP - $1 * INTERVAL '1 day'
        RETURNING conversation_id
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, days)
        count = len(rows)
        logger.info(f"ConversationMemory: cleaned up {count} turns older than {days} days")
        return count
