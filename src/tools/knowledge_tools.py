"""
Knowledge Toolkit - Tra cứu thông tin từ database.
"""

from __future__ import annotations
import logging
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from langchain.tools import tool

logger = logging.getLogger(__name__)


# ============ Tool 1: get_invoice_detail ============

class GetInvoiceDetailInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    month: str = Field(..., description="Tháng cần tra cứu, format YYYY-MM")


@tool(args_schema=GetInvoiceDetailInput)
async def get_invoice_detail(tenant_id: int, month: str) -> str:
    """
    Lấy chi tiết hóa đơn của tenant theo tháng.
    """
    from ..core import get_db_pool, current_tenant_id
    from datetime import datetime
    
    ctx_tenant_id = current_tenant_id.get()
    if ctx_tenant_id is not None:
        tenant_id = ctx_tenant_id
    
    # Normalize month format to YYYY-MM
    month = month.strip()
    if len(month) == 1 or len(month) == 2:
        # Assume current year if only month number given
        month = f"{datetime.now().year}-{month.zfill(2)}"
    elif len(month) == 4 and month.isdigit():
        # YYYY format - assume January
        month = f"{month}-01"
    elif len(month) == 6 and month.isdigit():
        # YYYYMM format
        month = f"{month[:4]}-{month[4:]}"
    elif len(month) == 7 and month[4] == '-':
        # Already YYYY-MM format
        pass
    elif '-' in month and len(month) == 7:
        # YYYY-MM format
        pass
    else:
        # Try to parse common formats
        try:
            dt = datetime.strptime(month, "%m/%Y")
            month = dt.strftime("%Y-%m")
        except ValueError:
            try:
                dt = datetime.strptime(month, "%Y-%m-%d")
                month = dt.strftime("%Y-%m")
            except ValueError:
                pass  # Keep original, let DB query fail gracefully
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            invoice = await conn.fetchrow("""
                SELECT i.invoice_id, i.invoice_month, i.base_rent, 
                       i.electricity_kwh, i.electricity_cost,
                       i.water_m3, i.water_cost,
                       i.service_fee, i.other_charges,
                       i.total_amount, i.due_date, i.paid_date, i.status,
                       r.room_number
                FROM invoices i
                JOIN rooms r ON i.room_id = r.room_id
                WHERE i.tenant_id = $1 
                  AND TO_CHAR(i.invoice_month, 'YYYY-MM') = $2
            """, tenant_id, month)
            
            if not invoice:
                return f"Không tìm thấy hóa đơn tháng {month} của tenant {tenant_id}."
            
            status_text = {
                'paid': 'Đã thanh toán',
                'unpaid': 'Chưa thanh toán',
                'overdue': 'Quá hạn',
                'cancelled': 'Đã hủy',
            }.get(invoice['status'], invoice['status'])
            
            return (
                f"Hóa đơn tháng {month} - Phòng {invoice['room_number']}:\n"
                f"- Tiền phòng: {float(invoice['base_rent']):,.0f}đ\n"
                f"- Tiền điện ({float(invoice['electricity_kwh'])} kWh): {float(invoice['electricity_cost']):,.0f}đ\n"
                f"- Tiền nước ({float(invoice['water_m3'])} m³): {float(invoice['water_cost']):,.0f}đ\n"
                f"- Phí dịch vụ: {float(invoice['service_fee']):,.0f}đ\n"
                f"- Phí khác: {float(invoice['other_charges']):,.0f}đ\n"
                f"- TỔNG: {float(invoice['total_amount']):,.0f}đ\n"
                f"- Hạn thanh toán: {invoice['due_date']}\n"
                f"- Trạng thái: {status_text}\n"
                + (f"- Ngày thanh toán: {invoice['paid_date']}" if invoice['paid_date'] else "")
            )
    
    except Exception as e:
        logger.exception(f"get_invoice_detail error: {e}")
        return f"Lỗi khi tra cứu hóa đơn: {str(e)}"


