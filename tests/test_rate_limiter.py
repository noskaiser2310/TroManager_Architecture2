"""
Tests cho RateLimiter - in-memory sliding window.
"""

import pytest
import asyncio


@pytest.fixture
def limiter():
    """Default limiter: 5 req/min, 10 req/hour."""
    from src.core.rate_limiter import RateLimiter, RateLimitConfig
    return RateLimiter(RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=10,
        enabled=True,
    ))


@pytest.fixture
def disabled_limiter():
    from src.core.rate_limiter import RateLimiter, RateLimitConfig
    return RateLimiter(RateLimitConfig(enabled=False))


@pytest.mark.asyncio
async def test_allows_under_limit(limiter):
    """Test requests dưới limit đều pass."""
    for _ in range(5):
        allowed, reason = await limiter.check("tenant:1")
        assert allowed is True
        assert reason == ""


@pytest.mark.asyncio
async def test_blocks_per_minute(limiter):
    """Test block khi vượt per-minute limit."""
    for _ in range(5):
        await limiter.check("tenant:1")
    # Request thứ 6 trong cùng phút
    allowed, reason = await limiter.check("tenant:1")
    assert allowed is False
    assert "minute" in reason.lower()


@pytest.mark.asyncio
async def test_separate_keys(limiter):
    """Test mỗi key có bucket riêng."""
    for _ in range(5):
        await limiter.check("tenant:1")
    # tenant:2 vẫn còn fresh
    allowed, _ = await limiter.check("tenant:2")
    assert allowed is True


@pytest.mark.asyncio
async def test_disabled_limiter_allows_all(disabled_limiter):
    """Test disabled limiter luôn pass."""
    for _ in range(100):
        allowed, _ = await disabled_limiter.check("tenant:1")
        assert allowed is True


@pytest.mark.asyncio
async def test_reset(limiter):
    """Test reset xóa bucket."""
    for _ in range(5):
        await limiter.check("tenant:1")
    # Block
    allowed, _ = await limiter.check("tenant:1")
    assert allowed is False
    # Reset
    await limiter.reset("tenant:1")
    # Should pass again
    allowed, _ = await limiter.check("tenant:1")
    assert allowed is True


@pytest.mark.asyncio
async def test_get_stats(limiter):
    """Test get_stats trả về counts."""
    for _ in range(3):
        await limiter.check("tenant:1")

    stats = limiter.get_stats("tenant:1")
    assert stats["key"] == "tenant:1"
    assert stats["minute_count"] == 3
    assert stats["hour_count"] == 3
    assert stats["limit_per_minute"] == 5
    assert stats["limit_per_hour"] == 10


@pytest.mark.asyncio
async def test_per_minute_vs_per_hour(limiter):
    """Test per-minute limit chặt hơn per-hour."""
    # 5 requests (đạt per-minute)
    for _ in range(5):
        await limiter.check("tenant:1")
    # 6th blocked bởi per-minute
    allowed, _ = await limiter.check("tenant:1")
    assert allowed is False
    # Vẫn dưới per-hour (10)
    stats = limiter.get_stats("tenant:1")
    assert stats["hour_count"] == 5  # dưới 10


@pytest.mark.asyncio
async def test_exports_in_core():
    """Test RateLimiter và RateLimitConfig exported từ src.core."""
    from src.core import RateLimiter, RateLimitConfig
    assert RateLimiter is not None
    assert RateLimitConfig is not None
