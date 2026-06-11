-- =====================================================================
-- TroManager - Seed Data
-- Dữ liệu mẫu cho development và testing
-- =====================================================================

-- Insert thêm một số invoices cho các tháng trước (để test behavior history)
INSERT INTO invoices (tenant_id, room_id, contract_id, invoice_month, base_rent, electricity_kwh, electricity_cost, water_m3, water_cost, service_fee, total_amount, due_date, status, paid_date) VALUES
(1, 1, 1, '2026-05-01', 3000000, 90, 315000, 5, 500000, 50000, 3865000, '2026-05-05', 'paid', '2026-05-04'),
(1, 1, 1, '2026-04-01', 3000000, 85, 297500, 4, 400000, 50000, 3747500, '2026-04-05', 'paid', '2026-04-05'),
(2, 2, 2, '2026-05-01', 3500000, 110, 385000, 5, 500000, 50000, 4435000, '2026-05-05', 'paid', '2026-05-07'),
(2, 2, 2, '2026-04-01', 3500000, 100, 350000, 5, 500000, 50000, 4400000, '2026-04-05', 'paid', '2026-04-08'),
(3, 4, 3, '2026-05-01', 3200000, 75, 262500, 4, 400000, 50000, 3912500, '2026-05-05', 'paid', '2026-05-05'),
(4, 7, 4, '2026-05-01', 3500000, 85, 297500, 5, 500000, 50000, 4352500, '2026-05-05', 'paid', '2026-05-10'),
(5, 8, 5, '2026-05-01', 4500000, 105, 367500, 6, 600000, 50000, 5517500, '2026-05-05', 'paid', '2026-05-05');

-- Thêm behavior logs để test persona_optimizer
INSERT INTO behavior_logs (tenant_id, action_type, description) VALUES
-- Tenant 1: Friendly, thường đúng hạn
(1, 'on_time_payment', 'Tháng 4 đúng hạn'),
(1, 'on_time_payment', 'Tháng 5 đúng hạn'),
(1, 'maintenance_request', 'Báo thay bóng đèn'),
(1, 'maintenance_request', 'Báo vòi nước rỉ'),
(1, 'noise_complaint', 'Phàn nàn nhà bên hát karaoke'),

-- Tenant 2: Professional, thỉnh thoảng trễ
(2, 'late_payment', 'Trễ 2 ngày tháng 4'),
(2, 'on_time_payment', 'Tháng 5 trễ 2 ngày vẫn tính đúng hạn'),
(2, 'maintenance_request', 'Báo điều hòa không mát'),

-- Tenant 3: Friendly, đúng hạn 100%
(3, 'on_time_payment', 'Tháng 3 đúng hạn'),
(3, 'on_time_payment', 'Tháng 4 đúng hạn'),
(3, 'on_time_payment', 'Tháng 5 đúng hạn'),
(3, 'room_transfer', 'Đã hỏi về chuyển phòng tầng 2'),

-- Tenant 4: Strict, hay trễ
(4, 'late_payment', 'Trễ 5 ngày tháng 5'),
(4, 'late_payment', 'Trễ 3 ngày tháng 4'),
(4, 'late_payment', 'Trễ 7 ngày tháng 3'),
(4, 'noise_complaint', 'Khiếu nại hàng xóm ồn'),

-- Tenant 5: Professional, đúng hạn
(5, 'on_time_payment', 'Tháng 4 đúng hạn'),
(5, 'on_time_payment', 'Tháng 5 đúng hạn'),
(5, 'contract_signed', 'Đã ký gia hạn hợp đồng');

-- Thêm maintenance tickets mẫu
INSERT INTO maintenance_tickets (ticket_code, tenant_id, room_id, issue_category, title, description, priority, status, assigned_to) VALUES
('TKT-2026-0001', 1, 1, 'plumbing', 'Vòi nước rỉ', 'Vòi nước bồn rửa mặt bị rỉ nước liên tục', 'normal', 'resolved', 'Anh Tài - thợ nước'),
('TKT-2026-0002', 2, 2, 'appliance', 'Điều hòa không mát', 'Điều hòa chạy nhưng không mát, nghi thiếu gas', 'high', 'in_progress', 'Anh Nam - điện lạnh'),
('TKT-2026-0003', 4, 7, 'electrical', 'Bóng đèn phòng tắm cháy', 'Bóng đèn LED phòng tắm không sáng', 'low', 'open', NULL),
('TKT-2026-0004', 3, 4, 'appliance', 'Máy nước nóng không hoạt động', 'Bật máy nước nóng 30 phút vẫn không nóng', 'high', 'resolved', 'Anh Nam - điện lạnh'),
('TKT-2026-0005', 5, 8, 'furniture', 'Kệ giày bị lỏng', 'Kệ giày ở lối vào bị lỏng, có thể ngã', 'low', 'open', NULL);

-- Thêm conversation history mẫu
INSERT INTO conversation_history (tenant_id, session_id, source, user_message, ai_response, system_used, iterations, latency_ms, tokens_used) VALUES
(1, uuid_generate_v4(), 'zalo', 'Wifi mật khẩu gì', 'Mật khẩu wifi là: trohai2026', 'system1', 1, 180, 320),
(1, uuid_generate_v4(), 'zalo', 'Phòng tôi giá bao nhiêu', 'Phòng 101 của anh có giá 3.000.000đ/tháng, chưa bao gồm điện nước.', 'system1', 2, 1450, 890),
(2, uuid_generate_v4(), 'zalo', 'Tôi còn nợ bao nhiêu', 'Chào chị Lan, tháng 6/2026 chị còn nợ 4.570.000đ. Hạn thanh toán là 05/06.', 'system2', 3, 4200, 2100),
(3, uuid_generate_v4(), 'zalo', 'Điều hòa phòng tôi bị hỏng, báo giúp tôi', 'Em đã tạo yêu cầu sửa chữa TKT-2026-0006. Anh Nam - thợ điện lạnh sẽ liên hệ anh trong 24h tới.', 'system2', 4, 5800, 3500),
(4, uuid_generate_v4(), 'zalo', 'Bao giờ hết hợp đồng', 'Hợp đồng của chị còn hiệu lực đến 10/07/2026 (còn 35 ngày).', 'system1', 1, 220, 450);

-- Thêm approval queue mẫu (cho sensitive tools)
INSERT INTO approval_queue (tool_name, tool_args, tenant_id, requested_by, approver_role, status) VALUES
('send_payment_reminder', '{"tenant_id": 4, "invoice_id": 4, "tone": "strict"}'::jsonb, 4, 'system_cron', 'landlord', 'pending'),
('send_payment_reminder', '{"tenant_id": 2, "invoice_id": 2, "tone": "friendly"}'::jsonb, 2, 'system_cron', 'landlord', 'approved'),
('modify_contract', '{"tenant_id": 3, "contract_id": 3, "new_end_date": "2027-05-31"}'::jsonb, 3, 'ai_agent', 'landlord', 'pending');

-- =====================================================================
-- END OF SEED DATA
-- =====================================================================
