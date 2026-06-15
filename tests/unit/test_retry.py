"""Tests cho retry_async helper."""
import asyncio
import pytest

from src.core.retry import retry_async


class FakeError(Exception):
    pass


@pytest.mark.asyncio
async def test_succeeds_first_attempt():
    calls = []

    async def func():
        calls.append(1)
        return "ok"

    result = await retry_async(func, operation_name="test", max_attempts=3)
    assert result == "ok"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_succeeds_after_failures():
    calls = []

    async def func():
        calls.append(1)
        if len(calls) < 3:
            raise FakeError("transient")
        return "ok"

    result = await retry_async(
        func, operation_name="test", max_attempts=5,
        initial_delay=0.01, max_delay=0.05,
    )
    assert result == "ok"
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_raises_after_max_attempts():
    calls = []

    async def func():
        calls.append(1)
        raise FakeError("permanent")

    with pytest.raises(FakeError, match="permanent"):
        await retry_async(
            func, operation_name="test", max_attempts=3,
            initial_delay=0.01, max_delay=0.05,
        )
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_does_not_retry_unexpected_exceptions():
    calls = []

    class OtherError(Exception):
        pass

    async def func():
        calls.append(1)
        raise OtherError("not retryable")

    # Mặc định chỉ retry Exception; OtherError cũng là Exception nên vẫn retry.
    # Test với exceptions=(ValueError,) thì OtherError sẽ không được retry.
    with pytest.raises(OtherError):
        await retry_async(
            func, operation_name="test", max_attempts=3,
            initial_delay=0.01, max_delay=0.05,
            exceptions=(ValueError,),
        )
    assert len(calls) == 1  # Chỉ gọi 1 lần, không retry


@pytest.mark.asyncio
async def test_exponential_backoff_delays():
    """Verify delays tăng theo backoff (dùng mock cho sleep)."""
    import time
    real_sleep = asyncio.sleep
    sleep_calls = []

    async def mock_sleep(delay):
        sleep_calls.append(delay)
        # Không sleep thật để test chạy nhanh
        await real_sleep(0)

    import src.core.retry as retry_mod
    retry_mod.asyncio.sleep = mock_sleep

    try:
        async def always_fail():
            raise FakeError("fail")

        with pytest.raises(FakeError):
            await retry_async(
                always_fail, operation_name="test", max_attempts=4,
                initial_delay=1.0, max_delay=10.0, backoff=2.0,
            )

        # 3 sleeps cho 4 attempts: 1.0, 2.0, 4.0
        assert sleep_calls == [1.0, 2.0, 4.0]
    finally:
        retry_mod.asyncio.sleep = real_sleep


@pytest.mark.asyncio
async def test_backoff_capped_at_max_delay():
    import src.core.retry as retry_mod
    sleep_calls = []
    real_sleep = asyncio.sleep

    async def mock_sleep(delay):
        sleep_calls.append(delay)
        await real_sleep(0)

    retry_mod.asyncio.sleep = mock_sleep

    try:
        async def always_fail():
            raise FakeError("fail")

        with pytest.raises(FakeError):
            await retry_async(
                always_fail, operation_name="test", max_attempts=5,
                initial_delay=1.0, max_delay=3.0, backoff=2.0,
            )

        # max_delay=3 cap delays: 1.0, 2.0, 3.0 (capped), 3.0 (capped)
        assert sleep_calls == [1.0, 2.0, 3.0, 3.0]
    finally:
        retry_mod.asyncio.sleep = real_sleep