# ============ Tool 2: get_contract_status ============

class GetContractStatusInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")


@tool(args_schema=GetContractStatusInput)
async def get_contract_status(tenant_id: int) -> str:
    """
    Lấy trạng thái hợp đồng hiện tại của tenant.
    """
    from ..core import get_db_pool, current_tenant_id
    
    ctx_tenant_id = current_tenant_id.get()
    if ctx_tenant_id is not None:
        tenant_id = ctx_tenant_id
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            contract = await conn.fetchrow("""
                SELECT c.contract_id, c.start_date, c.end_date, 
                       c.deposit_amount, c.monthly_rent, c.status,
                       r.room_number, r.floor, r.area_m2
                FROM contracts c
                JOIN rooms r ON c.room_id = r.room_id
                WHERE c.tenant_id = $1
                ORDER BY c.end_date DESC
                LIMIT 1
            """, tenant_id)
            
            if not contract:
                return f"Không tìm thấy hợp đồng của tenant {tenant_id}."
            
            status_text = {
                'active': 'Đang hiệu lực',
                'expired': 'Đã hết hạn',
                'terminated': 'Đã chấm dứt',
                'pending': 'Đang chờ',
            }.get(contract['status'], contract['status'])
            
            days_remaining = None
            if contract['end_date']:
                days_remaining = (contract['end_date'] - date.today()).days
            
            result = (
                f"Hợp đồng #{contract['contract_id']}:\n"
                f"- Phòng: {contract['room_number']} (tầng {contract['floor']}, {contract['area_m2']}m²)\n"
                f"- Thời hạn: {contract['start_date']} → {contract['end_date']}\n"
            )
            if days_remaining is not None:
                if days_remaining > 0:
                    result += f"- Còn lại: {days_remaining} ngày\n"
                else:
                    result += f"- Đã hết hạn: {-days_remaining} ngày trước\n"
            
            result += (
                f"- Tiền thuê: {float(contract['monthly_rent']):,.0f}đ/tháng\n"
                f"- Tiền cọc: {float(contract['deposit_amount']):,.0f}đ\n"
                f"- Trạng thái: {status_text}"
            )
            
            return result
    
    except Exception as e:
        logger.exception(f"get_contract_status error: {e}")
        return f"Lỗi khi tra cứu hợp đồng: {str(e)}"


# ============ Tool 3: get_payment_history ============

class GetPaymentHistoryInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")
    months: int = Field(6, description="Số tháng gần nhất (mặc định 6)")


@tool(args_schema=GetPaymentHistoryInput)
async def get_payment_history(tenant_id: int, months: int = 6) -> str:
    """
    Lấy lịch sử thanh toán của tenant trong N tháng gần nhất.
    """
    from ..core import get_db_pool, current_tenant_id
    
    ctx_tenant_id = current_tenant_id.get()
    if ctx_tenant_id is not None:
        tenant_id = ctx_tenant_id
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            invoices = await conn.fetch("""
                SELECT invoice_id, invoice_month, total_amount, 
                       due_date, paid_date, status
                FROM invoices
                WHERE tenant_id = $1
                  AND invoice_month >= CURRENT_DATE - ($2 || ' months')::INTERVAL
                ORDER BY invoice_month DESC
            """, tenant_id, str(months))
            
            if not invoices:
                return f"Không có lịch sử thanh toán trong {months} tháng gần nhất."
            
            lines = [f"Lịch sử thanh toán {len(invoices)} tháng gần nhất:"]
            for inv in invoices:
                month_str = inv['invoice_month'].strftime("%m/%Y")
                if inv['status'] == 'paid':
                    on_time = inv['paid_date'] and inv['paid_date'] <= inv['due_date']
                    timing = "đúng hạn" if on_time else f"trễ {(inv['paid_date'] - inv['due_date']).days} ngày" if inv['paid_date'] else "N/A"
                    lines.append(
                        f"- T{month_str}: {float(inv['total_amount']):,.0f}đ - "
                        f"Thanh toán {timing} ({inv['paid_date']})"
                    )
                else:
                    lines.append(
                        f"- T{month_str}: {float(inv['total_amount']):,.0f}đ - "
                        f"CHƯA THANH TOÁN (hạn {inv['due_date']})"
                    )
            
            return "\n".join(lines)
    
    except Exception as e:
        logger.exception(f"get_payment_history error: {e}")
        return f"Lỗi khi tra cứu lịch sử: {str(e)}"


