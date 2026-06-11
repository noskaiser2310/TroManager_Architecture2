"""
Tests cho System 2 - ReAct Loop.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage, ToolMessage

from src.system2.react_agent import ReActAgent, ReActRequest, ReActState
from src.system2.guardrails import Guardrails
from src.user_modeling.services import BehaviorTracker, ActionTypes


class TestReActAgent:
    """Test ReAct Agent loop."""
    
    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.ainvoke = AsyncMock()
        return llm
    
    @pytest.fixture
    def mock_context_builder(self):
        builder = MagicMock()
        builder.build = AsyncMock()
        return builder
    
    @pytest.fixture
    def mock_guardrails(self):
        guardrails = MagicMock()
        guardrails.check_token_limit = MagicMock(side_effect=lambda msgs, max_t: msgs)
        guardrails.validate_tool_input = MagicMock(return_value=(True, None))
        guardrails.is_sensitive_tool = MagicMock(return_value=False)
        return guardrails
    
    @pytest.fixture
    def mock_profile_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_behavior_tracker(self):
        tracker = MagicMock()
        tracker.log = AsyncMock(return_value=1)
        return tracker
    
    @pytest.fixture
    def agent(self, mock_llm, mock_context_builder, mock_guardrails,
              mock_profile_service, mock_behavior_tracker):
        config = {
            "max_iterations": 4,
            "max_tokens": 8000,
            "temperature": 0.4,
        }
        # Mock system prompt
        with open("config/prompts/system2_prompt.txt", "w") as f:
            f.write("Test prompt template {tenant_name} {tone} {lease_end} {payment_delay_days} {memories} {behavior_summary} {query}")
        
        return ReActAgent(
            config=config,
            llm_client=mock_llm,
            context_builder=mock_context_builder,
            guardrails=mock_guardrails,
            profile_service=mock_profile_service,
            behavior_tracker=mock_behavior_tracker,
        )
    
    @pytest.mark.asyncio
    async def test_final_answer_no_tool_calls(self, agent, mock_llm, mock_context_builder):
        """Test agent trả về final answer khi không có tool calls."""
        from src.user_modeling.services import UserProfile, BehaviorSummary
        from datetime import date, datetime
        
        # Mock context
        mock_context = MagicMock()
        mock_context.profile = UserProfile(
            tenant_id=1,
            full_name="Test User",
            phone_number="0901234567",
            email=None,
            zalo_id=None,
            room_id=101,
            lease_start=date(2024, 1, 1),
            lease_end=date(2026, 12, 31),
            communication_preference="zalo",
            tone_preference="friendly",
            notification_opt_out=[],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_context.behavior = None
        mock_context.memories = []
        mock_context.has_personalization = MagicMock(return_value=False)
        mock_context.behavior_summary_text = MagicMock(return_value="")
        mock_context_builder.build.return_value = mock_context
        
        # Mock LLM trả về final answer (không có tool calls)
        mock_llm.ainvoke.return_value = AIMessage(
            content="Đây là câu trả lời test",
            tool_calls=[],
        )
        
        request = ReActRequest(
            query="Test query",
            tenant_id=1,
            tools=[],
        )
        
        response = await agent.run(request)
        
        assert response.answer == "Đây là câu trả lời test"
        assert response.state == ReActState.COMPLETED
        assert response.iterations == 1
    
    @pytest.mark.asyncio
    async def test_loop_breaker_at_max_iterations(self, agent, mock_llm, mock_context_builder):
        """Test loop breaker khi đạt max iterations."""
        mock_context = MagicMock()
        mock_context.profile = None
        mock_context.behavior = None
        mock_context.memories = []
        mock_context.has_personalization = MagicMock(return_value=False)
        mock_context_builder.build.return_value = mock_context
        
        # Mock LLM luôn trả về tool calls
        from langchain_core.messages import AIMessage
        from uuid import uuid4
        
        mock_response = AIMessage(
            content="",
            tool_calls=[{
                "id": str(uuid4()),
                "name": "some_tool",
                "args": {},
                "type": "tool_call",
            }],
        )
        mock_llm.ainvoke.return_value = mock_response
        
        # Mock tool execution
        async def mock_execute(*args, **kwargs):
            return "Tool result"
        agent._execute_tool = mock_execute
        
        request = ReActRequest(
            query="Test",
            tenant_id=1,
            tools=[MagicMock(name="some_tool")],
        )
        
        response = await agent.run(request)
        
        # Phải đạt max iterations hoặc fail
        assert response.state in [ReActState.LOOP_BREAK, ReActState.FAILED]
        assert response.iterations <= agent.max_iterations + 1
    
    @pytest.mark.asyncio
    async def test_tool_execution_success(self, agent, mock_llm, mock_context_builder):
        """Test tool execution thành công."""
        from langchain_core.messages import AIMessage
        from langchain_core.tools import tool
        from uuid import uuid4

        mock_context = MagicMock()
        mock_context.profile = None
        mock_context.behavior = None
        mock_context.memories = []
        mock_context.has_personalization = MagicMock(return_value=False)
        mock_context_builder.build.return_value = mock_context

        # Define a simple tool
        @tool
        def test_tool() -> str:
            """A test tool."""
            return "Tool executed successfully"

        # LangChain returns tool_calls as dicts (ToolCall is a dict subclass).
        # react_agent.py now has a normalizer that handles both dicts and objects.
        tool_call_dict = {
            "id": str(uuid4()),
            "name": "test_tool",
            "args": {},
            "type": "tool_call",
        }

        # First call returns tool call, second returns final answer
        mock_llm.ainvoke.side_effect = [
            AIMessage(content="", tool_calls=[tool_call_dict]),
            AIMessage(content="Final answer", tool_calls=[]),
        ]
        
        request = ReActRequest(
            query="Test",
            tenant_id=1,
            tools=[test_tool],
        )
        
        response = await agent.run(request)
        
        assert response.state == ReActState.COMPLETED
        assert response.answer == "Final answer"
        assert "test_tool" in response.actions_taken


class TestGuardrails:
    """Test Guardrails."""
    
    def test_sensitive_tool_detection(self):
        """Test phát hiện sensitive tool."""
        guardrails = Guardrails()

        assert guardrails.is_sensitive_tool("send_payment_reminder") is True
        # modify_contract & refund_deposit removed: tools don't exist yet
        assert guardrails.is_sensitive_tool("send_zalo") is False
        assert guardrails.is_sensitive_tool("get_room_info") is False
    
    def test_token_limit_compression(self):
        """Test compression khi quá token limit."""
        from langchain_core.messages import HumanMessage, AIMessage
        
        guardrails = Guardrails(max_tokens=100)
        
        messages = [HumanMessage(content="x" * 200)]  # Very long
        compressed = guardrails.check_token_limit(messages, max_tokens=100)
        
        # Should return some compression
        assert len(compressed) >= 1
    
    def test_validate_tool_input_valid(self):
        """Test validation với input hợp lệ."""
        guardrails = Guardrails()
        
        tool_call = MagicMock()
        tool_call.name = "test_tool"
        tool_call.args = {"key": "value"}
        
        is_valid, error = guardrails.validate_tool_input(tool_call)
        assert is_valid is True
        assert error is None
    
    def test_validate_tool_input_empty_name(self):
        """Test validation với empty name."""
        guardrails = Guardrails()
        
        tool_call = MagicMock()
        tool_call.name = ""
        tool_call.args = {}
        
        is_valid, error = guardrails.validate_tool_input(tool_call)
        assert is_valid is False
    
    def test_fallback_message(self):
        """Test fallback message có nội dung."""
        guardrails = Guardrails()
        message = guardrails.get_fallback_message()
        assert message
        assert len(message) > 0
        # Default message sẽ có "không có" khi phone không được config
        assert "không có" in message

    def test_fallback_message_with_custom_config(self):
        """Test fallback message với custom config từ .env."""
        guardrails = Guardrails(
            fallback_config={
                "contact_name": "anh Minh",
                "contact_phone": "0901234567",
                "message": "Hệ thống đang bận, gọi {contact_label} qua {contact_phone}.",
            }
        )
        message = guardrails.get_fallback_message()
        assert "anh Minh" in message
        assert "0901234567" in message
        # Không còn placeholder chưa render
        assert "{contact_phone}" not in message
        assert "{contact_label}" not in message

    def test_fallback_message_no_hardcoded_phone(self):
        """Đảm bảo fallback không còn hardcode SĐT '0901-234-567'."""
        guardrails = Guardrails(
            fallback_config={"contact_phone": "0987654321"}
        )
        message = guardrails.get_fallback_message()
        # Phone cũ (hardcoded) không xuất hiện
        assert "0901-234-567" not in message
        # Phone mới từ config được dùng
        assert "0987654321" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
