"""
Core utilities - DB pool, knowledge lookup, notifications.
Centralized access pattern để tránh circular imports.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


from .context import current_tenant_id

# ============ DB Pool ============

_db_pool = None


def set_db_pool(pool):
    """Set global DB pool (called từ main.py on startup)."""
    global _db_pool
    _db_pool = pool
    logger.info("DB pool set")


def get_db_pool():
    """Get global DB pool. Raises if not initialized."""
    if _db_pool is None:
        raise RuntimeError(
            "DB pool not initialized. "
            "Call set_db_pool() in app lifespan startup."
        )
    return _db_pool


# ============ Knowledge Lookup ============

_knowledge_lookup = None


def set_knowledge_lookup(lookup):
    """Set global knowledge lookup (called từ main.py on startup)."""
    global _knowledge_lookup
    _knowledge_lookup = lookup


def get_knowledge_lookup():
    """Get global knowledge lookup. Raises if not initialized."""
    if _knowledge_lookup is None:
        raise RuntimeError(
            "Knowledge lookup not initialized. "
            "Call set_knowledge_lookup() in app lifespan startup."
        )


# ============ Notifications ============

_zalo_client = None
_sms_client = None


def set_zalo_client(client):
    """Set global Zalo client."""
    global _zalo_client
    _zalo_client = client


def get_zalo_client():
    """Get global Zalo client. Raises if not initialized."""
    if _zalo_client is None:
        raise RuntimeError("Zalo client not initialized")
    return _zalo_client


def set_sms_client(client):
    """Set global SMS client."""
    global _sms_client
    _sms_client = client


def get_sms_client():
    """Get global SMS client. Raises if not initialized."""
    if _sms_client is None:
        raise RuntimeError("SMS client not initialized")
    return _sms_client


# Re-exports for convenience
from ..llm import get_llm_client, get_embedding_client
from .rate_limiter import RateLimiter, RateLimitConfig
from .request_context import (
    RequestIDMiddleware,
    REQUEST_ID_HEADER,
    get_current_request_id,
    new_request_id,
    set_request_id,
)
from .json_parser import parse_llm_json
from .json_logging import (
    JSONFormatter,
    ConsoleJSONFormatter,
    setup_json_logging,
    get_logger,
)
from .metrics_aggregator import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    get_registry,
    metrics_counter,
    metrics_gauge,
    metrics_histogram,
    render_prometheus,
    render_json,
    reset_metrics,
)

__all__ = [
    "set_db_pool",
    "get_db_pool",
    "set_knowledge_lookup",
    "get_knowledge_lookup",
    "set_zalo_client",
    "get_zalo_client",
    "set_sms_client",
    "get_sms_client",
    "RateLimiter",
    "RateLimitConfig",
    "RequestIDMiddleware",
    "REQUEST_ID_HEADER",
    "get_current_request_id",
    "new_request_id",
    "set_request_id",
    "parse_llm_json",
    "JSONFormatter",
    "ConsoleJSONFormatter",
    "setup_json_logging",
    "get_logger",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsRegistry",
    "get_registry",
    "metrics_counter",
    "metrics_gauge",
    "metrics_histogram",
    "render_prometheus",
    "render_json",
    "reset_metrics",
]
