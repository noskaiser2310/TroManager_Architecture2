"""
Key Rotator — tự động xoay vòng API key khi gặp 429 (rate limit / quota exhausted).

Sử dụng:
    rotator = KeyRotator.from_env()
    key = rotator.get_key()      # Lấy key hiện tại
    rotator.on_error()           # Báo lỗi → tự động xoay sang key tiếp theo
    key = rotator.get_key()      # Key mới sau khi xoay
"""

from __future__ import annotations
import os
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class KeyRotator:
    """
    Vòng tròn API key. Thread-safe (asyncio.Lock).

    Khi một key bị 429, gọi on_error() để xoay sang key tiếp theo.
    Hết vòng thì quay lại key đầu tiên và log warning.
    """

    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("KeyRotator cần ít nhất 1 key")
        self._keys = list(dict.fromkeys(keys))  # unique + preserve order
        self._index = 0
        self._lock = asyncio.Lock()
        self._total_rotations = 0
        self._failed_keys: set[int] = set()
        logger.info(
            f"KeyRotator initialized: {len(self._keys)} keys, "
            f"starting with key #{0}"
        )

    @classmethod
    def from_env(cls, env_var: str = "GEMINI_API_KEYS") -> KeyRotator:
        """
        Tạo KeyRotator từ environment variable.

        Keys được phân cách bằng dấu phẩy.
        Fallback: nếu env không có, dùng GEMINI_API_KEY đơn lẻ.
        """
        raw = os.environ.get(env_var, "")
        if raw.strip():
            keys = [k.strip() for k in raw.split(",") if k.strip()]
            if keys:
                return cls(keys)

        # Fallback: single key from GEMINI_API_KEY
        single = os.environ.get("GEMINI_API_KEY", "")
        if single:
            return cls([single])

        logger.warning("No API keys found in env. Using empty placeholder.")
        return cls(["MISSING_API_KEY"])

    @property
    def key_count(self) -> int:
        return len(self._keys)

    @property
    def current_index(self) -> int:
        return self._index

    def get_key(self) -> str:
        """Lấy key hiện tại (thread-safe)."""
        return self._keys[self._index]

    async def on_error(self, error_msg: str = "") -> str:
        """
        Gọi khi gặp lỗi API (429 quota exhausted).

        Xoay sang key tiếp theo. Trả về key mới.
        Nếu tất cả keys đều failed, log warning và quay lại key đầu.
        """
        async with self._lock:
            old_idx = self._index
            self._failed_keys.add(old_idx)
            self._total_rotations += 1

            # Rotate to next key
            self._index = (self._index + 1) % len(self._keys)

            # Nếu đã thử hết tất cả keys mà vẫn lỗi, reset failed set
            if self._index == 0:
                if len(self._failed_keys) >= len(self._keys):
                    logger.error(
                        f"All {len(self._keys)} keys have failed! "
                        f"Resetting failed set. Last error: {error_msg}"
                    )
                    self._failed_keys.clear()
                else:
                    logger.warning(
                        f"Rotated through all keys. "
                        f"Failed keys: {sorted(self._failed_keys)}. "
                        f"Trying key #{self._index} again."
                    )

            logger.info(
                f"Key rotated: #{old_idx} -> #{self._index} "
                f"(total rotations: {self._total_rotations})"
            )
            return self._keys[self._index]

    def mark_success(self):
        """Đánh dấu key hiện tại hoạt động tốt (xoá khỏi failed set)."""
        self._failed_keys.discard(self._index)

    def get_stats(self) -> dict:
        return {
            "total_keys": len(self._keys),
            "current_index": self._index,
            "total_rotations": self._total_rotations,
            "failed_keys": sorted(self._failed_keys),
        }
