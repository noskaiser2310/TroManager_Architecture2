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
('101', 1, 25.0, 3500000, 'occupied', '{"Giường":"1m6x2m","Tủ quần áo":"3 cánh","Điều hòa":"Daikin 9000BTU","Nóng lạnh":"Năng lượng mặt trời","Vòi tắm":"Kính","Bàn bếp":"Có","Cửa sổ":"Hướng nam"}'),
('102', 1, 30.0, 4500000, 'occupied', '{"Giường":"1m8x2m","Tủ quần áo":"4 cánh","Điều hòa":"Daikin 12000BTU","Nóng lạnh":"Năng lượng mặt trời","Vòi tắm":"Kính","Bàn bếp":"Có","Cửa sổ":"Hướng đông","Ban công":"Nhỏ"}'),
('103', 1, 20.0, 3000000, 'available', '{"Giường":"1m6x2m","Tủ quần áo":"2 cánh","Điều hòa":"Panasonic 9000BTU","Nóng lạnh":"Gián tiếp","Bàn bếp":"Có","Cửa sổ":"Hướng bắc"}'),
('201', 2, 22.0, 3200000, 'occupied', '{"Giường":"1m6x2m","Tủ quần áo":"3 cánh","Điều hòa":"LG 9000BTU","Nóng lạnh":"Gián tiếp","Bàn bếp":"Có","Cửa sổ":"Hướng đông"}'),
('202', 2, 28.0, 4000000, 'available', '{"Giường":"1m8x2m","Tủ quần áo":"4 cánh","Điều hòa":"Daikin 12000BTU","Nóng lạnh":"Năng lượng mặt trời","Bàn bếp":"Có","Cửa sổ":"Hướng nam","Ban công":"Rộng"}'),
('203', 2, 22.0, 3200000, 'available', '{"Giường":"1m6x2m","Tủ quần áo":"2 cánh","Điều hòa":"Panasonic 9000BTU","Nóng lạnh":"Gián tiếp","Bàn bếp":"Có","Cửa sổ":"Hướng tây"}'),
('301', 3, 25.0, 3500000, 'occupied', '{"Giường":"1m6x2m","Tủ quần áo":"3 cánh","Điều hòa":"Daikin 9000BTU","Nóng lạnh":"Năng lượng mặt trời","Bàn bếp":"Có","Cửa sổ":"Hướng nam"}'),
('302', 3, 30.0, 4500000, 'occupied', '{"Giường":"1m8x2m","Tủ quần áo":"4 cánh","Điều hòa":"Daikin 12000BTU","Nóng lạnh":"Năng lượng mặt trời","Vòi tắm":"Kính","Bàn bếp":"Có","Cửa sổ":"Hướng đông","Ban công":"Nhỏ"}'),
('303', 3, 25.0, 3500000, 'available', '{"Giường":"1m6x2m","Tủ quần áo":"3 cánh","Điều hòa":"LG 9000BTU","Nóng lạnh":"Gián tiếp","Bàn bếp":"Có","Cửa sổ":"Hướng bắc"}');

-- =====================================================================
-- 2. TENANTS (user_profiles)
-- =====================================================================
INSERT INTO user_profiles (full_name, phone_number, room_id, lease_start, lease_end, tone_preference) VALUES
('Nguyễn Văn Minh', '0901234567', (SELECT room_id FROM rooms WHERE room_number='101'), '2024-01-15', '2026-12-31', 'friendly'),
('Trần Thị Hoa',   '0902345678', (SELECT room_id FROM rooms WHERE room_number='102'), '2025-03-01', '2026-08-31', 'professional'),
('Lê Hoàng Tuấn',  '0903456789', (SELECT room_id FROM rooms WHERE room_number='201'), '2024-06-01', '2026-12-31', 'friendly'),
('Phạm Thị Lan',   '0904567890', (SELECT room_id FROM rooms WHERE room_number='301'), '2025-01-10', '2026-07-10', 'strict'),
('Đỗ Văn Hùng',    '0905678901', (SELECT room_id FROM rooms WHERE room_number='302'), '2024-09-01', '2026-09-01', 'professional');

