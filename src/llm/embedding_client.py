"""
Embedding Client using OpenAI-compatible API.
"""

from __future__ import annotations
import asyncio
import time
import hashlib
import logging
from typing import Optional

from openai import AsyncOpenAI

from .config_loader import LLMConfig, load_llm_config
from .key_rotator import KeyRotator

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Real embedding client.
    
        Sử dụng:
        client = EmbeddingClient()
        vector = await client.encode("Some text")
        vectors = await client.encode_batch(["text1", "text2"])
    """
    
    def __init__(self, config: Optional[LLMConfig] = None, key_rotator: Optional[KeyRotator] = None):
        if config is None:
            config = load_llm_config()
        self.config = config
        self.model = config.embedding.model
        self.dimension = config.embedding_dim
        self._base_url = config.embedding.base_url
        self._request_timeout = config.embedding.request_timeout

        # Key rotation (dùng chung rotator với LLM hoặc tạo riêng)
        self._key_rotator = key_rotator or KeyRotator.from_env()
        self._current_key = self._key_rotator.get_key()

        if not self._current_key or self._current_key == "MISSING_API_KEY":
            logger.warning(
                "Embedding api_key chưa được set. Set GEMINI_API_KEY env var"
            )

        self._client = self._build_client(self._current_key)
        
        # Disk and memory cache
        self._cache: dict[str, list[float]] = {}
        from pathlib import Path
        self._cache_file = Path("config/embedding_cache.json")
        if config.embedding.extra.get("enable_cache", True):
            self._cache_enabled = True
            self._load_cache()
        else:
            self._cache_enabled = False
        
        self._quota_exhausted = False

    def _build_client(self, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=api_key,
            base_url=self._base_url,
            timeout=self._request_timeout,
        )

    def _on_key_rotated(self, new_key: str):
        self._current_key = new_key
        self._client = self._build_client(new_key)
        self._quota_exhausted = False  # reset flag với key mới

        logger.info(
            f"EmbeddingClient initialized: model={self.model}, "
            f"dim={self.dimension}, keys={self._key_rotator.key_count}, "
            f"cache={'on (disk)' if self._cache_enabled else 'off'}"
        )
    
    def _load_cache(self):
        import json
        if self._cache_file.exists():
            try:
                self._cache = json.loads(self._cache_file.read_text(encoding="utf-8"))
                logger.info(f"Loaded {len(self._cache)} cached embeddings from disk")
            except Exception as e:
                logger.warning(f"Failed to load embedding cache from disk: {e}")
                self._cache = {}

    def _save_cache(self):
        import json
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            self._cache_file.write_text(json.dumps(self._cache, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to save embedding cache to disk: {e}")

    async def encode(self, text: str) -> list[float]:
        """
        Encode một text thành vector.

        Args:
            text: Text cần encode

        Returns:
            list[float] với độ dài = dimension
        """
        if self._quota_exhausted:
            from openai import RateLimitError
            import httpx
            mock_req = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/openai/embeddings")
            mock_resp = httpx.Response(429, request=mock_req, json={"error": {"message": "Daily embedding quota limit exceeded (cached). Failing fast."}})
            raise RateLimitError(
                message="Daily embedding quota limit exceeded (cached). Failing fast.",
                response=mock_resp,
                body=mock_resp.json()
            )
            
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        # Check cache
        if self._cache_enabled:
            cache_key = self._cache_key(text)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        from openai import RateLimitError
        import re

        max_retries = 5
        retry_delay = 1.0
        vector = None
        key_rotated = False

        for attempt in range(max_retries):
            try:
                response = await self._client.embeddings.create(
                    model=self.model,
                    input=text,
                )
                if key_rotated:
                    self._key_rotator.mark_success()
                vector = response.data[0].embedding
                break
            except RateLimitError as e:
                err_msg = str(e).lower()
                if "quota" in err_msg or "exceeded your current quota" in err_msg:
                    if self._key_rotator.key_count > 1 and not key_rotated:
                        new_key = await self._key_rotator.on_error(str(e))
                        self._on_key_rotated(new_key)
                        key_rotated = True
                        logger.info(f"Embedding quota exhausted, rotated to key #{self._key_rotator.current_index}")
                        continue
                    elif key_rotated:
                        self._quota_exhausted = True
                        logger.error(f"All embedding keys exhausted. Giving up: {e}")
                        raise
                    else:
                        self._quota_exhausted = True
                        logger.error(f"Only 1 embedding key available. Quota exhausted: {e}")
                        raise
                if attempt == max_retries - 1:
                    logger.error(f"Rate limit hit on final embedding attempt: {e}")
                    raise
                wait_time = retry_delay * (2 ** attempt)
                match = re.search(r"retry in ([\d\.]+)s", str(e))
                if match:
                    wait_time = float(match.group(1)) + 0.5
                logger.warning(f"Embedding rate limit hit, retrying in {wait_time:.2f}s... (attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(wait_time)
        
        # Update cache
        if self._cache_enabled and vector is not None:
            self._cache[cache_key] = vector
            self._save_cache()
        
        return vector or [0.0] * self.dimension
    
    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Encode nhiều texts cùng lúc (hiệu quả hơn encode từng cái).

        Args:
            texts: list các texts

        Returns:
            list các vectors
        """
        if self._quota_exhausted:
            from openai import RateLimitError
            import httpx
            mock_req = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/openai/embeddings")
            mock_resp = httpx.Response(429, request=mock_req, json={"error": {"message": "Daily embedding quota limit exceeded (cached). Failing fast."}})
            raise RateLimitError(
                message="Daily embedding quota limit exceeded (cached). Failing fast.",
                response=mock_resp,
                body=mock_resp.json()
            )
            
        if not texts:
            return []
        
        batch_size = self.config.embedding.extra.get("batch_size", 5)
        batch_delay = float(self.config.embedding.extra.get("batch_delay", 4.0))
        all_vectors: list[list[float]] = []
        
        from openai import RateLimitError
        import re
        
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        
        for idx_b, batch in enumerate(batches):
            if idx_b > 0 and batch_delay > 0:
                logger.info(f"Sleeping {batch_delay}s between embedding batches to avoid 429 rate limit... (batch {idx_b+1}/{len(batches)})")
                await asyncio.sleep(batch_delay)
            
            # Check cache cho từng item
            uncached_indices = []
            uncached_texts = []
            results: list[Optional[list[float]]] = [None] * len(batch)
            
            for idx, text in enumerate(batch):
                if self._cache_enabled:
                    cache_key = self._cache_key(text)
                    if cache_key in self._cache:
                        results[idx] = self._cache[cache_key]
                        continue
                uncached_indices.append(idx)
                uncached_texts.append(text)
            
            # Call API cho uncached items
            if uncached_texts:
                max_retries = 5
                retry_delay = 1.0
                response = None
                
                batch_key_rotated = False
                for attempt in range(max_retries):
                    try:
                        response = await self._client.embeddings.create(
                            model=self.model,
                            input=uncached_texts,
                        )
                        if batch_key_rotated:
                            self._key_rotator.mark_success()
                        break
                    except RateLimitError as e:
                        err_msg = str(e).lower()
                        if "quota" in err_msg or "exceeded your current quota" in err_msg:
                            if self._key_rotator.key_count > 1 and not batch_key_rotated:
                                new_key = await self._key_rotator.on_error(str(e))
                                self._on_key_rotated(new_key)
                                batch_key_rotated = True
                                logger.info(f"Embedding batch quota exhausted, rotated to key #{self._key_rotator.current_index}")
                                continue
                            elif batch_key_rotated:
                                self._quota_exhausted = True
                                logger.error(f"All embedding keys exhausted in batch. Giving up: {e}")
                                raise
                            else:
                                self._quota_exhausted = True
                                logger.error(f"Only 1 embedding key. Quota exhausted in batch: {e}")
                                raise
                        if attempt == max_retries - 1:
                            logger.error(f"Rate limit hit on final embedding batch attempt: {e}")
                            raise
                        wait_time = retry_delay * (2 ** attempt)
                        match = re.search(r"retry in ([\d\.]+)s", str(e))
                        if match:
                            wait_time = float(match.group(1)) + 0.5
                        logger.warning(f"Embedding batch rate limit hit, retrying in {wait_time:.2f}s... (attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                
                if response:
                    for local_idx, emb_data in zip(uncached_indices, response.data):
                        vector = emb_data.embedding
                        results[local_idx] = vector
                        if self._cache_enabled:
                            self._cache[self._cache_key(batch[local_idx])] = vector
                    
                    if self._cache_enabled:
                        self._save_cache()
            
            all_vectors.extend(results)
        
        return all_vectors
    
    def _cache_key(self, text: str) -> str:
        """Generate cache key cho text."""
        return hashlib.sha256(f"{self.model}:{text}".encode()).hexdigest()
    
    def clear_cache(self):
        """Xóa embedding cache."""
        self._cache.clear()
        self._quota_exhausted = False
        logger.info("Embedding cache cleared and quota status reset")
    
    def get_cache_stats(self) -> dict:
        """Lấy thống kê cache."""
        return {
            "size": len(self._cache),
            "enabled": self._cache_enabled,
        }


# ============ Singleton ============

_default_embedding: Optional[EmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    """Get singleton embedding client."""
    global _default_embedding
    if _default_embedding is None:
        _default_embedding = EmbeddingClient()
    return _default_embedding


def reset_embedding_client():
    """Reset singleton (for testing)."""
    global _default_embedding
    _default_embedding = None
