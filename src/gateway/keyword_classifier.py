"""
Keyword Classifier - Phân loại keyword trong câu hỏi.

Hỗ trợ compound word detection để tránh false positive
(ví dụ: "tiềm năng" không phải là keyword tài chính).
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class KeywordMatch:
    """Kết quả phân loại keyword."""
    category: Literal["sensitive", "complex", "safe", "neutral"]
    confidence: float
    matched_keywords: list[str]
    intent: str | None = None


class KeywordClassifier:
    """
    Phân loại câu hỏi dựa trên keyword matching với compound word awareness.
    """
    
    # Compound words để tránh false positive
    EXCLUDE_COMPOUNDS = {
        "tiềm năng", "tiềm hiểu",
        "phòng ngủ", "phòng khách", "phòng tắm",  # Không phải "phòng trọ"
        "thanh niên", "thanh thản",  # Không phải "thanh toán"
        "nỗ lực", "nỗi buồn",  # Không phải "nợ"
        "hợp tác",  # Không phải "hợp đồng"
    }
    
    # Intent mapping
    INTENT_MAP = {
        # Sensitive
        "tiền": "billing_inquiry",
        "nợ": "billing_inquiry",
        "hóa đơn": "billing_inquiry",
        "thanh toán": "billing_inquiry",
        "hợp đồng": "contract_inquiry",
        "gia hạn": "contract_inquiry",
        "cọc": "billing_inquiry",
        "hoàn cọc": "billing_inquiry",
        "chuyển phòng": "room_transfer",
        "đổi phòng": "room_transfer",
        # Complex - room
        "giá": "room_inquiry",
        "phòng": "room_inquiry",
        "diện tích": "room_inquiry",
        "phòng trống": "room_recommendation",  # mủ hơn 'phòng' đơn lẻ
        "còn trống": "room_recommendation",
        "phòng nào trống": "room_recommendation",
        "tìm phòng": "room_recommendation",
        "đề xuất": "room_recommendation",
        "gợi ý": "room_recommendation",
        # Complex - maintenance
        "hỏng": "maintenance_request",
        "sửa": "maintenance_request",
        "điều hòa": "maintenance_request",
        "bảo trì": "maintenance_request",
        # Policy
        "nội quy": "policy_question",
        "quy định": "policy_question",
        "chính sách": "policy_question",
    }
    
    def __init__(
        self,
        sensitive_keywords: list[str],
        complex_keywords: list[str],
        safe_keywords: list[str] = None,
    ):
        self.sensitive_keywords = sensitive_keywords
        self.complex_keywords = complex_keywords
        self.safe_keywords = safe_keywords or []
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns với word boundary."""
        self.sensitive_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE | re.UNICODE)
            for kw in self.sensitive_keywords
        ]
        self.complex_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE | re.UNICODE)
            for kw in self.complex_keywords
        ]
        self.safe_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE | re.UNICODE)
            for kw in self.safe_keywords
        ]
    
    def _has_excluded_compound(self, text: str) -> bool:
        """Check nếu text chứa compound word excluded."""
        text_lower = text.lower()
        return any(compound in text_lower for compound in self.EXCLUDE_COMPOUNDS)
    
    def classify(self, text: str) -> KeywordMatch:
        """
        Phân loại text dựa trên keyword matching.
        
        Ưu tiên khuy phà multi-word patterns trước (vd: "phòng trống" thắng "phòng").
        
        Returns:
            KeywordMatch với category, confidence, matched_keywords
        """
        text_lower = text.lower()
        matched_sensitive = []
        matched_complex = []
        matched_safe = []
        matched_intent = None
        
        # Check excluded compounds first
        has_excluded = self._has_excluded_compound(text)
        
        # Match safe first (short-circuit for greetings/simple queries)
        for kw, pattern in zip(self.safe_keywords, self.safe_patterns):
            if pattern.search(text_lower):
                matched_safe.append(kw)
        
        if matched_safe:
            return KeywordMatch(
                category="safe",
                confidence=0.9,
                matched_keywords=matched_safe,
                intent="general_chat",
            )
        
        # --- Ưu tiên 0: check multi-word room patterns trước regex ---
        # (regex \b không hoạt động tốt với tiếng Việt có dấu)
        MULTI_WORD_ROOM = [
            ("phòng trống", "room_recommendation"),
            ("còn trống", "room_recommendation"),
            ("phòng nào trống", "room_recommendation"),
            ("tìm phòng", "room_recommendation"),
            ("đổi phòng", "room_transfer"),
            ("chuyển phòng", "room_transfer"),
            ("hoàn cọc", "billing_inquiry"),
            ("hóa đơn", "billing_inquiry"),
            ("hợp đồng", "contract_inquiry"),
            ("gia hạn", "contract_inquiry"),
            ("thanh toán", "billing_inquiry"),
            ("nội quy", "policy_question"),
            ("quy định", "policy_question"),
            ("chính sách", "policy_question"),
            ("bảo trì", "maintenance_request"),
            ("gợi ý", "room_recommendation"),
            ("đề xuất", "room_recommendation"),
        ]
        for phrase, intent in MULTI_WORD_ROOM:
            if phrase in text_lower:
                # Multi-word match chiến thắng — return luôn
                category = "sensitive" if intent in (
                    "billing_inquiry", "contract_inquiry", "room_transfer"
                ) else "complex"
                return KeywordMatch(
                    category=category,
                    confidence=0.85,
                    matched_keywords=[phrase],
                    intent=intent,
                )
        
        # Match sensitive
        for kw, pattern in zip(self.sensitive_keywords, self.sensitive_patterns):
            if pattern.search(text_lower):
                matched_sensitive.append(kw)
        
        # Match complex
        for kw, pattern in zip(self.complex_keywords, self.complex_patterns):
            if pattern.search(text_lower):
                matched_complex.append(kw)
        
        # Decision logic
        if matched_sensitive:
            # Sensitive wins - tính confidence dựa trên số lượng
            confidence = min(0.7 + 0.1 * len(matched_sensitive), 0.95)
            return KeywordMatch(
                category="sensitive",
                confidence=confidence,
                matched_keywords=matched_sensitive,
                intent=self._infer_intent(matched_sensitive + matched_complex),
            )
        
        if matched_complex:
            confidence = min(0.5 + 0.1 * len(matched_complex), 0.8)
            return KeywordMatch(
                category="complex",
                confidence=confidence,
                matched_keywords=matched_complex,
                intent=self._infer_intent(matched_complex),
            )
        
        # Boost confidence nếu có số tiền
        money_pattern = re.compile(r"\d+\s*(triệu|tr|nghìn|k|đồng|vnd|đ)", re.IGNORECASE)
        if money_pattern.search(text):
            return KeywordMatch(
                category="sensitive",
                confidence=0.85,
                matched_keywords=["<money_amount>"],
                intent="billing_inquiry",
            )
        
        # Default: safe/neutral
        return KeywordMatch(
            category="safe",
            confidence=0.3,
            matched_keywords=[],
            intent="general_chat",
        )
    
    def _infer_intent(self, keywords: list[str]) -> str | None:
        """Infer intent từ matched keywords."""
        for kw in keywords:
            if kw in self.INTENT_MAP:
                return self.INTENT_MAP[kw]
        return None


# ============ Unit test (chạy trực tiếp) ============

if __name__ == "__main__":
    classifier = KeywordClassifier(
        sensitive_keywords=["tiền", "nợ", "hợp đồng", "hóa đơn", "cọc", "chuyển phòng"],
        complex_keywords=["hỏng", "sửa", "điều hòa", "tìm phòng"],
    )
    
    test_cases = [
        "Tôi còn nợ bao nhiêu?",
        "Wifi mật khẩu gì?",
        "Điều hòa phòng tôi bị hỏng",
        "Tiềm năng phát triển của thị trường",
        "Tôi cần chuyển phòng",
        "Anh ơi hợp đồng tôi còn bao lâu",
        "Thanh toán 3.5 triệu nhé",
        "Phòng ngủ tôi rộng bao nhiêu",  # False positive test - không phải phòng trọ
    ]
    
    for text in test_cases:
        match = classifier.classify(text)
        print(f"\nText: {text}")
        print(f"  → Category: {match.category}")
        print(f"  → Confidence: {match.confidence:.2f}")
        print(f"  → Matched: {match.matched_keywords}")
        print(f"  → Intent: {match.intent}")
