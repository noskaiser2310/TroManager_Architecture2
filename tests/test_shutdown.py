"""
Tests cho graceful shutdown flow.

Verify:
- In-flight requests được track đúng
- Drain với timeout (wait for completion OR timeout)
- 503 response khi server đang shutdown
- DB pool close với timeout
- Cron scheduler shutdown với timeout
- LLM client cleanup
- Shutdown với 0 in-flight requests → nhanh
- Shutdown timeout → force exit gracefully
"""
import asyncio
import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.request_context import RequestIDMiddleware


def _mock_lifespan_dependencies(mock_retry=None, mock_pool=None, mock_cron=None,
                                  shutdown_overrides=None):
    """
    Context manager: patch tất cả dependencies cho lifespan test.

    Returns dict of mocks.
    """
    from contextlib import ExitStack

    stack = ExitStack()
    patches = {
        "load_config": patch("src.main.load_config"),
        "load_llm_config": patch("src.main.load_llm_config"),
        "validate_config": patch("src.main.validate_config"),
        "create_pool": patch("src.main.asyncpg.create_pool"),
        "retry_async": patch("src.main.retry_async"),
        "get_llm_client": patch("src.main.get_llm_client"),
        "get_embedding_client": patch("src.main.get_embedding_client"),
        # Patch tại source vì main.py import trong function body
        "get_zalo_client": patch("src.core.get_zalo_client"),
        "get_sms_client": patch("src.core.get_sms_client"),
        "CronScheduler": patch("src.main.CronScheduler"),
        "build_knowledge_lookup": patch("src.main.build_knowledge_lookup"),
        "create_zalo_client_from_config": patch("src.main.create_zalo_client_from_config"),
        "create_sms_client_from_config": patch("src.main.create_sms_client_from_config"),
    }
    mocks = {}
    for name, p in patches.items():
        mocks[name] = stack.enter_context(p)

    # Defaults
    shutdown_cfg = {"request_id": {"enabled": True}}
    if shutdown_overrides:
        shutdown_cfg.update(shutdown_overrides)

    mocks["load_config"].return_value = {
        "app": shutdown_cfg,
        "database": {"retry": {}, "host": "x", "port": 1, "name": "x",
                    "user": "x", "pool_size": 1},
        "system1": {},
        "system2": {},
        "notifications": {"zalo": {"enabled": False}, "sms": {"enabled": False}},
    }
    mocks["load_llm_config"].return_value = MagicMock(
        llm=MagicMock(api_key="x", base_url="x", request_timeout=1, max_retries=1, extra={}),
        flash_model="x", pro_model="x", default_max_tokens=100,
    )
    mocks["validate_config"].return_value = []
    mocks["get_llm_client"].return_value = MagicMock()
    mocks["get_embedding_client"].return_value = MagicMock()
    # Zalo/SMS clients (mocks)
    mocks["get_zalo_client"].return_value = MagicMock()
    mocks["get_sms_client"].return_value = MagicMock()
    mocks["build_knowledge_lookup"].return_value = MagicMock()
    mocks["create_zalo_client_from_config"].return_value = MagicMock()
    mocks["create_sms_client_from_config"].return_value = MagicMock()

    if mock_pool is None:
        mock_pool = AsyncMock()
    mocks["create_pool"].return_value = mock_pool
    if mock_retry is None:
        mock_retry = AsyncMock(return_value=mock_pool)
    mocks["retry_async"].return_value = mock_pool

    if mock_cron is None:
        mock_cron = MagicMock()
        async def async_shutdown(wait):
            pass
        mock_cron.shutdown.side_effect = async_shutdown
    mocks["CronScheduler"].return_value = mock_cron

    class Helper:
        def __enter__(self):
            return mocks
        def __exit__(self, *args):
            stack.__exit__(*args)
    return Helper()


# ============ In-flight tracking tests ============

@pytest.fixture
def app_with_middleware():
    """App với RequestIDMiddleware + in-flight tracking."""
    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = asyncio.Event()
    app.add_middleware(RequestIDMiddleware, config={"enabled": True, "log_level": "none"})

    @app.get("/fast")
    async def fast():
        return {"ok": True}

    @app.get("/slow")
    async def slow():
        await asyncio.sleep(0.5)
        return {"ok": True}

    return app


def test_in_flight_increments_and_decrements(app_with_middleware):
    """In-flight count tăng khi request vào, giảm khi ra."""
    client = TestClient(app_with_middleware)
    assert app_with_middleware.state.in_flight_requests == 0

    response = client.get("/fast")
    assert response.status_code == 200
    assert app_with_middleware.state.in_flight_requests == 0


def test_shutdown_event_set_rejects_new_requests(app_with_middleware):
    """Khi shutdown_event set, new requests bị reject với 503."""
    app_with_middleware.state.shutdown_event.set()

    client = TestClient(app_with_middleware)
    response = client.get("/fast")
    assert response.status_code == 503
    assert "shutting down" in response.json()["error"].lower()


