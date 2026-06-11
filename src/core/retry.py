"""
Retry utilities for connection / startup resilience.
"""
import asyncio
import logging
from typing import Awaitable, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff: float = 2.0,
    operation_name: str = "operation",
    exceptions: tuple = (Exception,),
) -> T:
    """
    Retry một async operation với exponential backoff.

    Args:
        func: Async callable (không nhận args) cần retry.
        max_attempts: Số lần thử tối đa (default 5).
        initial_delay: Delay ban đầu (giây) trước attempt thứ 2.
        max_delay: Cap cho delay giữa các attempt.
        backoff: Hệ số nhân delay sau mỗi lần fail.
        operation_name: Tên operation cho log messages.
        exceptions: Tuple exception types sẽ trigger retry.

    Returns:
        Kết quả của func() nếu thành công.

    Raises:
        Last exception nếu hết attempts.

    Example:
        pool = await retry_async(
            lambda: asyncpg.create_pool(...),
            operation_name="create db pool",
            max_attempts=5,
        )
    """
    attempt = 1
    delay = initial_delay
    last_exc: Optional[BaseException] = None

    while attempt <= max_attempts:
        try:
            result = await func()
            if attempt > 1:
                logger.info(
                    f"{operation_name} succeeded on attempt {attempt}/{max_attempts}"
                )
            return result
        except exceptions as e:
            last_exc = e
            if attempt == max_attempts:
                logger.error(
                    f"{operation_name} failed after {max_attempts} attempts: {e}"
                )
                break

            logger.warning(
                f"{operation_name} attempt {attempt}/{max_attempts} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)
            delay = min(delay * backoff, max_delay)
            attempt += 1

    assert last_exc is not None
    raise last_exc
