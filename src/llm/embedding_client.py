"""
Embedding Client - Real implementation sử dụng OpenAI-compatible API.
"""

from __future__ import annotations
import time
import hashlib
import logging
from typing import Optional

from openai import AsyncOpenAI

from .config_loader import LLMConfig, load_llm_config

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Real embedding client.
    
        Sử dụng:
        client = EmbeddingClient()
        vector = await client.encode("Some text")
        vectors = await client.encode_batch(["text1", "text2"])
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = load_llm_config()
        self.config = config
        self.model = config.embedding.model
        self.dimension = config.embedding_dim
        
        if not config.embedding.api_key:
            logger.warning(
                "Embedding api_key chưa được set. Set GEMINI_API_KEY env var"
            )
        
        self._client = AsyncOpenAI(
            api_key=config.embedding.api_key or "MISSING_API_KEY",
            base_url=config.embedding.base_url,
            timeout=config.embedding.request_timeout,
        )
        
        # Simple in-memory cache
        self._cache: dict[str, list[float]] = {}
        if config.embedding.extra.get("enable_cache", True):
            self._cache_enabled = True
        else:
            self._cache_enabled = False
        
        logger.info(
            f"EmbeddingClient initialized: model={self.model}, "
            f"dim={self.dimension}, cache={'on' if self._cache_enabled else 'off'}"
        )
    
    async def encode(self, text: str) -> list[float]:
        """
        Encode một text thành vector.

        Args:
            text: Text cần encode

        Returns:
            list[float] với độ dài = dimension
        """
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        # Check cache
        if self._cache_enabled:
            cache_key = self._cache_key(text)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        response = await self._client.embeddings.create(
            model=self.model,
            input=text,
        )
        
        vector = response.data[0].embedding
        
        # Update cache
        if self._cache_enabled:
            self._cache[cache_key] = vector
        
        return vector
    
    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Encode nhiều texts cùng lúc (hiệu quả hơn encode từng cái).

        Args:
            texts: list các texts

        Returns:
            list các vectors
        """
        if not texts:
            return []
        
        batch_size = self.config.embedding.extra.get("batch_size", 32)
        all_vectors: list[list[float]] = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
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
                response = await self._client.embeddings.create(
                    model=self.model,
                    input=uncached_texts,
                )
                for local_idx, emb_data in zip(uncached_indices, response.data):
                    vector = emb_data.embedding
                    results[local_idx] = vector
                    if self._cache_enabled:
                        self._cache[self._cache_key(batch[local_idx])] = vector
            
            all_vectors.extend(results)
        
        return all_vectors
    
    def _cache_key(self, text: str) -> str:
        """Generate cache key cho text."""
        return hashlib.sha256(f"{self.model}:{text}".encode()).hexdigest()
    
    def clear_cache(self):
        """Xóa embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")
    
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
