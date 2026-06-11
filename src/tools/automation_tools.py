"""
Automation Toolkit - Gửi thông báo và tạo tickets.

Tất cả tools thực hiện thật:
- Gọi Zalo OA API
- Gọi SMS API
- INSERT vào database
- Log behavior
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from langchain.tools import tool

logger = logging.getLogger(__name__)


# ============ Helper functions ============

async def _log_behavior(tenant_id: int, action_type: str, description: str, metadata: dict = None):
    """Log behavior vào DB."""
    try:
        from ..core import get_db_pool
        import json
        
        pool = get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO behavior_logs (tenant_id, action_type, description, metadata)
                VALUES ($1, $2, $3, $4::jsonb)
            """, tenant_id, action_type, description, json.dumps(metadata or {}, default=str))
    except Exception as e:
        logger.warning(f"Failed to log behavior: {e}")


def _generate_ticket_code() -> str:
    """Generate mã ticket TKT-YYYY-NNNN."""
    import random
    year = datetime.now().year
    num = random.randint(1000, 9999)
    return f"TKT-{year}-{num}"


# ============ Tool 1: send_zalo ============

class SendZaloInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    message: str = Field(..., description="Nội dung tin nhắn")
    template_id: Optional[str] = Field(None, description="ZNS template ID (optional)")


@tool(args_schema=SendZaloInput)
async def send_zalo(tenant_id: int, message: str, template_id: Optional[str] = None) -> str:
    """
    Gửi tin nhắn Zalo cho khách thuê qua Zalo OA API.
    """
    from ..core import get_db_pool, get_zalo_client
    
    try:
        # Lấy thông tin tenant
        pool = get_db_pool()
        async with pool.acquire() as conn:
            tenant = await conn.fetchrow(
                "SELECT full_name, zalo_id FROM user_profiles WHERE tenant_id = $1",
                tenant_id
            )
        
        if not tenant:
            return f"Không tìm thấy tenant {tenant_id}"
        
        if not tenant['zalo_id']:
            return f"Tenant {tenant['full_name']} chưa liên kết Zalo. Không thể gửi."
        
        # Gọi Zalo API
        zalo = get_zalo_client()
        result = await zalo.send_to_tenant(
            tenant_zalo_id=tenant['zalo_id'],
            message_text=message,
            template_id=template_id,
        )
        
        if result.success:
            await _log_behavior(
                tenant_id, "auto_zalo_sent",
                f"Sent Zalo: {message[:100]}",
                {"message_id": result.message_id}
            )
            return f"Đã gửi tin Zalo tới {tenant['full_name']}. Message ID: {result.message_id}"
        else:
            await _log_behavior(
                tenant_id, "auto_zalo_failed",
                f"Failed: {result.error}",
            )
            return f"Gửi Zalo thất bại: {result.error}"
    
    except Exception as e:
        logger.exception(f"send_zalo error: {e}")
        return f"Lỗi khi gửi Zalo: {str(e)}"


# ============ Tool 2: send_sms ============

class SendSMSInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    message: str = Field(..., description="Nội dung SMS (tối đa 160 ký tự)")


@tool(args_schema=SendSMSInput)
async def send_sms(tenant_id: int, message: str) -> str:
    """
    Gửi SMS cho khách thuê qua SMS gateway.
    """
    from ..core import get_db_pool, get_sms_client
    
    if len(message) > 160:
        message = message[:157] + "..."
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            tenant = await conn.fetchrow(
                "SELECT full_name, phone_number FROM user_profiles WHERE tenant_id = $1",
                tenant_id
            )
        
        if not tenant:
            return f"Không tìm thấy tenant {tenant_id}"
        
        if not tenant['phone_number']:
            return f"Tenant {tenant['full_name']} chưa có số điện thoại."
        
        sms = get_sms_client()
        result = await sms.send_sms(tenant['phone_number'], message)
        
        if result.success:
            await _log_behavior(
                tenant_id, "auto_sms_sent",
                f"Sent SMS: {message[:100]}",
                {"message_id": result.message_id}
            )
            return f"Đã gửi SMS tới {tenant['full_name']} ({tenant['phone_number']})"
        else:
            return f"Gửi SMS thất bại: {result.error}"
    
    except Exception as e:
        logger.exception(f"send_sms error: {e}")
        return f"Lỗi khi gửi SMS: {str(e)}"


