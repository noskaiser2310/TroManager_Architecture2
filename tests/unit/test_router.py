"""
Tests cho Router Gateway - LLMIntentRouter + RouterGateway.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.gateway.router import (
    RouterGateway,
    IncomingRequest,
    TargetSystem,
    Priority,
    RouteDecision,
)
from src.gateway.keyword_classifier import LLMIntentRouter, RouteMatch


class TestLLMIntentRouter:
    """Test LLMIntentRouter với mock LLM client."""

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.generate = AsyncMock()
        return llm

    @pytest.fixture
    def router(self, mock_llm):
        r = LLMIntentRouter(llm_client=mock_llm, config={"llm_timeout_seconds": 5.0})
        r.llm = mock_llm
        return r

    @pytest.mark.asyncio
    async def test_classify_system1(self, router, mock_llm):
        """Test classify trả về SYSTEM1 cho câu hỏi đơn giản."""
        mock_llm.generate.return_value = MagicMock(
            content='{"target_system": "SYSTEM1", "intent": "general_chat", "keywords": ["chào"]}'
        )
        result = await router.classify("Chào bạn")
        assert result.target_system == "SYSTEM1"
        assert result.intent == "general_chat"
        assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_classify_system2(self, router, mock_llm):
        """Test classify trả về SYSTEM2 cho câu hỏi phức tạp."""
        mock_llm.generate.return_value = MagicMock(
            content='{"target_system": "SYSTEM2", "intent": "billing_inquiry", "keywords": ["nợ", "tiền"]}'
        )
        result = await router.classify("Tôi còn nợ bao nhiêu?")
        assert result.target_system == "SYSTEM2"
        assert result.intent == "billing_inquiry"
        assert "nợ" in result.matched_keywords

    @pytest.mark.asyncio
    async def test_classify_timeout_fallback(self, router, mock_llm):
        """Test timeout fallback về SYSTEM2."""
        import asyncio
        mock_llm.generate.side_effect = asyncio.TimeoutError()
        result = await router.classify("Test timeout")
        assert result.target_system == "SYSTEM2"
        assert result.confidence == 0.5

    @pytest.mark.asyncio
    async def test_classify_error_fallback(self, router, mock_llm):
        """Test LLM error fallback về SYSTEM2."""
        mock_llm.generate.side_effect = Exception("API error")
        result = await router.classify("Test error")
        assert result.target_system == "SYSTEM2"
        assert result.confidence == 0.5

    @pytest.mark.asyncio
    async def test_invalid_json_fallback_system2(self, router, mock_llm):
        """Test invalid JSON bị lỗi → fallback SYSTEM2 (an toàn)."""
        mock_llm.generate.return_value = MagicMock(content="not json")
        result = await router.classify("Test bad json")
        assert result.target_system == "SYSTEM2"
        assert result.confidence == 0.5


class TestRouterGateway:
    """Test RouterGateway routing logic."""

    @pytest.fixture
    def mock_classifier(self):
        classifier = MagicMock(spec=LLMIntentRouter)
        classifier.classify = AsyncMock()
        return classifier

    @pytest.fixture
    def router(self, mock_classifier):
        return RouterGateway(config={"llm_timeout_seconds": 5.0}, classifier=mock_classifier)

    @pytest.mark.asyncio
    async def test_cron_bypass_to_system2(self, router):
        """Test event từ cron luôn đi System 2."""
        req = IncomingRequest(source="cron", query="anything", tenant_id=1)
        decision = await router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
        assert decision.priority == Priority.HIGH
        assert decision.intent == "background_event"

    @pytest.mark.asyncio
    async def test_long_query_to_system2(self, router):
        """Test query > 500 chars đi System 2."""
        long_msg = "Tôi muốn hỏi " + "nhiều thứ " * 100
        req = IncomingRequest(source="zalo", query=long_msg, tenant_id=1)
        decision = await router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
        assert decision.priority == Priority.NORMAL
        assert decision.fallback_on_failure == TargetSystem.SYSTEM1

    @pytest.mark.asyncio
    async def test_llm_says_system1(self, router, mock_classifier):
        """Test LLM trả về SYSTEM1 → route đến System1."""
        mock_classifier.classify.return_value = RouteMatch(
            target_system="SYSTEM1",
            intent="general_chat",
            matched_keywords=["chào"],
            confidence=0.9,
        )
        req = IncomingRequest(source="zalo", query="Chào bạn", tenant_id=1)
        decision = await router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM1
        assert decision.fallback_on_failure == TargetSystem.SYSTEM2

    @pytest.mark.asyncio
    async def test_llm_says_system2(self, router, mock_classifier):
        """Test LLM trả về SYSTEM2 → route đến System2."""
        mock_classifier.classify.return_value = RouteMatch(
            target_system="SYSTEM2",
            intent="billing_inquiry",
            matched_keywords=["nợ", "tiền"],
            confidence=0.9,
        )
        req = IncomingRequest(source="zalo", query="Tôi còn nợ bao nhiêu?", tenant_id=1)
        decision = await router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
        assert decision.fallback_on_failure is None

    @pytest.mark.asyncio
    async def test_decision_has_confidence(self, router, mock_classifier):
        """Test decision có confidence score."""
        mock_classifier.classify.return_value = RouteMatch(
            target_system="SYSTEM1",
            intent="general_chat",
            confidence=0.9,
        )
        req = IncomingRequest(source="zalo", query="Wifi?", tenant_id=1)
        decision = await router.route(req)
        assert 0.0 <= decision.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_decision_has_reasoning(self, router, mock_classifier):
        """Test decision có reasoning text."""
        mock_classifier.classify.return_value = RouteMatch(
            target_system="SYSTEM1",
            intent="general_chat",
        )
        req = IncomingRequest(source="zalo", query="Ok", tenant_id=1)
        decision = await router.route(req)
        assert decision.reasoning
        assert len(decision.reasoning) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
