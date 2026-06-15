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
*Chạy lúc: 2026-06-15 09:08:14*

**Turn 1**
- **Câu hỏi**: "Sao tháng này tiền điện lên tới 90 kWh mà tính 315.000đ? Hồi tháng trước cũng 90 kWh mà có 315.000đ thôi. Rồi tiền nước 6 khối tính 600.000đ nữa. Tổng cộng hoá đơn tháng 6 của tôi là bao nhiêu? Sao thấy cao quá vậy? Tôi dùng có khác gì đâu, có phải đọc nhầm đồng hồ không?"
- **Câu trả lời của AI**: Chào chị Lan,

Em đã kiểm tra chi tiết hóa đơn tháng 06/2026 của phòng 301. Tổng số tiền chị cần thanh toán là **4.465.000đ**.

Chi tiết các khoản phí như sau:
*   Tiền phòng: 3.500.000đ
*   Tiền điện (90 kWh): 315.000đ
*   Tiền nước (6 m³): 600.000đ
*   Phí dịch vụ: 50.000đ

Về thắc mắc của chị đối với tiền nước, theo quy định hiện hành, giá nước đang được áp dụng là 100.000đ/m³. Vì vậy, 6 khối nước có tổng chi phí là 600.000đ là chính xác theo đơn giá.

Về vấn đề tiền điện, đơn giá hiện tại là 3.500đ/kWh. Với 90 kWh, tổng tiền điện là 315.000đ, mức này tương đương với tháng trước như chị đã nêu.

Hiện tại hóa đơn tháng 6 của chị đã **quá hạn thanh toán từ ngày 05/06/2026**. Chị vui lòng sắp xếp thanh toán sớm để tránh các phát sinh không đáng có. Nếu chị vẫn nghi ngờ về chỉ số đồng hồ nước, em sẽ ghi nhận và báo bộ phận kỹ thuật kiểm tra lại đồng hồ cho chị ngay. Chị có muốn em tạo phiếu kiểm tra đồng hồ nước không ạ?

**Turn 2**
- **Câu hỏi**: "Tôi không tin. Tháng nào cũng 90 kWh mà sao lúc nào cũng 315.000đ hết vậy? Tính nhầm hay sao. Tôi yêu cầu có người qua kiểm tra đồng hồ điện nước, tôi muốn xem tận mắt. Bao giờ thì qua?"
- **Câu trả lời của AI**: Chào chị Lan,

Về thắc mắc của chị, em xin giải đáp như sau:

1. **Chi tiết hóa đơn tháng 06/2026**: Theo hệ thống, tiền điện của chị được tính dựa trên 90 kWh với đơn giá 3.500đ/kWh (tổng 315.000đ). Đây là mức giá điện theo quy định đã được niêm yết.

2. **Yêu cầu kiểm tra**: Em đã ghi nhận yêu cầu của chị và tạo phiếu bảo trì khẩn cấp (Mã phiếu: **TKT-2026-9BA7B9**) để kỹ thuật viên qua kiểm tra trực tiếp đồng hồ điện nước cho chị.

3. **Thời gian xử lý**: Thời gian xử lý dự kiến là trong vòng 24-48 giờ tới. Kỹ thuật viên sẽ liên hệ trực tiếp với chị để hẹn thời gian chị có mặt tại phòng để cùng kiểm tra.

Em rất xin lỗi vì sự bất tiện này. Chị vui lòng lưu ý giúp em, hiện tại hóa đơn tháng 06/2026 của chị đã quá hạn thanh toán 4 ngày, chị sắp xếp thanh toán sớm giúp em nhé.

**Turn 3**
- **Câu hỏi**: "Tôi yêu cầu tháng này giảm tiền phòng vì phòng tôi ồn quá, không ngủ được, ảnh hưởng sức khoẻ. Mà sao tôi báo ổ cắm điện cả tháng rồi chưa thấy ai qua sửa? Làm ăn kiểu gì vậy?"
- **Câu trả lời của AI**: Hệ thống đang xử lý yêu cầu phức tạp. Vui lòng liên hệ trực tiếp quản lý qua số ${LANDLORD_PHONE:-0901.234.567} để được hỗ trợ nhanh nhất.

**Turn 4**
- **Câu hỏi**: "Nếu không giải quyết được thì tôi đi. Hợp đồng hết tháng 7 này tôi không ở nữa. Mà tiền tháng 5 và tháng 6 tôi chưa đóng, bao lâu thì phải đóng?"
- **Câu trả lời của AI**: Chào chị Lan,

Về các vấn đề chị nêu, em xin phản hồi dựa trên quy định của tòa nhà như sau:

**1. Về việc thanh toán tiền thuê:**
Theo quy định, tiền thuê nhà phải được thanh toán trước ngày **05 hàng tháng**. Hiện tại, chị đang nợ tiền tháng 5 và tháng 6, tức là đã quá hạn thanh toán.
*   **Phí phạt:** Theo chính sách, nếu trễ từ 4-7 ngày, chị sẽ chịu phí phạt 50.000đ. Nếu trễ từ 8-14 ngày, phí là 100.000đ.
*   **Hỗ trợ:** Nếu chị đang gặp khó khăn tài chính đột xuất, chị vui lòng liên hệ trực tiếp với em để làm thủ tục gia hạn thanh toán (tối đa 7 ngày không phí) hoặc chia nhỏ kỳ thanh toán (có phí 50.000đ/lần).

**2. Về việc chấm dứt hợp đồng:**
Hợp đồng của chị tại phòng 301 sẽ hết hạn vào ngày **10/07/2026**.
*   Nếu chị quyết định không gia hạn và chuyển đi khi hợp đồng hết hạn, chị cần thông báo cho Ban quản lý trước ít nhất **30 ngày** (tức là trước ngày 10/06/2026).
*   Vì hiện tại đã qua thời điểm thông báo 30 ngày, chị vui lòng liên hệ trực tiếp với em để em báo cáo quản lý về trường hợp của chị, nhằm đảm bảo các thủ tục bàn giao phòng và tất toán tiền cọc được thực hiện đúng quy định.

Em rất mong chị sớm phản hồi để chúng ta có thể giải quyết dứt điểm các vấn đề trên.

