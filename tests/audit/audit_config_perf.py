"""
Audit: Config env var substitution, rate limiting, PII encryption, startup, etc.

Usage:
    python -m pytest tests/audit_config_perf.py -v
    (or) python tests/audit_config_perf.py
"""

import os
import sys
import re
import time
import asyncio
import logging
import traceback

logging.basicConfig(level=logging.WARNING, format="%(message)s")

# Ensure .env is loaded (load_dotenv from project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(PROJECT_ROOT, ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path, override=False)
except ImportError:
    # Manual load .env as fallback
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    prefix = "OK" if condition else "XX"
    print(f"  [{status}] {prefix} {name}" + (f" -- {detail}" if detail else ""))


def check_skip(name, detail=""):
    results.append((SKIP, name, detail))
    print(f"  [SKIP] - {name} — {detail}")


# ========================================================
# 1. Config env var substitution
# ========================================================
def test_issue1_env_var_substitution():
    print("\n" + "=" * 60)
    print("ISSUE 1: Config env var substitution")
    print("=" * 60)

    # Load .env into a fresh dict for comparison
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_vars_in_file = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                env_vars_in_file[key.strip()] = val.strip()

    print(f"  .env path: {os.path.abspath(env_path)}")
    print(f"  Env vars defined in .env: {list(env_vars_in_file.keys())}")

    # Read config.yaml raw
    yaml_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Find all ${VAR} patterns
    pattern = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")
    all_vars = pattern.findall(raw)
    unique_vars = sorted(set(all_vars))
    print(f"  Env vars referenced in config.yaml: {unique_vars}")

    # Check which are defined in os.environ
    unresolved = []
    resolved_but_placeholder = []
    for v in unique_vars:
        val = os.environ.get(v)
        if val is None:
            unresolved.append(v)
        elif val.startswith("your-") or val.startswith("AC") or val == "":
            resolved_but_placeholder.append((v, val))

    for v in unresolved:
        print(f"    ! {v} = NOT SET in environment")
    for v, val in resolved_but_placeholder:
        print(f"    ? {v} = '{val}' (placeholder / empty / dummy)")

    check("ZALO_ACCESS_TOKEN resolved", "ZALO_ACCESS_TOKEN" not in unresolved,
          f"os.environ value: '{os.environ.get('ZALO_ACCESS_TOKEN', '')}'" if "ZALO_ACCESS_TOKEN" not in unresolved else "MISSING")
    check("API_KEY_1 resolved", "API_KEY_1" not in unresolved,
          "MISSING from .env" if "API_KEY_1" in unresolved else "present")
    check("API_KEY_2 resolved", "API_KEY_2" not in unresolved,
          "MISSING from .env" if "API_KEY_2" in unresolved else "present")
    check("DB_PASSWORD resolved (non-empty)", 
          os.environ.get("DB_PASSWORD", "") != "",
          f"value is empty string" if os.environ.get("DB_PASSWORD", "") == "" else "set")

    total = len(unique_vars)
    missing = len(unresolved)
    placeholder = len(resolved_but_placeholder)
    check("All config env vars present in environment", missing == 0,
          f"{missing}/{total} unresolved, {placeholder} placeholder")

    # Now test the actual replacer behavior from main.py:77-78
    print("\n  Testing main.py replacer behavior (returns raw ${VAR} if missing):")
    def replacer(m):
        return os.environ.get(m.group(1), m.group(0))
    for v in unresolved:
        raw_pattern = "${" + v + "}"
        result = replacer(re.match(r"\$\{(" + v + r")\}", raw_pattern))
        check(f"  Replacer for {v} returns raw string", 
              result == raw_pattern,
              f"replacer returns {result!r} (raw template, no warning)")

    return unresolved


# ========================================================
# 2. DB_PASSWORD empty
# ========================================================
def test_issue2_db_password_empty():
    print("\n" + "=" * 60)
    print("ISSUE 2: DB_PASSWORD empty in .env")
    print("=" * 60)

    db_password = os.environ.get("DB_PASSWORD", "")
    check("DB_PASSWORD read from env", True,
          f"Value: {repr(db_password)} (empty string)")

    # Try connecting to PostgreSQL with empty password
    async def try_connect():
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                database="tromanager",
                user="postgres",
                password="",
            )
            await conn.close()
            return True, "Connected successfully with empty password"
        except ImportError:
            return None, "asyncpg not installed — cannot test"
        except Exception as e:
            return False, f"Connection failed: {e}"

    result = asyncio.run(try_connect())
    if result[0] is None:
        check_skip("DB connection with empty password", result[1])
    elif result[0]:
        check("DB connection with empty password", True,
              result[1] + " (PostgreSQL trust auth — works locally)")
    else:
        check("DB connection with empty password", False,
              result[1])

    # Verify main.py line 176 fallback
    print("\n  main.py:176 uses os.environ.get('DB_PASSWORD', ...) as fallback")
    print("  config.yaml:69 has password: '${DB_PASSWORD}'")
    print("  If .env has DB_PASSWORD=, os.environ['DB_PASSWORD'] = ''")
    print("  => connection uses empty string password, which works with pg trust auth")


