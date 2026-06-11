# Test Suite

## Cấu Trúc

```
tests/
├── test_router.py            # Router Gateway tests
├── test_system1_cache.py     # System 1 Semantic Cache tests
├── test_react_loop.py        # System 2 ReAct Agent tests
├── test_proactive_event.py   # Cron & EventDispatcher tests
└── test_tools.py             # Tool Registry & individual tool tests
```

## Cài Đặt

```bash
pip install pytest pytest-asyncio
```

## Chạy Tests

### Tất cả tests
```bash
pytest tests/ -v
```

### Theo file
```bash
pytest tests/test_router.py -v
```

### Theo test name pattern
```bash
pytest tests/ -v -k "test_sensitive"
```

### Với coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Coverage

| Module | Test File | Coverage Target |
|--------|-----------|-----------------|
| Router Gateway | test_router.py | 90% |
| Keyword Classifier | test_router.py | 95% |
| Semantic Cache | test_system1_cache.py | 85% |
| ReAct Agent | test_react_loop.py | 80% |
| Guardrails | test_react_loop.py | 90% |
| EventDispatcher | test_proactive_event.py | 85% |
| Tool Registry | test_tools.py | 90% |
| Individual Tools | test_tools.py | 70% |

## Các Test Quan Trọng

### 1. Routing Test
Đảm bảo tất cả sensitive keywords đều đi System 2:
```python
@pytest.mark.parametrize("query,expected_system,expected_keywords", [
    ("Tôi còn nợ bao nhiêu?", SYSTEM2, ["nợ"]),
    ("Hợp đồng còn bao lâu?", SYSTEM2, ["hợp đồng"]),
    # ...
])
```

### 2. Cache Test
Đảm bảo cache hit/miss hoạt động đúng với threshold 0.9.

### 3. ReAct Loop Test
- Test final answer (no tool calls)
- Test loop breaker tại max_iterations
- Test tool execution success/failure
- Test sensitive tool approval

### 4. Anti-Spam Test
Đảm bảo không spam notifications:
- Max 2 reminders/week
- Min 24h giữa các reminders

## Mock Strategy

Tests sử dụng mock cho:
- `asyncpg.Pool` - Database connection
- `httpx.AsyncClient` - HTTP client
- LLM clients (Gemini, etc.)
- LangChain components

Điều này cho phép tests chạy nhanh không cần real DB/API.

## Continuous Integration

GitHub Actions example:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio
      - run: pytest tests/ -v --cov=src
```

## Manual Integration Tests

Ngoài unit tests, cần manual integration tests:

### Scenario 1: User gửi câu hỏi về wifi
1. Khởi động app
2. Gửi message: "Wifi mật khẩu gì?"
3. Expected: System 1 xử lý, trả lời ngay từ cache
4. Verify: Log cho thấy cache hit

### Scenario 2: User báo hỏng điều hòa
1. Gửi: "Điều hòa phòng tôi bị hỏng"
2. Expected: System 2 xử lý, tạo ticket
3. Verify: Ticket được tạo trong DB, message gửi qua Zalo

### Scenario 3: Cron gửi nhắc nợ
1. Đợi cron job chạy
2. Expected: Tenant nhận được Zalo nhắc nợ
3. Verify: behavior_log có entry "auto_invoice_overdue"

## Test Data

Sử dụng seed data trong `database/seed_data.sql` cho integration tests.
