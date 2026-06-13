"""
Router Gateway - Phân luồng request đầu vào.

Quyết định request nào đi vào System 1, request nào đi vào System 2.
"""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Literal
from .keyword_classifier import LLMIntentRouter, RouteMatch

logger = logging.getLogger(__name__)


class TargetSystem(Enum):
    SYSTEM1 = "system1"  # Fast layer
    SYSTEM2 = "system2"  # ReAct agent


class Priority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


@dataclass
class RouteDecision:
    """Kết quả routing."""
    target_system: TargetSystem
    priority: Priority
    reasoning: str
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)
    intent: str | None = None
    fallback_on_failure: TargetSystem | None = None


@dataclass
class IncomingRequest:
    """Request đầu vào từ webhook hoặc API."""
    source: Literal["zalo", "sms", "app", "api", "cron", "cli"]
    query: str
    tenant_id: Optional[int] = None
    metadata: dict = field(default_factory=dict)


class RouterGateway:
    """
    Main router class - phân tích và route request bằng LLM.
    
    Logic:
    1. Nếu source == "cron" → System 2
    2. Nếu LLM chọn SYSTEM1 → System 1
    3. Nếu LLM chọn SYSTEM2 → System 2
    """
    
    def __init__(self, config: dict, classifier: Optional[LLMIntentRouter] = None):
        self.config = config
        self.classifier = classifier or LLMIntentRouter(config=config)
    
    async def route(self, request: IncomingRequest) -> RouteDecision:
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
        
        # Step 2: Query pre-check
        query = request.query.strip()
        
        # Special case: Quá dài (> 500 chars) → System 2 (cần context nhiều)
        if len(query) > 500:
            return RouteDecision(
                target_system=TargetSystem.SYSTEM2,
                priority=Priority.NORMAL,
                reasoning="Câu hỏi quá dài - mặc định System 2 xử lý",
                confidence=0.8,
                matched_keywords=[],
                intent="general_chat",
                fallback_on_failure=TargetSystem.SYSTEM1,
            )
        
        # Step 3: LLM Intent Routing
        match = await self.classifier.classify(query)
        
        # Mapping từ string SYSTEM1/SYSTEM2 sang Enum
        if match.target_system == "SYSTEM2":
            target = TargetSystem.SYSTEM2
            priority = Priority.NORMAL
            reasoning = "LLM Router quyết định gửi System 2"
        else:
            target = TargetSystem.SYSTEM1
            priority = Priority.NORMAL
            reasoning = "LLM Router quyết định gửi System 1"
            
        decision = RouteDecision(
            target_system=target,
            priority=priority,
            reasoning=reasoning,
            confidence=match.confidence,
            matched_keywords=match.matched_keywords,
            intent=match.intent,
            fallback_on_failure=TargetSystem.SYSTEM2 if target == TargetSystem.SYSTEM1 else None,
        )
        
        logger.info(
            f"Route decision: source={request.source} → {decision.target_system.value} "
            f"(intent={decision.intent}, keywords={decision.matched_keywords})"
        )
        
        return decision


# ============ Helper functions ============

def create_default_router(config: Optional[dict] = None) -> RouterGateway:
    """Factory function tạo router với default config."""
    if config is None:
        config = {
            "llm_timeout_seconds": 5.0,
        }
    return RouterGateway(config)


# ============ Example usage ============

if __name__ == "__main__":
    import asyncio
    
    async def demo():
        router = create_default_router()
        
        test_cases = [
            IncomingRequest(source="zalo", query="Wifi mật khẩu gì?", tenant_id=1),
            IncomingRequest(source="zalo", query="Tôi còn nợ bao nhiêu?", tenant_id=2),
            IncomingRequest(source="zalo", query="Điều hòa phòng tôi bị hỏng", tenant_id=3),
            IncomingRequest(source="zalo", query="Giờ giấc yên tĩnh?", tenant_id=1),
            IncomingRequest(source="cron", query="invoice_overdue", tenant_id=4),
        ]
        
        for req in test_cases:
            decision = await router.route(req)
            print(f"\nQuery: {req.query}")
            print(f"  → Target: {decision.target_system.value}")
            print(f"  → Reasoning: {decision.reasoning}")
            print(f"  → Confidence: {decision.confidence:.2f}")
    
    asyncio.run(demo())