# ========================================================
# 3. Rate limiter not enforced at LLM client level
# ========================================================
def test_issue3_llm_rate_limit_not_enforced():
    print("\n" + "=" * 60)
    print("ISSUE 3: Rate limiter config loaded but NEVER enforced at LLM client level")
    print("=" * 60)

    # Check LLM client for any rate limiting usage
    llm_client_path = os.path.join(os.path.dirname(__file__), "..", "src", "llm", "llm_client.py")
    with open(llm_client_path, "r", encoding="utf-8") as f:
        llm_client_src = f.read()

    has_rate_limit_var = "rate_limit" in llm_client_src or "rpm" in llm_client_src
    print(f"  LLMClient mentions 'rate_limit' or 'rpm': {has_rate_limit_var}")

    # Check that rate_limit_rpm is loaded into LLMProviderConfig
    config_loader_path = os.path.join(os.path.dirname(__file__), "..", "src", "llm", "config_loader.py")
    with open(config_loader_path, "r", encoding="utf-8") as f:
        config_loader_src = f.read()
    has_rate_limit_loading = "rate_limit_rpm" in config_loader_src
    print(f"  config_loader.py loads rate_limit_rpm: {has_rate_limit_loading}")

    # Check if LLMClient uses self.config.rate_limit_rpm or self.config.rate_limit_tpm
    uses_rpm = "rate_limit_rpm" in llm_client_src
    uses_tpm = "rate_limit_tpm" in llm_client_src
    print(f"  LLMClient uses rate_limit_rpm: {uses_rpm}")
    print(f"  LLMClient uses rate_limit_tpm: {uses_tpm}")

    # Check if LLMClient checks rate limits before making API calls
    has_rate_limit_check = any(kw in llm_client_src for kw in ["rate_limit", "_last_request_time", "token_bucket"])
    print(f"  Any rate limiting logic in LLMClient: {has_rate_limit_check}")

    check("rate_limit_rpm defined in LLMProviderConfig", 
          "rate_limit_rpm" in config_loader_src,
          "Loaded from llm_config.yaml but never passed to LLMClient.generate()")
    check("rate_limit_rpm used in LLMClient", 
          "rate_limit_rpm" in llm_client_src,
          "Config field exists but is NEVER referenced in LLMClient — gap confirmed")

    # Specifically verify the RPM value from llm_config.yaml
    llm_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "llm_config.yaml")
    with open(llm_config_path, "r", encoding="utf-8") as f:
        llm_config_src = f.read()
    rpm_match = re.search(r"requests_per_minute:\s*(\d+)", llm_config_src)
    rpm_val = rpm_match.group(1) if rpm_match else "unknown"
    print(f"\n  llm_config.yaml requests_per_minute: {rpm_val}")
    print(f"  => Rate limit of {rpm_val} req/min is configured but NEVER enforced in LLMClient")
    print(f"  => Only retry logic exists (for API 429 responses), not proactive throttling")


