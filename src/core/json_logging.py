"""
JSON structured logging cho production.

Format mỗi log line thành 1 JSON object với các trường chuẩn:
- timestamp (ISO 8601 UTC)
- level (INFO, WARNING, ERROR, ...)
- logger (tên module)
- message
- request_id (auto-injected từ contextvar nếu có)
- exception (stack trace nếu có)

Cho phép:
- Cloud logging services (CloudWatch, Stackdriver, ELK) parse dễ dàng
- Query theo request_id để debug
- Filter/aggregate theo level, logger, etc.

Usage:
    import logging
    from src.core.json_logging import setup_json_logging

    setup_json_logging(level="INFO")
    logger = logging.getLogger(__name__)
    logger.info("User logged in", extra={"user_id": 123, "tenant_id": 1})
"""
from __future__ import annotations

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Optional

from .request_context import get_current_request_id


# Sensitive keys to redact (passwords, tokens, etc.)
# Normalized to lowercase for case-insensitive matching
_REDACT_KEYS = {
    "password",
    "passwd",
    "api_key",
    "apikey",
    "token",
    "secret",
    "authorization",
    "auth",
    "access_token",
    "refresh_token",
    "db_password",
    "gemini_api_key",
    "openai_api_key",
    "zalo_webhook_secret",
}


def _redact_sensitive(data: Any) -> Any:
    """
    Recursively redact sensitive keys trong dict/list.

    Ví dụ: {"user": "alice", "password": "secret"} → {"user": "alice", "password": "***"}
    """
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            # Case-insensitive match
            if isinstance(k, str) and k.lower() in _REDACT_KEYS:
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = _redact_sensitive(v)
        return redacted
    elif isinstance(data, list):
        return [_redact_sensitive(item) for item in data]
    else:
        return data


class JSONFormatter(logging.Formatter):
    """
    LogFormatter xuất ra JSON.

    Output format (1 line per log):
    {"timestamp": "2026-06-06T12:34:56.789Z", "level": "INFO",
     "logger": "src.main", "message": "User logged in",
     "request_id": "abc123", "user_id": 1, "tenant_id": 1}
    """

    # Standard LogRecord attributes (để phân biệt với user-provided "extra")
    _RESERVED_ATTRS = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "asctime", "taskName",
    }

    def __init__(self, *, redact_sensitive: bool = True, include_extra: bool = True):
        super().__init__()
        self.redact_sensitive = redact_sensitive
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        # Base log object
        log_obj = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "func": record.funcName,
        }

        # Inject request_id nếu có (từ contextvar)
        rid = get_current_request_id()
        if rid:
            log_obj["request_id"] = rid

        # Thêm "extra" fields (user-provided)
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key in self._RESERVED_ATTRS or key.startswith("_"):
                    continue
                if key in log_obj:  # Tránh overwrite
                    continue
                # Chỉ serialize JSON-compatible types
                try:
                    json.dumps(value)
                    log_obj[key] = value
                except (TypeError, ValueError):
                    log_obj[key] = repr(value)

        # Exception info
        if record.exc_info:
            log_obj["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "traceback": "".join(traceback.format_exception(*record.exc_info)),
            }
        elif record.exc_text:
            log_obj["exception"] = {"traceback": record.exc_text}

        # Stack info
        if record.stack_info:
            log_obj["stack"] = record.stack_info

        # Redact sensitive
        if self.redact_sensitive:
            log_obj = _redact_sensitive(log_obj)

        try:
            return json.dumps(log_obj, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            # Fallback nếu vẫn không serialize được
            return json.dumps({
                "timestamp": log_obj["timestamp"],
                "level": "ERROR",
                "logger": "json_formatter",
                "message": f"Failed to serialize log: {e}",
                "original_message": str(record.getMessage()),
            }, ensure_ascii=False)


class ConsoleJSONFormatter(JSONFormatter):
    """
    JSON formatter cho console output (kết hợp với color codes optional).

    Mặc định không có color (production friendly).
    """


def setup_json_logging(
    level: str = "INFO",
    *,
    stream=None,
    redact_sensitive: bool = True,
    force: bool = True,
) -> None:
    """
    Setup root logger với JSON formatter.

    Args:
        level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL).
        stream: Output stream (default: stderr).
        redact_sensitive: Tự động redact password/api_key.
        force: Replace existing handlers (default True).
    """
    root_logger = logging.getLogger()

    if force:
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(JSONFormatter(redact_sensitive=redact_sensitive))
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Tắt propagate mặc định của uvicorn (để tránh duplicate logs)
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("uvicorn.error").propagate = False


def get_logger(name: str) -> logging.Logger:
    """Helper để lấy logger."""
    return logging.getLogger(name)
