"""
Request ID middleware - Correlation ID cho mọi HTTP request.

Mục đích:
- Mỗi HTTP request có 1 unique ID (auto-generate hoặc từ X-Request-ID header)
- ID propagate vào logger qua contextvar
- ID trả về client qua response header
- Tạo thuận lợi cho việc trace/debug khi user báo lỗi

Usage:
    from .core.request_context import request_id_var, RequestIDMiddleware

    # Trong code bất kỳ:
    from .core.request_context import get_current_request_id
    rid = get_current_request_id()  # -> "abc-123" hoặc None

    # Trong log message:
    logger.info(f"[{get_current_request_id()}] Processing chat")
"""
from __future__ import annotations

import contextvars
import logging
import time
import uuid
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Context var lưu request_id hiện tại (dùng trong async context)
_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

REQUEST_ID_HEADER = "X-Request-ID"


def get_current_request_id() -> Optional[str]:
    """Lấy request_id của request hiện tại, hoặc None nếu ngoài request context."""
    return _request_id_var.get()


def set_request_id(rid: Optional[str]) -> None:
    """Set request_id manually (vd: cho background task).

    Pass None để reset về default.
    """
    _request_id_var.set(rid)


def new_request_id() -> str:
    """Generate một request_id mới (UUID4 hex, ngắn gọn)."""
    return uuid.uuid4().hex[:16]


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware inject request_id vào context + response headers.

    Behavior:
    - Nếu client gửi X-Request-ID header: dùng luôn (cho phép client trace).
    - Nếu không có: generate UUID4 hex 16 chars.
    - Set vào contextvar để logger pick up.
    - Attach vào request.state.request_id cho handlers.
    - Trả về X-Request-ID header trong response.
    - Log mỗi request với method, path, status, duration_ms.
    - Có thể disable qua config["app"]["request_id"]["enabled"] = false.
    """

    def __init__(self, app, config: Optional[dict] = None):
        super().__init__(app)
        cfg = config or {}
        self.enabled = cfg.get("enabled", True)
        # log_level: "info" | "warning" | "error" | "none"
        self.log_level = cfg.get("log_level", "info")
        self.header_name = cfg.get("header_name", REQUEST_ID_HEADER)
        # Record HTTP metrics (counter, histogram) per request
        self.record_metrics = cfg.get("record_metrics", True)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled:
            return await call_next(request)

        # Lấy hoặc generate request_id
        rid = request.headers.get(self.header_name) or new_request_id()

        # Set vào contextvar
        token = _request_id_var.set(rid)
        request.state.request_id = rid
        request.state.start_time = time.time()

        # Track in-flight requests cho graceful shutdown
        in_flight = getattr(request.app.state, "in_flight_requests", None)
        shutdown_event = getattr(request.app.state, "shutdown_event", None)
        if in_flight is not None:
            in_flight += 1
            request.app.state.in_flight_requests = in_flight
            # Cập nhật gauge metric
            try:
                from .metrics_aggregator import HTTP_REQUESTS_IN_FLIGHT
                HTTP_REQUESTS_IN_FLIGHT.set(in_flight)
            except Exception:
                pass

        # Nếu đang shutdown, reject request mới với 503
        if shutdown_event is not None and shutdown_event.is_set():
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=503,
                content={
                    "error": "Server is shutting down",
                    "request_id": rid,
                },
                headers={self.header_name: rid},
            )
            # Vẫn giảm in_flight vì request không thực sự chạy
            if in_flight is not None:
                request.app.state.in_flight_requests = max(0, in_flight - 1)
            _request_id_var.reset(token)
            return response

        try:
            response = await call_next(request)
        except Exception as e:
            # Nếu exception chưa được handle, log + re-raise
            duration_ms = int((time.time() - request.state.start_time) * 1000)
            logger.exception(
                f"[{rid}] Unhandled exception in {request.method} {request.url.path} "
                f"after {duration_ms}ms: {e}"
            )
            raise
        finally:
            # Luôn decrement, kể cả khi exception
            if in_flight is not None:
                new_count = max(0, in_flight - 1)
                request.app.state.in_flight_requests = new_count
                # Cập nhật gauge metric
                try:
                    from .metrics_aggregator import HTTP_REQUESTS_IN_FLIGHT
                    HTTP_REQUESTS_IN_FLIGHT.set(new_count)
                except Exception:
                    pass
            _request_id_var.reset(token)

        # Add request_id vào response headers
        response.headers[self.header_name] = rid
        duration_ms = int((time.time() - request.state.start_time) * 1000)
        response.headers["X-Response-Time-Ms"] = str(duration_ms)

        # Record metrics (nếu enabled)
        if self.record_metrics:
            try:
                from .metrics_aggregator import (
                    HTTP_REQUESTS_TOTAL, HTTP_REQUEST_LATENCY, HTTP_REQUESTS_IN_FLIGHT,
                )
                # Normalize path (group dynamic IDs into placeholder)
                path = self._normalize_path(request.url.path)
                method = request.method
                status = str(response.status_code)
                HTTP_REQUESTS_TOTAL.inc(method=method, path=path, status=status)
                HTTP_REQUEST_LATENCY.observe(duration_ms, method=method, path=path)
            except Exception as e:
                # Không để metrics failure ảnh hưởng request
                logger.debug(f"Metrics recording failed: {e}")

        # Log request theo log_level config
        if self.log_level != "none":
            status = response.status_code
            log_msg = (
                f"[{rid}] {request.method} {request.url.path} "
                f"-> {status} ({duration_ms}ms)"
            )
            # Quyết định log dựa trên config log_level + status
            if status >= 500:
                logger.error(log_msg)
            elif status >= 400:
                if self.log_level in ("info", "warning"):
                    logger.warning(log_msg)
            else:
                if self.log_level == "info":
                    logger.info(log_msg)

        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize path để tránh cardinality explosion trong metrics.

        VD: /admin/approvals/123/approve → /admin/approvals/{id}/approve
        """
        import re
        # Replace numeric IDs
        path = re.sub(r"/\d+(/|$)", r"/{id}\1", path)
        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(/|$)",
            r"/{uuid}\1", path
        )
        return path
