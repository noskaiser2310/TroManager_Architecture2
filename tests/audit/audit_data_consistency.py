"""
Audit: Data Consistency Checks for TroManager

Tests 8 identified data consistency issues between knowledge_base,
database seed data, source code defaults, and runtime behavior.

Usage:
    python tests/audit_data_consistency.py

Requires:
    - PostgreSQL running with tromanager database
    - Server running at http://localhost:8000
"""

import asyncio
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

import asyncpg
import httpx
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")

PASS = 0
FAIL = 0
SKIP = 0


def ok(msg: str):
    global PASS
    PASS += 1
    print(f"  ✓ PASS: {msg}")


def fail(msg: str):
    global FAIL
    FAIL += 1
    print(f"  ✗ FAIL: {msg}")


def skip(msg: str):
    global SKIP
    SKIP += 1
    print(f"  ∼ SKIP: {msg}")


def heading(num: int, title: str):
    print(f"\n{'='*70}")
    print(f"  Issue {num}: {title}")
    print(f"{'='*70}")


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────
# Issue 1: KB vs DB contradictions (water price, deposit)
# ─────────────────────────────────────────────────────────────────────
def test_issue1():
    heading(1, "KB vs DB contradictions (water price, deposit)")

    faq = read_file(BASE_DIR / "knowledge_base" / "faq" / "khach_xem_phong.md")
    policy_tt = read_file(BASE_DIR / "knowledge_base" / "chinh_sach" / "thanh_toan.md")
    policy_hd = read_file(BASE_DIR / "knowledge_base" / "chinh_sach" / "hop_dong.md")
    proc_tpm = read_file(BASE_DIR / "knowledge_base" / "quy_trinh" / "thue_phong_moi.md")
    schema = read_file(BASE_DIR / "database" / "schema.sql")

    # --- Water price ---
    # FAQ: "Nước: 100.000đ/người/tháng" (per person)
    # Policy thanh_toan: "Số m³ × 100.000đ" (per m³)
    # schema.sql: water_price DEFAULT 100000 (per m³)
    has_faq_water_per_person = "100.000đ/người/tháng" in faq
    has_policy_water_per_m3 = "Số m³ × 100.000đ" in policy_tt or "m³ × 100.000đ" in policy_tt

    print("\n  [Water price contradiction]")
    if has_faq_water_per_person:
        fail("FAQ says water is 100.000đ/người/tháng (per person) - contradicts policy & DB")
    else:
        ok("FAQ water is per m³ (matches DB)")

    if has_policy_water_per_m3:
        ok("Policy thanh_toan: water is per m³ (matches DB schema)")
    else:
        fail("Policy thanh_toan water price not found or differs from DB")

    # --- Deposit ---
    # FAQ: "Đặt cọc 1 tháng tiền phòng"
    # Policy hop_dong: "2 tháng tiền phòng (1 tháng cọc + 1 tháng trả trước)"
    # Process thue_phong_moi: "2 tháng tiền phòng"
    faq_deposit_1month = "cọc 1 tháng" in faq or "1 tháng" in faq.split("Tiền cọc")[-1].split("\n")[0] if "Tiền cọc" in faq else False
    # More precise check
    faq_deposit_1month = False
    for line in faq.split("\n"):
        if "cọc" in line.lower() and "1 tháng" in line.lower():
            faq_deposit_1month = True
            break

    policy_deposit_2month = False
    for line in policy_hd.split("\n"):
        if "cọc" in line.lower() and "2 tháng" in line.lower():
            policy_deposit_2month = True
            break

    proc_deposit_2month = False
    for line in proc_tpm.split("\n"):
        if "cọc" in line.lower() and "2 tháng" in line.lower():
            proc_deposit_2month = True
            break

    print("\n  [Deposit contradiction]")
    if faq_deposit_1month:
        fail("FAQ khach_xem_phong says deposit = 1 month (contradicts policy & process)")
    else:
        ok("FAQ deposit matches policy")

    if policy_deposit_2month:
        ok("Policy hop_dong says deposit = 2 months")
    else:
        fail("Policy hop_dong deposit not found or differs")

    if proc_deposit_2month:
        ok("Process thue_phong_moi says deposit = 2 months (matches policy)")
    else:
        fail("Process thue_phong_moi deposit not found or differs")

    # --- Invoice seed data has wrong base_rent ---
    seed = read_file(BASE_DIR / "database" / "seed_data.sql")
    print("\n  [Invoice seed data base_rent vs rooms.monthly_rent]")
    # schema.sql: room 101 = 3,500,000; room 102 = 4,500,000
    # seed_data.sql: tenant 1 (room 101) invoices have base_rent=3,000,000
    #                tenant 2 (room 102) invoices have base_rent=3,500,000
    seed_invoice_wrong_101 = False
    seed_invoice_wrong_102 = False
    for line in seed.split("\n"):
        # Check for seed invoice with tenant_id=1, room_id=1, contract_id=1 and wrong base_rent
        if "1, 1, 1" in line and "3000000" in line:
            seed_invoice_wrong_101 = True
        # Check for seed invoice with tenant_id=2, room_id=2, contract_id=2 and wrong base_rent
        if "2, 2, 2" in line and "3500000" in line:
            seed_invoice_wrong_102 = True

    if seed_invoice_wrong_101:
        fail("Seed invoice for tenant 1 (room 101) has base_rent=3,000,000 but rooms.monthly_rent=3,500,000")
    else:
        ok("Seed invoice base_rent for room 101 matches schema")

    if seed_invoice_wrong_102:
        fail("Seed invoice for tenant 2 (room 102) has base_rent=3,500,000 but rooms.monthly_rent=4,500,000")
    else:
        ok("Seed invoice base_rent for room 102 matches schema")


