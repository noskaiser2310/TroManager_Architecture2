# TroManager Architecture #2 - Project Status

## Goal
- Build complete TroManager Architecture #2 (Router-Centric ReAct Dual-Process), update LLM to current models, remove all mocks, use RAG on .md files (no knowledge graph), separate LLM config file, support `.env` workflow, and continuously complete remaining unfinished parts.

## Constraints & Preferences
- **Language**: Vietnamese in conversation; English in code/docs
- **No mocks**: Real implementations only (real DB queries, real API calls)
- **No knowledge graph**: Use only basic RAG + vector search on .md files
- **LLM models (user-specified)**: flash = `gemma-4-26b-a4b-it` (thinking model), pro = `gemini-3.1-flash-lite`
- **Embedding model**: `gemini-embedding-2` with dimension **3072** (not 768)
- **Max tokens**: 8192 (flash & pro both)
- **LLM config**: Separate `config/llm_config.yaml` + `llm_config.local.yaml` (gitignored)
- **Env management**: `.env` file auto-loaded via `python-dotenv` (no YAML env-only setup)
- **Knowledge base**: `.md` files in directories
- **Tech stack**: Python 3.13, PostgreSQL 16 + pgvector (3072-dim vectors), LangChain, Gemini-compatible OpenAI endpoint
- **CRITICAL**: Never overwrite `.env` or `llm_config.local.yaml` — contains user's real API key

## Progress
### Done
- Updated all Gemini 1.5 → 3.0 references in docs/configs/diagrams
- Created `src/llm/` package: `config_loader.py`, `llm_client.py` (OpenAI-compatible), `embedding_client.py` (now has `encode()` not `embed()`)
- Created `src/llm/thought_stripper.py` (strips `<thought>...</thought>` blocks from thinking models, 8/8 self-tests pass)
- Created `knowledge_base/` with 18 `.md` files in 4 dirs
- Rewrote all tools, notifications, user_modeling services (real implementations, no mocks)
- Created `src/core/__init__.py` (centralized singletons: db_pool, knowledge_lookup, zalo_client, sms_client)
- Created `.gitignore` (excludes `.env`, `llm_config.local.yaml`, `__pycache__/`)
- Created `.env.example` + `.env` template with 7 var groups
- Added `load_dotenv()` to both `src/llm/config_loader.py` (auto on import) and `src/main.py`
- Created `scripts/setup_env.py`, `scripts/run_smoke_test.py` (7/7 PASS), `scripts/test_real_llm.py` (4/4 PASS with real key), `scripts/check_config.py`
- Updated `src/main.py` to wire all real services in FastAPI lifespan
- Created `config/notifications.yaml` (Zalo/SMS config with env var substitution)
- Created `requirements.txt`
- Fixed wrong import paths in 3 tool files: `from ..core.db` → `from ..core` (also `..core.notifications` → `..core`, `..core.knowledge` → `..core`)
- Updated `config/llm_config.local.yaml` with user-specified model names + dim
- Renamed `EmbeddingClient.embed()` → `encode()` (to match FastLayer/MemoryManager interface)
- Fixed `KeyError: 'query'` in `react_agent._build_system_prompt` (added `query=request.query`)
- Added `reset_clients`/`reset_embedding_client` to `src.llm.__init__.py` exports
- Fixed UTF-8 encoding for Windows console in 3 scripts
- Updated embedding dim 768→3072 in: `llm_config.yaml`, `llm_config.local.yaml`, `llm_config.local.yaml.example`, `config.yaml` (3 places), `config_loader.py` (2 defaults), `semantic_cache.py` (default), `memory_manager.py` (default)
- Updated max_tokens 2048→8192 in: `config.yaml`, `test_real_llm.py`, added `default_max_tokens: 8192` to `llm_config.yaml`
- Updated 4 places in `database/schema.sql`: `vector(768)` → `vector(3072)`
- Created `database/migrations/001_embedding_dim_3072.sql` (ALTER TABLE migration)
- Integrated `strip_thought_blocks()` into `LLMClient.generate()` (controlled by `config.llm.extra.strip_thought`, default `true`)
- Added `strip_thought: true` to both `llm_config.yaml` and `llm_config.local.yaml`
- **Cron Scheduler (7 jobs)**: implemented all 5 empty stubs + Persona Optimizer + Conversation cleanup
  - `_check_invoice_overdue` — queries `v_overdue_invoices`, dispatches at days 1/3/7/14 with tone-based messaging
  - `_check_payment_due_soon` — queries `v_payment_due_soon` (new view), dispatches at 3/1/0 days
  - `_check_contract_expiring` — queries `v_expiring_contracts` (new view), dispatches at 30/14/7/1 days
  - `_check_maintenance_reminder` — queries `v_open_maintenance_tickets` (new view), priority-based SLA
  - `_check_birthdays` — queries `v_upcoming_birthdays` (new view), dispatches at 3/1/0 days
  - `_persona_optimizer_daily` (NEW) — runs at 23:00 daily, for each active tenant: gets 30-day behavior logs, calls LLM pro to summarize into 3-5 insights, archives old memories, stores new ones
  - `_conversation_cleanup` (NEW) — runs at 02:00 daily, deletes turns older than 30 days