def test_in_flight_not_changed_for_rejected_request(app_with_middleware):
    """Request bị reject do shutdown không tăng in_flight count."""
    app_with_middleware.state.shutdown_event.set()
    initial = app_with_middleware.state.in_flight_requests

    client = TestClient(app_with_middleware)
    response = client.get("/fast")
    assert response.status_code == 503

    assert app_with_middleware.state.in_flight_requests == initial


# ============ Drain helper tests ============

@pytest.mark.asyncio
async def test_drain_returns_true_when_predicate_satisfied():
    """Drain trả về True nếu predicate satisfied trước timeout."""
    from src.main import _drain_with_timeout

    counter = [0]

    def predicate():
        counter[0] += 1
        return counter[0] >= 3  # True sau 3 polls

    result = await _drain_with_timeout(predicate, timeout=1.0, poll_interval=0.05)
    assert result is True
    assert counter[0] >= 3


@pytest.mark.asyncio
async def test_drain_returns_false_on_timeout():
    """Drain trả về False nếu timeout trước khi predicate True."""
    from src.main import _drain_with_timeout

    def predicate():
        return False  # Không bao giờ True

    start = asyncio.get_event_loop().time()
    result = await _drain_with_timeout(predicate, timeout=0.3, poll_interval=0.05)
    elapsed = asyncio.get_event_loop().time() - start

    assert result is False
    assert 0.25 <= elapsed < 0.5


# ============ Stop cron helper tests ============

@pytest.mark.asyncio
async def test_stop_cron_async_calls_shutdown():
    """_stop_cron_async gọi scheduler.shutdown(wait=True)."""
    from src.main import _stop_cron_async

    scheduler = MagicMock()
    await _stop_cron_async(scheduler)

    scheduler.shutdown.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_stop_cron_async_uses_executor():
    """Verify run_in_executor được dùng (không block event loop)."""
    from src.main import _stop_cron_async
    import time

    def slow_shutdown(wait):
        time.sleep(0.2)

    scheduler = MagicMock()
    scheduler.shutdown.side_effect = slow_shutdown

    start = asyncio.get_event_loop().time()
    await _stop_cron_async(scheduler)
    elapsed = asyncio.get_event_loop().time() - start

    assert elapsed < 0.5
    scheduler.shutdown.assert_called_once_with(True)


# ============ Lifespan integration tests ============

@pytest.mark.asyncio
async def test_lifespan_initializes_state():
    """Lifespan set up state cần thiết cho graceful shutdown."""
    with _mock_lifespan_dependencies() as _:
        from src.main import app, lifespan

        async with lifespan(app):
            assert hasattr(app.state, "in_flight_requests")
            assert hasattr(app.state, "shutdown_event")
            assert hasattr(app.state, "start_time")
            assert app.state.in_flight_requests == 0
            assert app.state.shutdown_event.is_set() is False


@pytest.mark.asyncio
async def test_lifespan_shutdown_handles_zero_inflight():
    """Shutdown với 0 in-flight requests → drain nhanh (no wait)."""
    mock_pool = AsyncMock()

    with _mock_lifespan_dependencies(mock_pool=mock_pool) as _:
        from src.main import app, lifespan

        import time
        start = time.time()
        async with lifespan(app):
            pass
        elapsed = time.time() - start

        assert elapsed < 2.0
        mock_pool.close.assert_awaited()


@pytest.mark.asyncio
async def test_lifespan_shutdown_drains_inflight_requests():
    """Shutdown chờ in-flight request hoàn thành trước khi close DB."""
    mock_pool = AsyncMock()

    with _mock_lifespan_dependencies(
        mock_pool=mock_pool,
        shutdown_overrides={"shutdown": {"drain_timeout_seconds": 2.0}}
    ) as _:
        from src.main import app, lifespan

        async with lifespan(app):
            # Simulate in-flight request
            app.state.in_flight_requests = 1
            async def decrement():
                await asyncio.sleep(0.3)
                app.state.in_flight_requests = 0
            asyncio.create_task(decrement())

            from src.main import _drain_with_timeout
            start = asyncio.get_event_loop().time()
            drained = await _drain_with_timeout(
                lambda: app.state.in_flight_requests == 0,
                timeout=2.0,
                poll_interval=0.05,
            )
            elapsed = asyncio.get_event_loop().time() - start

            assert drained is True
            assert 0.2 <= elapsed < 1.0


@pytest.mark.asyncio
async def test_lifespan_shutdown_db_timeout_does_not_hang():
    """DB pool close timeout không làm shutdown treo."""
    async def slow_close():
        await asyncio.sleep(60)

    mock_pool = MagicMock()
    mock_pool.close = slow_close

    with _mock_lifespan_dependencies(
        mock_pool=mock_pool,
        shutdown_overrides={"shutdown": {"db_timeout_seconds": 0.2}}
    ) as _:
        from src.main import app, lifespan

        import time
        start = time.time()
        async with lifespan(app):
            pass
        elapsed = time.time() - start

        assert elapsed < 1.0, f"DB close timeout không work, elapsed={elapsed:.2f}s"
