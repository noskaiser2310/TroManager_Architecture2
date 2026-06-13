"""
LLM Intent Router - Quyết định trực tiếp target system dựa trên LLM.
Thay thế KeywordClassifier cũ.
"""

from __future__ import annotations
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

@dataclass
class RouteMatch:
    """Kết quả phân loại route từ LLM."""
    target_system: Literal["SYSTEM1", "SYSTEM2"]
    intent: str | None = None
    matched_keywords: list[str] = None
    confidence: float = 1.0

class LLMIntentRouter:
    """
    Phân loại câu hỏi sử dụng model LLM siêu nhẹ (router_model).
    """
    
    def __init__(self, llm_client=None, config: dict | None = None):
        if llm_client is None:
            from src.llm.llm_client import LLMClient
            llm_client = LLMClient()
        self.llm = llm_client.with_model(llm_client.config.router_model)
        self.timeout = 5.0  # Mặc định 5s, có thể config qua tham số
        if config:
            self.timeout = float(config.get("llm_timeout_seconds", 5.0))
        
    async def classify(self, text: str) -> RouteMatch:
        """
        Quyết định route text sử dụng LLM.
        Timeout protection: nếu LLM không trả lời trong timeout, fallback về SYSTEM2.
        """
        from src.llm.llm_client import LLMMessage
        
        prompt = f"""Bạn là Router hệ thống AI cho nhà trọ.
Hãy đọc câu sau của người dùng: "{text}"

Quyết định hệ thống nào sẽ xử lý:
- SYSTEM1: Câu hỏi đơn giản, giao tiếp bình thường (chào hỏi), tra cứu nội quy cơ bản, hoặc cần trả lời siêu nhanh.
- SYSTEM2: Yêu cầu phức tạp, khiếu nại, báo hỏng hóc, tra cứu tài chính (nợ, hóa đơn, cọc), thao tác hợp đồng, đổi phòng, hoặc cần dùng tools (tra cứu DB, gọi API Zalo).

Hãy xác định:
1. target_system: Chỉ trả về "SYSTEM1" hoặc "SYSTEM2".
2. intent: Ý định của người dùng (vd: "billing_inquiry", "room_inquiry", "maintenance_request", "general_chat", "policy_question").
3. keywords: Các từ khóa chính trong câu.

Trả về duy nhất JSON format:
{{
  "target_system": "SYSTEM1",
  "intent": "general_chat",
  "keywords": ["chào"]
}}"""
        try:
            # Timeout protection: wrap LLM call với asyncio.wait_for
            response = await asyncio.wait_for(
                self.llm.generate(
                    messages=[LLMMessage(role="user", content=prompt)],
                    temperature=0.0,
                    max_tokens=150,
                    response_format={"type": "json_object"}
                ),
                timeout=self.timeout
            )
            
            import re
            
            content = response.content.strip()
            
            # Extract JSON block robustly
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
                
            data = json.loads(json_str)
            
            target = data.get("target_system", "SYSTEM1")
            if target not in ["SYSTEM1", "SYSTEM2"]:
                target = "SYSTEM1"
                
            return RouteMatch(
                target_system=target,
                intent=data.get("intent", "general_chat"),
                matched_keywords=data.get("keywords", []),
                confidence=0.9
            )
        except asyncio.TimeoutError:
            logger.warning(f"LLMIntentRouter timeout after {self.timeout}s — falling back to SYSTEM2")
            return RouteMatch(
                target_system="SYSTEM2",
                intent="general_chat",
                matched_keywords=["<timeout>"],
                confidence=0.5
            )
        except Exception as e:
            logger.error(f"LLMIntentRouter error: {e}")
            # Fallback an toàn về System 2 nếu lỗi LLM
            return RouteMatch(
                target_system="SYSTEM2",
                intent="general_chat",
                matched_keywords=["<error>"],
                confidence=0.5
            )