-- =====================================================================
-- 3. CONTRACTS
-- =====================================================================
INSERT INTO contracts (tenant_id, room_id, start_date, end_date, deposit_amount, monthly_rent, status)
SELECT u.tenant_id, u.room_id, u.lease_start, u.lease_end,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN 7000000
           WHEN 'Trần Thị Hoa' THEN 9000000
           WHEN 'Lê Hoàng Tuấn' THEN 6400000
           WHEN 'Phạm Thị Lan' THEN 7000000
           WHEN 'Đỗ Văn Hùng' THEN 9000000
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
           WHEN 'Nguyễn Văn Minh' THEN 95
           WHEN 'Trần Thị Hoa' THEN 115
           WHEN 'Lê Hoàng Tuấn' THEN 78
           WHEN 'Phạm Thị Lan' THEN 90
           WHEN 'Đỗ Văn Hùng' THEN 110
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN 332500
           WHEN 'Trần Thị Hoa' THEN 402500
           WHEN 'Lê Hoàng Tuấn' THEN 273000
           WHEN 'Phạm Thị Lan' THEN 315000
           WHEN 'Đỗ Văn Hùng' THEN 385000
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN 5
           WHEN 'Trần Thị Hoa' THEN 6
           WHEN 'Lê Hoàng Tuấn' THEN 4
           WHEN 'Phạm Thị Lan' THEN 6
           WHEN 'Đỗ Văn Hùng' THEN 6
           ELSE 0 END,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN 500000
           WHEN 'Trần Thị Hoa' THEN 600000
           WHEN 'Lê Hoàng Tuấn' THEN 400000
           WHEN 'Phạm Thị Lan' THEN 600000
           WHEN 'Đỗ Văn Hùng' THEN 600000
           ELSE 0 END,
       50000,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN r.monthly_rent + 332500 + 500000 + 50000
           WHEN 'Trần Thị Hoa' THEN r.monthly_rent + 402500 + 600000 + 50000
           WHEN 'Lê Hoàng Tuấn' THEN r.monthly_rent + 273000 + 400000 + 50000
           WHEN 'Phạm Thị Lan' THEN r.monthly_rent + 315000 + 600000 + 50000
           WHEN 'Đỗ Văn Hùng' THEN r.monthly_rent + 385000 + 600000 + 50000
       END,
       dates.due_date,
       CASE u.full_name
           WHEN 'Nguyễn Văn Minh' THEN 'paid'
           WHEN 'Trần Thị Hoa' THEN 'unpaid'
           WHEN 'Lê Hoàng Tuấn' THEN 'paid'
           WHEN 'Phạm Thị Lan' THEN 'overdue'
           WHEN 'Đỗ Văn Hùng' THEN 'paid'
       END::invoice_status_enum,
       CASE WHEN u.full_name IN ('Nguyễn Văn Minh', 'Lê Hoàng Tuấn', 'Đỗ Văn Hùng') THEN dates.due_date - INTERVAL '1 day'
            WHEN u.full_name = 'Trần Thị Hoa' THEN NULL ELSE NULL END
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
-- Tenant 1: Friendly, gương mẫu
(1, 'on_time_payment', 'Thanh toán đúng hạn tháng 5'),
(1, 'on_time_payment', 'Thanh toán đúng hạn tháng 4'),
(1, 'on_time_payment', 'Thanh toán đúng hạn tháng 3'),
(1, 'maintenance_request', 'Báo bóng đèn phòng khách cháy'),
(1, 'maintenance_request', 'Yêu cầu kiểm tra máy lạnh'),
(1, 'noise_complaint', 'Nhà bên cạnh mở nhạc to sau 22h'),
(1, 'compliment', 'Khen nhân viên sửa chữa nhiệt tình'),

