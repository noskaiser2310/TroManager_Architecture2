# Kịch bản: Khiếu nại hoá đơn — tiền điện tăng bất thường

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Phạm Thị Lan |
| Tenant ID | 4 |
| Phòng | 301 (tầng 3, 25m², 3.500.000đ/tháng) |
| Tone | strict |
| Hợp đồng | 2025-01-10 → 2026-07-10 |
| Lịch sử thanh toán | Trễ kinh niên (tháng 2: 4 ngày, tháng 3: 7 ngày, tháng 4: 3 ngày, tháng 5: 5 ngày) |
| Tình trạng hoá đơn | Overdue (cả tháng 5 và tháng 6) |
| Ticket | TKT-0004 (ổ cắm điện, in_progress), TKT-0005 (kiến ba khoang, open) |

### Multi-turn conversation

**Turn 1** — Khách phát hiện bất thường, khiếu nại.
> "Sao tháng này tiền điện lên tới 90 kWh mà tính 315.000đ? Hồi tháng trước cũng 90 kWh mà có 315.000đ thôi. Rồi tiền nước 6 khối tính 600.000đ nữa. Tổng cộng hoá đơn tháng 6 của tôi là bao nhiêu? Sao thấy cao quá vậy? Tôi dùng có khác gì đâu, có phải đọc nhầm đồng hồ không?"

**Hệ thống**: Kiểm tra invoice tháng 6 (overdue) — base_rent 3.500.000đ, điện 315.000đ (90kWh×3.500đ), nước 600.000đ (6m³×100.000đ), service 50.000đ → tổng 4.465.000đ. So với tháng trước không thay đổi nhiều.

**Turn 2** — Khách không tin, yêu cầu kiểm tra đồng hồ.
> "Tôi không tin. Tháng nào cũng 90 kWh mà sao lúc nào cũng 315.000đ hết vậy? Tính nhầm hay sao. Tôi yêu cầu có người qua kiểm tra đồng hồ điện nước, tôi muốn xem tận mắt. Bao giờ thì qua?"

**Hệ thống**: Giải thích cách tính (90×3.500=315.000đ là đúng), hẹn lịch kiểm tra đồng hồ để xác minh, đề nghị khách có mặt tại phòng.

**Turn 3** — Khách tỏ thái độ và đòi giảm tiền.
> "Tôi yêu cầu tháng này giảm tiền phòng vì phòng tôi ồn quá, không ngủ được, ảnh hưởng sức khoẻ. Mà sao tôi báo ổ cắm điện cả tháng rồi chưa thấy ai qua sửa? Làm ăn kiểu gì vậy?"

**Hệ thống**: Kiểm tra TKT-0004 (ổ cắm điện, in_progress), báo cáo tiến độ. Về tiếng ồn, tra nội quy giờ yên tĩnh, hứa nhắc nhở nếu có phòng khác gây ồn.

**Turn 4** — Khách dọa sẽ chuyển đi.
> "Nếu không giải quyết được thì tôi đi. Hợp đồng hết tháng 7 này tôi không ở nữa. Mà tiền tháng 5 và tháng 6 tôi chưa đóng, bao lâu thì phải đóng?"

**Hệ thống**: Xác nhận 2 hoá đơn quá hạn (tháng 5 + tháng 6), tổng nợ ~8.900.000đ. Nhắc nhở thanh toán, thông báo policy phí phạt trễ hạn.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_invoice_detail (tenant_id=4, month=6)
- Turn 2: Router → System 2 → schedule meter inspection
- Turn 3: Router → System 2 → get_maintenance_status (TKT-0004) + query_policies
- Turn 4: Router → System 2 → get_invoice_detail + get_payment_history
### Kịch bản test
- File test: `existing_04_test.py`




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:30:00*

**Turn 1**
- **Câu hỏi**: "Sao tháng này tiền điện lên tới 90 kWh mà tính 315.000đ? Hồi tháng trước cũng 90 kWh mà có 315.000đ thôi. Rồi tiền nước 6 khối tính 600.000đ nữa. Tổng cộng hoá đơn tháng 6 của tôi là bao nhiêu? Sao thấy cao quá vậy? Tôi dùng có khác gì đâu, có phải đọc nhầm đồng hồ không?"
- **Câu trả lời của AI**: Chào chị Lan,

Em đã kiểm tra chi tiết hóa đơn tháng 06/2026 của phòng 301. Tổng số tiền chị cần thanh toán là **4.465.000đ**.

Dưới đây là bảng kê chi tiết:
*   **Tiền phòng:** 3.500.000đ
*   **Tiền điện (90 kWh):** 315.000đ (Đơn giá: 3.500đ/kWh)
*   **Tiền nước (6 m³):** 600.000đ (Đơn giá: 100.000đ/m³)
*   **Phí dịch vụ:** 50.000đ

Về thắc mắc của chị:
1.  **Tiền điện:** Với 90 kWh, mức phí 315.000đ là hoàn toàn chính xác theo quy định (90 x 3.500đ = 315.000đ).
2.  **Tiền nước:** Đơn giá nước hiện tại là 100.000đ/m³. Với 6 khối nước, tổng tiền là 600.000đ.