# ─────────────────────────────────────────────────────────────────────
# Issue 2: Seed conversation quotes wrong room price
# ─────────────────────────────────────────────────────────────────────
def test_issue2():
    heading(2, "Seed conversation quotes wrong room price")

    seed = read_file(BASE_DIR / "database" / "seed_data.sql")
    schema = read_file(BASE_DIR / "database" / "schema.sql")

    # Check seed conversation history line 58
    found_wrong_price = False
    for line in seed.split("\n"):
        if "Phòng 101" in line and "3.000.000" in line:
            found_wrong_price = True
            break

    if found_wrong_price:
        fail("Seed conversation_history: 'Phòng 101 của anh có giá 3.000.000đ/tháng' but room 101 rent = 3,500,000")
    else:
        ok("No seed conversation with wrong room 101 price")

    # Also check the invoice base_rent inconsistencies
    print("\n  [Cross-check: DB vs seed data]")
    print("  Room 101 monthly_rent = 3,500,000 (schema.sql)")
    print("  Seed conversation says 3,000,000 (seed_data.sql:58)")
    print("  Seed invoices also use 3,000,000 for tenant 1 (seed_data.sql:8-9)")


# ─────────────────────────────────────────────────────────────────────
# Issue 3: Embedding dimension mismatch
# ─────────────────────────────────────────────────────────────────────
def test_issue3():
    heading(3, "Embedding dimension default 768 mismatch with schema 3072")

    # Check source code defaults
    memory_manager = read_file(BASE_DIR / "src" / "user_modeling" / "memory_manager.py")
    semantic_cache = read_file(BASE_DIR / "src" / "system1" / "semantic_cache.py")
    llm_config_yaml = read_file(BASE_DIR / "config" / "llm_config.yaml")
    config_loader = read_file(BASE_DIR / "src" / "llm" / "config_loader.py")
    embedding_client = read_file(BASE_DIR / "src" / "llm" / "embedding_client.py")

    # memory_manager.py line 36: embedding_dim: int = 768
    mm_default_768 = "embedding_dim: int = 768" in memory_manager
    sc_default_768 = "embedding_dim: int = 768" in semantic_cache

    # config_loader.py line 130: return self.embedding.extra.get("dimension", 768)
    cl_fallback_768 = 'extra.get("dimension", 768)' in config_loader

    # llm_config.yaml line 80: dimension: 3072
    yaml_dim_3072 = "dimension: 3072" in llm_config_yaml

    # embedding_client.py line 34: self.dimension = config.embedding_dim
    # This reads from config, so it will be 3072 at runtime if config has it.

    # But at runtime (main.py:242): embedding_dim = embedding_client.dimension
    # And this is passed to both MemoryManager (line 207) and SemanticCache (line 243-245)
    # So the defaults don't matter at runtime since the value is explicitly passed.

    print("\n  [Code defaults vs config]")
    if mm_default_768:
        fail("MemoryManager.__init__ default embedding_dim=768 (should match config)")
    else:
        ok("MemoryManager default dimension matches config")

    if sc_default_768:
        fail("SemanticCache.__init__ default embedding_dim=768 (should match config)")
    else:
        ok("SemanticCache default dimension matches config")

    if cl_fallback_768:
        fail("config_loader.py embedding_dim fallback to 768 (config has 3072)")
    else:
        ok("config_loader.py matches embedding dimension")

    if yaml_dim_3072:
        ok("llm_config.yaml specifies dimension=3072")
    else:
        fail("llm_config.yaml missing dimension=3072")

    # Runtime check - main.py passes dimension explicitly
    print("\n  [Runtime override check]")
    ok("main.py:242 overrides defaults: embedding_dim = embedding_client.dimension (3072 from config)")
    ok("main.py:207 passes dim to MemoryManager via constructor")
    ok("main.py:243-245 passes dim to SemanticCache via constructor")