-- Tenant 2: Professional, đôi lúc trễ
(2, 'on_time_payment', 'Thanh toán đúng hạn tháng 5'),
(2, 'late_payment', 'Thanh toán trễ 3 ngày tháng 3 do công tác'),
(2, 'on_time_payment', 'Thanh toán đúng hạn tháng 2'),
(2, 'maintenance_request', 'Điều hòa kêu to'),
(2, 'contract_signed', 'Ký hợp đồng thuê 1 năm'),

-- Tenant 3: Friendly, cực kỳ đúng giờ
(3, 'on_time_payment', 'Thanh toán đúng hạn tháng 5'),
(3, 'on_time_payment', 'Thanh toán đúng hạn tháng 4'),
(3, 'on_time_payment', 'Thanh toán đúng hạn tháng 3'),
(3, 'room_transfer', 'Đề nghị chuyển lên phòng có ban công'),
(3, 'positive_feedback', 'Khen dịch vụ wifi ổn định'),

-- Tenant 4: Strict, trễ kinh niên
(4, 'late_payment', 'Thanh toán trễ 5 ngày tháng 5'),
(4, 'late_payment', 'Thanh toán trễ 3 ngày tháng 4'),
(4, 'late_payment', 'Thanh toán trễ 7 ngày tháng 3'),
(4, 'late_payment', 'Thanh toán trễ 4 ngày tháng 2'),
(4, 'noise_complaint', 'Phàn nàn phòng bên cãi nhau ầm ĩ'),
(4, 'maintenance_request', 'Cửa sổ bị kẹt'),
(4, 'payment_promise_made', 'Hứa thanh toán trước ngày 10 tháng 6'),
(4, 'payment_promise_broken', 'Không thanh toán đúng hẹn lần 1'),

-- Tenant 5: Professional, mẫu mực
(5, 'on_time_payment', 'Thanh toán đúng hạn tháng 5'),
(5, 'on_time_payment', 'Thanh toán đúng hạn tháng 4'),
(5, 'on_time_payment', 'Thanh toán đúng hạn tháng 3'),
(5, 'contract_signed', 'Gia hạn hợp đồng thêm 1 năm'),
(5, 'maintenance_request', 'Kiểm tra hệ thống điện');

-- =====================================================================
-- 6. MAINTENANCE TICKETS
-- =====================================================================
INSERT INTO maintenance_tickets (ticket_code, tenant_id, room_id, issue_category, title, description, priority, status, assigned_to) VALUES
('TKT-2026-0001', 1, (SELECT room_id FROM rooms WHERE room_number='101'), 'plumbing', 'Vòi sen tắm bị tắc', 'Nước chảy yếu, có thể do cặn', 'normal', 'resolved', 'Anh Tài - thợ nước'),
('TKT-2026-0002', 2, (SELECT room_id FROM rooms WHERE room_number='102'), 'internet', 'Wifi chập chờn buổi tối', 'Mất kết nối liên tục từ 20h-23h', 'normal', 'in_progress', 'Anh Tú - IT'),
('TKT-2026-0003', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'appliance', 'Tủ lạnh kêu to bất thường', 'Tiếng ồn ảnh hưởng giấc ngủ', 'normal', 'open', NULL),
('TKT-2026-0004', 4, (SELECT room_id FROM rooms WHERE room_number='301'), 'electrical', 'Ổ cắm điện phòng khách không có điện', 'Đã kiểm tra cầu dao, vẫn không có', 'normal', 'in_progress', 'Anh Nam - điện lạnh'),
('TKT-2026-0005', 4, (SELECT room_id FROM rooms WHERE room_number='301'), 'pest', 'Kiến ba khoang xuất hiện nhiều', 'Cần phun thuốc khẩn cấp', 'high', 'open', NULL),
('TKT-2026-0006', 1, (SELECT room_id FROM rooms WHERE room_number='101'), 'appliance', 'Máy lạnh chảy nước trong phòng', 'Nước nhỏ giọt từ dàn lạnh', 'high', 'resolved', 'Anh Nam - điện lạnh'),
('TKT-2026-0007', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'plumbing', 'Rò rỉ ống nước dưới bồn rửa', 'Nước rỉ ra sàn, cần sửa gấp', 'high', 'in_progress', 'Anh Tài - thợ nước'),
('TKT-2026-0008', 5, (SELECT room_id FROM rooms WHERE room_number='302'), 'electrical', 'Công tơ điện nhảy sai số', 'Nghi công tơ cũ, cần thay mới', 'high', 'resolved', 'Anh Nam - điện lạnh'),
('TKT-2026-0009', 5, (SELECT room_id FROM rooms WHERE room_number='302'), 'furniture', 'Bàn làm việc bị ọp ẹp', 'Chân bàn lung lay, nguy hiểm', 'low', 'open', NULL),
('TKT-2026-0010', 3, (SELECT room_id FROM rooms WHERE room_number='201'), 'other', 'Yêu cầu đổi ổ khóa cửa chính', 'Muốn đổi khóa vì lý do an ninh', 'normal', 'resolved', 'Anh Hùng - mộc');

