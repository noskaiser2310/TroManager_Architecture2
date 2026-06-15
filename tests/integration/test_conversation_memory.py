"""
Tests cho ConversationMemory - sử dụng mock DB pool.

ConversationMemory lưu/đọc từ PostgreSQL, được mock để test không cần DB thật.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


@pytest.fixture
def mock_db_pool():
    """Mock DB pool với fetchrow/fetch trả về dữ liệu giả lập."""
    pool = MagicMock()
    conn = AsyncMock()

    # fetchrow returns row dict-like
    conn.fetchrow = AsyncMock(return_value={
        "conversation_id": 1,
        "tenant_id": 100,
        "session_id": "test-session-uuid",
        "source": "test",
        "user_message": "Hello",
        "ai_response": "Hi there",
        "system_used": "system1",
        "iterations": 0,
        "tool_calls": [],
        "latency_ms": 100,
        "tokens_used": 50,
        "cost_usd": 0.001,
        "timestamp": datetime.now(),
    })

    # fetch returns list of rows (in DESC order - newest first, simulating SQL ORDER BY timestamp DESC)
    conn.fetch = AsyncMock(return_value=[
        {
            "conversation_id": 2,
            "tenant_id": 100,
            "session_id": "sess-1",
            "source": "zalo",
            "user_message": "Cảm ơn bạn",
            "ai_response": "Không có gì",
            "system_used": "system1",
            "iterations": 0,
            "tool_calls": [],
            "latency_ms": 200,
            "tokens_used": 30,
            "cost_usd": 0.0001,
            "timestamp": datetime(2026, 6, 5, 10, 5),
        },
        {
            "conversation_id": 1,
            "tenant_id": 100,
            "session_id": "sess-1",
            "source": "zalo",
            "user_message": "Phòng tôi bị rò nước",
            "ai_response": "Tôi sẽ tạo ticket bảo trì cho bạn",
            "system_used": "system2",
            "iterations": 2,
            "tool_calls": [{"name": "create_ticket"}],
            "latency_ms": 1500,
            "tokens_used": 250,
            "cost_usd": 0.005,
            "timestamp": datetime(2026, 6, 5, 10, 0),
        },
    ])

    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    return pool


def test_new_session_id_format():
    """Test session ID là UUID hợp lệ."""
    from src.user_modeling.conversation_memory import ConversationMemory
    sid = ConversationMemory.new_session_id()
    assert isinstance(sid, str)
    assert len(sid) == 36  # UUID format: 8-4-4-4-12
    assert sid.count("-") == 4


@pytest.mark.asyncio
async def test_add_turn_returns_id(mock_db_pool):
    """Test add_turn returns conversation_id."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    conv_id = await cm.add_turn(
        tenant_id=100,
        user_message="Hello",
        ai_response="Hi there",
        source="test",
    )
    assert conv_id == 1
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_turn_generates_session_if_missing(mock_db_pool):
    """Test session_id được generate khi không cung cấp."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    await cm.add_turn(
        tenant_id=100,
        user_message="Test",
        ai_response="Response",
    )
    # call_args[0] = (sql, *params); sql is [0], params start at [1]
    call_args = mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow.call_args
    session_id = call_args[0][2]  # tenant_id is at [1], session_id at [2]
    assert session_id is not None
    assert len(session_id) == 36  # UUID format


@pytest.mark.asyncio
async def test_get_recent_turns_orders_ascending(mock_db_pool):
    """Test get_recent_turns returns turns ordered cũ → mới."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    turns = await cm.get_recent_turns(tenant_id=100, limit=5)
    assert len(turns) == 2
    # Mock returns DESC, service reverses to ASC
    assert turns[0].conversation_id == 1  # older first
    assert turns[1].conversation_id == 2  # newer second


@pytest.mark.asyncio
async def test_format_for_context_includes_both_sides(mock_db_pool):
    """Test format_for_context includes cả user và AI messages."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    formatted = await cm.format_for_context(tenant_id=100, max_turns=5)
    assert "LỊCH SỬ HỘI THOẠI" in formatted
    assert "Khách:" in formatted
    assert "AI:" in formatted
    assert "rò nước" in formatted
    assert "ticket bảo trì" in formatted


@pytest.mark.asyncio
async def test_format_for_context_empty_when_no_history(mock_db_pool):
    """Test format_for_context returns empty string khi không có history."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    # Override mock to return empty list
    conn = mock_db_pool.acquire.return_value.__aenter__.return_value
    conn.fetch = AsyncMock(return_value=[])

    formatted = await cm.format_for_context(tenant_id=999, max_turns=5)
    assert formatted == ""


@pytest.mark.asyncio
async def test_get_recent_turns_for_session(mock_db_pool):
    """Test get_recent_turns_for_session returns turns of a session."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    turns = await cm.get_recent_turns_for_session(session_id="sess-1", limit=10)
    assert len(turns) == 2
    assert all(t.session_id == "sess-1" for t in turns)


@pytest.mark.asyncio
async def test_cleanup_old(mock_db_pool):
    """Test cleanup_old returns count of deleted rows."""
    from src.user_modeling.conversation_memory import ConversationMemory
    cm = ConversationMemory(mock_db_pool)

    # Mock returns 5 deleted IDs
    conn = mock_db_pool.acquire.return_value.__aenter__.return_value
    conn.fetch = AsyncMock(return_value=[
        {"conversation_id": i} for i in range(1, 6)
    ])

    count = await cm.cleanup_old(days=30)
    assert count == 5


def test_conversation_turn_from_row():
    """Test ConversationTurn.from_row parses correctly."""
    from src.user_modeling.conversation_memory import ConversationTurn
    row = {
        "conversation_id": 42,
        "tenant_id": 100,
        "session_id": "abc-123",
        "source": "zalo",
        "user_message": "msg",
        "ai_response": "resp",
        "system_used": "system1",
        "iterations": 0,
        "tool_calls": [],
        "timestamp": datetime(2026, 6, 5),
    }
    turn = ConversationTurn.from_row(row)
    assert turn.conversation_id == 42
    assert turn.tenant_id == 100
    assert turn.session_id == "abc-123"
    assert turn.source == "zalo"


def test_exports_in_services():
    """Test ConversationMemory được export từ user_modeling.services."""
    from src.user_modeling.services import (
        ConversationMemory, ConversationTurn
    )
    assert ConversationMemory is not None
    assert ConversationTurn is not None
