-- =====================================================================
-- SEED DATA FOR TROMANAGER
-- All data references only tenants 1-5 and rooms 101-303
-- Idempotent: safe to re-run (TRUNCATE + cascade)
-- =====================================================================
-- Note: Conversation history has user messages only (no hardcoded AI
-- responses). AI responses are generated dynamically by the system.
-- =====================================================================

BEGIN;

-- =====================================================================
-- Idempotency: Clear + restart sequences (reset SERIAL IDs to 1)
-- =====================================================================
TRUNCATE TABLE rooms RESTART IDENTITY CASCADE;
TRUNCATE TABLE semantic_cache RESTART IDENTITY CASCADE;

-- =====================================================================
-- 1. ROOMS (rooms)
-- =====================================================================
INSERT INTO rooms (room_number, floor, area_m2, monthly_rent, status, amenities) VALUES
('101', 1, 25.0, 3500000, 'occupied', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"3 cÃ¡nh","Äiá»u hÃ²a":"Daikin 9000BTU","NÃ³ng láº¡nh":"NÄƒng lÆ°á»£ng máº·t trá»i","VÃ²i táº¯m":"KÃ­nh","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng nam"}'),
('102', 1, 30.0, 4500000, 'occupied', '{"GiÆ°á»ng":"1m8x2m","Tá»§ quáº§n Ã¡o":"4 cÃ¡nh","Äiá»u hÃ²a":"Daikin 12000BTU","NÃ³ng láº¡nh":"NÄƒng lÆ°á»£ng máº·t trá»i","VÃ²i táº¯m":"KÃ­nh","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng Ä‘Ã´ng","Ban cÃ´ng":"Nhá»"}'),
('103', 1, 20.0, 3000000, 'available', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"2 cÃ¡nh","Äiá»u hÃ²a":"Panasonic 9000BTU","NÃ³ng láº¡nh":"GiÃ¡n tiáº¿p","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng báº¯c"}'),
('201', 2, 22.0, 3200000, 'occupied', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"3 cÃ¡nh","Äiá»u hÃ²a":"LG 9000BTU","NÃ³ng láº¡nh":"GiÃ¡n tiáº¿p","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng Ä‘Ã´ng"}'),
('202', 2, 28.0, 4000000, 'available', '{"GiÆ°á»ng":"1m8x2m","Tá»§ quáº§n Ã¡o":"4 cÃ¡nh","Äiá»u hÃ²a":"Daikin 12000BTU","NÃ³ng láº¡nh":"NÄƒng lÆ°á»£ng máº·t trá»i","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng nam","Ban cÃ´ng":"Rá»™ng"}'),
('203', 2, 22.0, 3200000, 'available', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"2 cÃ¡nh","Äiá»u hÃ²a":"Panasonic 9000BTU","NÃ³ng láº¡nh":"GiÃ¡n tiáº¿p","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng tÃ¢y"}'),
('301', 3, 25.0, 3500000, 'occupied', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"3 cÃ¡nh","Äiá»u hÃ²a":"Daikin 9000BTU","NÃ³ng láº¡nh":"NÄƒng lÆ°á»£ng máº·t trá»i","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng nam"}'),
('302', 3, 30.0, 4500000, 'occupied', '{"GiÆ°á»ng":"1m8x2m","Tá»§ quáº§n Ã¡o":"4 cÃ¡nh","Äiá»u hÃ²a":"Daikin 12000BTU","NÃ³ng láº¡nh":"NÄƒng lÆ°á»£ng máº·t trá»i","VÃ²i táº¯m":"KÃ­nh","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng Ä‘Ã´ng","Ban cÃ´ng":"Nhá»"}'),
('303', 3, 25.0, 3500000, 'available', '{"GiÆ°á»ng":"1m6x2m","Tá»§ quáº§n Ã¡o":"3 cÃ¡nh","Äiá»u hÃ²a":"LG 9000BTU","NÃ³ng láº¡nh":"GiÃ¡n tiáº¿p","BÃ n báº¿p":"CÃ³","Cá»­a sá»•":"HÆ°á»›ng báº¯c"}');