-- =====================================================================
-- 7. CONVERSATION HISTORY (user messages only — no hardcoded AI responses)
--    The system generates ai_response dynamically. These exist to test
--    personalization / context awareness across tenants.
-- =====================================================================
INSERT INTO conversation_history (tenant_id, session_id, source, user_message, ai_response, system_used, iterations, latency_ms, tokens_used) VALUES
-- Tenant 1: Friendly, casual, on-time — hỏi thông tin cơ bản, tone thân thiện
(1, uuid_generate_v4(), 'zalo', 'Anh ơi phòng em giá bao nhiêu vậy?', NULL, NULL, NULL, NULL, NULL),
(1, uuid_generate_v4(), 'zalo', 'Dạ cho em hỏi wifi mật khẩu là gì ạ? Em quên mất rồi', NULL, NULL, NULL, NULL, NULL),

-- Tenant 2: Professional, busy — ngắn gọn, đúng trọng tâm, hỏi thanh toán & số liệu
(2, uuid_generate_v4(), 'messenger', 'Kiểm tra số dư hóa đơn tháng này giúp tôi', NULL, NULL, NULL, NULL, NULL),
(2, uuid_generate_v4(), 'zalo', 'Cung cấp số tài khoản ngân hàng để chuyển tiền thuê', NULL, NULL, NULL, NULL, NULL),
(2, uuid_generate_v4(), 'messenger', 'Tôi đi công tác, thanh toán trễ 2 ngày có được không?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 3: Friendly, pro-active, chi tiết — hỏi về tương lai, kế hoạch dài hạn
(3, uuid_generate_v4(), 'web', 'Em muốn xem thông tin hợp đồng, bao giờ hết hạn và gia hạn như thế nào?', NULL, NULL, NULL, NULL, NULL),
(3, uuid_generate_v4(), 'web', 'Phòng em điều hòa chảy nước, anh cho thợ qua kiểm tra giúp em với ạ', NULL, NULL, NULL, NULL, NULL),
(3, uuid_generate_v4(), 'web', 'Cảm ơn anh đã hỗ trợ lần trước. Em ở lâu dài, có chính sách ưu đãi gì không?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 4: Strict, hay phàn nàn, trễ hạn — tone khó chịu, đòi hỏi
(4, uuid_generate_v4(), 'sms', 'Sao tháng này tiền điện tăng vậy trời? Tính sai hết rồi hay sao á', NULL, NULL, NULL, NULL, NULL),
(4, uuid_generate_v4(), 'sms', 'Tôi yêu cầu giảm tiền phòng vì quá ồn, không ngủ được', NULL, NULL, NULL, NULL, NULL),
(4, uuid_generate_v4(), 'sms', 'Lần trước nói thợ qua mà không thấy ai hết, làm ăn kiểu gì vậy?', NULL, NULL, NULL, NULL, NULL),

-- Tenant 5: Professional, mẫu mực, có kế hoạch — lịch sự, đề xuất
(5, uuid_generate_v4(), 'zalo', 'Chào anh, hợp đồng của em sắp hết hạn, em muốn gia hạn thêm 1 năm. Thủ tục thế nào?', NULL, NULL, NULL, NULL, NULL),
(5, uuid_generate_v4(), 'zalo', 'Phòng em gần đây hay bị nhảy cầu dao, nhờ anh kiểm tra hệ thống điện giúp', NULL, NULL, NULL, NULL, NULL),
(5, uuid_generate_v4(), 'zalo', 'Cho em hỏi phòng 202 bên cạnh còn trống không? Em muốn giới thiệu bạn em vào ở', NULL, NULL, NULL, NULL, NULL);

-- =====================================================================
-- 8. APPROVAL QUEUE
-- =====================================================================
INSERT INTO approval_queue (tool_name, tool_args, tenant_id, requested_by, approver_role, status) VALUES
-- Nhắc nhở thanh toán
('send_payment_reminder', '{"tenant_id": 4, "tone": "strict", "final_notice": true}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),
('send_payment_reminder', '{"tenant_id": 2, "tone": "friendly"}'::jsonb, 2, 'system_cron', 'landlord', 'approved'),

-- Điều chỉnh hợp đồng
('modify_contract', '{"tenant_id": 5, "new_rent": 4700000, "effective_date": "2026-07-01"}'::jsonb, 5, 'ai_agent', 'landlord', 'pending'),
('modify_contract', '{"tenant_id": 3, "new_end_date": "2027-12-31"}'::jsonb, 3, 'tenant', 'landlord', 'approved'),

-- Chấm dứt hợp đồng
('terminate_contract', '{"tenant_id": 4, "reason": "Chậm thanh toán 3 tháng liên tiếp"}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),

-- Cảnh báo vi phạm
('send_warning', '{"tenant_id": 4, "reason": "Không hợp tác sửa chữa", "level": "final"}'::jsonb, 4, 'ai_agent', 'landlord', 'pending'),

-- Phê duyệt bảo trì
('approve_maintenance', '{"ticket_code": "TKT-2026-0005", "vendor": "Cty diệt côn trùng Sạch", "estimated_cost": 500000}'::jsonb, 4, 'ai_agent', 'landlord', 'approved');

-- =====================================================================
-- 9. USER EMBEDDINGS (placeholder vectors for semantic memory)
-- =====================================================================
INSERT INTO user_embeddings (tenant_id, memory_text, embedding) VALUES
(1, 'Khách thuê rất thân thiện, hay chào hỏi', array_fill(0.1, ARRAY[3072])::vector),
(1, 'Khách hay quên đóng tiền vào ngày 5 hàng tháng', array_fill(0.2, ARRAY[3072])::vector),
(2, 'Khách thích phòng yên tĩnh, nhạy cảm về tiếng ồn', array_fill(0.3, ARRAY[3072])::vector),
(3, 'Khách ở lâu dài, có ý định gia hạn hợp đồng', array_fill(0.4, ARRAY[3072])::vector),
(4, 'Khách thanh toán thường xuyên trễ, cần nhắc nhở', array_fill(0.5, ARRAY[3072])::vector);

-- =====================================================================
-- 10. SEMANTIC CACHE (System 1 fast answers)
-- =====================================================================
INSERT INTO semantic_cache (query_text, query_embedding, response_text) VALUES
('Mật khẩu wifi là gì', array_fill(0.6, ARRAY[3072])::vector, 'Mật khẩu wifi được cấp riêng khi bạn nhận phòng. Bạn có thể xem trong hồ sơ hoặc liên hệ quản lý (0901-234-567) để được cấp lại.'),
('Giờ yên tĩnh là mấy giờ', array_fill(0.7, ARRAY[3072])::vector, 'Khung giờ yên tĩnh tuyệt đối là từ 22:00 - 06:00 (T2-T6) và 22:00 - 07:00 (Cuối tuần). Vui lòng không hát karaoke hay gây ồn ào.'),
('Phí gửi xe máy bao nhiêu', array_fill(0.8, ARRAY[3072])::vector, 'Phí gửi xe máy là 100.000đ/tháng. Đối với xe điện là 150.000đ/tháng (đã bao gồm sạc). Vị trí gửi ở tầng hầm, ra vào 24/7.');

COMMIT;
