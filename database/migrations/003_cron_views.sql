-- =====================================================================
-- Migration 003: Cron job support views
-- Tạo các view cần thiết cho background cron jobs
-- =====================================================================

-- 1. Hóa đơn quá hạn
CREATE OR REPLACE VIEW v_overdue_invoices AS
SELECT
    i.invoice_id,
    i.tenant_id,
    u.full_name,
    i.total_amount,
    (CURRENT_DATE - i.due_date)::INT AS days_overdue,
    r.room_number
FROM invoices i
JOIN user_profiles u ON i.tenant_id = u.tenant_id
LEFT JOIN rooms r ON i.room_id = r.room_id
WHERE i.status = 'unpaid'
  AND i.due_date < CURRENT_DATE;

-- 2. Hóa đơn sắp đến hạn
CREATE OR REPLACE VIEW v_payment_due_soon AS
SELECT
    i.invoice_id,
    i.tenant_id,
    u.full_name,
    i.total_amount,
    (i.due_date - CURRENT_DATE)::INT AS days_until_due,
    r.room_number
FROM invoices i
JOIN user_profiles u ON i.tenant_id = u.tenant_id
LEFT JOIN rooms r ON i.room_id = r.room_id
WHERE i.status = 'unpaid'
  AND i.due_date >= CURRENT_DATE
  AND i.due_date <= CURRENT_DATE + INTERVAL '3 days';

-- 3. Hợp đồng sắp hết hạn
CREATE OR REPLACE VIEW v_expiring_contracts AS
SELECT
    c.contract_id,
    c.tenant_id,
    u.full_name,
    u.phone_number,
    c.end_date,
    (c.end_date - CURRENT_DATE)::INT AS days_until_expiry,
    r.room_number,
    c.monthly_rent
FROM contracts c
JOIN user_profiles u ON c.tenant_id = u.tenant_id
LEFT JOIN rooms r ON c.room_id = r.room_id
WHERE c.status = 'active'
  AND c.end_date >= CURRENT_DATE
  AND c.end_date <= CURRENT_DATE + INTERVAL '30 days';

-- 4. Ticket bảo trì đang mở
CREATE OR REPLACE VIEW v_open_maintenance_tickets AS
SELECT
    t.ticket_id,
    t.ticket_code,
    t.tenant_id,
    u.full_name,
    u.phone_number,
    t.issue_category,
    t.priority,
    t.title,
    (CURRENT_DATE - t.created_at::DATE)::INT AS days_open
FROM maintenance_tickets t
JOIN user_profiles u ON t.tenant_id = u.tenant_id
WHERE t.status IN ('open', 'in_progress');

-- 5. Sinh nhật sắp tới
CREATE OR REPLACE VIEW v_upcoming_birthdays AS
SELECT
    u.tenant_id,
    u.full_name,
    u.zalo_id,
    u.phone_number,
    u.birthday,
    CASE
        WHEN CURRENT_DATE <= make_date(EXTRACT(YEAR FROM CURRENT_DATE)::INT, EXTRACT(MONTH FROM u.birthday)::INT, EXTRACT(DAY FROM u.birthday)::INT)
        THEN (make_date(EXTRACT(YEAR FROM CURRENT_DATE)::INT, EXTRACT(MONTH FROM u.birthday)::INT, EXTRACT(DAY FROM u.birthday)::INT) - CURRENT_DATE)::INT
        ELSE (make_date(EXTRACT(YEAR FROM CURRENT_DATE)::INT + 1, EXTRACT(MONTH FROM u.birthday)::INT, EXTRACT(DAY FROM u.birthday)::INT) - CURRENT_DATE)::INT
    END AS days_until_birthday
FROM user_profiles u
WHERE u.birthday IS NOT NULL
  AND u.is_active = TRUE;