# ============ Tool 4: get_room_info ============

class GetRoomInfoInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")


@tool(args_schema=GetRoomInfoInput)
async def get_room_info(tenant_id: int) -> str:
    """
    Lấy thông tin phòng hiện tại của tenant.
    """
    from ..core import get_db_pool, current_tenant_id
    
    ctx_tenant_id = current_tenant_id.get()
    if ctx_tenant_id is not None:
        tenant_id = ctx_tenant_id
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            data = await conn.fetchrow("""
                SELECT t.full_name, t.phone_number, r.room_id, r.room_number,
                       r.floor, r.area_m2, r.monthly_rent, r.electricity_price,
                       r.water_price, r.service_fee, r.max_occupants, r.amenities,
                       c.end_date AS contract_end
                FROM user_profiles t
                LEFT JOIN rooms r ON t.room_id = r.room_id
                LEFT JOIN contracts c ON c.tenant_id = t.tenant_id 
                    AND c.status = 'active'
                WHERE t.tenant_id = $1
            """, tenant_id)
            
            if not data:
                return f"Không tìm thấy tenant {tenant_id}."
            
            if not data['room_id']:
                return f"Tenant {data['full_name']} chưa được gán phòng."
            
            import json
            amenities = data['amenities'] or {}
            if isinstance(amenities, str):
                amenities = json.loads(amenities)
            
            amenity_list = [k for k, v in amenities.items() if v]
            amenity_text = ", ".join(amenity_list) if amenity_list else "không có"
            
            return (
                f"Thông tin phòng của {data['full_name']}:\n"
                f"- Số phòng: {data['room_number']}\n"
                f"- Tầng: {data['floor']}\n"
                f"- Diện tích: {data['area_m2']}m²\n"
                f"- Tiền thuê: {float(data['monthly_rent']):,.0f}đ/tháng\n"
                f"- Số người tối đa: {data['max_occupants']}\n"
                f"- Tiện nghi: {amenity_text}\n"
                f"- SĐT liên hệ: {data['phone_number']}\n"
                + (f"- Hợp đồng đến: {data['contract_end']}" if data['contract_end'] else "")
            )
    
    except Exception as e:
        logger.exception(f"get_room_info error: {e}")
        return f"Lỗi khi tra cứu phòng: {str(e)}"


# ============ Tool 5: query_policies (RAG) ============

class QueryPoliciesInput(BaseModel):
    query: str = Field(..., description="Câu hỏi về chính sách/nội quy")
    tenant_id: Optional[int] = Field(None, description="ID khách thuê (optional, để personalize)")


