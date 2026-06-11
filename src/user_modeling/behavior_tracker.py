"""
Behavior Tracker - Ghi log và tổng hợp hành vi của tenant.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)


@dataclass
class BehaviorLog:
    """Một log entry."""
    log_id: int
    tenant_id: int
    action_type: str
    description: str
    metadata: dict
    timestamp: datetime


@dataclass
class BehaviorSummary:
    """Tổng hợp behavior trong 1 khoảng thời gian."""
    tenant_id: int
    period_days: int
    late_payment_count: int
    on_time_payment_count: int
    maintenance_count: int
    noise_complaint_count: int
    room_transfer_count: int
    auto_interactions_count: int
    first_interaction: Optional[datetime]
    last_interaction: Optional[datetime]
    avg_payment_delay_days: float


class BehaviorTracker:
    """
    Quản lý behavior logs và tạo summary.
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
    
    async def log(
        self,
        tenant_id: int,
        action_type: str,
        description: str = "",
        metadata: dict = None,
    ) -> int:
        """
        Ghi một behavior log.
        
        Args:
            tenant_id: ID khách thuê
            action_type: Loại hành động (late_payment, on_time_payment, ...)
            description: Mô tả chi tiết
            metadata: Additional data (JSONB)
            
        Returns:
            log_id
        """
        import json
        metadata_json = json.dumps(metadata or {})
        
        sql = """
        INSERT INTO behavior_logs (tenant_id, action_type, description, metadata)
        VALUES ($1, $2, $3, $4::jsonb)
        RETURNING log_id
        """
        async with self.db.acquire() as conn:
            log_id = await conn.fetchval(sql, tenant_id, action_type, description, metadata_json)
        logger.debug(f"Logged behavior {log_id}: tenant={tenant_id}, type={action_type}")
        return log_id
    
    async def get_logs(
        self,
        tenant_id: int,
        days: int = 30,
        action_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[BehaviorLog]:
        """Lấy logs gần đây của tenant."""
        sql = """
        SELECT log_id, tenant_id, action_type, description, metadata, timestamp
        FROM behavior_logs
        WHERE tenant_id = $1
          AND timestamp > CURRENT_TIMESTAMP - $2 * INTERVAL '1 day'
        """
        params = [tenant_id, days]
        
        if action_type:
            sql += " AND action_type = $3"
            params.append(action_type)
        
        sql += " ORDER BY timestamp DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)
        
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [self._row_to_log(row) for row in rows]
    
    async def get_summary(
        self,
        tenant_id: int,
        days: int = 90,
    ) -> BehaviorSummary:
        """
        Tổng hợp behavior trong N ngày gần nhất.
        """
        sql = """
        SELECT
            $1::INT as tenant_id,
            $2::INT as period_days,
            COUNT(*) FILTER (WHERE action_type = 'late_payment') AS late_count,
            COUNT(*) FILTER (WHERE action_type = 'on_time_payment') AS on_time_count,
            COUNT(*) FILTER (WHERE action_type = 'maintenance_request') AS maint_count,
            COUNT(*) FILTER (WHERE action_type = 'noise_complaint') AS noise_count,
            COUNT(*) FILTER (WHERE action_type = 'room_transfer') AS transfer_count,
            COUNT(*) FILTER (WHERE action_type LIKE 'auto_%') AS auto_count,
            MIN(timestamp) AS first_int,
            MAX(timestamp) AS last_int,
            COALESCE(AVG((metadata->>'delay_days')::FLOAT) FILTER (WHERE action_type = 'late_payment'), 0.0) AS avg_delay
        FROM behavior_logs
        WHERE tenant_id = $1
          AND timestamp > CURRENT_TIMESTAMP - $2 * INTERVAL '1 day'
        """
        
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id, days)
            if not row:
                return self._empty_summary(tenant_id, days)
            
            return BehaviorSummary(
                tenant_id=row["tenant_id"],
                period_days=row["period_days"],
                late_payment_count=row["late_count"] or 0,
                on_time_payment_count=row["on_time_count"] or 0,
                maintenance_count=row["maint_count"] or 0,
                noise_complaint_count=row["noise_count"] or 0,
                room_transfer_count=row["transfer_count"] or 0,
                auto_interactions_count=row["auto_count"] or 0,
                first_interaction=row["first_int"],
                last_interaction=row["last_int"],
                avg_payment_delay_days=float(row["avg_delay"] or 0.0),
            )
    
    async def get_anti_spam_check(self, tenant_id: int, max_per_week: int = 2) -> dict:
        """
        Check có nên gửi auto-reminder cho tenant không.
        
        Returns:
            dict với can_send, last_reminder, count_this_week
        """
        sql = """
        SELECT
            COUNT(*) FILTER (
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
            ) AS count_this_week,
            MAX(timestamp) AS last_reminder
        FROM behavior_logs
        WHERE tenant_id = $1
          AND action_type LIKE 'auto_%'
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id)
        
        count_this_week = row["count_this_week"] or 0
        last_reminder = row["last_reminder"]
        
        can_send = count_this_week < max_per_week
        if last_reminder:
            hours_since = (datetime.now() - last_reminder).total_seconds() / 3600
            if hours_since < 24:
                can_send = False
        
        return {
            "can_send": can_send,
            "last_reminder": last_reminder,
            "count_this_week": count_this_week,
        }
    
    def _row_to_log(self, row) -> BehaviorLog:
        """Convert row to BehaviorLog."""
        import json
        metadata = row["metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        return BehaviorLog(
            log_id=row["log_id"],
            tenant_id=row["tenant_id"],
            action_type=row["action_type"],
            description=row["description"] or "",
            metadata=metadata or {},
            timestamp=row["timestamp"],
        )
    
    def _empty_summary(self, tenant_id: int, days: int) -> BehaviorSummary:
        return BehaviorSummary(
            tenant_id=tenant_id,
            period_days=days,
            late_payment_count=0,
            on_time_payment_count=0,
            maintenance_count=0,
            noise_complaint_count=0,
            room_transfer_count=0,
            auto_interactions_count=0,
            first_interaction=None,
            last_interaction=None,
            avg_payment_delay_days=0.0,
        )


# ============ Common action types ============

class ActionTypes:
    """Constants for common action types."""
    LATE_PAYMENT = "late_payment"
    ON_TIME_PAYMENT = "on_time_payment"
    MAINTENANCE_REQUEST = "maintenance_request"
    NOISE_COMPLAINT = "noise_complaint"
    ROOM_TRANSFER = "room_transfer"
    CONTRACT_SIGNED = "contract_signed"
    CONTRACT_RENEWED = "contract_renewed"
    AUTO_INVOICE_REMINDER = "auto_invoice_reminder"
    AUTO_CONTRACT_REMINDER = "auto_contract_reminder"
    AUTO_MAINTENANCE_REMINDER = "auto_maintenance_reminder"
    AUTO_BIRTHDAY = "auto_birthday_greeting"
    AUTO_WELCOME = "auto_welcome_message"
    AI_RESPONSE = "ai_response"
    TOOL_CALLED = "tool_called"