-- =====================================================================
-- 2. TENANTS (user_profiles)
-- =====================================================================
INSERT INTO user_profiles (full_name, phone_number, room_id, lease_start, lease_end, tone_preference) VALUES
('Nguyá»…n VÄƒn Minh', '0901234567', (SELECT room_id FROM rooms WHERE room_number='101'), '2024-01-15', '2026-12-31', 'friendly'),
('Tráº§n Thá»‹ Hoa',   '0902345678', (SELECT room_id FROM rooms WHERE room_number='102'), '2025-03-01', '2026-08-31', 'professional'),
('LÃª HoÃ ng Tuáº¥n',  '0903456789', (SELECT room_id FROM rooms WHERE room_number='201'), '2024-06-01', '2026-12-31', 'friendly'),
('Pháº¡m Thá»‹ Lan',   '0904567890', (SELECT room_id FROM rooms WHERE room_number='301'), '2025-01-10', '2026-07-10', 'strict'),
('Äá»— VÄƒn HÃ¹ng',    '0905678901', (SELECT room_id FROM rooms WHERE room_number='302'), '2024-09-01', '2026-09-01', 'professional');

-- =====================================================================
-- 3. CONTRACTS
-- =====================================================================
INSERT INTO contracts (tenant_id, room_id, start_date, end_date, deposit_amount, monthly_rent, status)
SELECT u.tenant_id, u.room_id, u.lease_start, u.lease_end,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 7000000
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 9000000
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 6400000
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 7000000
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 9000000
       END,
       r.monthly_rent,
       'active'
FROM user_profiles u
JOIN rooms r ON u.room_id = r.room_id;

-- =====================================================================
-- 4. INVOICES (current month + historical)
-- =====================================================================
INSERT INTO invoices (tenant_id, room_id, contract_id, invoice_month, base_rent, electricity_kwh, electricity_cost, water_m3, water_cost, service_fee, total_amount, due_date, status, paid_date)
SELECT u.tenant_id, u.room_id, c.contract_id,
       dates.invoice_month,
       r.monthly_rent,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 95
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 115
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 78
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 90
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 110
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 332500
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 402500
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 273000
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 315000
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 385000
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 5
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 6
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 4
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 6
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 6
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 500000
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 600000
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 400000
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 600000
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 600000
           ELSE 0 END,
       50000,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN r.monthly_rent + 332500 + 500000 + 50000
           WHEN 'Tráº§n Thá»‹ Hoa' THEN r.monthly_rent + 402500 + 600000 + 50000
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN r.monthly_rent + 273000 + 400000 + 50000
           WHEN 'Pháº¡m Thá»‹ Lan' THEN r.monthly_rent + 315000 + 600000 + 50000
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN r.monthly_rent + 385000 + 600000 + 50000
       END,
       dates.due_date,
       CASE u.full_name
           WHEN 'Nguyá»…n VÄƒn Minh' THEN 'paid'
           WHEN 'Tráº§n Thá»‹ Hoa' THEN 'unpaid'
           WHEN 'LÃª HoÃ ng Tuáº¥n' THEN 'paid'
           WHEN 'Pháº¡m Thá»‹ Lan' THEN 'overdue'
           WHEN 'Äá»— VÄƒn HÃ¹ng' THEN 'paid'
       END::invoice_status_enum,
       CASE WHEN u.full_name IN ('Nguyá»…n VÄƒn Minh', 'LÃª HoÃ ng Tuáº¥n', 'Äá»— VÄƒn HÃ¹ng') THEN dates.due_date - INTERVAL '1 day'
            WHEN u.full_name = 'Tráº§n Thá»‹ Hoa' THEN NULL ELSE NULL END
FROM user_profiles u
JOIN rooms r ON u.room_id = r.room_id
JOIN contracts c ON u.tenant_id = c.tenant_id
CROSS JOIN LATERAL (
    VALUES
        ('2026-06-01'::DATE, '2026-06-05'::DATE),
        ('2026-05-01'::DATE, '2026-05-05'::DATE)
) AS dates(invoice_month, due_date);

-- Also add June invoice for contract_id matching
UPDATE invoices SET contract_id = c.contract_id
FROM contracts c WHERE invoices.tenant_id = c.tenant_id AND invoices.contract_id IS DISTINCT FROM c.contract_id;

