-- =====================================================================
-- Migration: 001 - Change embedding dimension from 768 to 3072
-- =====================================================================
-- Áp dụng khi:
-- - Đã có DB cũ với vector(768)
-- - Muốn nâng cấp lên gemini-embedding-2 (3072-dim)
--
-- LƯU Ý: Migration này SẼ XÓA dữ liệu vector cũ vì không thể
-- convert từ 768-dim sang 3072-dim. Cần re-embed lại sau khi chạy.
--
-- Cách chạy:
--   psql -U postgres -d tromanager -f database/migrations/001_embedding_dim_3072.sql
-- =====================================================================

BEGIN;

-- 1. Drop indexes cũ (nếu có) trên vector columns
DROP INDEX IF EXISTS idx_user_embeddings_embedding;
DROP INDEX IF EXISTS idx_semantic_cache_query_embedding;

-- 2. Drop các function cũ (sẽ recreate với dim mới)
DROP FUNCTION IF EXISTS search_semantic_cache(vector, FLOAT, INT);
DROP FUNCTION IF EXISTS search_user_memories(INT, vector, INT);

-- 3. Drop tables cũ và tạo lại với dim mới
-- CÁCH AN TOÀN: Tạo table mới, copy data non-vector, swap
-- CÁCH NHANH (mất vector data): Drop + recreate

-- Option B: An toàn (Thêm cột mới, re-embed, drop cột cũ sau)
ALTER TABLE user_embeddings ADD COLUMN embedding_v2 vector(3072);
-- Cần chạy script re-embed data vào embedding_v2, sau đó:
-- ALTER TABLE user_embeddings DROP COLUMN embedding;
-- ALTER TABLE user_embeddings RENAME COLUMN embedding_v2 TO embedding;

ALTER TABLE semantic_cache ADD COLUMN query_embedding_v2 vector(3072);
-- Tương tự cho semantic_cache

-- 4. Recreate functions với dim mới
CREATE OR REPLACE FUNCTION search_semantic_cache(
    query_embedding vector(3072),
    similarity_threshold FLOAT DEFAULT 0.9,
    max_results INT DEFAULT 1
)
RETURNS TABLE (
    cache_id INT,
    query_text TEXT,
    response_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.cache_id,
        sc.query_text,
        sc.response_text,
        1 - (sc.query_embedding <=> query_embedding) AS similarity
    FROM semantic_cache sc
    WHERE sc.expires_at > CURRENT_TIMESTAMP
      AND 1 - (sc.query_embedding <=> query_embedding) > similarity_threshold
    ORDER BY sc.query_embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_user_memories(
    p_tenant_id INT,
    query_embedding vector(3072),
    max_results INT DEFAULT 3
)
RETURNS TABLE (
    memory_id INT,
    memory_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ue.memory_id,
        ue.memory_text,
        1 - (ue.embedding <=> query_embedding) AS similarity
    FROM user_embeddings ue
    WHERE ue.tenant_id = p_tenant_id
      AND ue.is_archived = FALSE
    ORDER BY ue.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- 5. Recreate indexes (HNSW) với dim mới
CREATE INDEX IF NOT EXISTS idx_user_embeddings_embedding
    ON user_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_semantic_cache_query_embedding
    ON semantic_cache USING hnsw (query_embedding vector_cosine_ops);

COMMIT;

-- =====================================================================
-- SAU KHI CHẠY MIGRATION:
-- 1. Verify: SELECT column_name, data_type FROM information_schema.columns
--    WHERE table_name IN ('user_embeddings', 'semantic_cache');
-- 2. Re-embed dữ liệu cũ bằng gemini-embedding-2 (chạy script riêng)
-- 3. Verify vector dim: SELECT vector_dims(embedding) FROM user_embeddings LIMIT 1;
-- =====================================================================