@tool(args_schema=QueryPoliciesInput)
async def query_policies(query: str, tenant_id: Optional[int] = None) -> str:
    """
    Tra cứu chính sách, nội quy nhà trọ theo câu hỏi.
    
    Sử dụng RAG trên knowledge_base/*.md để tìm thông tin liên quan.
    Phù hợp cho cả khách thuê lẫn khách vãng lai (guest).
    """
    from ..core import get_knowledge_lookup
    
    # Sanitize: strip control chars, limit length
    query = query.strip().replace("\x00", "")[:500]
    if not query:
        return "Câu hỏi trống, vui lòng nhập nội dung cụ thể."
    
    try:
        lookup = get_knowledge_lookup()
        # Lấy nhiều hơn cho guest (không có context cá nhân)
        top_k = 5 if tenant_id is None else 3
        results = await lookup.retrieve(query, top_k=top_k)
        
        if not results:
            # Fallback: thử retrieve_simple nếu LlamaIndex index trống
            try:
                results = await lookup.retrieve_simple(query, top_k=top_k)
            except Exception:
                pass
        
        if not results:
            return (
                "Không tìm thấy thông tin phù hợp trong cơ sở tri thức. "
                "Vui lòng liên hệ quản lý 0901-234-567 để được hỗ trợ."
            )
        
        lines = ["Thông tin tìm được từ Knowledge Base:"]
        for r in results:
            source_label = r.get('source', 'không rõ nguồn')
            score_label = f"{r['score']:.2f}" if r.get('score') else "N/A"
            lines.append(f"\n[Nguồn: {source_label} | Độ liên quan: {score_label}]")
            lines.append(r['text'][:600])
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.exception(f"query_policies error: {e}")
        return f"Lỗi khi tra cứu chính sách: {str(e)}"


# ============ Tool 6: get_room_by_number (Guest-friendly) ============

class GetRoomByNumberInput(BaseModel):
    room_number: str = Field(..., description="Số phòng cần tra cứu (vd: 101, 102, 201)")
    include_tenants: bool = Field(False, description="Có bao gồm thông tin khách thuê hiện tại không")


@tool(args_schema=GetRoomByNumberInput)
async def get_room_by_number(room_number: str, include_tenants: bool = False) -> str:
    """
    Tra cứu thông tin phòng theo số phòng. Dùng được cho cả khách vãng lai và khách thuê.
    Trả về giá thuê, diện tích, tầng, tiện nghi và tình trạng phòng.
    """
    from ..core import get_db_pool

    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            room = await conn.fetchrow("""
                SELECT r.room_id, r.room_number, r.floor, r.area_m2,
                       r.monthly_rent, r.electricity_price, r.water_price,
                       r.service_fee, r.max_occupants, r.amenities,
                       r.status
                FROM rooms r
                WHERE r.room_number = $1
            """, room_number)

            if not room:
                return f"Không tìm thấy phòng {room_number}."

            import json
            amenities = room['amenities'] or {}
            if isinstance(amenities, str):
                amenities = json.loads(amenities)

            amenity_list = [k for k, v in amenities.items() if v]
            amenity_text = ", ".join(amenity_list) if amenity_list else "Chưa cập nhật"

            status_text = {
                'vacant': 'Còn trống',
                'occupied': 'Đã có khách',
                'maintenance': 'Đang bảo trì',
            }.get(room['status'], room['status'] or 'Còn trống')

            result = (
                f"Thông tin phòng {room['room_number']} (Tầng {room['floor']}):\n"
                f"- Diện tích: {room['area_m2']}m²\n"
                f"- Giá thuê: {float(room['monthly_rent']):,.0f}đ/tháng\n"
                f"- Phí điện: {float(room['electricity_price']):,.0f}đ/kWh\n"
                f"- Phí nước: {float(room['water_price']):,.0f}đ/m³\n"
                f"- Phí dịch vụ: {float(room['service_fee']):,.0f}đ/tháng\n"
                f"- Số người tối đa: {room['max_occupants']}\n"
                f"- Tiện nghi: {amenity_text}\n"
                f"- Tình trạng: {status_text}"
            )

            # NOTE: include_tenants được xóa cố ý — LLM không nên biết tên/SL khách
            # thuê của phòng khác (tiếm ẩn prompt injection PII leak).
            # Nếu cần, wrap bằng admin-only endpoint có auth riêng.

            return result

    except Exception as e:
        logger.exception(f"get_room_by_number error: {e}")
        return f"Lỗi khi tra cứu phòng: {str(e)}"


# ============ Export ============

KNOWLEDGE_TOOLS = [
    get_invoice_detail,
    get_contract_status,
    get_payment_history,
    get_room_info,
    query_policies,
    get_room_by_number,
]
