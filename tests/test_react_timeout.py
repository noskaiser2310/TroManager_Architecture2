"""
Tests cho tool & LLM timeout protection trong ReAct Agent.

Verify rằng:
- Tool execution timeout → graceful failure (observation message, không crash)
- LLM call timeout → fallback response với state=FAILED
- Timeout configurable qua config
- Metrics được track riêng (tool_timeouts, llm_timeouts)
"""
import asyncio
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from src.system2.react_agent import ReActAgent, ReActRequest, ReActState
from src.user_modeling.services import UserProfile, BehaviorTracker, ActionTypes


# ============ Helpers ============

def _make_user_profile():
    return UserProfile(
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


def _make_agent(config_overrides=None) -> tuple:
    """Tạo ReActAgent với mocks + tùy chỉnh config."""
    config = {
        "max_iterations": 4,
        "max_tokens": 8000,
        "temperature": 0.4,
    }
    if config_overrides:
        config.update(config_overrides)

    llm = MagicMock()
    llm.ainvoke = AsyncMock()

    context_builder = MagicMock()
    mock_context = MagicMock()
    mock_context.profile = _make_user_profile()
    mock_context.behavior = None
    mock_context.memories = []
    mock_context.has_personalization = MagicMock(return_value=False)
    mock_context.behavior_summary_text = MagicMock(return_value="")
    context_builder.build = AsyncMock(return_value=mock_context)

    guardrails = MagicMock()
    guardrails.check_token_limit = MagicMock(side_effect=lambda msgs, max_t: msgs)
    guardrails.validate_tool_input = MagicMock(return_value=(True, None))
    guardrails.is_sensitive_tool = MagicMock(return_value=False)
    guardrails.get_fallback_message = MagicMock(return_value="[FALLBACK]")

    profile_service = MagicMock()
    behavior_tracker = MagicMock()
    behavior_tracker.log = AsyncMock(return_value=1)

    # Patch system prompt file
    with open("config/prompts/system2_prompt.txt", "w", encoding="utf-8") as f:
        f.write("{tenant_name} {tone} {lease_end} {payment_delay_days} {memories} {behavior_summary} {query} {history_context}")

    agent = ReActAgent(
        config=config,
        llm_client=llm,
        context_builder=context_builder,
        guardrails=guardrails,
        profile_service=profile_service,
        behavior_tracker=behavior_tracker,
    )
    return agent, llm, guardrails, behavior_tracker


# ============ Config tests ============

def test_default_tool_timeout_is_10_seconds():
    """Default tool timeout là 10s."""
    agent, _, _, _ = _make_agent()
    assert agent.tool_timeout_seconds == 10.0


def test_default_llm_timeout_is_30_seconds():
    """Default LLM timeout là 30s."""
    agent, _, _, _ = _make_agent()
    assert agent.llm_timeout_seconds == 30.0


def test_custom_timeout_from_config():
    """Timeout có thể override qua config."""
    agent, _, _, _ = _make_agent({
        "tool_timeout_seconds": 5.0,
        "llm_timeout_seconds": 60.0,
    })
    assert agent.tool_timeout_seconds == 5.0
    assert agent.llm_timeout_seconds == 60.0


# ============ Tool timeout tests ============

@pytest.mark.asyncio
async def test_tool_timeout_returns_graceful_observation():
    """Tool chạy quá timeout → observation message, không crash."""
    agent, llm, _, _ = _make_agent({"tool_timeout_seconds": 0.1})

    @tool
    async def slow_tool() -> str:
        """Tool ngủ 5 giây."""
        await asyncio.sleep(5)
        return "should never see this"

    from uuid import uuid4
    tool_call_dict = {
        "id": str(uuid4()),
        "name": "slow_tool",
        "args": {},
        "type": "tool_call",
    }
    llm.ainvoke.side_effect = [
        AIMessage(content="", tool_calls=[tool_call_dict]),
        AIMessage(content="Final", tool_calls=[]),
    ]

    request = ReActRequest(query="Test", tenant_id=1, tools=[slow_tool])

    # Phải chạy được, không crash
    response = await agent.run(request)

    # Tool timeout được track trong metric
    assert agent.metrics.tool_timeouts == 1
    # Vẫn complete (không phải FAILED) vì tool timeout là 1 step failure
    # (agent vẫn tiếp tục loop để LLM có thể retry/reason)


@pytest.mark.asyncio
async def test_tool_timeout_does_not_block_forever():
    """Tool timeout PHẢI xảy ra trong khoảng thời gian config, không block forever."""
    import time
    agent, llm, _, _ = _make_agent({"tool_timeout_seconds": 0.2})

    @tool
    async def infinite_tool() -> str:
        """Tool ngủ 60s (sẽ bị cancel)."""
        await asyncio.sleep(60)
        return "never"

    from uuid import uuid4
    tool_call_dict = {
        "id": str(uuid4()),
        "name": "infinite_tool",
        "args": {},
        "type": "tool_call",
    }
    llm.ainvoke.side_effect = [
        AIMessage(content="", tool_calls=[tool_call_dict]),
        AIMessage(content="OK", tool_calls=[]),
    ]

    request = ReActRequest(query="Test", tenant_id=1, tools=[infinite_tool])
    start = time.time()
    response = await agent.run(request)
    elapsed = time.time() - start

    # Phải < 2s (timeout 0.2s + overhead)
    assert elapsed < 2.0, f"Tool timeout không work, elapsed={elapsed:.2f}s"


@pytest.mark.asyncio
async def test_tool_timeout_message_contains_tool_name_and_timeout():
    """Observation message phải có tool name + timeout value."""
    agent, llm, _, _ = _make_agent({"tool_timeout_seconds": 0.1})

    @tool
    async def slow_tool() -> str:
        """Slow tool."""
        await asyncio.sleep(5)
        return "x"

    from uuid import uuid4
    tool_call_dict = {
        "id": str(uuid4()),
        "name": "slow_tool",
        "args": {},
        "type": "tool_call",
    }
    # Capture messages passed to 2nd LLM call (should contain timeout error in history)
    captured = []

    async def mock_ainvoke(messages, tools=None):
        captured.append(messages[:])
        if len(captured) == 1:
            return AIMessage(content="", tool_calls=[tool_call_dict])
        return AIMessage(content="OK", tool_calls=[])

    llm.ainvoke.side_effect = mock_ainvoke

    request = ReActRequest(query="Test", tenant_id=1, tools=[slow_tool])
    await agent.run(request)

    # 2nd call's messages phải có ToolMessage với timeout error
    second_call_messages = captured[1]
    timeout_msgs = [
        m for m in second_call_messages
        if "Tool" in m.content and "timeout" in m.content and "0.1" in m.content
    ]
    assert len(timeout_msgs) >= 1


@pytest.mark.asyncio
async def test_fast_tool_completes_normally():
    """Tool chạy nhanh → complete bình thường, không bị timeout."""
    agent, llm, _, _ = _make_agent({"tool_timeout_seconds": 5.0})

    @tool
    async def fast_tool() -> str:
        """Fast tool."""
        await asyncio.sleep(0.01)
        return "fast result"

    from uuid import uuid4
    tool_call_dict = {
        "id": str(uuid4()),
        "name": "fast_tool",
        "args": {},
        "type": "tool_call",
    }
    llm.ainvoke.side_effect = [
        AIMessage(content="", tool_calls=[tool_call_dict]),
        AIMessage(content="Done", tool_calls=[]),
    ]

    request = ReActRequest(query="Test", tenant_id=1, tools=[fast_tool])
    response = await agent.run(request)

    # Không có timeout
    assert agent.metrics.tool_timeouts == 0
    # Tool được execute thành công
    assert "fast_tool" in response.actions_taken


# ============ LLM timeout tests ============

@pytest.mark.asyncio
async def test_llm_timeout_returns_fallback():
    """LLM timeout → trả về fallback response với state=FAILED."""
    agent, llm, guardrails, behavior_tracker = _make_agent(
        {"llm_timeout_seconds": 0.1}
    )

    # Mock LLM sleep lâu hơn timeout
    async def slow_llm(messages, tools=None):
        await asyncio.sleep(5)
        return AIMessage(content="late", tool_calls=[])

    llm.ainvoke.side_effect = slow_llm

    request = ReActRequest(query="Test", tenant_id=1, tools=[])
    response = await agent.run(request)

    # State = FAILED
    assert response.state == ReActState.FAILED
    # Fallback message được trả về
    assert response.answer == "[FALLBACK]"
    # Metric tracked
    assert agent.metrics.llm_timeouts == 1
    # Guardrails fallback được gọi
    guardrails.get_fallback_message.assert_called()


@pytest.mark.asyncio
async def test_llm_timeout_logs_behavior():
    """LLM timeout phải log behavior event."""
    agent, llm, _, behavior_tracker = _make_agent(
        {"llm_timeout_seconds": 0.1}
    )

    async def slow_llm(messages, tools=None):
        await asyncio.sleep(5)
        return AIMessage(content="late", tool_calls=[])

    llm.ainvoke.side_effect = slow_llm

    request = ReActRequest(query="Test", tenant_id=1, tools=[])
    await agent.run(request)

    # Verify behavior được log với description chứa "timeout"
    behavior_tracker.log.assert_called()
    call_args = behavior_tracker.log.call_args
    assert "timeout" in call_args.kwargs.get("description", "").lower()


@pytest.mark.asyncio
async def test_llm_timeout_does_not_block_forever():
    """LLM timeout phải xảy ra nhanh, không block."""
    import time
    agent, llm, _, _ = _make_agent({"llm_timeout_seconds": 0.2})

    async def slow_llm(messages, tools=None):
        await asyncio.sleep(60)
        return AIMessage(content="x", tool_calls=[])

    llm.ainvoke.side_effect = slow_llm

    request = ReActRequest(query="Test", tenant_id=1, tools=[])
    start = time.time()
    response = await agent.run(request)
    elapsed = time.time() - start

    # Phải < 2s
    assert elapsed < 2.0, f"LLM timeout không work, elapsed={elapsed:.2f}s"


# ============ Metrics tests ============

def test_metrics_have_timeout_fields():
    """System2Metrics có fields tool_timeouts, llm_timeouts."""
    from src.notifications.metrics import System2Metrics
    m = System2Metrics()
    assert hasattr(m, "tool_timeouts")
    assert hasattr(m, "llm_timeouts")
    assert m.tool_timeouts == 0
    assert m.llm_timeouts == 0

    d = m.to_dict()
    assert "tool_timeouts" in d
    assert "llm_timeouts" in d


@pytest.mark.asyncio
async def test_tool_failures_counted_separately_from_timeouts():
    """Tool timeout là failure nhưng được track riêng (tool_timeouts) ngoài tool_failures."""
    agent, llm, _, _ = _make_agent({"tool_timeout_seconds": 0.1})

    @tool
    async def slow_tool() -> str:
        """Slow tool that exceeds timeout."""
        await asyncio.sleep(5)
        return "x"

    from uuid import uuid4
    tool_call_dict = {
        "id": str(uuid4()),
        "name": "slow_tool",
        "args": {},
        "type": "tool_call",
    }
    llm.ainvoke.side_effect = [
        AIMessage(content="", tool_calls=[tool_call_dict]),
        AIMessage(content="OK", tool_calls=[]),
    ]

    request = ReActRequest(query="Test", tenant_id=1, tools=[slow_tool])
    await agent.run(request)

    # Tool timeout tracked
    assert agent.metrics.tool_timeouts == 1
    # Tool failure cũng tăng (timeout cũng là failure)
    assert agent.metrics.tool_failures == 1
