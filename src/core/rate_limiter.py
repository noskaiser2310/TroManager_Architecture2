"""
RateLimiter - Simple in-memory rate limiter cho API endpoints.

Algorithm: sliding window với in-memory dict.
Phù hợp cho single-process dev/staging. Production nên dùng Redis.

Cấu hình từ config.yaml:
    security.rate_limit:
        requests_per_minute: 60
        requests_per_hour: 1000
"""

from __future__ import annotations
import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Config cho rate limiter."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    enabled: bool = True


class RateLimiter:
    """
    Per-key rate limiter (key = tenant_id, IP, etc).

    Sử dụng:
        limiter = RateLimiter(config)
        allowed, reason = await limiter.check(tenant_id=123)
        if not allowed:
            raise HTTPException(429, reason)
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        # key -> deque of timestamps
        self._buckets: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    async def check(
        self,
        key: str,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
    ) -> tuple[bool, str]:
        """
        Check xem key có vượt rate limit không.

        Returns:
            (allowed, reason) - reason là "" nếu allowed
        """
        if not self.config.enabled:
            return True, ""

        rpm = requests_per_minute or self.config.requests_per_minute
        rph = requests_per_hour or self.config.requests_per_hour

        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        async with self._lock:
            bucket = self._buckets.setdefault(key, deque())

            # Dọn timestamps cũ
            while bucket and bucket[0] < hour_ago:
                bucket.popleft()

            # Count requests trong 1 phút và 1 giờ
            minute_count = sum(1 for ts in bucket if ts > minute_ago)
            hour_count = len(bucket)

            if minute_count >= rpm:
                logger.warning(
                    f"Rate limit hit (per minute) for key={key}: "
                    f"{minute_count}/{rpm} in last 60s"
                )
                return False, f"Rate limit: max {rpm} requests/minute. Try again later."

            if hour_count >= rph:
                logger.warning(
                    f"Rate limit hit (per hour) for key={key}: "
                    f"{hour_count}/{rph} in last hour"
                )
                return False, f"Rate limit: max {rph} requests/hour. Try again later."

            # OK - record this request
            bucket.append(now)
            return True, ""

    async def reset(self, key: str):
        """Xóa tracking của một key."""
        async with self._lock:
            if key in self._buckets:
                del self._buckets[key]

    async def reset_all(self):
        """Xóa toàn bộ tracking (dùng cho admin/test)."""
        async with self._lock:
            self._buckets.clear()

    async def get_stats(self, key: str) -> dict:
        """Lấy stats hiện tại của key (cho admin endpoint)."""
        async with self._lock:
            bucket = self._buckets.get(key, deque())
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        return {
            "key": key,
            "minute_count": sum(1 for ts in bucket if ts > minute_ago),
            "hour_count": sum(1 for ts in bucket if ts > hour_ago),
            "total_count": len(bucket),
            "limit_per_minute": self.config.requests_per_minute,
            "limit_per_hour": self.config.requests_per_hour,
        }
