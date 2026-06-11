"""
Decision Toolkit - Tools hỗ trợ ra quyết định về phòng, giá, chuyển phòng.

Tất cả tools query trực tiếp từ PostgreSQL database.
"""

from __future__ import annotations
import logging
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from langchain.tools import tool

logger = logging.getLogger(__name__)


# ============ Tool 1: fetch_available_rooms ============

class FetchAvailableRoomsInput(BaseModel):
    budget_max: Optional[int] = Field(None, description="Ngân sách tối đa (VND)")
    min_area: Optional[float] = Field(None, description="Diện tích tối thiểu (m2)")
    floor_preference: Optional[int] = Field(None, description="Tầng mong muốn (1-3)")


@tool(args_schema=FetchAvailableRoomsInput)
async def fetch_available_rooms(
    budget_max: Optional[int] = None,
    min_area: Optional[float] = None,
    floor_preference: Optional[int] = None,
) -> str:
    """
    Lấy danh sách phòng trống phù hợp với tiêu chí.
    
    Dùng khi khách hỏi về phòng trống, tìm phòng mới, hoặc xem giá phòng.
    Query trực tiếp từ bảng `rooms` trong PostgreSQL.
    """
    from ..core import get_db_pool
    
    try:
        pool = get_db_pool()
        
        # Build query động
        conditions = ["status = 'available'"]
        params = []
        
        if budget_max is not None:
            params.append(budget_max)
            conditions.append(f"monthly_rent <= ${len(params)}")
        
        if min_area is not None:
            params.append(min_area)
            conditions.append(f"area_m2 >= ${len(params)}")
        
        if floor_preference is not None:
            params.append(floor_preference)
            conditions.append(f"floor = ${len(params)}")
        
        where_clause = " AND ".join(conditions)
        sql = f"""
        SELECT room_id, room_number, floor, area_m2, monthly_rent,
               electricity_price, water_price, service_fee, max_occupants
        FROM rooms
        WHERE {where_clause}
        ORDER BY monthly_rent ASC
        LIMIT 20
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        if not rows:
            return "Hiện tại không có phòng trống phù hợp với tiêu chí của khách."
        
        # Format response
        lines = [f"Có {len(rows)} phòng trống phù hợp:"]
        for r in rows:
            lines.append(
                f"- Phòng {r['room_number']} (tầng {r['floor']}): "
                f"{r['area_m2']}m², {r['monthly_rent']:,.0f}đ/tháng, "
                f"tối đa {r['max_occupants']} người"
            )
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.exception(f"fetch_available_rooms error: {e}")
        return f"Lỗi khi truy vấn phòng: {str(e)}"


# ============ Tool 2: calc_rent ============

class CalcRentInput(BaseModel):
    room_id: int = Field(..., description="ID phòng cần tính tiền")
    month: str = Field(..., description="Tháng cần tính, format YYYY-MM")
    electricity_kwh: Optional[float] = Field(0, description="Số kWh điện tiêu thụ (mặc định lấy từ chỉ số)")
    water_m3: Optional[float] = Field(0, description="Số m3 nước tiêu thụ (mặc định lấy từ chỉ số)")


@tool(args_schema=CalcRentInput)
async def calc_rent(
    room_id: int,
    month: str,
    electricity_kwh: float = 0,
    water_m3: float = 0,
) -> str:
    """
    Tính tổng tiền thuê phòng trong tháng.
    
    Bao gồm: tiền phòng + điện + nước + phí dịch vụ.
    Nếu không truyền electricity_kwh/water_m3, sẽ tự lấy từ bảng invoices.
    """
    from ..core import get_db_pool
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            # Lấy thông tin phòng
            room = await conn.fetchrow(
                """SELECT room_id, room_number, monthly_rent, 
                          electricity_price, water_price, service_fee
                FROM rooms WHERE room_id = $1""",
                room_id
            )
            
            if not room:
                return f"Không tìm thấy phòng với ID {room_id}"
            
            # Lấy chỉ số điện nước từ invoice nếu chưa truyền
            if electricity_kwh == 0 or water_m3 == 0:
                invoice = await conn.fetchrow(
                    """SELECT electricity_kwh, water_m3 
                    FROM invoices 
                    WHERE room_id = $1 AND TO_CHAR(invoice_month, 'YYYY-MM') = $2""",
                    room_id, month
                )
                if invoice:
                    if electricity_kwh == 0:
                        electricity_kwh = float(invoice['electricity_kwh'] or 0)
                    if water_m3 == 0:
                        water_m3 = float(invoice['water_m3'] or 0)
            
            # Tính tiền
            base_rent = float(room['monthly_rent'])
            elec_cost = electricity_kwh * float(room['electricity_price'])
            water_cost = water_m3 * float(room['water_price'])
            service_cost = float(room['service_fee'])
            total = base_rent + elec_cost + water_cost + service_cost
            
            return (
                f"Tính tiền phòng {room['room_number']} tháng {month}:\n"
                f"- Tiền phòng: {base_rent:,.0f}đ\n"
                f"- Tiền điện ({electricity_kwh} kWh × {room['electricity_price']:,.0f}đ): {elec_cost:,.0f}đ\n"
                f"- Tiền nước ({water_m3} m³ × {room['water_price']:,.0f}đ): {water_cost:,.0f}đ\n"
                f"- Phí dịch vụ: {service_cost:,.0f}đ\n"
                f"- TỔNG: {total:,.0f}đ"
            )
    
    except Exception as e:
        logger.exception(f"calc_rent error: {e}")
        return f"Lỗi khi tính tiền: {str(e)}"


# ============ Tool 3: recommend_transfer ============

class RecommendTransferInput(BaseModel):
    tenant_id: int = Field(..., description="ID khách thuê")


@tool(args_schema=RecommendTransferInput)
async def recommend_transfer(tenant_id: int) -> str:
    """
    Đề xuất phòng phù hợp hơn cho tenant.
    
    Logic:
    - Đọc lịch sử behavior_logs của tenant
    - Phân tích: noise_complaint, maintenance_issues, room_transfer requests
    - Tìm phòng trống phù hợp với nhu cầu suy ra
    """
    from ..core import get_db_pool
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            # Lấy thông tin tenant hiện tại
            tenant = await conn.fetchrow("""
                SELECT t.tenant_id, t.full_name, t.room_id, r.floor, r.area_m2, r.monthly_rent
                FROM user_profiles t
                LEFT JOIN rooms r ON t.room_id = r.room_id
                WHERE t.tenant_id = $1
            """, tenant_id)
            
            if not tenant:
                return f"Không tìm thấy tenant {tenant_id}"
            
            # Lấy behavior insights
            noise_count = await conn.fetchval("""
                SELECT COUNT(*) FROM behavior_logs
                WHERE tenant_id = $1 AND action_type = 'noise_complaint'
                  AND timestamp > CURRENT_DATE - INTERVAL '90 days'
            """, tenant_id)
            
            maintenance_count = await conn.fetchval("""
                SELECT COUNT(*) FROM behavior_logs
                WHERE tenant_id = $1 AND action_type = 'maintenance_request'
                  AND timestamp > CURRENT_DATE - INTERVAL '90 days'
            """, tenant_id)
            
            # Logic đề xuất
            current_floor = tenant['floor']
            preferred_floor = current_floor
            reason = ""
            
            if noise_count and noise_count >= 2:
                # Nhiều khiếu nại tiếng ồn → đề xuất tầng cao hơn
                preferred_floor = min(3, current_floor + 1)
                reason = f"Khách có {noise_count} khiếu nại tiếng ồn trong 90 ngày qua → đề xuất tầng cao hơn"
            
            # Tìm phòng phù hợp
            candidate_rooms = await conn.fetch("""
                SELECT room_id, room_number, floor, area_m2, monthly_rent
                FROM rooms
                WHERE status = 'available'
                  AND floor = $1
                  AND area_m2 >= $2
                ORDER BY monthly_rent ASC
                LIMIT 3
            """, preferred_floor, float(tenant['area_m2'] or 0))
            
            if not candidate_rooms:
                # Fallback: tìm bất kỳ phòng trống nào
                candidate_rooms = await conn.fetch("""
                    SELECT room_id, room_number, floor, area_m2, monthly_rent
                    FROM rooms
                    WHERE status = 'available'
                    ORDER BY monthly_rent ASC
                    LIMIT 3
                """)
            
            if not candidate_rooms:
                return "Hiện không có phòng trống phù hợp để đề xuất."
            
            # Format
            lines = [
                f"Đề xuất phòng cho khách {tenant['full_name']} (đang ở phòng {tenant['room_id']}, tầng {current_floor}):",
            ]
            if reason:
                lines.append(f"Lý do đề xuất: {reason}")
            lines.append("")
            
            for r in candidate_rooms:
                lines.append(
                    f"- Phòng {r['room_number']} (tầng {r['floor']}): "
                    f"{r['area_m2']}m², {r['monthly_rent']:,.0f}đ/tháng"
                )
            
            lines.append("\nBước tiếp theo: Hỏi khách có muốn xem phòng cụ thể nào không.")
            
            return "\n".join(lines)
    
    except Exception as e:
        logger.exception(f"recommend_transfer error: {e}")
        return f"Lỗi khi đề xuất phòng: {str(e)}"


# ============ Tool 4: compare_rooms ============

class CompareRoomsInput(BaseModel):
    room_id_1: int = Field(..., description="ID phòng thứ nhất")
    room_id_2: int = Field(..., description="ID phòng thứ hai")


@tool(args_schema=CompareRoomsInput)
async def compare_rooms(room_id_1: int, room_id_2: int) -> str:
    """
    So sánh chi tiết 2 phòng để giúp khách quyết định.
    """
    from ..core import get_db_pool
    
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            rooms = await conn.fetch("""
                SELECT room_id, room_number, floor, area_m2, monthly_rent,
                       electricity_price, water_price, service_fee, max_occupants
                FROM rooms
                WHERE room_id IN ($1, $2)
            """, room_id_1, room_id_2)
            
            if len(rooms) < 2:
                return "Không tìm thấy đủ 2 phòng để so sánh."
            
            r1, r2 = rooms
            
            def room_to_dict(r):
                return {
                    "Số phòng": r['room_number'],
                    "Tầng": r['floor'],
                    "Diện tích": f"{r['area_m2']}m²",
                    "Giá thuê": f"{r['monthly_rent']:,.0f}đ",
                    "Giá điện": f"{r['electricity_price']:,.0f}đ/kWh",
                    "Giá nước": f"{r['water_price']:,.0f}đ/m³",
                    "Phí DV": f"{r['service_fee']:,.0f}đ",
                    "Max người": r['max_occupants'],
                }
            
            d1 = room_to_dict(r1)
            d2 = room_to_dict(r2)
            
            lines = ["So sánh 2 phòng:"]
            lines.append("")
            for k in d1.keys():
                lines.append(f"**{k}**: Phòng {d1[k.split(':')[0]] if False else ''}{d1[k]} | Phòng {d2[k]}")
            
            # Recommendation
            cheaper = r1 if r1['monthly_rent'] < r2['monthly_rent'] else r2
            bigger = r1 if r1['area_m2'] > r2['area_m2'] else r2
            
            lines.append("")
            lines.append(f"Phòng rẻ hơn: {cheaper['room_number']} ({cheaper['monthly_rent']:,.0f}đ)")
            lines.append(f"Phòng rộng hơn: {bigger['room_number']} ({bigger['area_m2']}m²)")
            lines.append(f"Chênh lệch giá: {abs(float(r1['monthly_rent']) - float(r2['monthly_rent'])):,.0f}đ/tháng")
            
            return "\n".join(lines)
    
    except Exception as e:
        logger.exception(f"compare_rooms error: {e}")
        return f"Lỗi khi so sánh phòng: {str(e)}"


# ============ Export ============

DECISION_TOOLS = [
    fetch_available_rooms,
    calc_rent,
    recommend_transfer,
    compare_rooms,
]