Chị vui lòng lưu ý hóa đơn này đã đến hạn thanh toán từ ngày 05/06/2026. Nếu chị cảm thấy chỉ số điện/nước có sự sai lệch so với thực tế sử dụng, chị có thể yêu cầu kiểm tra lại đồng hồ. Chị có muốn em tạo phiếu yêu cầu kỹ thuật kiểm tra đồng hồ cho chị không ạ?

**Turn 2**
- **Câu hỏi**: "Tôi không tin. Tháng nào cũng 90 kWh mà sao lúc nào cũng 315.000đ hết vậy? Tính nhầm hay sao. Tôi yêu cầu có người qua kiểm tra đồng hồ điện nước, tôi muốn xem tận mắt. Bao giờ thì qua?"
- **Câu trả lời của AI**: Chào chị Lan,

Em đã kiểm tra hóa đơn tháng 06/2026 của phòng 301. Theo hệ thống, tiền điện của chị là 315.000đ cho 90 kWh (đơn giá 3.500đ/kWh).

Để giải quyết thắc mắc của chị, em đã ghi nhận yêu cầu kiểm tra đồng hồ điện nước vào hệ thống với mức độ ưu tiên cao:
- **Mã phiếu:** TKT-2026-BDF27D
- **Nội dung:** Kiểm tra đồng hồ điện nước, khách muốn trực tiếp giám sát.
- **Thời gian xử lý dự kiến:** Trong vòng 24-48 giờ tới.

Thợ kỹ thuật sẽ liên hệ trực tiếp với chị để hẹn thời gian qua kiểm tra. Chị vui lòng giữ điện thoại để nhận thông báo từ thợ nhé.

**Turn 3**
- **Câu hỏi**: "Tôi yêu cầu tháng này giảm tiền phòng vì phòng tôi ồn quá, không ngủ được, ảnh hưởng sức khoẻ. Mà sao tôi báo ổ cắm điện cả tháng rồi chưa thấy ai qua sửa? Làm ăn kiểu gì vậy?"
- **Câu trả lời của AI**: Chào chị Lan, em rất xin lỗi về sự bất tiện chị đang gặp phải.

Về vấn đề của chị, em xin phản hồi như sau:

1. **Về yêu cầu sửa ổ cắm điện:** Em đã ghi nhận sự việc và sẽ kiểm tra lại ngay với đội ngũ kỹ thuật tại sao yêu cầu của chị chưa được xử lý. Em sẽ đốc thúc thợ qua kiểm tra và khắc phục cho chị trong hôm nay.

2. **Về yêu cầu giảm tiền phòng do tiếng ồn:** Theo nội quy nhà trọ, các hành vi gây ồn sau 22:00 là vi phạm quy định. Tuy nhiên, trong chính sách hiện tại không có điều khoản quy định về việc giảm tiền thuê phòng do tiếng ồn. Em sẽ ghi nhận khiếu nại này của chị và báo cáo lên Ban quản lý để xem xét giải quyết trường hợp của chị một cách thỏa đáng nhất.

Chị vui lòng cho em biết số phòng cụ thể để em kiểm tra lại tình trạng phiếu bảo trì của chị nhé.

**Turn 4**
- **Câu hỏi**: "Nếu không giải quyết được thì tôi đi. Hợp đồng hết tháng 7 này tôi không ở nữa. Mà tiền tháng 5 và tháng 6 tôi chưa đóng, bao lâu thì phải đóng?"
- **Câu trả lời của AI**: Chào chị Lan, em rất tiếc khi biết chị có ý định chuyển đi.

Về các thắc mắc của chị, em xin phản hồi như sau:

1.  **Về thời hạn thanh toán:** Theo quy định của tòa nhà, tiền thuê phòng hàng tháng phải được thanh toán **trước ngày 05 của tháng đó**. Hiện tại, chị đang nợ tiền tháng 5 và tháng 6, vì vậy chị vui lòng hoàn tất thanh toán các khoản này sớm nhất có thể để tránh phát sinh phí phạt trễ hạn.
2.  **Về việc chấm dứt hợp đồng:** Hợp đồng của chị tại phòng 301 có thời hạn đến ngày **10/07/2026**. Theo quy định, nếu chị muốn chấm dứt hợp đồng, chị cần báo trước ít nhất **30 ngày** và đảm bảo đã thanh toán đầy đủ các khoản phí đến ngày bàn giao phòng.

Vì chị đang có những phản hồi chưa hài lòng về dịch vụ (tiếng ồn, bảo trì), em rất mong có cơ hội được trao đổi trực tiếp hoặc hỗ trợ chị giải quyết dứt điểm các vấn đề này trước khi chị đưa ra quyết định cuối cùng.

Chị có cần em hỗ trợ kiểm tra chi tiết số tiền còn nợ của tháng 5 và tháng 6 không ạ?

