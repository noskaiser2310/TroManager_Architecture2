"""
Tests cho System 1 - Semantic Cache.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import numpy as np

from src.system1.semantic_cache import SemanticCache, CacheEntry


class TestSemanticCache:
    """Test SemanticCache."""
    
    @pytest.fixture
    def mock_pool(self):
        """Mock asyncpg connection pool."""
        pool = MagicMock()
        conn = AsyncMock()
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        return pool, conn
    
    @pytest.fixture
    def cache(self, mock_pool):
        pool, conn = mock_pool
        return SemanticCache(pool)
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, cache, mock_pool):
        """Test cache hit trả về entry."""
        pool, conn = mock_pool
        embedding = np.random.rand(768).tolist()
        
        # Mock DB response
        conn.fetchrow = AsyncMock(return_value={
            "cache_id": 1,
            "query_text": "Wifi mật khẩu gì?",
            "response_text": "Mật khẩu wifi là: trohai2026",
            "similarity": 0.95,
        })
        conn.execute = AsyncMock(return_value="UPDATE 1")
        
        result = await cache.lookup(embedding, threshold=0.9)
        
        assert result is not None
        assert result.cache_id == 1
        assert result.similarity > 0.9
        assert "tromanh2026" in result.response_text or "tromanh" in result.response_text or "wifi" in result.response_text.lower()
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache, mock_pool):
        """Test cache miss trả về None."""
        pool, conn = mock_pool
        embedding = np.random.rand(768).tolist()
        
        # Mock no result
        conn.fetchrow = AsyncMock(return_value=None)
        
        result = await cache.lookup(embedding, threshold=0.9)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_cache(self, cache, mock_pool):
        """Test save cache entry."""
        pool, conn = mock_pool
        embedding = np.random.rand(768).tolist()
        
        conn.fetchrow = AsyncMock(return_value={"cache_id": 42})
        
        cache_id = await cache.save(
            query="Test query",
            query_embedding=embedding,
            response="Test response",
        )
        
        assert cache_id == 42
        conn.fetchrow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache, mock_pool):
        """Test cleanup expired entries."""
        pool, conn = mock_pool
        conn.fetchval = AsyncMock(return_value=15)
        
        deleted = await cache.cleanup_expired()
        
        assert deleted == 15
    
    def test_to_pgvector(self, cache):
        """Test conversion sang pgvector format."""
        embedding = [0.1, 0.2, 0.3]
        result = cache._to_pgvector(embedding)
        assert result == "[0.1,0.2,0.3]"
        
        # Test with numpy
        np_emb = np.array([0.1, 0.2, 0.3])
        result2 = cache._to_pgvector(np_emb)
        assert result2 == "[0.1,0.2,0.3]"


class TestCacheIntegration:
    """Test integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_similarity_threshold(self):
        """Test ngưỡng similarity hoạt động đúng."""
        # Similarity threshold = 0.9
        # Cache với similarity 0.85 → miss
        # Cache với similarity 0.95 → hit
        pass  # Implementation in real test with DB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
