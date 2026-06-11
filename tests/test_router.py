"""
Tests cho Router Gateway.
"""

import pytest
from src.gateway import (
    RouterGateway,
    IncomingRequest,
    TargetSystem,
    Priority,
    create_default_router,
)
from src.gateway.keyword_classifier import KeywordClassifier


class TestKeywordClassifier:
    """Test KeywordClassifier."""
    
    @pytest.fixture
    def classifier(self):
        return KeywordClassifier(
            sensitive_keywords=["tiền", "nợ", "hợp đồng", "hóa đơn", "cọc", "chuyển phòng"],
            complex_keywords=["hỏng", "sửa", "điều hòa", "tìm phòng"],
        )
    
    def test_sensitive_keyword_detected(self, classifier):
        """Test phát hiện keyword nhạy cảm."""
        result = classifier.classify("Tôi còn nợ bao nhiêu?")
        assert result.category == "sensitive"
        assert "nợ" in result.matched_keywords
        assert result.confidence > 0.7
    
    def test_safe_keyword_not_sensitive(self, classifier):
        """Test keyword an toàn không bị phân loại nhạy cảm."""
        result = classifier.classify("Wifi mật khẩu gì?")
        assert result.category == "safe"
        assert result.confidence < 0.5
    
    def test_complex_keyword(self, classifier):
        """Test keyword phức tạp."""
        result = classifier.classify("Điều hòa phòng tôi bị hỏng")
        assert result.category == "complex"
        assert "hỏng" in result.matched_keywords or "điều hòa" in result.matched_keywords
    
    def test_money_amount_triggers_sensitive(self, classifier):
        """Test số tiền trigger sensitive."""
        result = classifier.classify("Tôi cần thanh toán 3.5 triệu")
        assert result.category == "sensitive"
        assert result.confidence > 0.8
    
    def test_false_positive_excluded(self, classifier):
        """Test compound word excluded."""
        result = classifier.classify("Phòng ngủ tôi rộng bao nhiêu?")
        # "phòng" không nên match "phòng trọ" / "chuyển phòng"
        # Tuy nhiên trong test này, classifier không có "phòng" trong sensitive
        # nên sẽ là safe
        assert result.category in ["safe", "neutral"]
    
    def test_intent_inference(self, classifier):
        """Test infer intent từ keyword."""
        result = classifier.classify("Hợp đồng tôi còn bao lâu?")
        assert result.intent == "contract_inquiry"
        
        result2 = classifier.classify("Điều hòa hỏng")
        assert result2.intent == "maintenance_request"


class TestRouterGateway:
    """Test RouterGateway."""
    
    @pytest.fixture
    def router(self):
        return create_default_router()
    
    def test_cron_bypass_to_system2(self, router):
        """Test event từ cron luôn đi System 2."""
        req = IncomingRequest(source="cron", query="anything", tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
        assert decision.priority == Priority.HIGH
        assert decision.intent == "background_event"
    
    def test_sensitive_query_to_system2(self, router):
        """Test câu hỏi nhạy cảm đi System 2."""
        req = IncomingRequest(source="zalo", query="Tôi còn nợ bao nhiêu?", tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
        assert "nợ" in decision.matched_keywords
    
    def test_complex_query_to_system2(self, router):
        """Test câu hỏi phức tạp đi System 2."""
        req = IncomingRequest(source="zalo", query="Điều hòa phòng tôi bị hỏng", tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
    
    def test_safe_query_to_system1(self, router):
        """Test câu hỏi đơn giản đi System 1."""
        req = IncomingRequest(source="zalo", query="Wifi mật khẩu gì?", tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM1
    
    def test_very_short_message_to_system1(self, router):
        """Test tin nhắn quá ngắn đi System 1."""
        req = IncomingRequest(source="zalo", query="ok", tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM1
    
    def test_very_long_message_to_system2(self, router):
        """Test tin nhắn quá dài đi System 2."""
        long_msg = "Tôi muốn hỏi " + "nhiều thứ " * 100
        req = IncomingRequest(source="zalo", query=long_msg, tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == TargetSystem.SYSTEM2
    
    def test_decision_includes_confidence(self, router):
        """Test decision có confidence score."""
        req = IncomingRequest(source="zalo", query="Còn nợ không?", tenant_id=1)
        decision = router.route(req)
        assert 0.0 <= decision.confidence <= 1.0
    
    def test_decision_has_reasoning(self, router):
        """Test decision có reasoning."""
        req = IncomingRequest(source="zalo", query="Wifi?", tenant_id=1)
        decision = router.route(req)
        assert decision.reasoning
        assert len(decision.reasoning) > 0


class TestRoutingScenarios:
    """Test các kịch bản routing thực tế."""
    
    @pytest.fixture
    def router(self):
        return create_default_router()
    
    @pytest.mark.parametrize("query,expected_system,expected_keywords", [
        ("Wifi mật khẩu gì?", TargetSystem.SYSTEM1, []),
        ("Tôi còn nợ bao nhiêu?", TargetSystem.SYSTEM2, ["nợ"]),
        ("Điều hòa hỏng", TargetSystem.SYSTEM2, ["điều hòa", "hỏng"]),
        ("Giờ giấc yên tĩnh?", TargetSystem.SYSTEM1, []),
        ("Hợp đồng còn bao lâu?", TargetSystem.SYSTEM2, ["hợp đồng"]),
        ("Có phòng trống không?", TargetSystem.SYSTEM2, ["phòng trống"]),  # complex
        ("Tôi muốn chuyển phòng", TargetSystem.SYSTEM2, ["chuyển phòng"]),
        ("Phí gửi xe bao nhiêu?", TargetSystem.SYSTEM1, []),
    ])
    def test_routing_scenarios(self, router, query, expected_system, expected_keywords):
        """Test các kịch bản routing phổ biến."""
        req = IncomingRequest(source="zalo", query=query, tenant_id=1)
        decision = router.route(req)
        assert decision.target_system == expected_system
        for kw in expected_keywords:
            assert kw in decision.matched_keywords or any(kw in mk for mk in decision.matched_keywords)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
