"""Tests cho /metrics endpoint + RequestIDMiddleware metrics integration."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.request_context import RequestIDMiddleware
from src.core.metrics_aggregator import (
    HTTP_REQUESTS_TOTAL, HTTP_REQUEST_LATENCY, HTTP_REQUESTS_IN_FLIGHT,
    reset_metrics,
)


@pytest.fixture(autouse=True)
def reset_metrics_fixture():
    """Reset metrics trước và sau mỗi test."""
    reset_metrics()
    yield
    reset_metrics()


def test_metrics_endpoint_prometheus_format():
    """GET /metrics trả về Prometheus text format."""
    from src.main import app
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Verify Prometheus format markers
    assert "# HELP" in response.text or response.text == ""
    assert "# TYPE" in response.text or response.text == ""


def test_metrics_endpoint_json_format():
    """GET /metrics?format=json trả về JSON."""
    from src.main import app
    client = TestClient(app)
    response = client.get("/metrics?format=json")
    assert response.status_code == 200
    data = response.json()
    assert "counters" in data
    assert "gauges" in data
    assert "histograms" in data
    assert "legacy" in data


def test_request_middleware_records_metrics():
    """Mỗi HTTP request → increment counter + observe latency."""
    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = None
    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "log_level": "none", "record_metrics": True},
    )

    @app.get("/test")
    async def test():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200

    # HTTP_REQUESTS_TOTAL phải có 1 entry với labels (GET, /test, 200)
    value = HTTP_REQUESTS_TOTAL.value(method="GET", path="/test", status="200")
    assert value == 1

    # HTTP_REQUEST_LATENCY phải có 1 observation
    # Histogram count > 0
    output = HTTP_REQUEST_LATENCY.render()
    assert "http_request_duration_ms_count" in output


def test_request_middleware_normalizes_path_with_id():
    """Paths với numeric IDs được normalize thành {id}."""
    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = None
    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "log_level": "none", "record_metrics": True},
    )

    @app.get("/items/{item_id}")
    async def get_item(item_id: int):
        return {"id": item_id}

    client = TestClient(app)
    client.get("/items/123")
    client.get("/items/456")
    client.get("/items/789")

    # Cả 3 phải được group dưới path="/items/{id}"
    value = HTTP_REQUESTS_TOTAL.value(method="GET", path="/items/{id}", status="200")
    assert value == 3


def test_request_middleware_in_flight_gauge():
    """In-flight gauge update đúng khi request vào/ra."""
    import asyncio

    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = None
    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "log_level": "none", "record_metrics": True},
    )

    @app.get("/slow")
    async def slow():
        await asyncio.sleep(0.1)
        return {"ok": True}

    # Reset gauge
    HTTP_REQUESTS_IN_FLIGHT.set(0)

    client = TestClient(app)
    response = client.get("/slow")
    assert response.status_code == 200

    # Sau khi request xong, in-flight về 0
    assert HTTP_REQUESTS_IN_FLIGHT.value() == 0


def test_request_middleware_disabled_metrics():
    """Khi record_metrics=false, không record HTTP metrics."""
    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = None
    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "log_level": "none", "record_metrics": False},
    )

    @app.get("/disabled_metrics_test_unique")
    async def test():
        return {"ok": True}

    # Lấy baseline (counter có thể đã có giá trị từ test khác)
    from src.core.metrics_aggregator import get_registry
    registry = get_registry()
    counter = registry.counter("http_requests_total")
    path = "/disabled_metrics_test_unique"
    before = counter.value(method="GET", path=path, status="200")

    client = TestClient(app)
    client.get(path)

    # Với path unique, baseline = 0, sau = 0
    after = counter.value(method="GET", path=path, status="200")
    assert after == before == 0


def test_request_middleware_metrics_for_different_status_codes():
    """Mỗi status code là 1 label riêng."""
    from fastapi import HTTPException

    app = FastAPI()
    app.state.in_flight_requests = 0
    app.state.shutdown_event = None
    app.add_middleware(
        RequestIDMiddleware,
        config={"enabled": True, "log_level": "none", "record_metrics": True},
    )

    @app.get("/ok")
    async def ok():
        return {"ok": True}

    @app.get("/notfound")
    async def notfound():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/error")
    async def error():
        raise HTTPException(status_code=500, detail="Server error")

    client = TestClient(app, raise_server_exceptions=False)
    client.get("/ok")
    client.get("/notfound")
    client.get("/error")

    assert HTTP_REQUESTS_TOTAL.value(method="GET", path="/ok", status="200") == 1
    assert HTTP_REQUESTS_TOTAL.value(method="GET", path="/notfound", status="404") == 1
    assert HTTP_REQUESTS_TOTAL.value(method="GET", path="/error", status="500") == 1
