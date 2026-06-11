"""
Tests cho ApprovalService - sử dụng mock DB pool + mock zalo client.

Test các flow:
- create_request returns approval_id
- list_pending returns pending requests
- approve sets status='approved' + executes action
- reject sets status='rejected' (no execution)
- approve idempotent: cannot approve non-pending
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


@pytest.fixture
def mock_db_pool():
    """Mock DB pool với fetchrow/fetch configurable."""
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    return pool, conn


@pytest.fixture
def mock_zalo_client():
    """Mock ZaloClient."""
    from src.notifications.zalo_client import ZaloSendResult
    client = MagicMock()
    client.send_message = AsyncMock(return_value=ZaloSendResult(
        success=True,
        message_id="zl_test_123",
    ))
    return client


@pytest.fixture
def mock_behavior_tracker():
    """Mock BehaviorTracker."""
    tracker = MagicMock()
    tracker.log = AsyncMock()
    return tracker


@pytest.mark.asyncio
async def test_create_request_returns_id(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test create_request returns approval_id."""
    pool, conn = mock_db_pool
    conn.fetchrow = AsyncMock(return_value={"approval_id": 42})

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    aid = await svc.create_request(
        tool_name="send_payment_reminder",
        tool_args={"invoice_id": 100, "amount": 1500000},
        tenant_id=1,
        reason="Test",
    )
    assert aid == 42
    conn.fetchrow.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_request_serializes_dict_args(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test tool_args dict được convert thành JSON string."""
    pool, conn = mock_db_pool
    conn.fetchrow = AsyncMock(return_value={"approval_id": 1})

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    args = {"invoice_id": 5, "tone": "strict", "nested": {"key": "value"}}
    await svc.create_request(
        tool_name="send_payment_reminder",
        tool_args=args,
        tenant_id=1,
    )

    # call_args[0] = (sql, tool_name, tool_args_json, tenant_id, ...)
    call_args = conn.fetchrow.call_args
    tool_args_json = call_args[0][2]
    assert isinstance(tool_args_json, str)
    import json
    parsed = json.loads(tool_args_json)
    assert parsed["invoice_id"] == 5
    assert parsed["nested"]["key"] == "value"


@pytest.mark.asyncio
async def test_list_pending_filters_by_status(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test list_pending chỉ trả về status='pending'."""
    pool, conn = mock_db_pool
    conn.fetch = AsyncMock(return_value=[
        {
            "approval_id": 1,
            "tool_name": "send_payment_reminder",
            "tool_args": '{"invoice_id": 1}',
            "tenant_id": 1,
            "requested_by": "system",
            "approver_role": "landlord",
            "status": "pending",
            "requested_at": datetime(2026, 6, 6, 10, 0),
            "reviewed_at": None,
            "reviewer_id": None,
            "notes": None,
        },
    ])

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    pending = await svc.list_pending()
    assert len(pending) == 1
    assert pending[0].status == "pending"
    assert pending[0].tool_args == {"invoice_id": 1}


@pytest.mark.asyncio
async def test_list_pending_with_tenant_filter(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test list_pending filter theo tenant_id."""
    pool, conn = mock_db_pool
    conn.fetch = AsyncMock(return_value=[])

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    await svc.list_pending(limit=10, tenant_id=42)
    call_args = conn.fetch.call_args
    assert 42 in call_args[0]


@pytest.mark.asyncio
async def test_approve_sets_status_and_executes(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test approve chuyển status + execute send_payment_reminder."""
    pool, conn = mock_db_pool
    now = datetime(2026, 6, 6, 10, 0)

    # Mock for get() call (returns pending request)
    # Mock for UPDATE call (returns the updated row)
    # Mock for invoice fetch (inside _execute_send_payment_reminder)

    request_data = {
        "approval_id": 1,
        "tool_name": "send_payment_reminder",
        "tool_args": '{"tenant_id": 1, "invoice_id": 100, "tone": "friendly", "amount": 1500000, "days_overdue": 3}',
        "tenant_id": 1,
        "requested_by": "system",
        "approver_role": "landlord",
        "status": "pending",
        "requested_at": now,
        "reviewed_at": None,
        "reviewer_id": None,
        "notes": None,
    }

    invoice_data = {
        "full_name": "Nguyen Van A",
        "phone_number": "0901234567",
        "zalo_id": "zl_abc",
        "tone_preference": "friendly",
        "due_date": datetime(2026, 6, 1).date(),
        "invoice_month": "2026-06",
        "room_number": "205",
    }

    # Configure conn methods in order
    # 1st call: fetchrow for get()
    # 2nd call: fetchrow for UPDATE
    # 3rd call: fetchrow for invoice fetch
    conn.fetchrow = AsyncMock(side_effect=[request_data, {"approval_id": 1}, invoice_data])

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    success, message = await svc.approve(approval_id=1, reviewer_id=99)
    assert success is True
    assert "Zalo sent" in message

    # Verify Zalo was called
    mock_zalo_client.send_message.assert_awaited_once()
    call_kwargs = mock_zalo_client.send_message.call_args
    msg_obj = call_kwargs[0][0]
    assert msg_obj.recipient_id == "zl_abc"
    assert "Nguyen Van A" in msg_obj.message

    # Verify behavior was logged
    mock_behavior_tracker.log.assert_awaited_once()
    log_args = mock_behavior_tracker.log.call_args.kwargs
    assert log_args["tenant_id"] == 1
    assert log_args["action_type"] == "auto_payment_reminder"


@pytest.mark.asyncio
async def test_approve_returns_error_if_not_found(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test approve trả error khi request không tồn tại."""
    pool, conn = mock_db_pool
    conn.fetchrow = AsyncMock(return_value=None)  # get() returns None

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    success, message = await svc.approve(approval_id=999)
    assert success is False
    assert "not found" in message


@pytest.mark.asyncio
async def test_approve_returns_error_if_not_pending(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test approve trả error khi request đã approved/rejected."""
    pool, conn = mock_db_pool
    conn.fetchrow = AsyncMock(return_value={
        "approval_id": 1,
        "tool_name": "send_payment_reminder",
        "tool_args": "{}",
        "tenant_id": 1,
        "requested_by": "system",
        "approver_role": "landlord",
        "status": "approved",  # already approved
        "requested_at": datetime(2026, 6, 6),
        "reviewed_at": datetime(2026, 6, 6, 10, 5),
        "reviewer_id": 99,
        "notes": None,
    })

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    success, message = await svc.approve(approval_id=1)
    assert success is False
    assert "approved" in message


@pytest.mark.asyncio
async def test_reject_sets_status_no_execution(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test reject set status=rejected, không execute."""
    pool, conn = mock_db_pool
    conn.fetchrow = AsyncMock(side_effect=[
        {
            "approval_id": 1,
            "tool_name": "send_payment_reminder",
            "tool_args": "{}",
            "tenant_id": 1,
            "requested_by": "system",
            "approver_role": "landlord",
            "status": "pending",
            "requested_at": datetime(2026, 6, 6),
            "reviewed_at": None,
            "reviewer_id": None,
            "notes": None,
        },
        {"approval_id": 1},  # UPDATE returns row
    ])

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    success, message = await svc.reject(approval_id=1, reviewer_id=5, notes="test")
    assert success is True
    assert "Rejected" in message
    # Zalo should NOT be called
    mock_zalo_client.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_approve_handles_zalo_failure(mock_db_pool, mock_zalo_client, mock_behavior_tracker):
    """Test approve vẫn thành công dù Zalo gửi fail."""
    pool, conn = mock_db_pool

    request_data = {
        "approval_id": 1,
        "tool_name": "send_payment_reminder",
        "tool_args": '{"tenant_id": 1, "invoice_id": 100, "amount": 1500000, "days_overdue": 5}',
        "tenant_id": 1,
        "requested_by": "system",
        "approver_role": "landlord",
        "status": "pending",
        "requested_at": datetime(2026, 6, 6),
        "reviewed_at": None,
        "reviewer_id": None,
        "notes": None,
    }

    invoice_data = {
        "full_name": "Test",
        "phone_number": "0901234567",
        "zalo_id": "zl_abc",
        "tone_preference": "friendly",
        "due_date": datetime(2026, 6, 1).date(),
        "invoice_month": "2026-06",
        "room_number": "101",
    }

    conn.fetchrow = AsyncMock(side_effect=[request_data, {"approval_id": 1}, invoice_data])

    # Make Zalo fail
    from src.notifications.zalo_client import ZaloSendResult
    mock_zalo_client.send_message = AsyncMock(return_value=ZaloSendResult(
        success=False,
        error="API timeout",
    ))

    from src.user_modeling.approval_service import ApprovalService
    svc = ApprovalService(pool, mock_zalo_client, mock_behavior_tracker)

    success, message = await svc.approve(approval_id=1)
    # Approval is still recorded as success, but execution failed
    assert success is True
    assert "failed" in message.lower() or "send failed" in message


def test_build_reminder_message_strict_overdue():
    """Test build message strict khi overdue >= 7 ngày."""
    from src.user_modeling.approval_service import ApprovalService

    msg = ApprovalService._build_reminder_message(
        full_name="Nguyen Van A",
        room_number="205",
        amount=1500000,
        days_overdue=10,
        tone="strict",
    )
    assert "Nguyen Van A" in msg
    assert "205" in msg
    assert "1.500.000" in msg
    assert "10 ngày" in msg  # 10 days overdue
    assert "24h" in msg  # urgent


def test_build_reminder_message_friendly_short_overdue():
    """Test build message friendly khi overdue < 3 ngày."""
    from src.user_modeling.approval_service import ApprovalService

    msg = ApprovalService._build_reminder_message(
        full_name="Tran Thi B",
        room_number="101",
        amount=2500000,
        days_overdue=1,
        tone="friendly",
    )
    assert "Tran Thi B" in msg
    assert "2.500.000" in msg
    assert "Cảm ơn" in msg  # polite ending


def test_exports():
    """Test ApprovalService và ApprovalRequest exported từ services."""
    from src.user_modeling.services import ApprovalService, ApprovalRequest
    assert ApprovalService is not None
    assert ApprovalRequest is not None


def test_sensitive_tools_removed_undefined():
    """Test guardrails SENSITIVE_TOOLS không còn modify_contract/refund_deposit."""
    from src.system2.guardrails import Guardrails
    assert "modify_contract" not in Guardrails.SENSITIVE_TOOLS
    assert "refund_deposit" not in Guardrails.SENSITIVE_TOOLS
    assert "send_payment_reminder" in Guardrails.SENSITIVE_TOOLS
