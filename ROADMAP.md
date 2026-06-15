# 🗺️ TroManager ROADMAP

Tài liệu này phác thảo lộ trình phát triển tương lai cho hệ thống **TroManager Architecture #2** sau khi Phase 1 (Core Architecture) đã hoàn tất 100%. Lộ trình tập trung vào việc mở rộng quy mô (Scale Out), tăng cường bảo mật, và bổ sung các tính năng AI siêu cấp.

---

## Phase 1: Observability & Optimization (Hiện tại - Sắp hoàn thành)
**Mục tiêu**: Đưa hệ thống vào trạng thái Production-Ready với khả năng giám sát toàn diện.

- [x] Tích hợp **Prometheus/Grafana** qua `/metrics` endpoint.
- [x] Structured JSON Logging để theo dõi ID từng request.
- [ ] Theo dõi và cảnh báo **Cost USD** thực tế trên từng phiên Chat để ngăn chặn abuse.
- [ ] Xây dựng **UMLMetrics** (User Modeling Layer Metrics) để giám sát: `avg_context_build_time`, `vector_search_p99`, `cache_hit_rate`, v.v.
- [ ] Rate Limiting cấp độ mạng (tích hợp Redis/Nginx) thay vì chỉ ở mức Application.

## Phase 2: Quản lý Đa cơ sở & Tối ưu Trải nghiệm Chủ trọ (Quý tới)
**Mục tiêu**: Hỗ trợ chủ trọ quản lý vài cơ sở (Boarding Houses) với quy mô dưới 100 khách thuê một cách mượt mà và bảo mật. Lưu ý hệ thống hiện tại đã phù hợp với quy mô nhỏ < 100 khách, tránh over-engineering.

- **Mở rộng Schema Database**: Thêm trường `boarding_house_id` vào các bảng (`user_profiles`, `behavior_logs`, `user_embeddings`) để chủ trọ dễ dàng quản lý độc lập từng khu trọ (nhà A, nhà B).
- **Tenant Isolation & GDPR**: Bổ sung Role-Based Access Control (RBAC) cơ bản để Agent không nhầm lẫn thông tin giữa các khu trọ. Triển khai API xóa toàn bộ dữ liệu (Right to be Forgotten) theo chuẩn GDPR khi khách trả phòng.
- **Tối ưu hóa Database Nhỏ gọn**: Thiết lập tự động dọn dẹp (auto-vacuum) và nén log định kỳ, giữ cho PostgreSQL và PgVector hoạt động cực kỳ nhẹ nhàng và chi phí thấp (phù hợp quy mô nhỏ < 100 tenants).
- **Real-time Personalization (Cập nhật)**: Loại bỏ các CronJob tối ưu Persona nặng nề chạy mỗi ngày. Thay vào đó, hệ thống tập trung hoàn toàn vào Cập nhật Real-time qua tool `update_user_preference` của System 2 và trích xuất Insight tức thì trong từng lượt Chat (ReAct Agent).

## Phase 3: Advanced Reasoning & Multi-Agent (Tương lai gần)
**Mục tiêu**: Nâng cao trí thông minh của AI trong các tình huống tranh chấp pháp lý và tài chính phức tạp.

- **Knowledge Graph Integration**: Bổ sung đồ thị tri thức (Knowledge Graph) cho các quy định pháp lý phức tạp mà RAG Vector cơ bản không thể cover hết (ví dụ: truy vết chuỗi hành vi vi phạm).
- **Legal/Financial Sub-agents**: Tách System 2 thành một Multi-Agent Framework (như LangGraph StateMachine) nơi một agent lo tài chính, một agent lo pháp lý hợp đồng, và một agent tổng hợp.
- **Voice Agent Interface**: Tích hợp module Speech-to-Text để người thuê có thể gửi voice chat phàn nàn sự cố qua Zalo, AI tự động chuyển text và book lịch bảo trì.

## Phase 4: Admin UI & Control Plane (Dài hạn)
**Mục tiêu**: Cung cấp giao diện trực quan cho Chủ trọ.

- **Next.js Dashboard**: Xây dựng Frontend cho phép chủ trọ:
  - Xem danh sách `Approval Queue` và bấm nút "Duyệt" tin nhắn từ UI.
  - Quản lý kho kiến thức (Upload `.md` files).
  - Trực quan hoá Persona của từng khách thuê (Dashboard hành vi).
- **Agent Analytics**: Biểu đồ phân tích lý do LLM chọn System 1 hay System 2, và báo cáo chi phí token.

---

> **Lưu ý**: Lộ trình này mang tính định hướng và có thể thay đổi dựa trên phản hồi của người dùng cuối (End-users) sau khi triển khai thực tế.
