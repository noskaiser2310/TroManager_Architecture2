"""
conftest.py — Shared fixtures cho toàn bộ test suite TroManager.

Fixtures ở đây tự động available cho tất cả tests trong tests/unit/,
tests/integration/, tests/audit/, và tests/e2e/ mà không cần import.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ============ Event Loop ============

@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop (tránh tạo mới cho mỗi test)."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ============ Mock DB Pool ============

@pytest.fixture
def mock_db_pool():
    """Mock asyncpg Pool — trả về MagicMock có acquire() context manager."""
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    return pool, conn


# ============ Mock LLM Client ============

@pytest.fixture
def mock_llm_client():
    """Mock LLMClient với generate() trả về chuỗi rỗng mặc định."""
    client = AsyncMock()
    client.model_name = "gemma-4-31b-it"
    client.generate = AsyncMock(return_value="Mock LLM response")
    client.generate_structured = AsyncMock(return_value={})
    return client


@pytest.fixture
def mock_flash_client(mock_llm_client):
    """Flash model mock (System 1 + Persona Optimizer)."""
    mock_llm_client.model_name = "gemma-4-31b-it"
    return mock_llm_client


@pytest.fixture
def mock_pro_client(mock_llm_client):
    """Pro model mock (System 2 ReAct)."""
    mock_llm_client.model_name = "gemini-3.1-flash-lite"
    return mock_llm_client


# ============ Mock Embedding Client ============

@pytest.fixture
def mock_embedding_client():
    """Mock embedding client — trả về vector 3072-dim toàn 0.0."""
    client = AsyncMock()
    client.embed = AsyncMock(return_value=[0.0] * 3072)
    return client


# ============ Mock Zalo Client ============

@pytest.fixture
def mock_zalo_client():
    """Mock Zalo OA client."""
    client = AsyncMock()
    client.send_message = AsyncMock(return_value={"error": 0, "message": "Success"})
    return client


# ============ Shared Tenant Data ============

@pytest.fixture
def sample_tenant():
    """Tenant mẫu dùng trong tests."""
    return {
        "tenant_id": 1,
        "full_name": "Nguyễn Văn A",
        "phone_number": "0901234567",
        "zalo_id": "zalo_001",
        "room_id": 101,
        "tone_preference": "friendly",
        "personalization_profile": {
            "demographics": {"occupation": "student"},
            "preferences": {"communication_tone": "friendly"},
            "interaction_patterns": {"active_hours": "18:00-22:00"},
        },
        "lease_end": "2026-12-31",
        "is_active": True,
    }


@pytest.fixture
def sample_behavior_log():
    """Behavior log mẫu."""
    return {
        "tenant_id": 1,
        "action_type": "chat",
        "description": "Hỏi về WiFi",
        "metadata": {"source": "zalo"},
    }