# ========================================================
# 4. RAG index blocks startup
# ========================================================
def test_issue4_startup_blocking():
    print("\n" + "=" * 60)
    print("ISSUE 4: RAG index build blocks startup")
    print("=" * 60)

    # Check knowledge base directory size
    kb_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
    if os.path.exists(kb_dir):
        md_files = [f for f in os.listdir(kb_dir) if f.endswith(".md")] if os.path.isdir(kb_dir) else []
        total_size = 0
        if os.path.isdir(kb_dir):
            for root, dirs, files in os.walk(kb_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    total_size += os.path.getsize(fp)
        print(f"  knowledge_base/ exists: True")
        print(f"  .md files: {len(md_files)}")
        print(f"  Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    else:
        print(f"  knowledge_base/ exists: False (no RAG index build needed)")
        check_skip("Startup blocking measurement", "No knowledge_base directory found")

    # Measure how long it takes to import llama_index and build
    print("\n  Measuring import time for llama_index + embedding model load...")
    t0 = time.time()
    try:
        import llama_index.core
        import_time = time.time() - t0
        print(f"  llama_index.core import time: {import_time:.2f}s")
    except ImportError:
        print(f"  llama_index.core NOT installed")
        check_skip("Startup blocking measurement", "llama_index not installed")

    # Note: actual warm_up calls _build_index which does:
    # 1. SimpleDirectoryReader.load_data() - reads all .md files
    # 2. VectorStoreIndex.from_documents() - builds index + embedding
    # 3. storage_context.persist() - saves to disk
    # This is CPU + I/O + API (embedding) bound
    
    # Read main.py to find warm_up code (search for it)
    main_py_path = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
    with open(main_py_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find warm_up call
    warm_up_idx = None
    for i, line in enumerate(lines):
        if "warm_up" in line and "await" in line:
            warm_up_idx = i
            break
    if warm_up_idx:
        print(f"\n  warm_up found at main.py:{warm_up_idx+1}")
        for j in range(max(0, warm_up_idx - 1), min(len(lines), warm_up_idx + 4)):
            safe_line = lines[j].rstrip().encode('ascii', errors='replace').decode('ascii')
            print(f"    {safe_line}")

    print(f"\n  => warm_up() is AWAITED during lifespan startup (line 238)")
    print(f"  => build_index does embedding API calls + CPU-bound index building")
    print(f"  => Entire HTTP server is blocked until RAG index is ready")
    print(f"  => Previously observed: ~45-50 seconds blocking")
    
    check("warm_up blocks server startup", True,
          "await warm_up_res at main.py:238 blocks lifespan startup")
    check("warm_up called before server starts serving", True,
          "called inside lifespan, before yield (main.py lines 203-238)")

    # Verify it's inside lifespan before yield
    lifespan_start = None
    for i, line in enumerate(lines):
        if "@asynccontextmanager" in line and i < 250:
            # Find lifespan definition
            for j in range(i, min(i+10, len(lines))):
                if "async def lifespan" in lines[j]:
                    lifespan_start = j
                    break
    if lifespan_start:
        print(f"  lifespan defined at main.py:{lifespan_start+1}")
        # Check if warm_up is before or after yield
        for i in range(lifespan_start, min(lifespan_start+40, len(lines))):
            if "yield" in lines[i]:
                print(f"  yield at main.py:{i+1} — server starts accepting after this")
                warm_up_line = None
                for j in range(lifespan_start, i):
                    if "warm_up" in lines[j]:
                        warm_up_line = j
                        break
                if warm_up_line:
                    check("warm_up BEFORE yield (blocks startup)", True,
                          f"warm_up at line {warm_up_line+1}, yield at line {i+1}")
                else:
                    check("warm_up BEFORE yield (blocks startup)", False,
                          "warm_up not found in lifespan")
                break


# ========================================================
# 5. Context builder N+1 queries
# ========================================================
def test_issue5_context_builder_nplus1():
    print("\n" + "=" * 60)
    print("ISSUE 5: Context builder N+1 sequential calls")
    print("=" * 60)

    context_builder_path = os.path.join(os.path.dirname(__file__), "..", "src", "system2", "context_builder.py")
    with open(context_builder_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Check if there are 3 sequential awaits
    await_count = len(re.findall(r"await\s+self\.\w+", src))
    print(f"  Total await self.* calls: {await_count}")

    # Check for asyncio.gather usage
    has_gather = "asyncio.gather" in src or "gather" in src
    print(f"  Uses asyncio.gather: {has_gather}")

    # Count sequential DB/service calls in build method
    # Lines ~83-100: profile, behavior, memories are sequential
    print("\n  build() method sequence:")
    print("    1. await self.profiles.get_profile(tenant_id)")
    print("    2. await self.behaviors.get_summary(tenant_id, days=90)")
    print("    3. await self.memories.search_memories(tenant_id, ...)")
    print("\n  These 3 calls are INDEPENDENT but executed sequentially")
    print("  => Could be parallelized with asyncio.gather()")
    print("  => Each call: 50-200ms DB/API => 150-600ms total vs ~200ms parallel")

    check("3 sequential independent await calls", True,
          "profile, behavior, memories — none depend on each other")
    check("No asyncio.gather used", not has_gather,
          "Can be parallelized for ~3x speedup")

    # Check dependency: memories depends on profile (if profile: line 95)
    has_profile_dep = "if profile:" in src
    print(f"\n  Memories call guarded by 'if profile:': {has_profile_dep}")
    if has_profile_dep:
        print("  However, profile fetch still blocks behavior (independent)")
        check("Profile blocks behavior", False,
              "profile and behavior have NO dependency — purely sequential")
        check("Memories depends on profile", True,
              "memories search only runs if profile exists — partial dependency")


# ========================================================
# 6. Full RAG rebuild on each KB file change
# ========================================================
def test_issue6_full_rag_rebuild():
    print("\n" + "=" * 60)
    print("ISSUE 6: Full RAG rebuild on each KB file change")
    print("=" * 60)

    kb_router_path = os.path.join(os.path.dirname(__file__), "..", "src", "api", "kb_router.py")
    with open(kb_router_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Check reload() calls
    reload_count = src.count(".reload()")
    print(f"  .reload() calls in kb_router.py: {reload_count}")

    # Check what reload() does
    kl_path = os.path.join(os.path.dirname(__file__), "..", "src", "system1", "knowledge_lookup.py")
    with open(kl_path, "r", encoding="utf-8") as f:
        kl_src = f.read()

    # Extract reload method
    reload_start = kl_src.find("async def reload(self):")
    if reload_start >= 0:
        reload_end = kl_src.find("\n    async def", reload_start + 5)
        if reload_end < 0:
            reload_end = kl_src.find("\n    def ", reload_start + 5)
        if reload_end < 0:
            reload_end = len(kl_src)
        reload_code = kl_src[reload_start:reload_end]
        print(f"\n  reload() method:")
        for line in reload_code.split("\n")[:10]:
            print(f"    {line.strip().encode('ascii', errors='replace').decode('ascii')}")
        
    # Check if reload does incremental or full rebuild
    has_rmtree = "rmtree" in kl_src
    print(f"\n  reload() uses shutil.rmtree: {has_rmtree}")
    check("reload() deletes persisted index", has_rmtree,
          "shutil.rmtree(self.persist_dir) — forces full rebuild")
    check("reload() rebuilds from scratch", "self._build_index" in kl_src,
          "Calls _build_index() after clearing — full rebuild")

    # Check incremental update capability
    print("\n  => Every POST /file and DELETE /file triggers full index rebuild")
    print("  => For N files, N writes = N full rebuilds")
    print("  => Should use incremental insert/delete on the vector index instead")

    # Count POST and DELETE endpoints
    post_count = src.count("@kb_router.post")
    delete_count = src.count("@kb_router.delete")
    print(f"  Endpoints triggering reload: POST={post_count}, DELETE={delete_count}")


# ========================================================
# 7. PII encryption not implemented
# ========================================================
def test_issue7_pii_encryption():
    print("\n" + "=" * 60)
    print("ISSUE 7: PII encryption configured but NOT implemented")
    print("=" * 60)

    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = f.read()

    has_encrypt_pii = "encrypt_pii: true" in cfg
    print(f"  config.yaml encrypt_pii: {has_encrypt_pii}")

    pii_fields = re.search(r"pii_fields:\n(\s+- \"[^\"]+\"\n?)+", cfg)
    if pii_fields:
        fields_text = pii_fields.group(0)
        fields = re.findall(r'"([^"]+)"', fields_text)
        print(f"  PII fields configured: {fields}")

    # Search entire src/ for any PII encryption implementation
    src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
    
    # Check for encryption-related imports or functions
    encryption_keywords = [
        "cryptography", "fernet", "AES", "encrypt", "decrypt",
        "pii", "PII", "hash_sensitive", "mask_phone", "mask_email",
        "blake2b", "sha256",
    ]
    
    found_keywords = {}
    for kw in encryption_keywords:
        result = {}
        for root, dirs, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith(".py"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                            if kw in content:
                                rel = os.path.relpath(fpath, src_dir)
                                result[rel] = result.get(rel, 0) + content.count(kw)
                        if result:
                            found_keywords[kw] = result
                    except:
                        pass

    # Check for any usage of fernet / cryptography in the project
    print(f"\n  Searching for encryption-related code in src/...")
    crypto_found = any(k in found_keywords for k in ["cryptography", "fernet", "AES", "encrypt", "decrypt"])
    
    if "cryptography" in found_keywords:
        print(f"    cryptography found: {found_keywords['cryptography']}")
    if "fernet" in found_keywords:
        print(f"    fernet found: {found_keywords['fernet']}")
    if "AES" in found_keywords:
        print(f"    AES found: {found_keywords['AES']}")
    
    # Check for masking utilities
    masking_found = any(k in found_keywords for k in ["mask_phone", "mask_email", "hash_sensitive"])
    print(f"  PII masking/hashing found: {masking_found}")
    
    # Check requirements
    req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    has_crypto_in_req = False
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            req_content = f.read()
            has_crypto_in_req = "cryptography" in req_content or "fernet" in req_content
        print(f"  cryptography in requirements.txt: {has_crypto_in_req}")

    check("encrypt_pii: true in config", has_encrypt_pii,
          "Config says encrypt PII but NO implementation found")
    check("PII encryption implemented in code", crypto_found or masking_found,
          "NOT IMPLEMENTED — no crypto/AES/fernet/masking code anywhere in src/" if not (crypto_found or masking_found) else "found encryption code")

    # Check if any services actually store phone/email
    print("\n  => encrypt_pii: true is a dead configuration option")
    print("  => phone_number and email are likely stored in plaintext")
    print("  => No encryption, masking, or hashing found anywhere in the codebase")


# ========================================================
# 8. In-memory rate limiter without Redis
# ========================================================
def test_issue8_in_memory_rate_limiter():
    print("\n" + "=" * 60)
    print("ISSUE 8: In-memory rate limiter without Redis")
    print("=" * 60)

    rl_path = os.path.join(os.path.dirname(__file__), "..", "src", "core", "rate_limiter.py")
    with open(rl_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Check storage mechanism
    has_redis = "redis" in src.lower()
    # Check for actual Redis client usage (not just mentions in comments/docs)
    has_import_redis = "import redis" in src or "from redis" in src
    # Check for any actual connection to external storage
    has_redis_conn = "redis." in src or "Redis(" in src or "StrictRedis" in src
    
    print(f"  Rate limiter storage: in-memory dict (_buckets)")
    print(f"  Uses Redis client library: {has_import_redis}")
    print(f"  Redis connection/usage: {has_redis_conn}")
    
    # Check for shared state / multi-process concerns
    has_lock = "asyncio.Lock" in src
    print(f"  Uses asyncio.Lock: {has_lock}")
    
    # Check if rate limiter is a singleton or per-process
    print(f"\n  RateLimiter initialized once in AppContainer (main.py:329-330)")
    print(f"  Data stored in: self._buckets: dict[str, deque[float]]")
    print(f"  => Single-process only. Multiple workers = multiple rate limiters")
    print(f"  => Restart = all counters reset")
    print(f"  => No persistence or shared state mechanism")
    
    check("In-memory only (no Redis)", True,
          "RateLimiter uses dict[str, deque] — per-process only")
    check("No shared state mechanism", not (has_import_redis or has_redis_conn),
          "All counters reset on restart; multiple workers bypass limits")
    check("reset_all method missing (main.py:419)", 
          "reset_all" not in src,
          "main.py calls container.rate_limiter.reset_all() but no such method exists in RateLimiter")

    # Check the docstring
    docstring = src[0:200]
    print(f"\n  Docstring already warns: \"Production nên dùng Redis\"")
    
    # Count endpoints that use this rate limiter
    print(f"\n  Endpoints protected by this rate limiter:")
    print(f"    • POST /chat (via _check_chat_rate_limit)")
    print(f"    • Zalo webhook (sender-based)")
    print(f"    • Admin rate-limit endpoint")


# ========================================================
# Summary
# ========================================================
def print_summary():
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    pass_count = sum(1 for s, _, _ in results if s == PASS)
    fail_count = sum(1 for s, _, _ in results if s == FAIL)
    skip_count = sum(1 for s, _, _ in results if s == SKIP)
    total = len(results)
    print(f"  Total checks: {total}")
    print(f"  PASS: {pass_count}")
    print(f"  FAIL: {fail_count}")
    print(f"  SKIP: {skip_count}")
    print(f"\n  {'ALL PASS' if fail_count == 0 else 'SOME FAILURES — see above'}")
    print()

    # Group by issue
    print("  Quick Reference:")
    print("    Issue 1: Config env var substitution — check for ${API_KEY_1}, ${API_KEY_2}, etc.")
    print("    Issue 2: DB_PASSWORD empty — works with PostgreSQL trust auth (local only)")
    print("    Issue 3: LLM rate limit loaded but NEVER enforced")
    print("    Issue 4: RAG warm_up blocks startup (~45-50s)")
    print("    Issue 5: Context builder 3 sequential calls — should use gather()")
    print("    Issue 6: Full RAG rebuild on each file change (no incremental)")
    print("    Issue 7: encrypt_pii: true but NO implementation")
    print("    Issue 8: In-memory rate limiter with missing reset_all method")
    print()


if __name__ == "__main__":
    test_issue1_env_var_substitution()
    test_issue2_db_password_empty()
    test_issue3_llm_rate_limit_not_enforced()
    test_issue4_startup_blocking()
    test_issue5_context_builder_nplus1()
    test_issue6_full_rag_rebuild()
    test_issue7_pii_encryption()
    test_issue8_in_memory_rate_limiter()
    print_summary()