# ============ Tool 3: create_maintenance_ticket ============

class CreateMaintenanceTicketInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    issue: str = Field(..., description="Mô tả sự cố")
    priority: str = Field("normal", description="low, normal, high, urgent")
    category: str = Field("general", description="electrical, plumbing, appliance, ... ")
    room_id: Optional[int] = Field(None, description="ID phòng (mặc định lấy từ tenant)")


@tool(args_schema=CreateMaintenanceTicketInput)
async def create_maintenance_ticket(
    tenant_id: int,
    issue: str,
    priority: str = "normal",
    category: str = "general",
    room_id: Optional[int] = None,
) -> str:
    """
    Tạo phiếu yêu cầu sửa chữa/bảo trì trong database.
    """
    from ..core import get_db_pool
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            # Lấy room_id nếu không có
            if room_id is None:
                room_id = await conn.fetchval(
                    "SELECT room_id FROM user_profiles WHERE tenant_id = $1",
                    tenant_id
                )
            
            if not room_id:
                return f"Tenant {tenant_id} chưa có phòng - không thể tạo ticket."
            
            ticket_code = _generate_ticket_code()
            title = f"{category}: {issue[:50]}"
            
            ticket_id = await conn.fetchval("""
                INSERT INTO maintenance_tickets 
                (ticket_code, tenant_id, room_id, issue_category, title, description, priority, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, 'open')
                RETURNING ticket_id
            """, ticket_code, tenant_id, room_id, category, title, issue, priority)
            
            # Log behavior
            await _log_behavior(
                tenant_id, "maintenance_request",
                f"Created ticket {ticket_code}: {issue[:100]}",
                {"ticket_id": ticket_id, "category": category, "priority": priority}
            )
            
            # Map priority to text
            priority_text = {
                'low': 'Thấp',
                'normal': 'Bình thường',
                'high': 'Cao',
                'urgent': 'Khẩn cấp',
            }.get(priority, priority)
            
            return (
                f"Đã tạo phiếu sửa chữa:\n"
                f"- Mã phiếu: {ticket_code}\n"
                f"- Phân loại: {category}\n"
                f"- Mức độ: {priority_text}\n"
                f"- Mô tả: {issue}\n"
                f"- Trạng thái: Mới tiếp nhận\n"
                f"- Thời gian xử lý dự kiến: 24-48h\n"
                f"Thợ sẽ liên hệ anh/chị sớm nhất."
            )
    
    except Exception as e:
        logger.exception(f"create_maintenance_ticket error: {e}")
        return f"Lỗi khi tạo ticket: {str(e)}"


# ============ Tool 4: send_payment_reminder (SENSITIVE) ============

class SendPaymentReminderInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    invoice_id: int = Field(..., description="ID hóa đơn")
    tone: str = Field("professional", description="friendly, professional, strict")


