# Test Suite — TroManager Architecture #2

## Cấu Trúc

```
tests/
├── conftest.py                    # Shared fixtures (mock DB, LLM, Zalo, tenant data)
├── unit/                          # Unit tests — không cần DB/API thật
│   ├── test_router.py             # Router Gateway & LLM Intent Router
│   ├── test_system1_cache.py      # System 1 Semantic Cache (cosine threshold)
│   ├── test_react_loop.py         # System 2 ReAct loop logic
│   ├── test_react_timeout.py      # ReAct timeout & retry behavior
│   ├── test_rate_limiter.py       # Token bucket rate limiter
│   ├── test_retry.py              # Retry với exponential backoff
│   ├── test_json_parser.py        # JSON parsing từ LLM responses
│   ├── test_json_logging.py       # Structured JSON logging
│   ├── test_request_context.py    # Request ID middleware & context vars
│   └── test_metrics_aggregator.py # Prometheus metrics aggregation
├── integration/                   # Integration tests — cần DB mock hoặc live DB
│   ├── test_main_endpoints.py     # FastAPI endpoint tests (/chat, /health, /webhook)
│   ├── test_tools.py              # Tool Registry & individual tools
│   ├── test_proactive_event.py    # Cron EventDispatcher (invoice, contract, birthday)
│   ├── test_approval_service.py   # Human-in-the-loop Approval Queue
│   ├── test_conversation_memory.py# ConversationMemory lưu/truy xuất turns
│   ├── test_metrics_endpoint.py   # /metrics endpoint (Prometheus format)
│   └── test_shutdown.py           # Graceful shutdown & drain logic
├── audit/                         # Audit, bảo mật & hiệu năng
│   ├── audit_config_perf.py       # Config validation & performance benchmarks
│   ├── audit_data_consistency.py  # Data consistency giữa các bảng
│   ├── audit_deep_tests.py        # Deep edge cases
│   ├── audit_error_handling.py    # Error handling toàn diện
│   └── audit_security.py          # SQL injection, HMAC, rate limit abuse
└── e2e/                           # End-to-end & stress tests (cần live server)
    ├── e2e_stress_test.py          # Load testing concurrent users
    └── complex_scenarios.py        # Multi-turn conversation scenarios
```

---

## Chạy Tests

### Tất cả unit tests (nhanh, không cần DB)
```bash
pytest tests/unit/ -v
```

### Tất cả integration tests
```bash
pytest tests/integration/ -v
```

### Chỉ audit/security
```bash
pytest tests/audit/ -v
```

### E2E (cần server đang chạy)
```bash
# Khởi động server trước:
python -m uvicorn src.main:app --port 8000
# Rồi chạy:
pytest tests/e2e/ -v
```

### Toàn bộ (trừ e2e)
```bash
pytest tests/unit/ tests/integration/ tests/audit/ -v
```

### Theo marker
```bash
pytest -m unit -v
pytest -m integration -v
pytest -m "not e2e" -v
```

### Với coverage
```bash
pytest tests/unit/ tests/integration/ --cov=src --cov-report=html
```

---

## Cấu Hình

| Setting | Giá trị |
|---------|---------|
| `asyncio_mode` | `auto` (tất cả async tests) |
| `testpaths` | `tests/` |
| `python_files` | `test_*.py`, `audit_*.py` |
| `pythonpath` | `.` (project root) |

---

## Shared Fixtures (conftest.py)

| Fixture | Mô tả |
|---------|-------|
| `mock_db_pool` | Mock asyncpg Pool + Connection |
| `mock_llm_client` | Mock LLMClient với generate() |
| `mock_flash_client` | Flash model (gemma-4-31b-it) |
| `mock_pro_client` | Pro model (gemini-3.1-flash-lite) |
| `mock_embedding_client` | Embedding client (gemini-embedding-2, 3072-dim) |
| `mock_zalo_client` | Zalo OA API mock |
| `sample_tenant` | Tenant data mẫu |
| `sample_behavior_log` | Behavior log mẫu |

---

## Test Coverage Targets

| Module | Test File | Target |
|--------|-----------|--------|
| Router Gateway | `unit/test_router.py` | 90% |
| Semantic Cache | `unit/test_system1_cache.py` | 85% |
| ReAct Agent | `unit/test_react_loop.py` | 80% |
| Rate Limiter | `unit/test_rate_limiter.py` | 95% |
| API Endpoints | `integration/test_main_endpoints.py` | 80% |
| Tool Registry | `integration/test_tools.py` | 70% |
| Approval Service | `integration/test_approval_service.py` | 85% |
| Security | `audit/audit_security.py` | 100% |

---

## Mock Strategy

Tests sử dụng mock cho:
- `asyncpg.Pool` — Database connection (fixtures trong conftest.py)
- `httpx.AsyncClient` — HTTP client (Zalo, SMS)
- LLM clients — Gemini/Gemma models
- `APScheduler` — Background cron jobs

> Tests unit/ và integration/ **không** cần server đang chạy.  
> Tests e2e/ **cần** server đang chạy tại `localhost:8000`.