-- =====================================================================
-- 5. BEHAVIOR LOGS
-- =====================================================================
INSERT INTO behavior_logs (tenant_id, action_type, description) VALUES
-- Tenant 1: Friendly, gÆ°Æ¡ng máº«u
(1, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 5'),
(1, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 4'),
(1, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 3'),
(1, 'maintenance_request', 'BÃ¡o bÃ³ng Ä‘Ã¨n phÃ²ng khÃ¡ch chÃ¡y'),
(1, 'maintenance_request', 'YÃªu cáº§u kiá»ƒm tra mÃ¡y láº¡nh'),
(1, 'noise_complaint', 'NhÃ  bÃªn cáº¡nh má»Ÿ nháº¡c to sau 22h'),
(1, 'compliment', 'Khen nhÃ¢n viÃªn sá»­a chá»¯a nhiá»‡t tÃ¬nh'),

-- Tenant 2: Professional, Ä‘Ã´i lÃºc trá»…
(2, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 5'),
(2, 'late_payment', 'Thanh toÃ¡n trá»… 3 ngÃ y thÃ¡ng 3 do cÃ´ng tÃ¡c'),
(2, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 2'),
(2, 'maintenance_request', 'Äiá»u hÃ²a kÃªu to'),
(2, 'contract_signed', 'KÃ½ há»£p Ä‘á»“ng thuÃª 1 nÄƒm'),

-- Tenant 3: Friendly, cá»±c ká»³ Ä‘Ãºng giá»
(3, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 5'),
(3, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 4'),
(3, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 3'),
(3, 'room_transfer', 'Äá» nghá»‹ chuyá»ƒn lÃªn phÃ²ng cÃ³ ban cÃ´ng'),
(3, 'positive_feedback', 'Khen dá»‹ch vá»¥ wifi á»•n Ä‘á»‹nh'),

-- Tenant 4: Strict, trá»… kinh niÃªn
(4, 'late_payment', 'Thanh toÃ¡n trá»… 5 ngÃ y thÃ¡ng 5'),
(4, 'late_payment', 'Thanh toÃ¡n trá»… 3 ngÃ y thÃ¡ng 4'),
(4, 'late_payment', 'Thanh toÃ¡n trá»… 7 ngÃ y thÃ¡ng 3'),
(4, 'late_payment', 'Thanh toÃ¡n trá»… 4 ngÃ y thÃ¡ng 2'),
(4, 'noise_complaint', 'PhÃ n nÃ n phÃ²ng bÃªn cÃ£i nhau áº§m Ä©'),
(4, 'maintenance_request', 'Cá»­a sá»• bá»‹ káº¹t'),
(4, 'payment_promise_made', 'Há»©a thanh toÃ¡n trÆ°á»›c ngÃ y 10 thÃ¡ng 6'),
(4, 'payment_promise_broken', 'KhÃ´ng thanh toÃ¡n Ä‘Ãºng háº¹n láº§n 1'),

-- Tenant 5: Professional, máº«u má»±c
(5, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 5'),
(5, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 4'),
(5, 'on_time_payment', 'Thanh toÃ¡n Ä‘Ãºng háº¡n thÃ¡ng 3'),
(5, 'contract_signed', 'Gia háº¡n há»£p Ä‘á»“ng thÃªm 1 nÄƒm'),
(5, 'maintenance_request', 'Kiá»ƒm tra há»‡ thá»‘ng Ä‘iá»‡n');

-- =====================================================================
-- 6. MAINTENANCE TICKETS
-- =====================================================================
INSERT INTO maintenance_tickets (ticket_code, tenant_id, room_id, issue_category, title, description, priority, status, assigned_to) VALUES
('TKT-2026-0001', 1, (SELECT room_id FROM rooms WHERE room_number='101'), 'plumbing', 'VÃ²i sen táº¯m bá»‹ táº¯c', 'NÆ°á»›c cháº£y yáº¿u, cÃ³ thá»ƒ do cáº·n', 'normal', 'resolved', 'Anh TÃ i - thá»£ nÆ°á»›c'),
('TKT-2026-0002', 2, (SELECT room_id FROM rooms WHERE room_number='102'), 'internet', 'Wifi cháº­p chá»n buá»•i tá»‘i', 'Máº¥t káº¿t ná»‘i liÃªn tá»¥c tá»« 20h-23h', 'normal', 'in_progress', 'Anh TÃº - IT'),
('TKT-2026-0003', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'appliance', 'Tá»§ láº¡nh kÃªu to báº¥t thÆ°á»ng', 'Tiáº¿ng á»“n áº£nh hÆ°á»Ÿng giáº¥c ngá»§', 'normal', 'open', NULL),
('TKT-2026-0004', 4, (SELECT room_id FROM rooms WHERE room_number='301'), 'electrical', 'á»” cáº¯m Ä‘iá»‡n phÃ²ng khÃ¡ch khÃ´ng cÃ³ Ä‘iá»‡n', 'ÄÃ£ kiá»ƒm tra cáº§u dao, váº«n khÃ´ng cÃ³', 'normal', 'in_progress', 'Anh Nam - Ä‘iá»‡n láº¡nh'),
('TKT-2026-0005', 4, (SELECT room_id FROM rooms WHERE room_number='301'), 'pest', 'Kiáº¿n ba khoang xuáº¥t hiá»‡n nhiá»u', 'Cáº§n phun thuá»‘c kháº©n cáº¥p', 'high', 'open', NULL),
('TKT-2026-0006', 1, (SELECT room_id FROM rooms WHERE room_number='101'), 'appliance', 'MÃ¡y láº¡nh cháº£y nÆ°á»›c trong phÃ²ng', 'NÆ°á»›c nhá» giá»t tá»« dÃ n láº¡nh', 'high', 'resolved', 'Anh Nam - Ä‘iá»‡n láº¡nh'),
('TKT-2026-0007', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'plumbing', 'RÃ² rá»‰ á»‘ng nÆ°á»›c dÆ°á»›i bá»“n rá»­a', 'NÆ°á»›c rá»‰ ra sÃ n, cáº§n sá»­a gáº¥p', 'high', 'in_progress', 'Anh TÃ i - thá»£ nÆ°á»›c'),
('TKT-2026-0008', 5, (SELECT room_id FROM rooms WHERE room_number='302'), 'electrical', 'CÃ´ng tÆ¡ Ä‘iá»‡n nháº£y sai sá»‘', 'Nghi cÃ´ng tÆ¡ cÅ©, cáº§n thay má»›i', 'high', 'resolved', 'Anh Nam - Ä‘iá»‡n láº¡nh'),
('TKT-2026-0009', 5, (SELECT room_id FROM rooms WHERE room_number='302'), 'furniture', 'BÃ n lÃ m viá»‡c bá»‹ á»p áº¹p', 'ChÃ¢n bÃ n lung lay, nguy hiá»ƒm', 'low', 'open', NULL),
('TKT-2026-0010', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'other', 'YÃªu cáº§u Ä‘á»•i á»• khÃ³a cá»­a chÃ­nh', 'Muá»‘n Ä‘á»•i khÃ³a vÃ¬ lÃ½ do an ninh', 'normal', 'resolved', 'Anh HÃ¹ng - má»™c');

-- =====================================================================
-- 7. CONVERSATION HISTORY (user messages only â€” no hardcoded AI responses)
--    The system generates ai_response dynamically. These exist to test
--    personalization / context awareness across tenants.
-- =====================================================================
INSERT INTO conversation_history (tenant_id, session_id, source, user_message, ai_response, system_used, iterations, latency_ms, tokens_used) VALUES
-- Tenant 1: Friendly, casual, on-time â€” há»i thÃ´ng tin cÆ¡ báº£n, tone thÃ¢n thiá»‡n
(1, uuid_generate_v4(), 'zalo', 'Anh Æ¡i phÃ²ng em giÃ¡ bao nhiÃªu váº­y?', NULL, NULL, NULL, NULL, NULL),
(1, uuid_generate_v4(), 'zalo', 'Dáº¡ cho em há»i wifi máº­t kháº©u lÃ  gÃ¬ áº¡? Em quÃªn máº¥t rá»“i', NULL, NULL, NULL, NULL, NULL),

-- Tenant 2: Professional, busy â€” ngáº¯n gá»n, Ä‘Ãºng trá»ng tÃ¢m, há»i thanh toÃ¡n & sá»‘ liá»‡u
(2, uuid_generate_v4(), 'messenger', 'Kiá»ƒm tra sá»‘ dÆ° hÃ³a Ä‘Æ¡n thÃ¡ng nÃ y giÃºp tÃ´i', NULL, NULL, NULL, NULL, NULL),
(2, uuid_generate_v4(), 'zalo', 'Cung cáº¥p sá»‘ tÃ i khoáº£n ngÃ¢n hÃ ng Ä‘á»ƒ chuyá»ƒn tiá»n thuÃª', NULL, NULL, NULL, NULL, NULL),
(2, uuid_generate_v4(), 'messenger', 'TÃ´i Ä‘i cÃ´ng tÃ¡c, thanh toÃ¡n trá»… 2 ngÃ y cÃ³ Ä‘Æ°á»£c khÃ´ng?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 3: Friendly, pro-active, chi tiáº¿t â€” há»i vá» tÆ°Æ¡ng lai, káº¿ hoáº¡ch dÃ i háº¡n
(3, uuid_generate_v4(), 'web', 'Em muá»‘n xem thÃ´ng tin há»£p Ä‘á»“ng, bao giá» háº¿t háº¡n vÃ  gia háº¡n nhÆ° tháº¿ nÃ o?', NULL, NULL, NULL, NULL, NULL),
(3, uuid_generate_v4(), 'web', 'PhÃ²ng em Ä‘iá»u hÃ²a cháº£y nÆ°á»›c, anh cho thá»£ qua kiá»ƒm tra giÃºp em vá»›i áº¡', NULL, NULL, NULL, NULL, NULL),
(3, uuid_generate_v4(), 'web', 'Cáº£m Æ¡n anh Ä‘Ã£ há»— trá»£ láº§n trÆ°á»›c. Em á»Ÿ lÃ¢u dÃ i, cÃ³ chÃ­nh sÃ¡ch Æ°u Ä‘Ã£i gÃ¬ khÃ´ng?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 4: Strict, hay phÃ n nÃ n, trá»… háº¡n â€” tone khÃ³ chá»‹u, Ä‘Ã²i há»i
(4, uuid_generate_v4(), 'sms', 'Sao thÃ¡ng nÃ y tiá»n Ä‘iá»‡n tÄƒng váº­y trá»i? TÃ­nh sai háº¿t rá»“i hay sao Ã¡', NULL, NULL, NULL, NULL, NULL),
(4, uuid_generate_v4(), 'sms', 'TÃ´i yÃªu cáº§u giáº£m tiá»n phÃ²ng vÃ¬ quÃ¡ á»“n, khÃ´ng ngá»§ Ä‘Æ°á»£c', NULL, NULL, NULL, NULL, NULL),
(4, uuid_generate_v4(), 'sms', 'Láº§n trÆ°á»›c nÃ³i thá»£ qua mÃ  khÃ´ng tháº¥y ai háº¿t, lÃ m Äƒn kiá»ƒu gÃ¬ váº­y?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 5: Professional, máº«u má»±c, cÃ³ káº¿ hoáº¡ch â€” lá»‹ch sá»±, Ä‘á» xuáº¥t
(5, uuid_generate_v4(), 'zalo', 'ChÃ o anh, há»£p Ä‘á»“ng cá»§a em sáº¯p háº¿t háº¡n, em muá»‘n gia háº¡n thÃªm 1 nÄƒm. Thá»§ tá»¥c tháº¿ nÃ o?', NULL, NULL, NULL, NULL, NULL),
(5, uuid_generate_v4(), 'zalo', 'PhÃ²ng em gáº§n Ä‘Ã¢y hay bá»‹ nháº£y cáº§u dao, nhá» anh kiá»ƒm tra há»‡ thá»‘ng Ä‘iá»‡n giÃºp', NULL, NULL, NULL, NULL, NULL),
(5, uuid_generate_v4(), 'zalo', 'Cho em há»i phÃ²ng 202 bÃªn cáº¡nh cÃ²n trá»‘ng khÃ´ng? Em muá»‘n giá»›i thiá»‡u báº¡n em vÃ o á»Ÿ', NULL, NULL, NULL, NULL, NULL);

-- =====================================================================
-- 8. APPROVAL QUEUE
-- =====================================================================
INSERT INTO approval_queue (tool_name, tool_args, tenant_id, requested_by, approver_role, status) VALUES
-- Nháº¯c nhá»Ÿ thanh toÃ¡n
('send_payment_reminder', '{"tenant_id": 4, "tone": "strict", "final_notice": true}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),
('send_payment_reminder', '{"tenant_id": 2, "tone": "friendly"}'::jsonb, 2, 'system_cron', 'landlord', 'approved'),

-- Äiá»u chá»‰nh há»£p Ä‘á»“ng
('modify_contract', '{"tenant_id": 5, "new_rent": 4700000, "effective_date": "2026-07-01"}'::jsonb, 5, 'ai_agent', 'landlord', 'pending'),
('modify_contract', '{"tenant_id": 3, "new_end_date": "2027-12-31"}'::jsonb, 3, 'tenant', 'landlord', 'approved'),

-- Cháº¥m dá»©t há»£p Ä‘á»“ng
('terminate_contract', '{"tenant_id": 4, "reason": "Cháº­m thanh toÃ¡n 3 thÃ¡ng liÃªn tiáº¿p"}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),

-- Cáº£nh bÃ¡o vi pháº¡m
('send_warning', '{"tenant_id": 4, "reason": "KhÃ´ng há»£p tÃ¡c sá»­a chá»¯a", "level": "final"}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),

-- PhÃª duyá»‡t báº£o trÃ¬
('approve_maintenance', '{"ticket_code": "TKT-2026-0005", "vendor": "Cty diá»‡t cÃ´n trÃ¹ng Sáº¡ch", "estimated_cost": 500000}'::jsonb, 4, 'ai_agent', 'landlord', 'approved');

-- =====================================================================
-- 9. USER EMBEDDINGS (placeholder vectors for semantic memory)
-- =====================================================================
INSERT INTO user_embeddings (tenant_id, memory_text, embedding) VALUES
(1, 'KhÃ¡ch thuÃª ráº¥t thÃ¢n thiá»‡n, hay chÃ o há»i', array_fill(0.1, ARRAY[3072])::vector),
(1, 'KhÃ¡ch hay quÃªn Ä‘Ã³ng tiá»n vÃ o ngÃ y 5 hÃ ng thÃ¡ng', array_fill(0.2, ARRAY[3072])::vector),
(2, 'KhÃ¡ch thÃ­ch phÃ²ng yÃªn tÄ©nh, nháº¡y cáº£m vá» tiáº¿ng á»“n', array_fill(0.3, ARRAY[3072])::vector),
(3, 'KhÃ¡ch á»Ÿ lÃ¢u dÃ i, cÃ³ Ã½ Ä‘á»‹nh gia háº¡n há»£p Ä‘á»“ng', array_fill(0.4, ARRAY[3072])::vector),
(4, 'KhÃ¡ch thanh toÃ¡n thÆ°á»ng xuyÃªn trá»…, cáº§n nháº¯c nhá»Ÿ', array_fill(0.5, ARRAY[3072])::vector);

-- =====================================================================
-- 10. SEMANTIC CACHE (System 1 fast answers)
-- =====================================================================
INSERT INTO semantic_cache (query_text, query_embedding, response_text) VALUES
('Máº­t kháº©u wifi lÃ  gÃ¬', array_fill(0.6, ARRAY[3072])::vector, 'Máº­t kháº©u wifi Ä‘Æ°á»£c cáº¥p riÃªng khi báº¡n nháº­n phÃ²ng. Báº¡n cÃ³ thá»ƒ xem trong há»“ sÆ¡ hoáº·c liÃªn há»‡ quáº£n lÃ½ (0901-234-567) Ä‘á»ƒ Ä‘Æ°á»£c cáº¥p láº¡i.'),
('Giá» yÃªn tÄ©nh lÃ  máº¥y giá»', array_fill(0.7, ARRAY[3072])::vector, 'Khung giá» yÃªn tÄ©nh tuyá»‡t Ä‘á»‘i lÃ  tá»« 22:00 - 06:00 (T2-T6) vÃ  22:00 - 07:00 (Cuá»‘i tuáº§n). Vui lÃ²ng khÃ´ng hÃ¡t karaoke hay gÃ¢y á»“n Ã o.'),
('PhÃ­ gá»­i xe mÃ¡y bao nhiÃªu', array_fill(0.8, ARRAY[3072])::vector, 'PhÃ­ gá»­i xe mÃ¡y lÃ  100.000Ä‘/thÃ¡ng. Äá»‘i vá»›i xe Ä‘iá»‡n lÃ  150.000Ä‘/thÃ¡ng (Ä‘Ã£ bao gá»“m sáº¡c). Vá»‹ trÃ­ gá»­i á»Ÿ táº§ng háº§m, ra vÃ o 24/7.');

COMMIT;
