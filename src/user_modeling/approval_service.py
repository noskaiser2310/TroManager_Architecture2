"""
ApprovalService - Quản lý approval queue cho sensitive tool calls.

Flow:
1. Tool gọi `create_request()` → INSERT vào approval_queue với status='pending'
2. Tool return message "Yêu cầu #{id} đang chờ duyệt"
3. Admin gọi `GET /admin/approvals` để xem pending
4. Admin gọi `POST /admin/approvals/{id}/approve` → set status='approved' VÀ execute original action
5. Hoặc `POST /admin/approvals/{id}/reject` → set status='rejected'

Sau khi approve, `execute_approved()` sẽ replay tool call dựa trên `tool_name` + `tool_args`.
Hiện tại hỗ trợ:
- send_payment_reminder: gửi Zalo thật + log behavior
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

logger = logging.getLogger(__name__)


# Status constants
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    """Một approval request."""
    approval_id: int
    tool_name: str
    tool_args: dict
    tenant_id: int
    requested_by: Optional[str]
    approver_role: Optional[str]
    status: str
    requested_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_id: Optional[int]
    notes: Optional[str]

    @classmethod
    def from_row(cls, row) -> "ApprovalRequest":
        tool_args = row["tool_args"]
        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
            except (TypeError, ValueError):
                tool_args = {}
        return cls(
            approval_id=row["approval_id"],
            tool_name=row["tool_name"],
            tool_args=tool_args or {},
            tenant_id=row["tenant_id"],
            requested_by=row["requested_by"],
            approver_role=row["approver_role"],
            status=row["status"],
            requested_at=row["requested_at"],
            reviewed_at=row["reviewed_at"],
            reviewer_id=row["reviewer_id"],
            notes=row["notes"],
        )


class ApprovalService:
    """
    Quản lý approval queue: create, list, approve, reject + execute approved actions.

    Dependencies:
    - db_pool: asyncpg pool
    - zalo_client: ZaloClient instance (gửi tin sau khi approve)
    - behavior_tracker: BehaviorTracker (log behavior)
    """

    def __init__(self, db_pool, zalo_client=None, behavior_tracker=None):
        self.db = db_pool
        self.zalo = zalo_client
        self.behaviors = behavior_tracker

    async def create_request(
        self,
        tool_name: str,
        tool_args: dict,
        tenant_id: int,
        requested_by: str = "system",
        approver_role: str = "landlord",
        reason: Optional[str] = None,
    ) -> int:
        """
        Tạo approval request mới, status='pending'.

        Returns:
            approval_id mới tạo
        """
        # tool_args là dict - convert sang JSON string cho JSONB column
        tool_args_json = json.dumps(tool_args)

        sql = """
        INSERT INTO approval_queue (
            tool_name, tool_args, tenant_id,
            requested_by, approver_role, status, notes
        )
        VALUES ($1, $2::jsonb, $3, $4, $5, 'pending', $6)
        RETURNING approval_id
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(
                sql,
                tool_name,
                tool_args_json,
                tenant_id,
                requested_by,
                approver_role,
                reason,
            )
            approval_id = row["approval_id"]
            logger.info(
                f"ApprovalService: created request {approval_id} for {tool_name} "
                f"(tenant={tenant_id}, approver={approver_role})"
            )
            return approval_id

    async def list_pending(
        self,
        limit: int = 50,
        tenant_id: Optional[int] = None,
    ) -> list[ApprovalRequest]:
        """Lấy danh sách approval requests đang pending."""
        sql = """
        SELECT * FROM approval_queue
        WHERE status = 'pending'
        """
        params: list[Any] = []
        if tenant_id is not None:
            sql += " AND tenant_id = $2"
            params.append(tenant_id)
        sql += " ORDER BY requested_at ASC LIMIT $1"
        params.insert(0, limit)

        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        return [ApprovalRequest.from_row(r) for r in rows]

    async def list_all(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[ApprovalRequest]:
        """Lấy tất cả requests (filter theo status nếu có)."""
        if status:
            sql = """
            SELECT * FROM approval_queue
            WHERE status = $1
            ORDER BY requested_at DESC
            LIMIT $2
            """
            params = [status, limit]
        else:
            sql = """
            SELECT * FROM approval_queue
            ORDER BY requested_at DESC
            LIMIT $1
            """
            params = [limit]

        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        return [ApprovalRequest.from_row(r) for r in rows]

    async def get(self, approval_id: int) -> Optional[ApprovalRequest]:
        """Lấy 1 approval request theo id."""
        sql = "SELECT * FROM approval_queue WHERE approval_id = $1"
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, approval_id)
        return ApprovalRequest.from_row(row) if row else None

    async def approve(
        self,
        approval_id: int,
        reviewer_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Duyệt approval request: set status='approved' VÀ execute original action.

        Returns:
            (success, message)
        """
        request = await self.get(approval_id)
        if not request:
            return False, f"Approval request {approval_id} not found"
        if request.status != STATUS_PENDING:
            return False, f"Approval request {approval_id} is {request.status}, not pending"

        # Update status first (atomic-ish)
        sql = """
        UPDATE approval_queue
        SET status = 'approved',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewer_id = $2,
            notes = COALESCE($3, notes)
        WHERE approval_id = $1 AND status = 'pending'
        RETURNING approval_id
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, approval_id, reviewer_id, notes)

        if not row:
            return False, f"Approval request {approval_id} was modified concurrently"

        logger.info(
            f"ApprovalService: approved {approval_id} ({request.tool_name}) "
            f"by reviewer={reviewer_id}"
        )

        # Execute the original action
        try:
            result_msg = await self._execute_approved(request)
            return True, f"Approved and executed: {result_msg}"
        except Exception as e:
            logger.exception(
                f"ApprovalService: execution failed for approved request {approval_id}: {e}"
            )
            return True, f"Approved but execution failed: {str(e)}"

    async def reject(
        self,
        approval_id: int,
        reviewer_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Từ chối approval request.

        Returns:
            (success, message)
        """
        request = await self.get(approval_id)
        if not request:
            return False, f"Approval request {approval_id} not found"
        if request.status != STATUS_PENDING:
            return False, f"Approval request {approval_id} is {request.status}, not pending"

        sql = """
        UPDATE approval_queue
        SET status = 'rejected',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewer_id = $2,
            notes = COALESCE($3, notes)
        WHERE approval_id = $1 AND status = 'pending'
        RETURNING approval_id
        """
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, approval_id, reviewer_id, notes)

        if not row:
            return False, f"Approval request {approval_id} was modified concurrently"

        logger.info(
            f"ApprovalService: rejected {approval_id} ({request.tool_name}) "
            f"by reviewer={reviewer_id}, notes={notes}"
        )
        return True, f"Rejected (notes: {notes or 'none'})"

    async def _execute_approved(self, request: ApprovalRequest) -> str:
        """
        Replay tool call sau khi approved.

        Hiện tại hỗ trợ:
        - send_payment_reminder: gửi Zalo thật + log behavior
        """
        if request.tool_name == "send_payment_reminder":
            return await self._execute_send_payment_reminder(request)
        else:
            # Unknown tool - just log
            logger.warning(
                f"ApprovalService: no executor for tool '{request.tool_name}' "
                f"(approval {request.approval_id})"
            )
            return f"No executor for tool '{request.tool_name}'"

    async def _execute_send_payment_reminder(
        self, request: ApprovalRequest
    ) -> str:
        """
        Execute send_payment_reminder: gửi Zalo + log behavior.

        tool_args structure (from send_payment_reminder tool):
        {
            "tenant_id": int,
            "invoice_id": int,
            "tone": str,
            "amount": float,        # from invoice
            "days_overdue": int,    # from invoice
        }
        """
        args = request.tool_args
        tenant_id = args.get("tenant_id") or request.tenant_id
        invoice_id = args.get("invoice_id")
        tone = args.get("tone", "professional")
        amount = args.get("amount")
        days_overdue = args.get("days_overdue", 0)

        if not invoice_id:
            return "Missing invoice_id in tool_args"

        # Lấy thông tin tenant + invoice
        async with self.db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT t.full_name, t.phone_number, t.zalo_id, t.tone_preference,
                       i.due_date, i.invoice_month, r.room_number
                FROM invoices i
                JOIN user_profiles t ON i.tenant_id = t.tenant_id
                LEFT JOIN rooms r ON i.room_id = r.room_id
                WHERE i.invoice_id = $1 AND i.tenant_id = $2
            """, invoice_id, tenant_id)

        if not row:
            return f"Invoice {invoice_id} not found for tenant {tenant_id}"

        zalo_id = row["zalo_id"]
        if not zalo_id:
            return f"Tenant {tenant_id} has no zalo_id, cannot send"

        # Build message theo tone
        full_name = row["full_name"]
        room_number = row["room_number"] or "N/A"
        actual_tone = tone or row["tone_preference"] or "professional"
        msg = self._build_reminder_message(
            full_name=full_name,
            room_number=room_number,
            amount=amount or 0,
            days_overdue=days_overdue,
            tone=actual_tone,
        )

        # Gửi Zalo
        if not self.zalo:
            logger.warning("ApprovalService: no zalo_client configured, skipping send")
            return "Approved but no zalo_client configured (message not sent)"

        from src.notifications.zalo_client import ZaloMessage
        result = await self.zalo.send_message(ZaloMessage(
            recipient_id=zalo_id,
            message=msg,
        ))

        # Log behavior
        if self.behaviors:
            try:
                await self.behaviors.log(
                    tenant_id=tenant_id,
                    action_type="auto_payment_reminder",
                    description=f"Sent payment reminder for invoice {invoice_id} (approved #{request.approval_id})",
                    metadata={
                        "approval_id": request.approval_id,
                        "invoice_id": invoice_id,
                        "amount": amount,
                        "days_overdue": days_overdue,
                        "tone": actual_tone,
                        "zalo_success": result.success,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to log behavior: {e}")

        if result.success:
            return f"Zalo sent to {full_name} (msg_id={result.message_id})"
        else:
            return f"Zalo send failed: {result.error}"

    @staticmethod
    def _build_reminder_message(
        full_name: str,
        room_number: str,
        amount: float,
        days_overdue: int,
        tone: str,
    ) -> str:
        """Build message text theo tone."""
        amount_str = f"{amount:,.0f}".replace(",", ".")

        if tone == "strict" and days_overdue >= 7:
            return (
                f"Anh/chị {full_name},\n"
                f"Phòng {room_number} đã quá hạn đóng {amount_str}đ {days_overdue} ngày. "
                f"Vui lòng thanh toán trong 24h tới để tránh ảnh hưởng đến hợp đồng."
            )
        elif tone == "firm" or (days_overdue >= 3 and days_overdue < 7):
            return (
                f"Chào anh/chị {full_name},\n"
                f"Phòng {room_number} có hóa đơn {amount_str}đ quá hạn {days_overdue} ngày. "
                f"Mong anh/chị sắp xếp thanh toán sớm."
            )
        else:
            return (
                f"Chào anh/chị {full_name},\n"
                f"Nhà trọ xin nhắc nhỏ về hóa đơn phòng {room_number} ({amount_str}đ) "
                f"quá hạn {days_overdue} ngày. "
                f"Anh/chị vui lòng thanh toán khi tiện nhé. Cảm ơn!"
            )
