-- Migration 004: Thêm tenant_id vào semantic_cache để tránh cache nhầm giữa các tenant
-- Tenant A chào → cache lưu "Chào anh Minh" → Tenant B không nhận được "Chào anh Minh"

ALTER TABLE semantic_cache ADD COLUMN IF NOT EXISTS tenant_id INT REFERENCES user_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cache_tenant ON semantic_cache(tenant_id);

-- Drop old function and recreate with tenant_id filter
DROP FUNCTION IF EXISTS search_semantic_cache(vector, FLOAT, INT);

CREATE OR REPLACE FUNCTION search_semantic_cache(
    query_emb vector(3072),
    match_threshold FLOAT,
    input_tenant_id INT DEFAULT NULL
)
RETURNS TABLE(
    cache_id INT,
    query_text TEXT,
    response_text TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.cache_id,
        sc.query_text,
        sc.response_text,
        1 - (sc.query_embedding <=> query_emb) AS similarity
    FROM semantic_cache sc
    WHERE 1 - (sc.query_embedding <=> query_emb) > match_threshold
      AND sc.expires_at > CURRENT_TIMESTAMP
      AND (sc.tenant_id IS NULL OR sc.tenant_id = input_tenant_id)
    ORDER BY sc.query_embedding <=> query_emb
    LIMIT 1;
END;
$$;

-- Xóa seed data cũ (không có tenant_id) — sẽ được rebuild khi cần
DELETE FROM semantic_cache;