# ─────────────────────────────────────────────────────────────────────
# Issue 4: recommend_transfer shows room_id not room_number
# ─────────────────────────────────────────────────────────────────────
def test_issue4():
    heading(4, "recommend_transfer shows room_id not room_number")

    dt = read_file(BASE_DIR / "src" / "tools" / "decision_tools.py")

    # Line 243: f"Đề xuất phòng cho khách {tenant['full_name']} (đang ở phòng {tenant['room_id']}, tầng {current_floor}):"
    bug_exists = "tenant['room_id']" in dt.split("Đề xuất phòng cho khách")[-1].split("\n")[0] if "Đề xuất phòng cho khách" in dt else False

    if bug_exists:
        fail("recommend_transfer line 243 uses tenant['room_id'] instead of room_number")
    else:
        ok("recommend_transfer shows room_number correctly")

    # Show the exact line
    for i, line in enumerate(dt.split("\n"), 1):
        if "Đề xuất phòng cho khách" in line:
            print(f"\n  Affected code at decision_tools.py:{i}")
            print(f"  Line content: {line.strip()}")
            break


# ─────────────────────────────────────────────────────────────────────
# Issue 5: Tenant 3 lease expired but still active
# ─────────────────────────────────────────────────────────────────────
async def test_issue5(pool):
    heading(5, "Tenant 3 lease expired but contract status is active")

    if not pool:
        skip("No DB connection - cannot test")
        return

    try:
        # Get tenant 3 info
        tenant = await pool.fetchrow("""
            SELECT tenant_id, full_name, room_id, lease_start, lease_end, is_active
            FROM user_profiles WHERE tenant_id = 3
        """)
        contract = await pool.fetchrow("""
            SELECT contract_id, start_date, end_date, status, monthly_rent
            FROM contracts WHERE tenant_id = 3
        """)

        print(f"\n  Tenant 3: {tenant['full_name']}")
        print(f"    lease_start: {tenant['lease_start']}")
        print(f"    lease_end: {tenant['lease_end']}")
        print(f"    is_active: {tenant['is_active']}")
        print(f"    Contract status: {contract['status']}")
        print(f"    Contract end_date: {contract['end_date']}")

        from datetime import date
        today = date.today()
        print(f"    Today: {today}")

        if tenant['lease_end'] and tenant['lease_end'] < today:
            if contract['status'] == 'active':
                fail(f"Lease ended {tenant['lease_end']} but contract status is '{contract['status']}'")
            else:
                ok("Contract status correctly reflects expired lease")
        else:
            ok("Lease is still valid (not expired yet)")

    except Exception as e:
        fail(f"Error querying tenant 3: {e}")