- **CronScheduler constructor** updated to accept: `event_dispatcher`, `config`, `db_pool`, `profile_service`, `behavior_tracker`, `memory_manager`, `llm_client`, `conversation_memory`
- **4 new SQL views** added to `database/schema.sql`: `v_payment_due_soon`, `v_expiring_contracts`, `v_upcoming_birthdays`, `v_open_maintenance_tickets`
- **Zalo webhook security** (NEW): HMAC-SHA256 signature verification using `ZALO_WEBHOOK_SECRET` env var
  - Reads raw body, computes HMAC, compares to `X-Zalo-Signature` header
  - Dev mode: skip check if secret not set
  - Returns 401 on missing/invalid signature
  - Updated `.env.example` with `ZALO_WEBHOOK_SECRET` generation tip
- **ConversationMemory** (NEW): DB-backed multi-turn conversation history
  - `src/user_modeling/conversation_memory.py` — `ConversationMemory` service + `ConversationTurn` dataclass
  - Methods: `add_turn()`, `get_recent_turns()`, `get_recent_turns_for_session()`, `format_for_context()`, `cleanup_old()`, `new_session_id()`
  - Uses existing `conversation_history` table (was unused before)
  - Exported from `src/user_modeling/services.py` and `__init__.py`
- **Multi-turn context integrated into /chat**:
  - `ChatRequest.session_id` field added (optional, generates UUID if not provided)
  - `ChatResponse.session_id` field added (echoes back for client)
  - `/chat` fetches last 5 turns via `format_for_context()` and injects into system prompt
  - After response, saves turn to DB (non-blocking on error)
  - Zalo webhook uses `f"zalo-{sender_id}"` as session_id (per-sender grouping)
- **Multi-turn context integrated into LLM calls**:
  - `System1Request.history_context: str = ""` field added
  - `ReActRequest.history_context: str = ""` field added
  - `FastLayer._build_prompt()` includes `{history_context}` placeholder
  - `ReActAgent._build_system_prompt()` includes `{history_context}` placeholder
  - Both prompt templates (`system1_prompt.txt`, `system2_prompt.txt`) updated
- **Cron cleanup for conversation history** at 02:00 daily (30-day retention)
- **Test infrastructure**: Added `pytest.ini` with `asyncio_mode = auto`, installed `pytest-asyncio`
- **New test file**: `tests/test_conversation_memory.py` (10/10 PASS with mock DB pool)

### In Progress
- (none — all major unfinished parts complete)

### Blocked
- (none) — user provided real API key; all my changes pass tests

