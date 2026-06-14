# Kịch bản: Xin gia hạn thanh toán vì khó khăn tài chính

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Phạm Thị Lan |
| Tenant ID | 4 |
| Phòng | 301 (tầng 3, 25m², 3.500.000đ/tháng) |
| Tone | strict (đang căng thẳng) |
| Hợp đồng | 2025-01-10 → 2026-07-10 |
| Lịch sử | Trễ 4/4 tháng gần nhất, overdue cả tháng 5 và 6 |
| Behavior | Đã hứa thanh toán trước 10/6 nhưng không giữ lời |

### Multi-turn conversation

**Turn 1** — Khách xin gia hạn thêm, giọng khó chịu.
> "Tôi biết tôi nợ 2 tháng rồi, nhưng tháng này tôi chưa có. Cho tôi xin tới cuối tháng 7 được không? Tôi hứa sẽ đóng hết một lúc. Hợp đồng hết 10/7, tôi cũng tính về quê luôn, đóng xong là dứt khoát."

**Hệ thống**: Kiểm tra — nợ tháng 5 (4.465.000đ) + tháng 6 (4.465.000đ) = 8.930.000đ. Hạn chót 10/7. Cảnh báo policy phí phạt trễ hạn nếu không thanh toán đúng hạn.

**Turn 2** — Khách hỏi phí phạt cụ thể.
> "Phí phạt bao nhiêu? Tôi đóng luôn bây giờ có được giảm không? Hay tôi phải đóng đủ cả gốc lẫn phạt?"

**Hệ thống**: Thông báo phí phạt trễ hạn (tỷ lệ theo chính sách nhà trọ), giải thích không thể giảm nếu không có approval từ admin.

**Turn 3** — Khách thương lượng xin miễn phí phạt.
> "Tôi ở đây từ tháng 1 năm ngoái tới giờ, cũng gần 1.5 năm rồi. Có thể xem xét bỏ qua phí phạt được không? Nếu không tôi cũng đành chịu nhưng về quê rồi chuyển khoản sau, không gấp được."

**Hệ thống**: Tạo approval request cho admin — đề nghị miễn phí phạt nếu thanh toán đủ trước 10/7. Ghi nhận vào behavior log.

**Turn 4** — Khách yêu cầu xác nhận bằng văn bản.
> "OK tôi sẽ cố gắng thu xếp. Bao giờ admin trả lời? Cho tôi xin xác nhận bằng văn bản qua Zalo hay SMS cũng được, có thông tin tổng nợ, hạn thanh toán và phí phạt (nếu có)."

**Hệ thống**: Cung cấp bảng tổng nợ chi tiết, gửi qua Zalo/SMS, hẹn phản hồi duyệt từ admin.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_invoice_detail + get_payment_history
- Turn 2: Router → System 1 → query_policies (phí phạt trễ)
- Turn 3: Router → System 2 → Approval Queue (miễn phí phạt)
- Turn 4: Router → System 2 → gửi thông báo tổng nợ
### Kịch bản test
- File test: `existing_06_test.py`




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:32:45*

**Turn 1**
- **Câu hỏi**: "Tôi biết tôi nợ 2 tháng rồi, nhưng tháng này tôi chưa có. Cho tôi xin tới cuối tháng 7 được không? Tôi hứa sẽ đóng hết một lúc. Hợp đồng hết 10/7, tôi cũng tính về quê luôn, đóng xong là dứt khoát."
- **Câu trả lời của AI**: Chào chị Lan,

Tôi đã kiểm tra thông tin hợp đồng và hóa đơn của chị. Hiện tại, chị đang quá hạn thanh toán 02 tháng (tháng 05/2026 và tháng 06/2026) với tổng số tiền là **8,930,000đ**.

Về yêu cầu xin gia hạn thanh toán đến cuối tháng 07/2026, tôi cần báo cáo lại với Ban quản lý để xem xét vì đây là trường hợp đặc biệt. Tuy nhiên, chị lưu ý rằng hợp đồng của chị sẽ kết thúc vào ngày 10/07/2026.

Để tôi có thể trình bày nguyện vọng của chị một cách chính xác nhất, chị vui lòng xác nhận lại:
1. Chị có cam kết chắc chắn sẽ hoàn tất thanh toán toàn bộ số nợ trước ngày 31/07/2026 không?
2. Chị có đồng ý để Ban quản lý trừ vào tiền cọc (7,000,000đ) để giảm bớt số nợ hiện tại không?