@tool(args_schema=SendPaymentReminderInput)
async def send_payment_reminder(
    tenant_id: int,
    invoice_id: int,
    tone: str = "professional",
) -> str:
    """
    Gửi tin nhắn nhắc nhở đóng tiền (SENSITIVE - cần duyệt bởi quản lý).
    
    Flow:
    1. Tạo approval request
    2. Quản lý duyệt
    3. Nếu approved → gửi Zalo + log
    """
    from ..core import get_db_pool
    
    try:
        import json
        pool = get_db_pool()
        async with pool.acquire() as conn:
            # Lấy thông tin invoice
            invoice = await conn.fetchrow("""
                SELECT i.total_amount, i.due_date, 
                       EXTRACT(DAY FROM (CURRENT_DATE - i.due_date))::INT as days_overdue,
                       t.full_name, t.tone_preference
                FROM invoices i
                JOIN user_profiles t ON i.tenant_id = t.tenant_id
                WHERE i.invoice_id = $1 AND i.tenant_id = $2
            """, invoice_id, tenant_id)
            
            if not invoice:
                return f"Không tìm thấy hóa đơn {invoice_id} của tenant {tenant_id}"
            
            # Tạo approval request
            tool_args = json.dumps({
                "tenant_id": tenant_id,
                "invoice_id": invoice_id,
                "tone": tone,
                "amount": float(invoice['total_amount']),
                "days_overdue": invoice['days_overdue']
            })
            
            approval_id = await conn.fetchval("""
                INSERT INTO approval_queue 
                (tool_name, tool_args, tenant_id, requested_by, approver_role, status)
                VALUES ('send_payment_reminder', $1::jsonb, $2, 'system', 'landlord', 'pending')
                RETURNING approval_id
            """, tool_args, tenant_id)
            
            return (
                f"Đã tạo yêu cầu nhắc thanh toán #{approval_id}.\n"
                f"- Khách: {invoice['full_name']}\n"
                f"- Số tiền: {float(invoice['total_amount']):,.0f}đ\n"
                f"- Quá hạn: {invoice['days_overdue']} ngày\n"
                f"- Tông giọng: {tone}\n"
                f"\nĐang chờ quản lý duyệt trước khi gửi."
            )
    
    except Exception as e:
        logger.exception(f"send_payment_reminder error: {e}")
        return f"Lỗi: {str(e)}"


# ============ Tool 5: schedule_room_viewing ============

class ScheduleRoomViewingInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    room_id: int = Field(..., description="ID phòng muốn xem")
    datetime_str: str = Field(..., description="Thời gian hẹn, format YYYY-MM-DD HH:MM")


@tool(args_schema=ScheduleRoomViewingInput)
async def schedule_room_viewing(tenant_id: int, room_id: int, datetime_str: str) -> str:
    """
    Đặt lịch xem phòng cho khách.
    """
    from ..core import get_db_pool
    
    try:
        from datetime import datetime
        scheduled_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        if scheduled_dt < datetime.now():
            return "Thời gian hẹn phải ở tương lai."

        pool = get_db_pool()
        async with pool.acquire() as conn:
            # Lấy thông tin
            tenant = await conn.fetchrow(
                "SELECT full_name, phone_number FROM user_profiles WHERE tenant_id = $1",
                tenant_id
            )
            room = await conn.fetchrow(
                "SELECT room_number, floor, monthly_rent FROM rooms WHERE room_id = $1",
                room_id
            )

            if not tenant or not room:
                return "Không tìm thấy thông tin tenant hoặc phòng."

            if room['room_number'] is None:
                return f"Phòng {room_id} không tồn tại."

            # Persist appointment to DB
            appointment_id = await conn.fetchval("""
                INSERT INTO appointments (tenant_id, room_id, scheduled_at, status)
                VALUES ($1, $2, $3, 'pending')
                RETURNING appointment_id
            """, tenant_id, room_id, scheduled_dt)

        # Log behavior
        await _log_behavior(
            tenant_id, "room_viewing_scheduled",
            f"Xem phòng {room['room_number']} lúc {datetime_str}",
            {"room_id": room_id, "datetime": datetime_str, "appointment_id": appointment_id}
        )

        return (
            f"Đã đặt lịch xem phòng (ID: #{appointment_id}):\n"
            f"- Khách: {tenant['full_name']} ({tenant['phone_number']})\n"
            f"- Phòng: {room['room_number']} (tầng {room['floor']}, {float(room['monthly_rent']):,.0f}đ)\n"
            f"- Thời gian: {datetime_str}\n"
            f"- Trạng thái: Chờ xác nhận từ quản lý\n"
            f"Quản lý sẽ gọi điện xác nhận với khách trong 24h."
        )

    except ValueError:
        return "Format thời gian không đúng. Vui lòng dùng YYYY-MM-DD HH:MM"
    except Exception as e:
        logger.exception(f"schedule_room_viewing error: {e}")
        return f"Lỗi: {str(e)}"


# ============ Export ============

AUTOMATION_TOOLS = [
    send_zalo,
    send_sms,
    create_maintenance_ticket,
    send_payment_reminder,
    schedule_room_viewing,
]
