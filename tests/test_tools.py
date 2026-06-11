"""
Tests cho các tools - sử dụng mock DB pool và notification clients.

Real DB queries được mock để tests chạy được mà không cần PostgreSQL.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


# ============ Fixtures ============

@pytest.fixture(autouse=True)
def mock_core_dependencies():
    """Mock global DB pool và notification clients cho tất cả tests."""
    from src.core import set_db_pool, set_zalo_client, set_sms_client, set_knowledge_lookup
    
    # Mock DB pool
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    set_db_pool(mock_pool)
    
    # Mock Zalo client
    mock_zalo = MagicMock()
    mock_zalo.send_to_tenant = AsyncMock(return_value=MagicMock(
        success=True,
        message_id="zl_msg_123",
        error=None,
    ))
    set_zalo_client(mock_zalo)
    
    # Mock SMS client
    mock_sms = MagicMock()
    mock_sms.send_sms = AsyncMock(return_value=MagicMock(
        success=True,
        message_id="sms_456",
        error=None,
    ))
    set_sms_client(mock_sms)
    
    # Mock knowledge lookup
    mock_lookup = MagicMock()
    mock_lookup.retrieve = AsyncMock(return_value=[
        {"text": "Giờ giấc yên tĩnh từ 22h đến 6h.", "source": "noi_quy/gio_giac.md", "score": 0.92},
    ])
    set_knowledge_lookup(mock_lookup)
    
    return {
        "pool": mock_pool,
        "conn": mock_conn,
        "zalo": mock_zalo,
        "sms": mock_sms,
        "knowledge": mock_lookup,
    }


# ============ ToolRegistry tests ============

class TestToolRegistry:
    """Test ToolRegistry."""
    
    @pytest.fixture
    def registry(self):
        from src.tools.tool_registry import get_default_registry
        return get_default_registry()
    
    def test_get_all_tools(self, registry):
        """Test lấy tất cả tools."""
        tools = registry.get_all_tools()
        assert len(tools) > 0
        tool_names = [t.name for t in tools]
        assert "fetch_available_rooms" in tool_names
        assert "calc_rent" in tool_names
        assert "query_policies" in tool_names
        assert "get_invoice_detail" in tool_names
        assert "send_zalo" in tool_names
        assert "create_maintenance_ticket" in tool_names
    
    def test_get_for_intent_billing(self, registry):
        tools = registry.get_for_intent("billing_inquiry")
        tool_names = [t.name for t in tools]
        assert "get_invoice_detail" in tool_names
        assert "query_policies" in tool_names
        assert "send_payment_reminder" not in tool_names
    
    def test_get_for_intent_maintenance(self, registry):
        tools = registry.get_for_intent("maintenance_request")
        tool_names = [t.name for t in tools]
        assert "create_maintenance_ticket" in tool_names
        assert "get_room_info" in tool_names
    
    def test_get_for_intent_general_chat(self, registry):
        tools = registry.get_for_intent("general_chat")
        assert len(tools) == 0
    
    def test_intent_to_toolkit_mapping_coverage(self):
        from src.tools.tool_registry import INTENT_TOOLKIT_MAP
        for intent in [
            "billing_inquiry", "payment_reminder", "billing_dispute",
            "maintenance_request", "maintenance_status",
            "room_recommendation", "room_transfer", "room_inquiry",
            "contract_inquiry", "contract_renewal",
            "policy_question", "general_chat",
        ]:
            assert intent in INTENT_TOOLKIT_MAP
    
    def test_unknown_intent_falls_back_to_knowledge(self, registry):
        tools = registry.get_for_intent("completely_made_up_intent")
        assert len(tools) > 0
    
    def test_get_tool_by_name(self, registry):
        tool = registry.get_tool_by_name("calc_rent")
        assert tool is not None
        assert tool.name == "calc_rent"
    
    def test_describe_tools(self, registry):
        tools = registry.get_for_intent("maintenance_request")
        description = registry.describe_tools(tools)
        assert "create_maintenance_ticket" in description
        assert ":" in description


# ============ Decision tools tests ============

class TestDecisionTools:
    """Test decision tools với mocked DB."""
    
    @pytest.mark.asyncio
    async def test_calc_rent(self, mock_core_dependencies):
        from src.tools.decision_tools import calc_rent
        conn = mock_core_dependencies["conn"]
        conn.fetchrow = AsyncMock(return_value={
            "room_number": "205",
            "monthly_rent": 3500000,
            "electricity_price": 3500,
            "water_price": 25000,
            "service_fee": 200000,
        })
        
        result = await calc_rent.ainvoke({
            "room_id": 205,
            "month": "2026-06",
            "electricity_kwh": 100,
            "water_m3": 5,
        })
        
        assert "TỔNG" in result
        assert "phòng" in result.lower() or "205" in result
    
    @pytest.mark.asyncio
    async def test_fetch_available_rooms(self, mock_core_dependencies):
        from src.tools.decision_tools import fetch_available_rooms
        conn = mock_core_dependencies["conn"]
        conn.fetch = AsyncMock(return_value=[
            {"room_number": "201", "floor": 2, "area_m2": 20, "monthly_rent": 3000000, "max_occupants": 2},
            {"room_number": "301", "floor": 3, "area_m2": 25, "monthly_rent": 3800000, "max_occupants": 2},
        ])
        
        result = await fetch_available_rooms.ainvoke({"budget_max": 4000000})
        
        assert "201" in result or "phòng" in result.lower()


# ============ Knowledge tools tests ============

class TestKnowledgeTools:
    """Test knowledge tools với mocked DB."""
    
    @pytest.mark.asyncio
    async def test_get_invoice_detail(self, mock_core_dependencies):
        from src.tools.knowledge_tools import get_invoice_detail
        conn = mock_core_dependencies["conn"]
        conn.fetchrow = AsyncMock(return_value={
            "invoice_id": 1,
            "invoice_month": "2026-06-01",
            "base_rent": 3500000,
            "electricity_kwh": 100,
            "electricity_cost": 350000,
            "water_m3": 5,
            "water_cost": 125000,
            "service_fee": 200000,
            "other_charges": 0,
            "total_amount": 4175000,
            "due_date": "2026-07-05",
            "paid_date": None,
            "status": "unpaid",
            "room_number": "205",
        })
        
        result = await get_invoice_detail.ainvoke({"tenant_id": 1, "month": "2026-06"})
        
        assert "4,175,000" in result or "4175000" in result
        assert "Chưa thanh toán" in result
    
    @pytest.mark.asyncio
    async def test_get_contract_status(self, mock_core_dependencies):
        import datetime
        from src.tools.knowledge_tools import get_contract_status
        conn = mock_core_dependencies["conn"]
        # end_date phải là date object (không phải string) vì code làm
        # `contract['end_date'] - date.today()`.days ở knowledge_tools.py:115
        conn.fetchrow = AsyncMock(return_value={
            "contract_id": 10,
            "start_date": "2024-01-01",
            "end_date": datetime.date(2026, 12, 31),
            "deposit_amount": 3500000,
            "monthly_rent": 3500000,
            "status": "active",
            "room_number": "205",
            "floor": 2,
            "area_m2": 20,
        })

        result = await get_contract_status.ainvoke({"tenant_id": 1})

        assert "Hợp đồng" in result
        assert "205" in result
        assert "Đang hiệu lực" in result
    
    @pytest.mark.asyncio
    async def test_query_policies(self, mock_core_dependencies):
        from src.tools.knowledge_tools import query_policies
        result = await query_policies.ainvoke({"query": "Giờ yên tĩnh?"})
        
        assert "yên tĩnh" in result.lower() or "22h" in result


# ============ Automation tools tests ============

class TestAutomationTools:
    """Test automation tools với mocked dependencies."""
    
    @pytest.mark.asyncio
    async def test_create_maintenance_ticket(self, mock_core_dependencies):
        from src.tools.automation_tools import create_maintenance_ticket
        conn = mock_core_dependencies["conn"]
        conn.fetchval = AsyncMock(return_value=101)  # room_id
        conn.fetchval.return_value = 999  # ticket_id
        
        result = await create_maintenance_ticket.ainvoke({
            "tenant_id": 1,
            "issue": "Điều hòa không mát",
            "priority": "high",
            "category": "appliance",
        })
        
        assert "TKT-" in result
        assert "phiếu" in result.lower() or "Điều hòa" in result
    
    @pytest.mark.asyncio
    async def test_send_zalo(self, mock_core_dependencies):
        from src.tools.automation_tools import send_zalo
        conn = mock_core_dependencies["conn"]
        conn.fetchrow = AsyncMock(return_value={
            "full_name": "Nguyễn Văn A",
            "zalo_id": "zalo_abc_123",
        })
        
        result = await send_zalo.ainvoke({
            "tenant_id": 1,
            "message": "Test message",
        })
        
        assert "Đã gửi" in result
        assert "zl_msg_123" in result  # message_id from mock
    
    @pytest.mark.asyncio
    async def test_send_sms(self, mock_core_dependencies):
        from src.tools.automation_tools import send_sms
        conn = mock_core_dependencies["conn"]
        conn.fetchrow = AsyncMock(return_value={
            "full_name": "Nguyễn Văn A",
            "phone_number": "0901234567",
        })
        
        result = await send_sms.ainvoke({
            "tenant_id": 1,
            "message": "Test SMS",
        })
        
        assert "Đã gửi SMS" in result
        assert "0901234567" in result
    
    @pytest.mark.asyncio
    async def test_send_payment_reminder_creates_approval(self, mock_core_dependencies):
        """Test send_payment_reminder tạo approval_queue entry thay vì gửi trực tiếp."""
        from src.tools.automation_tools import send_payment_reminder
        conn = mock_core_dependencies["conn"]
        conn.fetchrow = AsyncMock(return_value={
            "total_amount": 3500000,
            "due_date": "2026-06-05",
            "days_overdue": 5,
            "full_name": "Nguyễn Văn A",
            "tone_preference": "friendly",
        })
        conn.fetchval = AsyncMock(return_value=42)  # approval_id
        
        result = await send_payment_reminder.ainvoke({
            "tenant_id": 1,
            "invoice_id": 100,
            "tone": "friendly",
        })
        
        assert "duyệt" in result.lower() or "approval" in result.lower()
        assert "42" in result  # approval_id
    
    def test_send_payment_reminder_is_sensitive(self):
        """Test send_payment_reminder được đánh dấu sensitive."""
        from src.system2.guardrails import Guardrails
        guardrails = Guardrails()
        assert guardrails.is_sensitive_tool("send_payment_reminder") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
