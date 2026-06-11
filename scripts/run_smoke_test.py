"""
Smoke test - Chạy thử toàn bộ pipeline với mock, không cần DB/API key.

Mục đích:
- Verify tất cả imports hoạt động đúng
- Verify routing logic (Router → System 1 / System 2)
- Verify tools có thể được gọi (với mocked DB)
- Verify LLM clients có thể khởi tạo (không gọi API thật)

Chạy: python scripts/run_smoke_test.py
"""

from __future__ import annotations
import asyncio
import sys
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Force UTF-8 stdout/stderr for Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smoke_test")


# ============ Test 1: Verify imports ============

def test_imports():
    """Verify tất cả modules import được."""
    print("\n" + "=" * 60)
    print("TEST 1: Module imports")
    print("=" * 60)
    
    try:
        from src.gateway import RouterGateway, IncomingRequest, create_default_router
        print("  [OK] gateway")
        
        from src.system1.fast_layer import FastLayer, System1Request
        from src.system1.semantic_cache import SemanticCache
        from src.system1.knowledge_lookup import KnowledgeLookup
        print("  [OK] system1")
        
        from src.system2.react_agent import ReActAgent, ReActRequest
        from src.system2.context_builder import ContextBuilder
        from src.system2.guardrails import Guardrails
        print("  [OK] system2")
        
        from src.user_modeling.services import (
            ProfileService, BehaviorTracker, MemoryManager, UserProfile, BehaviorSummary
        )
        print("  [OK] user_modeling")
        
        from src.tools.tool_registry import get_default_registry
        from src.tools.decision_tools import DECISION_TOOLS
        from src.tools.knowledge_tools import KNOWLEDGE_TOOLS
        from src.tools.automation_tools import AUTOMATION_TOOLS
        print("  [OK] tools")
        
        from src.notifications.zalo_client import ZaloClient, create_zalo_client_from_config
        from src.notifications.sms_client import (
            SMSClient, TwilioSMSClient, create_sms_client_from_config
        )
        print("  [OK] notifications")
        
        from src.llm import LLMClient, EmbeddingClient, get_llm_client, get_embedding_client
        from src.llm.config_loader import load_llm_config, validate_config
        print("  [OK] llm")
        
        from src.cron.scheduler import CronScheduler
        from src.cron.event_dispatcher import EventDispatcher
        print("  [OK] cron")
        
        from src.core import set_db_pool, get_db_pool, get_knowledge_lookup
        print("  [OK] core")
        
        print("\n[PASS] Tất cả imports OK")
        return True
    except ImportError as e:
        print(f"\n[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============ Test 2: Router ============

def test_router():
    """Test Router Gateway routing decisions."""
    print("\n" + "=" * 60)
    print("TEST 2: Router Gateway")
    print("=" * 60)
    
    from src.gateway import IncomingRequest, create_default_router, TargetSystem
    
    router = create_default_router()
    
    test_cases = [
        ("Wifi mật khẩu gì?", "zalo", TargetSystem.SYSTEM1, "Câu đơn giản → System 1"),
        ("Tôi còn nợ bao nhiêu?", "zalo", TargetSystem.SYSTEM2, "Sensitive keyword → System 2"),
        ("Điều hòa phòng tôi bị hỏng", "zalo", TargetSystem.SYSTEM2, "Complex keyword → System 2"),
        ("Giờ yên tĩnh?", "zalo", TargetSystem.SYSTEM1, "FAQ → System 1"),
        ("invoice_overdue", "cron", TargetSystem.SYSTEM2, "Cron → System 2"),
    ]
    
    all_pass = True
    for query, source, expected, desc in test_cases:
        req = IncomingRequest(source=source, query=query, tenant_id=1)
        decision = router.route(req)
        actual = decision.target_system
        status = "[OK]" if actual == expected else "[FAIL]"
        if actual != expected:
            all_pass = False
        print(f"  {status} {desc}")
        print(f"     Query: {query}")
        print(f"     Expected: {expected.value}, Got: {actual.value}")
    
    if all_pass:
        print("\n[PASS] Router routing OK")
    else:
        print("\n[FAIL] Một số routing decisions sai")
    return all_pass


# ============ Test 3: Tool registry ============

def test_tool_registry():
    """Test tool registry resolves tools for intents."""
    print("\n" + "=" * 60)
    print("TEST 3: Tool Registry")
    print("=" * 60)
    
    from src.tools.tool_registry import get_default_registry
    
    registry = get_default_registry()
    
    test_cases = [
        ("billing_inquiry", ["get_invoice_detail", "query_policies"], []),
        ("maintenance_request", ["create_maintenance_ticket"], []),
        ("room_recommendation", ["fetch_available_rooms"], []),
        ("contract_inquiry", ["get_contract_status"], []),
        ("general_chat", [], []),  # Không cần tool
        ("background_event_invoice_overdue", ["send_payment_reminder"], []),
    ]
    
    all_pass = True
    for intent, must_have, must_not_have in test_cases:
        tools = registry.get_for_intent(intent)
        tool_names = {t.name for t in tools}
        
        missing = [t for t in must_have if t not in tool_names]
        unwanted = [t for t in must_not_have if t in tool_names]
        
        if missing or unwanted:
            all_pass = False
            print(f"  [FAIL] intent={intent}")
            if missing:
                print(f"     Missing: {missing}")
            if unwanted:
                print(f"     Unwanted: {unwanted}")
        else:
            print(f"  [OK]   intent={intent} → {sorted(tool_names)}")
    
    if all_pass:
        print(f"\n[PASS] Tool registry OK ({len(registry.get_all_tools())} tools total)")
    else:
        print(f"\n[FAIL] Tool registry có vấn đề")
    return all_pass


# ============ Test 4: LLM client init ============

def test_llm_client_init():
    """Test LLM clients có thể khởi tạo (không gọi API)."""
    print("\n" + "=" * 60)
    print("TEST 4: LLM Client initialization")
    print("=" * 60)
    
    from src.llm import get_llm_client, get_embedding_client, reset_clients
    from src.llm.config_loader import load_llm_config, validate_config
    
    reset_clients()
    
    try:
        config = load_llm_config()
        issues = validate_config(config)
        
        if issues:
            print("  [WARN] Config có issues (chấp nhận được nếu API key chưa set):")
            for issue in issues:
                print(f"     - {issue}")
        
        flash_client = get_llm_client("flash")
        print(f"  [OK] Flash client: {flash_client.model_name}")
        
        pro_client = get_llm_client("pro")
        print(f"  [OK] Pro client: {pro_client.model_name}")
        
        emb_client = get_embedding_client()
        print(f"  [OK] Embedding client: {emb_client.model} (dim={emb_client.dimension})")
        
        print("\n[PASS] LLM clients khởi tạo thành công")
        return True
    except FileNotFoundError as e:
        print(f"  [FAIL] Config file not found: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============ Test 5: Knowledge base load ============

def test_knowledge_base():
    """Test knowledge base files tồn tại và có thể load."""
    print("\n" + "=" * 60)
    print("TEST 5: Knowledge base")
    print("=" * 60)
    
    kb_dir = PROJECT_ROOT / "knowledge_base"
    if not kb_dir.exists():
        print(f"  [FAIL] Knowledge base dir not found: {kb_dir}")
        return False
    
    md_files = list(kb_dir.rglob("*.md"))
    if not md_files:
        print(f"  [FAIL] Không tìm thấy file .md nào trong {kb_dir}")
        return False
    
    print(f"  [OK] Tìm thấy {len(md_files)} file .md")
    
    # Group by subdir
    by_dir: dict[str, list[str]] = {}
    for f in md_files:
        rel = f.relative_to(kb_dir)
        subdir = str(rel.parent) if rel.parent != Path(".") else "root"
        by_dir.setdefault(subdir, []).append(rel.name)
    
    for subdir, files in sorted(by_dir.items()):
        print(f"     {subdir}/ ({len(files)} files)")
        for fname in sorted(files)[:3]:
            print(f"       - {fname}")
        if len(files) > 3:
            print(f"       ... +{len(files) - 3} more")
    
    # Test KnowledgeLookup can be built (without building index)
    from src.system1.knowledge_lookup import KnowledgeLookup
    from src.llm.config_loader import load_llm_config
    
    config = load_llm_config()
    emb_dim = config.embedding_dim
    
    # Mock embedding client
    mock_emb = MagicMock()
    mock_emb.dimension = emb_dim
    
    lookup = KnowledgeLookup(
        config={"rag_top_k": 3, "rag_similarity_threshold": 0.5},
        embedding_client=mock_emb,
        knowledge_base_dir=str(kb_dir),
    )
    
    stats = lookup.get_stats()
    print(f"  [OK] KnowledgeLookup stats: {stats}")
    
    print("\n[PASS] Knowledge base OK")
    return True


# ============ Test 6: Tool execution với mock DB ============

async def test_tool_execution():
    """Test một tool thực thi với mocked DB."""
    print("\n" + "=" * 60)
    print("TEST 6: Tool execution với mock DB")
    print("=" * 60)
    
    from src.core import set_db_pool, set_zalo_client, set_sms_client, set_knowledge_lookup
    from src.tools.knowledge_tools import get_invoice_detail
    from src.tools.automation_tools import send_zalo
    
    # Mock DB pool
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    set_db_pool(mock_pool)
    
    # Mock Zalo client
    mock_zalo = MagicMock()
    mock_zalo.send_to_tenant = AsyncMock(return_value=MagicMock(
        success=True, message_id="test_msg_001", error=None
    ))
    set_zalo_client(mock_zalo)
    
    # Mock SMS client
    mock_sms = MagicMock()
    mock_sms.send_sms = AsyncMock(return_value=MagicMock(
        success=True, message_id="test_sms_001", error=None
    ))
    set_sms_client(mock_sms)
    
    # Mock knowledge lookup
    mock_lookup = MagicMock()
    mock_lookup.retrieve = AsyncMock(return_value=[
        {"text": "Giờ yên tĩnh từ 22h.", "source": "noi_quy/gio_giac.md", "score": 0.9}
    ])
    set_knowledge_lookup(mock_lookup)
    
    all_pass = True
    
    # Test get_invoice_detail
    try:
        mock_conn.fetchrow = AsyncMock(return_value={
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
        
        result = await get_invoice_detail.ainvoke({
            "tenant_id": 1, "month": "2026-06"
        })
        if "4,175,000" in result or "4175000" in result:
            print(f"  [OK]   get_invoice_detail returned valid data")
        else:
            print(f"  [FAIL] get_invoice_detail returned unexpected: {result[:200]}")
            all_pass = False
    except Exception as e:
        print(f"  [FAIL] get_invoice_detail raised: {e}")
        all_pass = False
    
    # Test send_zalo
    try:
        mock_conn.fetchrow = AsyncMock(return_value={
            "full_name": "Nguyễn Văn A",
            "zalo_id": "zalo_abc_123",
        })
        
        result = await send_zalo.ainvoke({
            "tenant_id": 1, "message": "Test"
        })
        if "Đã gửi" in result and "test_msg_001" in result:
            print(f"  [OK]   send_zalo returned success")
        else:
            print(f"  [FAIL] send_zalo returned unexpected: {result[:200]}")
            all_pass = False
    except Exception as e:
        print(f"  [FAIL] send_zalo raised: {e}")
        all_pass = False
    
    if all_pass:
        print("\n[PASS] Tool execution OK")
    else:
        print("\n[FAIL] Một số tools failed")
    return all_pass


# ============ Test 7: ReAct loop với mock LLM ============

async def test_react_loop():
    """Test ReAct agent chạy được với mock LLM."""
    print("\n" + "=" * 60)
    print("TEST 7: ReAct loop với mock LLM")
    print("=" * 60)
    
    from src.system2.react_agent import ReActAgent, ReActRequest, ReActState
    from src.system2.guardrails import Guardrails
    from langchain_core.messages import AIMessage
    from uuid import uuid4
    
    # Create temp system2_prompt.txt for test
    prompt_path = PROJECT_ROOT / "config" / "prompts" / "system2_prompt.txt"
    if not prompt_path.exists():
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(
            "Test prompt {tenant_name} {tone} {lease_end} {payment_delay_days} {memories} {behavior_summary} {query}",
            encoding="utf-8"
        )
    
    # Mock LLM trả về final answer ngay
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(
        content="Đây là câu trả lời test từ System 2",
        tool_calls=[],
    ))
    
    # Mock context builder
    mock_context_builder = MagicMock()
    mock_context = MagicMock()
    mock_context.profile = None
    mock_context.behavior = None
    mock_context.memories = []
    mock_context.has_personalization = MagicMock(return_value=False)
    mock_context_builder.build = AsyncMock(return_value=mock_context)
    
    mock_guardrails = MagicMock()
    mock_guardrails.check_token_limit = MagicMock(side_effect=lambda msgs, max_t: msgs)
    mock_guardrails.validate_tool_input = MagicMock(return_value=(True, None))
    mock_guardrails.is_sensitive_tool = MagicMock(return_value=False)
    
    mock_profile_service = MagicMock()
    mock_behavior_tracker = MagicMock()
    mock_behavior_tracker.log = AsyncMock(return_value=1)
    
    agent = ReActAgent(
        config={"max_iterations": 4, "max_tokens": 8000, "temperature": 0.4},
        llm_client=mock_llm,
        context_builder=mock_context_builder,
        guardrails=mock_guardrails,
        profile_service=mock_profile_service,
        behavior_tracker=mock_behavior_tracker,
    )
    
    request = ReActRequest(
        query="Tôi còn nợ bao nhiêu?",
        tenant_id=1,
        tools=[],
    )
    
    try:
        response = await agent.run(request)
        if response.state == ReActState.COMPLETED and "test" in response.answer:
            print(f"  [OK]   ReAct completed in {response.iterations} iterations")
            print(f"     Answer: {response.answer}")
            print(f"     Tools: {response.actions_taken}")
            print(f"\n[PASS] ReAct loop OK")
            return True
        else:
            print(f"  [FAIL] ReAct failed: state={response.state}, answer={response.answer[:100]}")
            return False
    except Exception as e:
        print(f"  [FAIL] ReAct raised: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============ Main ============

async def main():
    """Run tất cả tests."""
    print("\n" + "#" * 60)
    print("# TroManager Smoke Test")
    print("#" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    
    results = []
    
    # Sync tests
    results.append(("Imports", test_imports()))
    results.append(("Router", test_router()))
    results.append(("Tool registry", test_tool_registry()))
    results.append(("LLM init", test_llm_client_init()))
    results.append(("Knowledge base", test_knowledge_base()))
    
    # Async tests
    results.append(("Tool execution", await test_tool_execution()))
    results.append(("ReAct loop", await test_react_loop()))
    
    # Summary
    print("\n" + "#" * 60)
    print("# SUMMARY")
    print("#" * 60)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] Smoke test thành công! Sẵn sàng để chạy thật.")
        return 0
    else:
        print(f"\n[FAIL] Có {total - passed} test(s) failed. Xem chi tiết ở trên.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
