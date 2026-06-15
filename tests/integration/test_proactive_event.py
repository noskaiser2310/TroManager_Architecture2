"""
Tests cho Proactive Events (Cron + EventDispatcher).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.cron.event_dispatcher import EventDispatcher, BackgroundEvent, AntiSpamGuard


class TestEventDispatcher:
    """Test EventDispatcher."""
    
    @pytest.fixture
    def mock_react_agent(self):
        agent = MagicMock()
        agent.run = AsyncMock()
        return agent
    
    @pytest.fixture
    def mock_behavior_tracker(self):
        tracker = MagicMock()
        tracker.log = AsyncMock(return_value=1)
        tracker.get_anti_spam_check = AsyncMock(return_value={
            "can_send": True,
            "last_reminder": None,
            "count_this_week": 0,
        })
        return tracker
    
    @pytest.fixture
    def mock_tool_registry(self):
        registry = MagicMock()
        registry.get_for_intent = MagicMock(return_value=[])
        return registry
    
    @pytest.fixture
    def dispatcher(self, mock_react_agent, mock_behavior_tracker, mock_tool_registry):
        return EventDispatcher(
            react_agent=mock_react_agent,
            behavior_tracker=mock_behavior_tracker,
            tool_registry=mock_tool_registry,
        )
    
    @pytest.mark.asyncio
    async def test_dispatch_invoice_overdue(self, dispatcher, mock_react_agent, mock_behavior_tracker):
        """Test dispatch invoice_overdue event."""
        from src.system2.react_agent import ReActResponse, ReActState
        
        mock_react_agent.run.return_value = ReActResponse(
            answer="Đã gửi nhắc nhở",
            iterations=2,
            tool_calls=[],
            state=ReActState.COMPLETED,
            latency_ms=1000,
        )
        
        event = BackgroundEvent(
            event_type="invoice_overdue",
            tenant_id=1,
            data={"invoice_id": 100, "amount": 3500000},
            instruction="Nhắc khách đóng tiền",
        )
        
        result = await dispatcher.dispatch(event)
        
        assert "Đã gửi nhắc nhở" in result
        mock_react_agent.run.assert_called_once()
        mock_behavior_tracker.log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_anti_spam_blocks(self, dispatcher, mock_react_agent, mock_behavior_tracker):
        """Test anti-spam block event."""
        # Mock anti-spam returns can_send=False
        mock_behavior_tracker.get_anti_spam_check = AsyncMock(return_value={
            "can_send": False,
            "last_reminder": datetime.now(),
            "count_this_week": 3,
        })
        
        event = BackgroundEvent(
            event_type="invoice_overdue",
            tenant_id=1,
            data={},
        )
        
        result = await dispatcher.dispatch(event)
        
        assert "SKIPPED" in result
        mock_react_agent.run.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_event_intent_mapping(self, dispatcher):
        """Test mapping event types to intents."""
        assert dispatcher.EVENT_INTENT_MAP["invoice_overdue"] == "background_event_invoice_overdue"
        assert dispatcher.EVENT_INTENT_MAP["contract_expiring"] == "background_event_contract_expiring"
        assert dispatcher.EVENT_INTENT_MAP["birthday_greeting"] == "background_event_birthday"


class TestAntiSpamGuard:
    """Test AntiSpamGuard."""
    
    @pytest.mark.asyncio
    async def test_can_send_when_no_history(self):
        """Test cho phép gửi khi chưa có history."""
        mock_tracker = MagicMock()
        mock_tracker.get_anti_spam_check = AsyncMock(return_value={
            "can_send": True,
            "count_this_week": 0,
            "last_reminder": None,
        })
        
        guard = AntiSpamGuard(mock_tracker, max_per_week=2)
        result = await guard.can_send(tenant_id=1, event_type="invoice_overdue")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_blocks_after_max_per_week(self):
        """Test block khi đã đạt max/week."""
        mock_tracker = MagicMock()
        mock_tracker.get_anti_spam_check = AsyncMock(return_value={
            "can_send": False,
            "count_this_week": 3,
            "last_reminder": None,
        })
        
        guard = AntiSpamGuard(mock_tracker, max_per_week=2)
        result = await guard.can_send(tenant_id=1, event_type="invoice_overdue")
        
        assert result is False


class TestProactiveFlow:
    """Integration test cho toàn bộ proactive flow."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_invoice_reminder(self):
        """Test E2E flow: Cron → Dispatcher → Agent → Log."""
        # Mock toàn bộ chain
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock()
        
        mock_tracker = MagicMock()
        mock_tracker.log = AsyncMock()
        mock_tracker.get_anti_spam_check = AsyncMock(return_value={
            "can_send": True, "count_this_week": 0, "last_reminder": None,
        })
        
        mock_registry = MagicMock()
        mock_registry.get_for_intent = MagicMock(return_value=[])
        
        dispatcher = EventDispatcher(
            react_agent=mock_agent,
            behavior_tracker=mock_tracker,
            tool_registry=mock_registry,
        )
        
        # Configure mock agent response
        from src.system2.react_agent import ReActResponse, ReActState
        mock_agent.run.return_value = ReActResponse(
            answer="Đã gửi tin nhắn Zalo",
            iterations=2,
            tool_calls=[],
            state=ReActState.COMPLETED,
            latency_ms=2000,
        )
        
        # Trigger event
        event = BackgroundEvent(
            event_type="invoice_overdue",
            tenant_id=1,
            data={"invoice_id": 5, "amount": 4000000, "days_overdue": 3},
        )
        
        result = await dispatcher.dispatch(event)
        
        # Verify
        assert "Đã gửi tin nhắn" in result
        mock_tracker.log.assert_called_once()
        # Verify logged action
        call_args = mock_tracker.log.call_args
        assert "auto_invoice_overdue" in str(call_args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
