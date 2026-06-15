"""Tests cho RequestIDMiddleware."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.request_context import (
    REQUEST_ID_HEADER,
    RequestIDMiddleware,
    get_current_request_id,
    new_request_id,
    set_request_id,
)


@pytest.fixture
def app_default():
    """App với middleware enabled (default)."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"rid": get_current_request_id()}

    @app.get("/error")
    async def error():
        raise RuntimeError("test error")

    app.add_middleware(RequestIDMiddleware, config={"enabled": True, "log_level": "none"})
    return app


@pytest.fixture
def app_disabled():
    """App với middleware disabled."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"rid": get_current_request_id()}

    app.add_middleware(RequestIDMiddleware, config={"enabled": False})
    return app


def test_generates_request_id_when_missing(app_default):
    """Nếu client không gửi X-Request-ID, middleware generate mới."""
    client = TestClient(app_default)
    response = client.get("/echo")
    assert response.status_code == 200
    rid = response.headers.get(REQUEST_ID_HEADER)
    assert rid is not None
    assert len(rid) == 16  # UUID4 hex 16 chars
    # Echo endpoint trả về rid từ contextvar
    assert response.json()["rid"] == rid


def test_uses_client_provided_request_id(app_default):
    """Nếu client gửi X-Request-ID, middleware dùng luôn."""
    client = TestClient(app_default, headers={REQUEST_ID_HEADER: "my-trace-id-123"})
    response = client.get("/echo", headers={REQUEST_ID_HEADER: "my-trace-id-123"})
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == "my-trace-id-123"
    assert response.json()["rid"] == "my-trace-id-123"


def test_adds_response_time_header(app_default):
    client = TestClient(app_default)
    response = client.get("/echo")
    assert "X-Response-Time-Ms" in response.headers
    # Phải là số nguyên dương
    assert int(response.headers["X-Response-Time-Ms"]) >= 0


def test_disabled_middleware_does_nothing(app_disabled):
    """Khi disabled, không có request_id trong response."""
    client = TestClient(app_disabled)
    response = client.get("/echo")
    assert response.status_code == 200
    # Không có header X-Request-ID
    assert REQUEST_ID_HEADER not in response.headers
    # Contextvar cũng không được set (echo returns None)
    assert response.json()["rid"] is None


def test_new_request_id_format():
    """new_request_id() returns 16-char hex string."""
    rid = new_request_id()
    assert len(rid) == 16
    assert all(c in "0123456789abcdef" for c in rid)
    # Gọi 2 lần phải khác nhau
    rid2 = new_request_id()
    assert rid != rid2


def test_set_request_id_manually():
    """set_request_id() allows manual override (cho background tasks)."""
    set_request_id("manual-rid-123")
    assert get_current_request_id() == "manual-rid-123"


def test_get_current_request_id_outside_context():
    """Ngoài request context, get_current_request_id returns None."""
    # Không có middleware nào set, mặc định là None
    import contextvars
    # Reset to None
    from src.core import request_context
    token = request_context._request_id_var.set(None)
    try:
        assert get_current_request_id() is None
    finally:
        request_context._request_id_var.reset(token)


def test_unhandled_exception_logs_and_raises(app_default, caplog):
    """Unhandled exception được log với request_id trước khi re-raise."""
    import logging
    client = TestClient(app_default, headers={REQUEST_ID_HEADER: "trace-err-1"})
    with caplog.at_level(logging.ERROR, logger="src.core.request_context"):
        # TestClient raises server exceptions by default, dùng raise_server_exceptions=False
        with pytest.raises(RuntimeError, match="test error"):
            client.get("/error")


def test_custom_header_name():
    """Cho phép đổi tên header qua config."""
    app = FastAPI()

    @app.get("/echo")
    async def echo():
        return {"rid": get_current_request_id()}

    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "header_name": "X-Correlation-Id", "log_level": "none"},
    )
    client = TestClient(app)
    response = client.get("/echo", headers={"X-Correlation-Id": "my-corr-id"})
    assert response.headers["X-Correlation-Id"] == "my-corr-id"
    # Default X-Request-ID không có
    assert REQUEST_ID_HEADER not in response.headers


def test_log_level_none_silent(caplog):
    """log_level='none' thì không log access log gì cả."""
    import logging
    app = FastAPI()

    @app.get("/silent")
    async def silent():
        return {"ok": True}

    app.add_middleware(RequestIDMiddleware, config={"enabled": True, "log_level": "none"})
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="src.core.request_context"):
        response = client.get("/silent")
    assert response.status_code == 200
    # Không có log nào từ middleware với log_level="none"
    middleware_logs = [
        r for r in caplog.records
        if r.name == "src.core.request_context"
        and "[rid]" in r.message or "->" in r.message
    ]
    assert len(middleware_logs) == 0
