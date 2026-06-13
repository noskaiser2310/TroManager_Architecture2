-- =====================================================================
-- TroManager - Database Schema
-- Kiến trúc số 2: Router-Centric ReAct (Dual-Process)
-- =====================================================================
-- Database: PostgreSQL 16+
-- Extension: pgvector
-- =====================================================================

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =====================================================================
-- 2. ENUMS
-- =====================================================================

CREATE TYPE tone_preference_enum AS ENUM ('friendly', 'professional', 'strict');
CREATE TYPE communication_enum AS ENUM ('zalo', 'sms', 'app');
CREATE TYPE invoice_status_enum AS ENUM ('unpaid', 'paid', 'overdue', 'cancelled');
CREATE TYPE contract_status_enum AS ENUM ('active', 'expired', 'terminated', 'pending');
CREATE TYPE room_status_enum AS ENUM ('available', 'occupied', 'maintenance', 'reserved');
CREATE TYPE ticket_status_enum AS ENUM ('open', 'in_progress', 'resolved', 'closed');
CREATE TYPE ticket_priority_enum AS ENUM ('low', 'normal', 'high', 'urgent');

-- =====================================================================
-- 3. Bảng ROOMS (Phòng)
-- =====================================================================

CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    floor INT NOT NULL,
    area_m2 DECIMAL(5,2) NOT NULL,
    monthly_rent DECIMAL(12,2) NOT NULL,
    electricity_price DECIMAL(8,2) NOT NULL DEFAULT 3500,  -- VND/kWh
    water_price DECIMAL(8,2) NOT NULL DEFAULT 100000,       -- VND/m3
    service_fee DECIMAL(12,2) NOT NULL DEFAULT 50000,        -- VND/month
    max_occupants INT NOT NULL DEFAULT 1,
    status room_status_enum NOT NULL DEFAULT 'available',
    description TEXT,
    amenities JSONB DEFAULT '{}',  -- {"wifi": true, "ac": true, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_rooms_rent ON rooms(monthly_rent);

-- =====================================================================
-- 4. Bảng USER_PROFILES (Hồ sơ tường minh)
-- =====================================================================

CREATE TABLE user_profiles (
    tenant_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    zalo_id VARCHAR(100),
    room_id INT REFERENCES rooms(room_id) ON DELETE SET NULL,
    lease_start DATE,
    birthday DATE,
    lease_end DATE,
    communication_preference communication_enum DEFAULT 'zalo',
    tone_preference tone_preference_enum DEFAULT 'professional',
    notification_opt_out JSONB DEFAULT '[]',  -- ["birthday", "marketing"]
    personalization_profile JSONB DEFAULT '{}', -- SOTA Persona Optimizer data
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profile_phone ON user_profiles(phone_number);
CREATE INDEX idx_profile_room ON user_profiles(room_id);
CREATE INDEX idx_profile_active ON user_profiles(is_active);
CREATE INDEX idx_profile_lease_end ON user_profiles(lease_end);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rooms_updated_at
    BEFORE UPDATE ON rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- 5. Bảng CONTRACTS (Hợp đồng)
-- =====================================================================

CREATE TABLE contracts (
    contract_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    room_id INT NOT NULL REFERENCES rooms(room_id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    deposit_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    monthly_rent DECIMAL(12,2) NOT NULL,
    status contract_status_enum DEFAULT 'active',
    signed_date DATE,
    termination_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contract_tenant ON contracts(tenant_id);
CREATE INDEX idx_contract_room ON contracts(room_id);
CREATE INDEX idx_contract_status ON contracts(status);
CREATE INDEX idx_contract_end_date ON contracts(end_date);

CREATE TRIGGER update_contracts_updated_at
    BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- 6. Bảng INVOICES (Hóa đơn)
-- =====================================================================

CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    room_id INT NOT NULL REFERENCES rooms(room_id) ON DELETE RESTRICT,
    contract_id INT REFERENCES contracts(contract_id) ON DELETE SET NULL,
    invoice_month DATE NOT NULL,  -- First day of month
    base_rent DECIMAL(12,2) NOT NULL,
    electricity_kwh DECIMAL(10,2) DEFAULT 0,
    electricity_cost DECIMAL(12,2) DEFAULT 0,
    water_m3 DECIMAL(10,2) DEFAULT 0,
    water_cost DECIMAL(12,2) DEFAULT 0,
    service_fee DECIMAL(12,2) DEFAULT 0,
    other_charges DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status invoice_status_enum DEFAULT 'unpaid',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoice_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoice_month ON invoices(invoice_month);
CREATE INDEX idx_invoice_status ON invoices(status);
CREATE INDEX idx_invoice_due_date ON invoices(due_date);
CREATE UNIQUE INDEX idx_invoice_unique_month ON invoices(tenant_id, invoice_month);

CREATE TRIGGER update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- 8. Bảng BEHAVIOR_LOGS (Hồ sơ ngầm & Hành vi)
-- =====================================================================

CREATE TABLE behavior_logs (
    log_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (timestamp);

CREATE INDEX idx_behavior_tenant_time ON behavior_logs(tenant_id, timestamp DESC);
CREATE INDEX idx_behavior_type ON behavior_logs(tenant_id, action_type);
CREATE INDEX idx_behavior_timestamp ON behavior_logs(timestamp);
CREATE INDEX idx_behavior_tenant_type_time ON behavior_logs(tenant_id, action_type, timestamp DESC);

-- Partition by month for performance
CREATE TABLE behavior_logs_y2026m06 PARTITION OF behavior_logs
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');

-- =====================================================================
-- 9. Bảng USER_EMBEDDINGS (Semantic Memory)
-- =====================================================================

CREATE TABLE user_embeddings (
    memory_id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES user_profiles(tenant_id) ON DELETE CASCADE,
    memory_text TEXT NOT NULL,
    embedding vector(3072) NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    source VARCHAR(50) DEFAULT 'persona_optimizer',  -- persona_optimizer, manual
    last_retrieved TIMESTAMP,
    retrieval_count INT DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_emb_tenant ON user_embeddings(tenant_id);
CREATE INDEX idx_user_emb_vector ON user_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_user_emb_archived ON user_embeddings(is_archived);

-- =====================================================================
-- 10. Bảng SEMANTIC_CACHE (Dành cho System 1)
-- =====================================================================

CREATE TABLE semantic_cache (
    cache_id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(3072) NOT NULL,
    response_text TEXT NOT NULL,
    hit_count INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days')
);

CREATE INDEX idx_cache_query_vector ON semantic_cache USING hnsw (query_embedding vector_cosine_ops);
CREATE INDEX idx_cache_last_accessed ON semantic_cache(last_accessed);
CREATE INDEX idx_cache_expires ON semantic_cache(expires_at);

-- =====================================================================
-- 11. Bảng MAINTENANCE_TICKETS (Phiếu sửa chữa)
-- =====================================================================

CREATE TABLE maintenance_tickets (
    ticket_id SERIAL PRIMARY KEY,
    ticket_code VARCHAR(20) UNIQUE NOT NULL,  -- TKT-2026-0001
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    room_id INT REFERENCES rooms(room_id) ON DELETE SET NULL,
    issue_category VARCHAR(50),  -- electrical, plumbing, appliance, ...
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority ticket_priority_enum DEFAULT 'normal',
    status ticket_status_enum DEFAULT 'open',
    assigned_to VARCHAR(100),  -- staff name or vendor
    estimated_cost DECIMAL(12,2),
    actual_cost DECIMAL(12,2),
    scheduled_date DATE,
    completed_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticket_tenant ON maintenance_tickets(tenant_id);
CREATE INDEX idx_ticket_status ON maintenance_tickets(status);
CREATE INDEX idx_ticket_priority ON maintenance_tickets(priority);
CREATE INDEX idx_ticket_created ON maintenance_tickets(created_at DESC);

CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON maintenance_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- 12. Bảng CONVERSATION_HISTORY (Lịch sử hội thoại - cho debug & audit)
-- =====================================================================

CREATE TABLE conversation_history (
    conversation_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    session_id UUID,
    source VARCHAR(50),  -- zalo, sms, cron
    user_message TEXT,
    ai_response TEXT,
    system_used VARCHAR(20),  -- system1, system2
    iterations INT,
    tool_calls JSONB DEFAULT '[]',
    latency_ms INT,
    tokens_used INT,
    cost_usd DECIMAL(8,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conv_tenant ON conversation_history(tenant_id);
CREATE INDEX idx_conv_timestamp ON conversation_history(timestamp DESC);
CREATE INDEX idx_conv_session ON conversation_history(session_id);

-- =====================================================================
-- 13. Bảng APPROVAL_QUEUE (Hàng chờ duyệt cho sensitive tools)
-- =====================================================================

CREATE TABLE approval_queue (
    approval_id SERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL,
    tool_args JSONB NOT NULL,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    requested_by VARCHAR(50),  -- system, user_id
    approver_role VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewer_id INT,
    notes TEXT
);

CREATE INDEX idx_approval_status ON approval_queue(status);
CREATE INDEX idx_approval_tenant ON approval_queue(tenant_id);

-- =====================================================================
-- 13.5. Bảng APPOINTMENTS (Lịch hẹn xem phòng)
-- =====================================================================

CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    tenant_id INT REFERENCES user_profiles(tenant_id) ON DELETE SET NULL,
    room_id INT REFERENCES rooms(room_id) ON DELETE SET NULL,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, cancelled, completed
    notes TEXT,
    created_by VARCHAR(50) DEFAULT 'system',  -- system, user_id, staff_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_appointments_tenant ON appointments(tenant_id);
CREATE INDEX idx_appointments_room ON appointments(room_id);
CREATE INDEX idx_appointments_scheduled ON appointments(scheduled_at);
CREATE INDEX idx_appointments_status ON appointments(status);

-- =====================================================================
-- 14. VIEWS - Hỗ trợ queries thường gặp
-- =====================================================================

-- View: Behavior summary trong 90 ngày
CREATE OR REPLACE VIEW v_tenant_behavior_90d AS
SELECT
    t.tenant_id,
    t.full_name,
    t.room_id,
    COUNT(*) FILTER (WHERE bl.action_type = 'late_payment') AS late_payment_count,
    COUNT(*) FILTER (WHERE bl.action_type = 'on_time_payment') AS on_time_payment_count,
    COUNT(*) FILTER (WHERE bl.action_type = 'maintenance_request') AS maintenance_count,
    COUNT(*) FILTER (WHERE bl.action_type = 'noise_complaint') AS noise_complaint_count,
    MAX(bl.timestamp) AS last_interaction,
    MIN(bl.timestamp) FILTER (WHERE bl.action_type LIKE 'auto_%') AS first_auto_interaction
FROM user_profiles t
LEFT JOIN behavior_logs bl ON t.tenant_id = bl.tenant_id
    AND bl.timestamp > CURRENT_DATE - INTERVAL '90 days'
GROUP BY t.tenant_id, t.full_name, t.room_id;

-- View: Active tenants with room info
CREATE OR REPLACE VIEW v_active_tenants AS
SELECT
    t.tenant_id,
    t.full_name,
    t.phone_number,
    t.tone_preference,
    t.communication_preference,
    t.lease_end,
    r.room_number,
    r.floor,
    r.monthly_rent,
    (t.lease_end - CURRENT_DATE)::INT AS days_to_lease_end
FROM user_profiles t
LEFT JOIN rooms r ON t.room_id = r.room_id
WHERE t.is_active = TRUE;

-- View: Overdue invoices
CREATE OR REPLACE VIEW v_overdue_invoices AS
SELECT
    i.invoice_id,
    i.tenant_id,
    t.full_name,
    t.phone_number,
    t.tone_preference,
    i.invoice_month,
    i.total_amount,
    i.due_date,
    (CURRENT_DATE - i.due_date)::INT AS days_overdue,
    r.room_number
FROM invoices i
JOIN user_profiles t ON i.tenant_id = t.tenant_id
LEFT JOIN rooms r ON i.room_id = r.room_id
WHERE i.status IN ('unpaid', 'overdue')
  AND i.due_date < CURRENT_DATE;

-- View: Invoices sắp đến hạn (trong 3 ngày tới)
CREATE OR REPLACE VIEW v_payment_due_soon AS
SELECT
    i.invoice_id,
    i.tenant_id,
    t.full_name,
    t.phone_number,
    t.tone_preference,
    i.invoice_month,
    i.total_amount,
    i.due_date,
    (i.due_date - CURRENT_DATE)::INT AS days_until_due,
    r.room_number
FROM invoices i
JOIN user_profiles t ON i.tenant_id = t.tenant_id
LEFT JOIN rooms r ON i.room_id = r.room_id
WHERE i.status = 'unpaid'
  AND i.due_date >= CURRENT_DATE
  AND i.due_date <= CURRENT_DATE + INTERVAL '3 days';

-- View: Hợp đồng sắp hết hạn (trong 30 ngày tới)
CREATE OR REPLACE VIEW v_expiring_contracts AS
SELECT
    c.contract_id,
    c.tenant_id,
    t.full_name,
    t.phone_number,
    t.zalo_id,
    t.tone_preference,
    c.end_date,
    (c.end_date - CURRENT_DATE)::INT AS days_until_expiry,
    r.room_number,
    c.monthly_rent
FROM contracts c
JOIN user_profiles t ON c.tenant_id = t.tenant_id
LEFT JOIN rooms r ON c.room_id = r.room_id
WHERE c.status = 'active'
  AND c.end_date >= CURRENT_DATE
  AND c.end_date <= CURRENT_DATE + INTERVAL '30 days';

-- View: Sinh nhật sắp tới (trong 7 ngày tới)
CREATE OR REPLACE VIEW v_upcoming_birthdays AS
SELECT
    t.tenant_id,
    t.full_name,
    t.phone_number,
    t.zalo_id,
    t.birthday,
    (MAKE_DATE(
        EXTRACT(YEAR FROM CURRENT_DATE)::INT,
        EXTRACT(MONTH FROM t.birthday)::INT,
        EXTRACT(DAY FROM t.birthday)::INT
    ) - CURRENT_DATE)::INT AS days_until_birthday
FROM user_profiles t
WHERE t.is_active = TRUE
  AND t.birthday IS NOT NULL
  AND (MAKE_DATE(
        EXTRACT(YEAR FROM CURRENT_DATE)::INT,
        EXTRACT(MONTH FROM t.birthday)::INT,
        EXTRACT(DAY FROM t.birthday)::INT
      ) - CURRENT_DATE) BETWEEN 0 AND 7;

-- View: Tickets maintenance cần follow-up
CREATE OR REPLACE VIEW v_open_maintenance_tickets AS
SELECT
    mt.ticket_id,
    mt.ticket_code,
    mt.tenant_id,
    t.full_name,
    t.phone_number,
    mt.room_id,
    r.room_number,
    mt.issue_category,
    mt.priority,
    mt.title,
    mt.status,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - mt.created_at))::INT AS days_open
FROM maintenance_tickets mt
JOIN user_profiles t ON mt.tenant_id = t.tenant_id
LEFT JOIN rooms r ON mt.room_id = r.room_id
WHERE mt.status IN ('open', 'in_progress')
ORDER BY
    CASE mt.priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        WHEN 'low' THEN 4
    END,
    mt.created_at;

-- =====================================================================
-- 15. FUNCTIONS - Stored procedures hữu ích
-- =====================================================================

-- Function: Cosine similarity search trên semantic cache
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
        (1 - (sc.query_embedding <=> query_embedding))::FLOAT AS similarity
    FROM semantic_cache sc
    WHERE (1 - (sc.query_embedding <=> query_embedding)) > similarity_threshold
      AND sc.expires_at > CURRENT_TIMESTAMP
    ORDER BY sc.query_embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Cosine similarity search trên user memories
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
        (1 - (ue.embedding <=> query_embedding))::FLOAT AS similarity
    FROM user_embeddings ue
    WHERE ue.tenant_id = p_tenant_id
      AND ue.is_archived = FALSE
    ORDER BY ue.embedding <=> query_embedding
    LIMIT max_results;
    
END;
$$ LANGUAGE plpgsql;

-- Function: Cache cleanup (chạy daily)
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM semantic_cache
    WHERE expires_at < CURRENT_TIMESTAMP
       OR last_accessed < CURRENT_DATE - INTERVAL '60 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 16. COMMENTS
-- =====================================================================

COMMENT ON TABLE user_profiles IS 'Hồ sơ tường minh của khách thuê';
COMMENT ON TABLE behavior_logs IS 'Lịch sử hành vi - dùng cho personalization';
COMMENT ON TABLE user_embeddings IS 'Vector semantic memory - đúc kết sở thích từ behavior';
COMMENT ON TABLE semantic_cache IS 'Cache Q&A cho System 1 Fast Layer';
COMMENT ON COLUMN user_embeddings.embedding IS 'Vector 3072-dim từ nomic-embed-text';
COMMENT ON COLUMN semantic_cache.query_embedding IS 'Vector 3072-dim từ nomic-embed-text';

-- =====================================================================
-- END OF SCHEMA
-- =====================================================================