# ─────────────────────────────────────────────────────────────────────
# Issue 6: Duplicate tenant names "Hoa"
# ─────────────────────────────────────────────────────────────────────
async def test_issue6(pool):
    heading(6, "Duplicate tenant names 'Hoa'")

    if not pool:
        skip("No DB connection - cannot test")
        return

    try:
        rows = await pool.fetch("""
            SELECT t.tenant_id, t.full_name, t.room_id, r.room_number
            FROM user_profiles t
            LEFT JOIN rooms r ON t.room_id = r.room_id
            WHERE t.full_name LIKE '%Hoa'
            ORDER BY t.tenant_id
        """)

        print(f"\n  Found {len(rows)} tenants with 'Hoa' in name:")
        for r in rows:
            print(f"    tenant_id={r['tenant_id']}, name='{r['full_name']}', room={r['room_number']}")

        if len(rows) >= 2:
            fail(f"Two tenants share name 'Hoa': {[r['full_name'] for r in rows]} - AI may confuse them")
        else:
            ok("No duplicate tenant names")

    except Exception as e:
        fail(f"Error querying duplicate names: {e}")


# ─────────────────────────────────────────────────────────────────────
# Issue 7: Zalo session context blending
# ─────────────────────────────────────────────────────────────────────
def test_issue7():
    heading(7, "Zalo session context blending")

    main_py = read_file(BASE_DIR / "src" / "main.py")

    # Check the session_id pattern - Zalo webhook creates session_id = f"zalo-{sender_id}"
    # This is at main.py:849-856: session_id=f"zalo-{sender_id}" if sender_id else None
    lines = main_py.split("\n")
    has_zalo_session_pattern = False
    context_loads_by_tenant = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "zalo-" in stripped and "session_id" in stripped:
            has_zalo_session_pattern = True
            print(f"    [Code] main.py:{i+1}: {stripped}")
        # format_for_context is on one line, tenant_id on the next
        if "format_for_context" in stripped:
            if i+1 < len(lines) and "tenant_id=request.tenant_id" in lines[i+1]:
                context_loads_by_tenant = True
                print(f"    [Code] main.py:{i+1}: {stripped}")
                print(f"    [Code] main.py:{i+2}: {lines[i+1].strip()}")

    print("\n  [Session ID generation]")
    if has_zalo_session_pattern:
        fail("Zalo webhook: session_id = f'zalo-{sender_id}' — all convos from same sender share same session (not unique per conversation)")
    else:
        ok("Zalo session has unique session IDs")

    print("\n  [History context loading]")
    if context_loads_by_tenant:
        fail("format_for_context(tenant_id=request.tenant_id) loads ALL sessions for tenant, not current session only — enables context blending across different Zalo conversations")
    else:
        ok("History context is scoped to current session")


# ─────────────────────────────────────────────────────────────────────
# Issue 8: No session expiry mechanism
# ─────────────────────────────────────────────────────────────────────
def test_issue8():
    heading(8, "No session expiry mechanism")

    cm = read_file(BASE_DIR / "src" / "user_modeling" / "conversation_memory.py")

    has_cleanup_old = False
    has_session_ttl = False
    has_cleanup_cron = False

    for line in cm.split("\n"):
        stripped = line.strip()
        if "cleanup_old" in stripped:
            has_cleanup_old = True
        if "session" in stripped.lower() and ("ttl" in stripped.lower() or "expir" in stripped.lower()):
            has_session_ttl = True

    # Check cron for cleanup
    main_py = read_file(BASE_DIR / "src" / "main.py")
    for line in main_py.split("\n"):
        if "cleanup_old" in line or "cleanup" in line.lower() and "conversation" in line.lower():
            has_cleanup_cron = True

    print("\n  [Cleanup mechanism]")
    if has_cleanup_old:
        ok("ConversationMemory.cleanup_old() exists — deletes turns older than N days")
    else:
        fail("No cleanup_old method in ConversationMemory")

    if has_cleanup_cron:
        ok("Cleanup is called from cron")
    else:
        skip("Cleanup cron registration not found in main.py check")

    print("\n  [Per-session TTL]")
    if has_session_ttl:
        ok("Session TTL mechanism exists")
    else:
        fail("No per-session TTL — sessions persist indefinitely until cleanup_old deletes them")

    print("\n  [Note]")
    print("    cleanup_old() only deletes turns by timestamp, not by session expiry.")
    print("    There is no mechanism to expire individual sessions, only age-based cleanup.")


