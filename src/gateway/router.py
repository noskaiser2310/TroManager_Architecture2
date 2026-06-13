"""
Router Gateway - Phân luồng request đầu vào.

Quyết định request nào đi vào System 1, request nào đi vào System 2.
"""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional

from .keyword_classifier import KeywordClassifier, KeywordMatch

logger = logging.getLogger(__name__)


class TargetSystem(str, Enum):
    SYSTEM1 = "system1"
    SYSTEM2 = "system2"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class RouteDecision:
    """Quyết định routing cho một request."""
    target_system: TargetSystem
    priority: Priority
    reasoning: str
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    intent: Optional[str] = None
    fallback_on_failure: TargetSystem = TargetSystem.SYSTEM2
    
    def to_dict(self) -> dict:
        return {
            "target_system": self.target_system.value,
            "priority": self.priority.value,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "matched_keywords": self.matched_keywords,
            "intent": self.intent,
            "fallback_on_failure": self.fallback_on_failure.value,
        }


@dataclass
class IncomingRequest:
    """Request đầu vào từ webhook hoặc API."""
    source: Literal["zalo", "sms", "app", "api", "cron", "cli"]
    query: str
    tenant_id: Optional[int] = None
    metadata: dict = field(default_factory=dict)


class RouterGateway:
    """
    Main router class - phân tích và route request.
    
    Logic:
    1. Nếu source == "cron" → System 2
    2. Nếu chứa sensitive keyword → System 2
    3. Nếu chứa complex keyword → System 2
    4. Default → System 1
    """
    
    def __init__(self, config: dict, classifier: Optional[KeywordClassifier] = None):
        self.config = config
        self.classifier = classifier or KeywordClassifier(
            sensitive_keywords=config.get("sensitive_keywords", []),
            complex_keywords=config.get("complex_keywords", []),
            safe_keywords=config.get("safe_keywords", []),
        )
        self.threshold = config.get("threshold_confidence", 0.5)
    
    def route(self, request: IncomingRequest) -> RouteDecision:
        """
        Phân tích request và quyết định route.
        
        Args:
            request: IncomingRequest với source, query, tenant_id
            
        Returns:
            RouteDecision chỉ định target system
        """
        # Step 1: Cron bypass - luôn đi System 2
        if request.source == "cron":
            return RouteDecision(
                target_system=TargetSystem.SYSTEM2,
                priority=Priority.HIGH,
                reasoning="Background event từ Cron Job - luôn xử lý bởi System 2",
                confidence=1.0,
                matched_keywords=[],
                intent="background_event",
            )
        
        # Step 2: Keyword classification
        match = self.classifier.classify(request.query)
        
        # Step 3: Decision logic
        if match.category == "sensitive" or match.confidence > self.threshold:
            target = TargetSystem.SYSTEM2
            # Sensitive (nợ, hợp đồng, v.v.) → ưu tiên cao; complex → bình thường
            priority = Priority.HIGH if match.category == "sensitive" else Priority.NORMAL
            reasoning = f"Phát hiện keyword nhạy cảm/phức tạp: {match.matched_keywords}"
        else:
            target = TargetSystem.SYSTEM1
            priority = Priority.NORMAL
            reasoning = "Câu hỏi đơn giản, có thể xử lý bằng System 1"
        
        # Special case: Quá ngắn (< 3 chars) → System 1
        # Dùng biến local confidence thay vì match.confidence để RouteDecision phản ánh đúng
        final_confidence = match.confidence
        if len(request.query.strip()) < 3:
            target = TargetSystem.SYSTEM1
            priority = Priority.NORMAL
            reasoning = "Tin nhắn quá ngắn - System 1 xử lý"
            final_confidence = 0.6
        
        # Special case: Quá dài (> 500 chars) → System 2 (cần context nhiều)
        if len(request.query) > 500:
            target = TargetSystem.SYSTEM2
            priority = priority if priority == Priority.HIGH else Priority.NORMAL
            reasoning = "Câu hỏi phức tạp/dài - System 2 xử lý"
            final_confidence = max(match.confidence, 0.7)
        
        decision = RouteDecision(
            target_system=target,
            priority=priority,
            reasoning=reasoning,
            confidence=final_confidence,  # dùng final_confidence, không phải match.confidence cứng
            matched_keywords=match.matched_keywords,
            intent=match.intent,
            fallback_on_failure=TargetSystem.SYSTEM2,
        )
        
        logger.info(
            f"Route decision: source={request.source} → {decision.target_system.value} "
            f"(confidence={decision.confidence:.2f}, keywords={decision.matched_keywords})"
        )
        
        return decision


# ============ Helper functions ============

def create_default_router(config: Optional[dict] = None) -> RouterGateway:
    """Factory function tạo router với default config."""
    if config is None:
        config = {
            "sensitive_keywords": [
                "tiền", "nợ", "tiền thuê", "tiền điện", "tiền nước",
                "hợp đồng", "gia hạn", "thanh lý", "chấm dứt",
                "chuyển phòng", "đổi phòng",
                "hóa đơn", "bill",
                "cọc", "hoàn cọc",
            ],
            "complex_keywords": [
                "hỏng", "sửa", "bảo trì", "điều hòa",
                "tìm phòng", "phòng trống",
                "tư vấn", "đề xuất", "gợi ý",
                "phòng", "giá", "diện tích",
                "nội quy", "quy định", "chính sách",
            ],
            "safe_keywords": [
                "chào", "xin chào", "hello", "hi",
                "cảm ơn", "thanks", "ok", "dạ", "vâng",
                "wifi", "mật khẩu wifi", "pass wifi",
                "rác", "đổ rác",
            ],
            "threshold_confidence": 0.5,
        }
    return RouterGateway(config)


# ============ Example usage ============

if __name__ == "__main__":
    # Demo
    router = create_default_router()
    
    test_cases = [
        IncomingRequest(source="zalo", query="Wifi mật khẩu gì?", tenant_id=1),
        IncomingRequest(source="zalo", query="Tôi còn nợ bao nhiêu?", tenant_id=2),
        IncomingRequest(source="zalo", query="Điều hòa phòng tôi bị hỏng", tenant_id=3),
        IncomingRequest(source="zalo", query="Giờ giấc yên tĩnh?", tenant_id=1),
        IncomingRequest(source="cron", query="invoice_overdue", tenant_id=4),
    ]
    
    for req in test_cases:
        decision = router.route(req)
        print(f"\nQuery: {req.query}")
        print(f"  → Target: {decision.target_system.value}")
        print(f"  → Reasoning: {decision.reasoning}")
        print(f"  → Confidence: {decision.confidence:.2f}")