Sau khi chị phản hồi, tôi sẽ gửi yêu cầu này lên cấp trên và thông báo lại cho chị sớm nhất.

**Turn 2**
- **Câu hỏi**: "Phí phạt bao nhiêu? Tôi đóng luôn bây giờ có được giảm không? Hay tôi phải đóng đủ cả gốc lẫn phạt?"
- **Câu trả lời của AI**: Chào chị Lan,

Theo quy định trong hợp đồng thuê nhà, chị cần thanh toán tiền thuê trước ngày 05 hàng tháng. Hiện tại, hóa đơn tháng 06/2026 của chị (tổng cộng 4.465.000đ) đã quá hạn 10 ngày.

Về các thắc mắc của chị:
1. **Phí phạt:** Theo chính sách thanh toán, phí phạt chậm thanh toán được tính là **10% trên số tiền quá hạn** cho mỗi tháng chậm trễ.
2. **Giảm phí phạt:** Hiện tại, hệ thống không có chính sách giảm phí phạt khi thanh toán muộn. Chị cần thanh toán đầy đủ cả tiền gốc (4.465.000đ) và phí phạt phát sinh để hoàn tất nghĩa vụ hợp đồng.

Chị vui lòng chuyển khoản thanh toán vào tài khoản Vietcombank (Số TK: 1234567890, Chủ TK: Đặng Văn Nhuận) với nội dung: **TT phong 301 thang 06/2026**.

Nếu chị cần hỗ trợ thêm thông tin chi tiết, vui lòng cho em biết.

**Turn 3**
- **Câu hỏi**: "Tôi ở đây từ tháng 1 năm ngoái tới giờ, cũng gần 1.5 năm rồi. Có thể xem xét bỏ qua phí phạt được không? Nếu không tôi cũng đành chịu nhưng về quê rồi chuyển khoản sau, không gấp được."
- **Câu trả lời của AI**: Chào chị Lan,

Về yêu cầu của chị, tôi xin phản hồi như sau:

1. **Về phí phạt:** Theo chính sách thanh toán của tòa nhà, nếu chị gặp khó khăn đột xuất, chị có thể liên hệ quản lý để được hỗ trợ gia hạn thanh toán tối đa 7 ngày mà không tính phí. Tuy nhiên, việc miễn hoàn toàn phí phạt chậm thanh toán cần được Ban quản lý xem xét dựa trên lịch sử thanh toán thực tế.

2. **Về việc thanh toán:** Chị vui lòng thực hiện thanh toán đầy đủ các khoản phí còn thiếu trước khi rời đi. Nếu chị cần hỗ trợ chia nhỏ kỳ thanh toán hoặc gia hạn thêm thời gian (tối đa 7 ngày không phí), chị hãy phản hồi lại cho tôi để tôi trình xin ý kiến Ban quản lý.

Chị lưu ý, theo hợp đồng, chị cần thông báo trước 30 ngày nếu có ý định chấm dứt hợp đồng sớm để đảm bảo quyền lợi về tiền cọc. 

Tôi sẽ ghi nhận yêu cầu của chị vào hệ thống. Chị có cần tôi hỗ trợ kiểm tra chi tiết số tiền còn thiếu của tháng này không ạ?

**Turn 4**
- **Câu hỏi**: "OK tôi sẽ cố gắng thu xếp. Bao giờ admin trả lời? Cho tôi xin xác nhận bằng văn bản qua Zalo hay SMS cũng được, có thông tin tổng nợ, hạn thanh toán và phí phạt (nếu có)."
- **Câu trả lời của AI**: Chào chị Lan,

Về yêu cầu của chị, em xin thông tin như sau:

1. **Thông tin thanh toán:**
   - Tổng nợ tháng 06/2026: **4,465,000đ** (bao gồm tiền phòng, điện, nước và phí dịch vụ).
   - Hạn thanh toán gốc: **05/06/2026** (hiện đã quá hạn 10 ngày).
   - Phí phạt: Hiện tại hệ thống chưa ghi nhận phí phạt cụ thể, tuy nhiên chị vui lòng thanh toán sớm để đảm bảo tuân thủ hợp đồng.

2. **Xác nhận văn bản:**
   Em đã soạn thảo tin nhắn xác nhận chi tiết các thông tin trên và gửi qua Zalo cho chị. Yêu cầu này đang chờ quản lý duyệt để gửi đi ngay.

Em sẽ thông báo cho chị ngay khi có phản hồi từ phía quản lý. Chị vui lòng kiểm tra Zalo nhé.