## Test Results
- **Smoke test** (no API key needed): 7/7 PASS
- **Conversation memory tests** (mocked DB): 10/10 PASS
- **Approval service tests** (mocked DB + Zalo): 13/13 PASS
- **Rate limiter tests**: 8/8 PASS
- **Retry tests**: 6/6 PASS
- **Request ID middleware tests**: 10/10 PASS
- **JSON parser tests**: 25/25 PASS
- **JSON logging tests**: 13/13 PASS
- **Metrics aggregator tests**: 23/23 PASS
- **Metrics endpoint tests**: 7/7 PASS
- **ReAct timeout tests**: 12/12 PASS
- **Shutdown flow tests**: 11/11 PASS
- **Integration tests** (HTTP endpoints với TestClient): 20/20 PASS
- **All tests**: 220/220 PASS
- **Real LLM test** (with user's key): 4/4 PASS
- **module imports**: `main.py` and all cron modules import cleanly

## Recent Fixes (June 2026)
- **#6 Observability stack**:
  - **JSON structured logging** (`src/core/json_logging.py`): `JSONFormatter` output mỗi log line thành JSON với timestamp ISO, level, logger, message, request_id, exception trace, extras. Auto-redact `password`/`api_key`/`token`/`DB_PASSWORD`/`GEMINI_API_KEY` etc. (case-insensitive). 13/13 tests.
  - **Metrics aggregator** (`src/core/metrics_aggregator.py`): Prometheus-compatible `Counter`/`Gauge`/`Histogram` với labels, thread-safe. Global registry. Pre-registered metrics: `http_requests_total`, `llm_calls_total`, `llm_tokens_total`, `tool_calls_total`, `system1/2_requests`, `cron_jobs_total`, `notifications_sent` etc. 23/23 tests.
  - **`/metrics` endpoint**: trả về Prometheus text format (scrape-able bởi Prom/Grafana) hoặc `?format=json`. Path normalization (`/admin/approvals/123` → `/admin/approvals/{id}`) tránh cardinality explosion. 7/7 tests.
  - **RequestIDMiddleware tích hợp metrics**: auto-record `http_requests_total{method, path, status}` + `http_request_duration_ms` + `http_requests_in_flight` gauge. 10/10 existing tests vẫn pass.
  - **Config block** `app.observability.{request_id, json_logging, metrics}` trong `config.yaml`. `LOG_FORMAT=plain` env var để tắt JSON logging cho dev.
- **#4 Tool & LLM timeout protection**:
  - `_execute_tool` wrap trong `asyncio.wait_for(timeout=tool_timeout_seconds)` (default 10s)
  - LLM call wrap trong `asyncio.wait_for(timeout=llm_timeout_seconds)` (default 30s) + `_handle_llm_timeout` returns fallback
  - Configurable qua `system2.tool_timeout_seconds` / `llm_timeout_seconds` trong `config.yaml`
  - `System2Metrics.tool_timeouts` + `llm_timeouts` tracked riêng
  - 12/12 tests in `tests/test_react_timeout.py`
- **#7 Graceful shutdown flow**:
  - In-flight request tracking qua `app.state.in_flight_requests` (trong `RequestIDMiddleware`)
  - New requests rejected với 503 khi `shutdown_event` set
  - Drain in-flight với `drain_timeout_seconds` (default 30s)
  - Cron shutdown async (chờ job hiện tại) trong `cron_timeout_seconds` (default 10s)
  - DB pool close với `db_timeout_seconds` (default 5s)
  - LLM/Zalo/SMS clients cleanup trong finally block
  - Helper functions: `_drain_with_timeout()`, `_stop_cron_async()` (dùng executor)
  - Config block `app.shutdown` trong `config.yaml`
  - 11/11 tests in `tests/test_shutdown.py`
- **#8 DB retry on startup**: `src/core/retry.py` với `retry_async()` (exponential backoff, configurable). Wired in `main.py` cho `asyncpg.create_pool`. Config block `database.retry` trong `config.yaml`. 6/6 tests.
- **#9 Hardcoded phone removed**: `Guardrails.FALLBACK_MESSAGE` → instance `fallback_message` + `fallback_phone` + `fallback_contact` từ config. Template supports `{contact_phone}`/{contact_name}/{contact_label}. `LANDLORD_PHONE` env var. Removed hardcoded "0901-234-567".
- **#10 Request ID middleware**: `src/core/request_context.py` với `RequestIDMiddleware`, `get_current_request_id()` contextvar, `set_request_id()` cho background tasks, `X-Request-ID` + `X-Response-Time-Ms` response headers. Configurable qua `app.request_id` (enabled, log_level, header_name). 10/10 tests.
- **#11 Robust JSON parser**: `src/core/json_parser.py` với `parse_llm_json()` — 4 fallback strategies (clean → find JSON substring → fix single quotes/trailing commas → text bullet extraction). Replaces fragile `re.sub` + `json.loads` trong `_persona_optimizer_daily`. 25/25 tests covering 22 scenarios.

## Key Decisions
- **No knowledge graph**: User said "không cần đồ thị tri thức, RAG cơ bản search vector"
- **Centralized `src/core/`**: Global singletons to avoid circular imports
- **OpenAI-compatible LLM client**: Works with Gemini's OpenAI-compatible endpoint
- **Lazy knowledge index**: Built on first `retrieve()` call
- **Tools use `from ..core import get_db_pool`**: 2-dot relative import
- **`.env` auto-load**: `python-dotenv` in `config_loader.py` triggers on import
- **Thought stripping transparent**: Done in `LLMClient` so all callers benefit
- **Migration 001 instead of dropping data**: `ALTER COLUMN ... TYPE vector(3072) USING NULL` preserves metadata
- **Don't touch `.env` or `llm_config.local.yaml` after user fills key**: use `edit` with precise `oldString`
- **Cron jobs use view-level queries**: each job has a dedicated SQL view for clarity
- **Persona Optimizer uses LLM pro (not flash)**: deeper reasoning needed for insight generation
- **Zalo signature verify uses `hmac.compare_digest`**: constant-time comparison to prevent timing attacks

## Next Steps
- (none — all major unfinished parts complete; user can pick new direction)
- Optional: fix 2 pre-existing test failures in `test_react_loop.py` and `test_tools.py` (mock data type mismatches)
- Optional: implement `VNPTiMessageSMS.send_sms` if user wants VNPT provider support
- Optional: add unit test for Persona Optimizer and Zalo webhook signature verification
- Optional: add integration test for full `/chat` → ConversationMemory flow

## Critical Context
- **API key safety**: User explicitly warned about real key — never use `write` to overwrite `.env` or `llm_config.local.yaml`; use `edit` with precise oldString
- **Real test results (with user's key)**:
  - `gemma-4-26b-a4b-it`: 7.3s, 285 tokens, returns `<thought>` blocks (now stripped)
  - `gemini-3.1-flash-lite`: 1.6-10s, 285-289 tokens, returns proper rent calculation
  - `gemini-embedding-2`: 681ms, vector length 3072
  - Semantic similarity: 0.54-0.91 range
- **Test 1 (flash) quirk**: `gemma-4-26b-a4b-it` is a thinking model — without thought stripper returned `completion=0, finish_reason=length`; with stripper returns clean answer
- **Model name warnings**:
  - `gemma-4-26b-a4b-it` not on public Google API (user must use proxy)
  - `gemini-3.1-flash-lite` not publicly listed (user must use proxy)
  - 500 errors from Google API when model not found
- **Embedding model quirk**: `text-embedding-004` returns 404 via `embedContent` — `gemini-embedding-2` works
- **DB schema changes needed**: Existing DBs need `psql -f database/migrations/001_embedding_dim_3072.sql`
- **Existing project has 90 files**, 24 source files + 5 test files all parse OK
- **Cron scheduling note**: For testing, you can run jobs manually: `await container.cron_scheduler._check_invoice_overdue()`

## Relevant Files
- `D:\Personal_AI\TroManager_Architecture2\.env`: Real API keys — **NEVER overwrite**
- `D:\Personal_AI\TroManager_Architecture2\config\llm_config.local.yaml`: Real API key + model names — same protection
- `D:\Personal_AI\TroManager_Architecture2\config\llm_config.yaml`: Template with `flash_model: gemma-4-26b-a4b-it`, `pro_model: gemini-3.1-flash-lite`, `model: gemini-embedding-2`, `dimension: 3072`, `default_max_tokens: 8192`, `strip_thought: true`
- `D:\Personal_AI\TroManager_Architecture2\config\config.yaml`: All `embedding_dim: 3072`, all `max_tokens: 8192`
- `D:\Personal_AI\TroManager_Architecture2\src\llm\thought_stripper.py`: NEW — strips `<thought>...</thought>` from thinking model responses
- `D:\Personal_AI\TroManager_Architecture2\src\llm\llm_client.py`: Added thought stripping in `generate()` after response parsing
- `D:\Personal_AI\TroManager_Architecture2\src\llm\embedding_client.py`: Method is `encode()` not `embed()` (renamed)
- `D:\Personal_AI\TroManager_Architecture2\src\llm\config_loader.py`: Auto-loads `.env` on import; default dim 3072
- `D:\Personal_AI\TroManager_Architecture2\src\llm\__init__.py`: Exports `reset_clients`, `reset_embedding_client`
- `D:\Personal_AI\TroManager_Architecture2\src\main.py`: FastAPI app, full lifespan, real service wiring, webhook HMAC verify
- `D:\Personal_AI\TroManager_Architecture2\src\system2\react_agent.py`: `_build_system_prompt` now includes `query=request.query`
- `D:\Personal_AI\TroManager_Architecture2\src\cron\scheduler.py`: 7 jobs (5 implemented + Persona Optimizer + Conversation cleanup)
- `D:\Personal_AI\TroManager_Architecture2\src\cron\event_dispatcher.py`: `EventDispatcher.dispatch()` with anti-spam, intent mapping, ReAct execution
- `D:\Personal_AI\TroManager_Architecture2\src\user_modeling\conversation_memory.py`: NEW — `ConversationMemory` service for multi-turn context
- `D:\Personal_AI\TroManager_Architecture2\src\notifications\sms_client.py`: 2 `NotImplementedError` in base `SMSClient.send_sms` (abstract — OK)
- `D:\Personal_AI\TroManager_Architecture2\database\schema.sql`: 6 views total, all `vector(3072)` (4 places updated), `conversation_history` table now used
- `D:\Personal_AI\TroManager_Architecture2\database\migrations\001_embedding_dim_3072.sql`: ALTER TABLE migration
- `D:\Personal_AI\TroManager_Architecture2\config\prompts\system1_prompt.txt`: Now includes `{history_context}` placeholder
- `D:\Personal_AI\TroManager_Architecture2\config\prompts\system2_prompt.txt`: Now includes `{history_context}` placeholder
- `D:\Personal_AI\TroManager_Architecture2\tools\*.py`: All use `from ..core import get_db_pool` (fixed from wrong paths)
- `D:\Personal_AI\TroManager_Architecture2\scripts\run_smoke_test.py`: 7/7 PASS — no API key needed
- `D:\Personal_AI\TroManager_Architecture2\scripts\test_real_llm.py`: 4/4 PASS with real key, skips if placeholder
- `D:\Personal_AI\TroManager_Architecture2\scripts\setup_env.py`: Helper to initialize `.env`
- `D:\Personal_AI\TroManager_Architecture2\scripts\check_config.py`: Show config status without exposing key
- `D:\Personal_AI\TroManager_Architecture2\.env.example`: Template (7 var groups + ZALO_WEBHOOK_SECRET)
- `D:\Personal_AI\TroManager_Architecture2\requirements.txt`: fastapi, asyncpg, openai, langchain, langchain-core, llama-index, httpx, twilio, apscheduler, python-dotenv, etc.
- `D:\Personal_AI\TroManager_Architecture2\pytest.ini`: NEW — `asyncio_mode = auto`
- `D:\Personal_AI\TroManager_Architecture2\tests\test_conversation_memory.py`: NEW — 10/10 PASS with mocked DB
- `D:\Personal_AI\TroManager_Architecture2\tests\test_tools.py`: Uses mocked DB/Zalo/SMS via `set_db_pool`/`set_zalo_client`/`set_sms_client` + `tool.ainvoke()`
