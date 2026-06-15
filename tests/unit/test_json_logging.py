"""Tests cho JSON structured logging."""
import io
import json
import logging
import pytest

from src.core.json_logging import (
    JSONFormatter,
    setup_json_logging,
    _redact_sensitive,
)
from src.core.request_context import set_request_id


class TestRedactSensitive:
    def test_redact_password(self):
        result = _redact_sensitive({"user": "alice", "password": "secret"})
        assert result == {"user": "alice", "password": "***REDACTED***"}

    def test_redact_nested(self):
        data = {
            "request": {
                "headers": {"Authorization": "Bearer xyz"},
                "body": {"username": "alice", "api_key": "key123"},
            }
        }
        result = _redact_sensitive(data)
        assert result["request"]["headers"]["Authorization"] == "***REDACTED***"
        assert result["request"]["body"]["api_key"] == "***REDACTED***"
        assert result["request"]["body"]["username"] == "alice"

    def test_redact_list(self):
        data = [{"token": "abc"}, {"name": "bob"}]
        result = _redact_sensitive(data)
        assert result[0]["token"] == "***REDACTED***"
        assert result[1]["name"] == "bob"

    def test_redact_case_insensitive_keys(self):
        """Các biến thể PascalCase/camelCase đều bị redact."""
        result = _redact_sensitive({"API_KEY": "x", "ApiKey": "y", "password": "z"})
        assert result["API_KEY"] == "***REDACTED***"
        assert result["ApiKey"] == "***REDACTED***"
        assert result["password"] == "***REDACTED***"

    def test_redact_env_var_names(self):
        result = _redact_sensitive({"DB_PASSWORD": "x", "GEMINI_API_KEY": "y"})
        assert result["DB_PASSWORD"] == "***REDACTED***"
        assert result["GEMINI_API_KEY"] == "***REDACTED***"


class TestJSONFormatter:
    def test_basic_format(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x.py", lineno=1,
            msg="Hello world", args=(), exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Hello world"
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")  # ISO UTC

    def test_extra_fields_included(self):
        formatter = JSONFormatter(include_extra=True)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x.py", lineno=1,
            msg="User login", args=(), exc_info=None,
        )
        record.user_id = 123
        record.tenant_id = 5
        output = formatter.format(record)
        data = json.loads(output)
        assert data["user_id"] == 123
        assert data["tenant_id"] == 5

    def test_extras_excluded_when_disabled(self):
        formatter = JSONFormatter(include_extra=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x.py", lineno=1,
            msg="Hi", args=(), exc_info=None,
        )
        record.user_id = 123
        output = formatter.format(record)
        data = json.loads(output)
        assert "user_id" not in data

    def test_exception_info_included(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test", level=logging.ERROR, pathname="x.py", lineno=1,
                msg="Error occurred", args=(), exc_info=sys.exc_info(),
            )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert "test error" in data["exception"]["message"]
        assert "Traceback" in data["exception"]["traceback"]

    def test_request_id_included(self):
        formatter = JSONFormatter()
        set_request_id("rid-12345")
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="x.py", lineno=1,
                msg="Test", args=(), exc_info=None,
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert data["request_id"] == "rid-12345"
        finally:
            set_request_id(None)  # Reset to default

    def test_redact_sensitive_in_message(self):
        formatter = JSONFormatter(redact_sensitive=True)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x.py", lineno=1,
            msg="Login", args=(), exc_info=None,
        )
        record.password = "secret"
        output = formatter.format(record)
        data = json.loads(output)
        assert data["password"] == "***REDACTED***"

    def test_unicode_preserved(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="x.py", lineno=1,
            msg="Xin chào, hợp đồng #123", args=(), exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "Xin chào" in data["message"]
        assert "hợp đồng" in data["message"]


class TestSetupJSONLogging:
    def test_setup_replaces_handlers(self):
        root = logging.getLogger()
        # Add a dummy handler
        dummy = logging.NullHandler()
        root.addHandler(dummy)
        try:
            setup_json_logging(level="WARNING", force=True)
            # Dummy handler should be gone
            assert dummy not in root.handlers
            # New handler should be JSONFormatter
            new_handler = root.handlers[-1]
            assert isinstance(new_handler.formatter, JSONFormatter)
            assert root.level == logging.WARNING
        finally:
            # Cleanup
            setup_json_logging(level="INFO", force=True)

    def test_setup_with_stream(self):
        stream = io.StringIO()
        setup_json_logging(level="INFO", stream=stream, force=True)
        logging.getLogger("test").info("hello")
        # Get handler output
        for handler in logging.getLogger().handlers:
            handler.flush()
        output = stream.getvalue()
        assert "hello" in output
        data = json.loads(output.strip().split("\n")[-1])
        assert data["message"] == "hello"
