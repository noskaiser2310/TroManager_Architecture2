"""
LLM Intent Router - Quyết định target system.

Chiến lược 2 lớp:
1. Keyword pre-filter: chào hỏi/cảm ơn/tạm biệt → SYSTEM1 ngay, không tốn LLM call
2. LLM classifier: câu phức tạp → gọi flash model → SYSTEM1 hoặc SYSTEM2
   Fallback: SYSTEM2 nếu timeout/lỗi (an toàn cho complex queries)
"""

from __future__ import annotations
import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

@dataclass
class RouteMatch:
    target_system: Literal["SYSTEM1", "SYSTEM2"]
    intent: str | None = None
    matched_keywords: list[str] = None
    confidence: float = 1.0

_SYSTEM1_KEYWORDS = {
    "chào": "greeting", "chao": "greeting", "hello": "greeting", "hi": "greeting",
    "xin chào": "greeting", "xin chao": "greeting",
    "cảm ơn": "thanks", "cam on": "thanks", "cám ơn": "thanks", "thank": "thanks",
    "tạm biệt": "goodbye", "tam biet": "goodbye", "bye": "goodbye",
    "không có gì": "dismiss", "ko co gi": "dismiss",
    "dạ": "acknowledge", "da": "acknowledge", "vâng": "acknowledge", "vang": "acknowledge",
    "ok": "acknowledge", "oke": "acknowledge", "được": "acknowledge", "duoc": "acknowledge",
    "ừ": "acknowledge", "uh": "acknowledge",
    "khỏe": "wellbeing", "khoe": "wellbeing",
    "tốt": "wellbeing", "tot": "wellbeing",
    "thời tiết": "weather", "thoi tiet": "weather", "nóng quá": "weather", "nong qua": "weather",
    "mưa": "weather", "mua": "weather", "nắng": "weather", "nang": "weather",
}

_SYSTEM1_PATTERNS = [
    re.compile(r"^(chào|chao|hello|hi|hey)\b", re.IGNORECASE),
    re.compile(r"(cảm ơn|cám ơn|cam on|thank|thanks)$", re.IGNORECASE),
    re.compile(r"^(tạm biệt|tam biet|bye)\b", re.IGNORECASE),
    re.compile(r"^(dạ|da|vâng|vang|oke|ok|ừ|uh)\s*$", re.IGNORECASE),
]


class LLMIntentRouter:
    """
    Phân loại câu hỏi bằng LLM, có keyword pre-filter cho câu đơn giản.
    """

    def __init__(self, llm_client=None, config: dict | None = None):
        if llm_client is None:
            from src.llm.llm_client import LLMClient
            llm_client = LLMClient()
        self.llm = llm_client.with_model(llm_client.config.flash_model)
        self.timeout = 15.0
        if config:
            self.timeout = float(config.get("llm_timeout_seconds", 15.0))

    async def classify(self, text: str) -> RouteMatch:
        # Step 1: Keyword pre-filter — 0 LLM call
        normalized = text.strip().lower()
        words = set(normalized.split())
        matched_intents = []
        for kw, intent in _SYSTEM1_KEYWORDS.items():
            if " " in kw:
                # Multi-word: substring match (e.g. "cam on" in "cam on ban")
                if kw in normalized:
                    matched_intents.append(intent)
            elif len(kw) <= 3:
                # Short keyword: exact word match (e.g. "da" but not "dad")
                if kw in words:
                    matched_intents.append(intent)
            else:
                # Long keyword: substring is safe (e.g. "chao" but "khong" in "khong gian")
                if kw in normalized:
                    matched_intents.append(intent)

        if matched_intents:
            logger.info(
                f"Keyword router: SYSTEM1 (matched={matched_intents})"
            )
            return RouteMatch(
                target_system="SYSTEM1",
                intent=matched_intents[0],
                matched_keywords=list(set(matched_intents)),
                confidence=1.0,
            )

        # Step 2: LLM classifier cho câu phức tạp
        from src.llm.llm_client import LLMMessage

        prompt = f"""Bạn là Router hệ thống AI cho nhà trọ.
Hãy đọc câu sau của người dùng: "{text}"

Quyết định hệ thống nào sẽ xử lý:
- SYSTEM1: Chào hỏi xã giao, cảm ơn, tạm biệt, hỏi thăm sức khỏe/thời tiết, câu hỏi chính sách CHUNG (giờ giấc, an ninh, vệ sinh, nội quy, wifi, giờ mở cổng, gửi xe), câu trả lời ngắn gọn không cần tra cứu DB.
- SYSTEM2: Yêu cầu phức tạp, khiếu nại, báo hỏng hóc, tra cứu tài chính, thao tác hợp đồng, tra cứu cá nhân hóa, hoặc cần gọi tools.
- SYSTEM2: Khi không chắc chắn.

Hãy xác định:
1. target_system: "SYSTEM1" hoặc "SYSTEM2".
2. intent: Ý định của người dùng.
3. keywords: Các từ khóa chính.

Trả về JSON:
{{"target_system": "SYSTEM1", "intent": "general_chat", "keywords": ["chào"]}}"""
        try:
            response = await asyncio.wait_for(
                self.llm.generate(
                    messages=[LLMMessage(role="user", content=prompt)],
                    temperature=0.0,
                    max_tokens=150,
                    response_format={"type": "json_object"},
                ),
                timeout=self.timeout,
            )

            content = response.content.strip()
            json_match = re.search(r"\{.*?\}", content, re.DOTALL)
            json_str = json_match.group(0) if json_match else content
            data = json.loads(json_str)

            target = data.get("target_system", "SYSTEM1")
            if target not in ["SYSTEM1", "SYSTEM2"]:
                target = "SYSTEM1"

            logger.info(
                f"LLM router: {target} (intent={data.get('intent', '?')})"
            )
            return RouteMatch(
                target_system=target,
                intent=data.get("intent", "general_chat"),
                matched_keywords=data.get("keywords", []),
                confidence=0.9,
            )
        except asyncio.TimeoutError:
            logger.warning(
                f"LLM router timeout after {self.timeout}s — SYSTEM2 (safe fallback)"
            )
            return RouteMatch(
                target_system="SYSTEM2", intent="general_chat",
                matched_keywords=["<timeout>"], confidence=0.5,
            )
        except Exception as e:
            logger.error(f"LLM router error: {e}")
            return RouteMatch(
                target_system="SYSTEM2", intent="general_chat",
                matched_keywords=["<error>"], confidence=0.5,
            )