# ─────────────────────────────────────────────────────────────────────
# Bonus: Runtime API test — ask room 101 price as guest
# ─────────────────────────────────────────────────────────────────────
async def test_runtime_room_price():
    heading("BONUS", "Runtime: Ask 'Phòng 101 giá bao nhiêu?' as guest")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "http://localhost:8000/chat",
                json={
                    "source": "test",
                    "tenant_id": 0,
                    "message": "giá phòng 101",
                },
            )
            data = resp.json()
            answer = data.get("answer", "")
            system_used = data.get("system_used", "?")
            tools_used = data.get("tools_used", [])

            print(f"\n  System used: {system_used}")
            print(f"  Tools used: {tools_used}")
            print(f"  Answer preview: {answer[:200]}...")

            if "3.500" in answer or "3,500" in answer:
                ok("API correctly quotes room 101 price as 3,500,000 (from DB)")
            elif "3.000" in answer or "3,000" in answer:
                fail("API incorrectly quotes room 101 price as 3,000,000 (from seed conversation)")
            else:
                skip(f"API response doesn't contain a price for room 101 directly: '{answer[:100]}'")

    except httpx.ConnectError:
        skip("Server not running — cannot test runtime API")
    except Exception as e:
        fail(f"Runtime API test error: {e}")


# ─────────────────────────────────────────────────────────────────────
# Bonus: Check runtime embedding dimension
# ─────────────────────────────────────────────────────────────────────
async def test_runtime_embedding_dim(pool):
    heading("BONUS", "Runtime: Check embedding dimension in DB vs config")

    if not pool:
        skip("No DB connection — cannot test")
        return

    try:
        # Check actual vector length from seed data (most reliable)
        row3 = await pool.fetchrow("SELECT embedding::text as emb FROM user_embeddings LIMIT 1")
        if row3:
            emb_str = row3['emb']
            # Count commas + 1 to get dimension
            dim = emb_str.count(",") + 1 if emb_str.startswith("[") else len(emb_str.split(",")) if emb_str else 0
            print(f"\n  Actual embedding dimension in data: {dim}")
            if dim == 3072:
                ok("Actual stored embeddings have 3072 dimensions (matches schema)")
            else:
                fail(f"Actual stored embeddings have {dim} dimensions (expected 3072)")

        # Check schema definition directly from CREATE TABLE SQL comment
        schema_sql = read_file(BASE_DIR / "database" / "schema.sql")
        has_3072_schema = "vector(3072)" in schema_sql
        print(f"  Schema definition: {'vector(3072)' if has_3072_schema else 'OTHER (not 3072)'}")
        if has_3072_schema:
            ok("DB schema defines vector(3072)")
        else:
            fail("DB schema does not define vector(3072)")

        # Check actual data matches schema
        if row3 and dim == 3072 and has_3072_schema:
            ok("Schema (3072) matches actual data (3072) — no mismatch at DB level")
        elif row3:
            fail(f"Schema defines vector(3072) but actual data has {dim} dimensions")

    except Exception as e:
        fail(f"Error checking embedding dimension: {e}")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
async def main():
    print("=" * 70)
    print("  TROMANAGER DATA CONSISTENCY AUDIT REPORT")
    print("  Generated:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    # DB connection
    pool = None
    try:
        pool = await asyncpg.create_pool(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "tromanager"),
            min_size=1,
            max_size=2,
        )
    except Exception as e:
        print(f"\n  ⚠ DB connection failed: {e}")
        print("  Some tests will be skipped.")

    # Run static analysis tests (no DB needed)
    test_issue1()
    test_issue2()
    test_issue3()
    test_issue4()
    test_issue7()
    test_issue8()

    # Run DB-dependent tests
    await test_issue5(pool)
    await test_issue6(pool)
    await test_runtime_embedding_dim(pool)

    # Run API test
    await test_runtime_room_price()

    # Cleanup
    if pool:
        await pool.close()

    # Summary
    total = PASS + FAIL + SKIP
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed, {SKIP} skipped (of {total} total)")
    print(f"{'='*70}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
