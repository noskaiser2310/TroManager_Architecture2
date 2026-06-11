"""
Dynamic Persona Optimizer

Reads recent chat logs/memories and uses Gemini 2.5 Structured Output to update the JSONB personalization_profile.
"""

import json
import logging
from typing import Optional, List
from pydantic import BaseModel, Field
import asyncpg
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# ==============================================================================
# Pydantic Schemas for Structured Output
# ==============================================================================

class Demographics(BaseModel):
    age_group: Optional[str] = Field(description="Ví dụ: Gen Z, Millennial, Trung niên, Lớn tuổi")
    occupation: Optional[str] = Field(description="Ví dụ: Sinh viên, NV văn phòng, Làm ca đêm, Tự do")
    family_status: Optional[str] = Field(description="Ví dụ: Độc thân, Có gia đình, Ở ghép")

class FinancialAndHabits(BaseModel):
    financial_capacity: Optional[str] = Field(description="Đánh giá: Ổn định, Thường trễ hạn, Gặp khó khăn")
    living_habits: Optional[str] = Field(description="Ví dụ: Nuôi thú cưng, Thường xuyên nấu ăn, Hay tụ tập")

class Preferences(BaseModel):
    primary_concerns: Optional[str] = Field(description="Ví dụ: Tiếng ồn, Giá cả, Vệ sinh, An ninh, Wifi")
    ai_response_style: str = Field(description="AI nên phản hồi: Dạ/vâng thân thiện, Ngắn gọn súc tích, Chuyên nghiệp")
    active_hours: Optional[str] = Field(description="Ví dụ: Sáng, Tối, Nửa đêm (Rất quan trọng để gửi tin nhắn)")

class InteractionPatterns(BaseModel):
    tech_savvy_level: Optional[str] = Field(description="Cao (thích dùng App), Trung bình, Thấp (chỉ xài Zalo/Gọi)")
    strictness_level: Optional[str] = Field(description="Dễ tính, Hay phàn nàn, Khắt khe")
    late_payment_count: int = Field(description="Số lần đã đóng tiền nhà trễ")

class PersonalizationProfile(BaseModel):
    demographics: Demographics
    financial_and_habits: FinancialAndHabits
    preferences: Preferences
    interaction_patterns: InteractionPatterns
    summary: str = Field(description="Một đoạn văn (tiếng Việt) tóm tắt toàn diện về khách thuê, cách tiếp cận tốt nhất khi đàm phán hoặc đòi nợ.")

# ==============================================================================
# Persona Optimizer Service
# ==============================================================================

class PersonaOptimizer:
    def __init__(self, db_pool: asyncpg.Pool, api_key: str):
        self.db = db_pool
        self.client = genai.Client(api_key=api_key)
        
    async def optimize_tenant_profile(self, tenant_id: int) -> Optional[PersonalizationProfile]:
        """
        Reads recent conversation history and current profile, then runs Gemini Structured Output
        to generate an updated profile.
        """
        # 1. Fetch current profile
        current_profile_json = await self._get_current_profile(tenant_id)
        
        # 2. Fetch recent conversation history (last 10 interactions)
        recent_conversations = await self._get_recent_conversations(tenant_id, limit=10)
        
        if not recent_conversations:
            logger.info(f"No recent conversations for tenant {tenant_id}. Skipping optimization.")
            return None
            
        # 3. Construct prompt
        prompt = f"""
        Bạn là một chuyên gia Tâm lý học Hành vi AI. Nhiệm vụ của bạn là phân tích và cập nhật Hồ sơ Cá nhân hóa của khách thuê dựa trên lịch sử tương tác gần đây.
        
        HỒ SƠ HIỆN TẠI (JSON):
        {json.dumps(current_profile_json, ensure_ascii=False, indent=2)}
        
        CÁC TƯƠNG TÁC GẦN ĐÂY:
        {recent_conversations}
        
        HƯỚNG DẪN QUAN TRỌNG:
        1. Phân tích tin nhắn, thái độ và hành vi của khách thuê. BẤT CỨ SUY LUẬN NÀO ĐƯỢC XUẤT RA PHẢI HOÀN TOÀN BẰNG TIẾNG VIỆT (kể cả các values trong JSON).
        2. Nếu họ đề cập làm ca đêm -> active_hours: "Nửa đêm".
        3. Nếu họ phàn nàn giá cao -> primary_concerns: "Giá cả".
        4. Phân tích ngữ khí để định hình "ai_response_style".
        5. Xuất ra hồ sơ cập nhật dưới định dạng JSON khớp tuyệt đối với schema yêu cầu. (Keys giữ nguyên tiếng Anh, Values phải là Tiếng Việt).
        """
        
        # 4. Call Gemini 2.5 with Structured Output
        logger.info(f"Running Persona Optimizer for tenant {tenant_id}...")
        try:
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PersonalizationProfile,
                    temperature=0.2, # Low temp for analytical extraction
                ),
            )
            
            updated_profile_data = json.loads(response.text)
            validated_profile = PersonalizationProfile(**updated_profile_data)
            
            # 5. Save back to database
            await self._save_profile(tenant_id, updated_profile_data)
            logger.info(f"Successfully updated profile for tenant {tenant_id}.")
            
            return validated_profile
            
        except Exception as e:
            logger.error(f"Failed to optimize persona for tenant {tenant_id}: {e}")
            return None

    async def _get_current_profile(self, tenant_id: int) -> dict:
        sql = "SELECT personalization_profile FROM user_profiles WHERE tenant_id = $1"
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id)
            if row and row['personalization_profile']:
                if isinstance(row['personalization_profile'], str):
                    return json.loads(row['personalization_profile'])
                return row['personalization_profile']
        return {}
        
    async def _get_recent_conversations(self, tenant_id: int, limit: int = 10) -> str:
        sql = """
        SELECT user_message, ai_response, timestamp 
        FROM conversation_history 
        WHERE tenant_id = $1 
        ORDER BY timestamp DESC 
        LIMIT $2
        """
        async with self.db.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, limit)
            
        if not rows:
            return ""
            
        # Reverse to chronological order
        history = reversed(rows)
        formatted_history = []
        for r in history:
            formatted_history.append(f"[{r['timestamp']}] User: {r['user_message']}\n[{r['timestamp']}] AI: {r['ai_response']}")
            
        return "\n\n".join(formatted_history)
        
    async def _save_profile(self, tenant_id: int, profile_dict: dict):
        sql = "UPDATE user_profiles SET personalization_profile = $1 WHERE tenant_id = $2"
        async with self.db.acquire() as conn:
            await conn.execute(sql, json.dumps(profile_dict, ensure_ascii=False), tenant_id)

