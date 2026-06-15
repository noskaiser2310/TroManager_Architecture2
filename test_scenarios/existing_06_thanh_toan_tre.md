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
*Chạy lúc: 2026-06-15 09:10:30*

**Turn 1**
- **Câu hỏi**: "Tôi biết tôi nợ 2 tháng rồi, nhưng tháng này tôi chưa có. Cho tôi xin tới cuối tháng 7 được không? Tôi hứa sẽ đóng hết một lúc. Hợp đồng hết 10/7, tôi cũng tính về quê luôn, đóng xong là dứt khoát."
- **Câu trả lời của AI**: Chào chị Lan,

Tôi đã kiểm tra thông tin hợp đồng và tình trạng thanh toán của chị. Hiện tại, chị đang quá hạn thanh toán hóa đơn tháng 06/2026 với tổng số tiền là 4.465.000đ.

Về yêu cầu gia hạn thời gian đóng tiền đến cuối tháng 07/2026 và việc chị dự định kết thúc hợp đồng vào ngày 10/07/2026, tôi không có thẩm quyền tự quyết định thay đổi thời hạn thanh toán.

Tôi sẽ ghi nhận yêu cầu này và chuyển tiếp đến Ban quản lý để họ xem xét. Sau khi có phản hồi chính thức, tôi sẽ thông báo lại cho chị ngay.

Trong thời gian chờ đợi, chị vui lòng lưu ý rằng hợp đồng của chị sẽ kết thúc vào ngày 10/07/2026. Nếu chị có kế hoạch chuyển đi, chị cần thực hiện các thủ tục bàn giao phòng theo đúng quy định. Tôi sẽ tra cứu thêm về chính sách bàn giao phòng để hướng dẫn chị chi tiết hơn nếu chị cần.

**Turn 2**
- **Câu hỏi**: "Phí phạt bao nhiêu? Tôi đóng luôn bây giờ có được giảm không? Hay tôi phải đóng đủ cả gốc lẫn phạt?"
- **Câu trả lời của AI**: Chào chị Lan,

Theo quy định về thanh toán của tòa nhà, mức phí phạt trễ hạn được áp dụng như sau:

*   **Trễ 1-3 ngày:** Nhắc nhở qua Zalo.
*   **Trễ 4-7 ngày:** Phí phạt 50.000đ.
*   **Trễ 8-14 ngày:** Phí phạt 100.000đ và cảnh cáo.

Vì chị đang trễ 4 ngày, mức phí phạt hiện tại là **50.000đ**.

Về yêu cầu giảm phí, chính sách của tòa nhà không có điều khoản giảm phí phạt khi thanh toán ngay. Chị vui lòng thanh toán đủ cả tiền gốc và phí phạt theo quy định. Nếu chị gặp khó khăn đột xuất, chị có thể liên hệ trực tiếp với Ban quản lý để được hỗ trợ xem xét các phương án gia hạn thanh toán theo quy định (gia hạn tối đa 7 ngày không phí hoặc chia nhỏ kỳ thanh toán).

Chị có muốn em hỗ trợ tạo yêu cầu gửi Ban quản lý để trình bày về trường hợp của mình không ạ?

**Turn 3**
- **Câu hỏi**: "Tôi ở đây từ tháng 1 năm ngoái tới giờ, cũng gần 1.5 năm rồi. Có thể xem xét bỏ qua phí phạt được không? Nếu không tôi cũng đành chịu nhưng về quê rồi chuyển khoản sau, không gấp được."
- **Câu trả lời của AI**: Chào chị Lan,

Về yêu cầu của chị, em xin phản hồi như sau:

1. **Về phí phạt:** Theo quy định của tòa nhà, phí phạt trễ hạn từ 4-7 ngày là 50.000đ. Tuy nhiên, ghi nhận chị đã gắn bó với tòa nhà hơn 1 năm, em sẽ báo cáo lại với Ban quản lý để xem xét trường hợp của chị. Em sẽ thông báo lại kết quả cho chị sớm nhất có thể.
2. **Về việc thanh toán:** Chị có thể yên tâm về quê. Chị vui lòng thực hiện chuyển khoản ngay khi có thể để hoàn tất nghĩa vụ hợp đồng.

Hiện tại hợp đồng của chị sẽ hết hạn vào ngày **10/07/2026**. Nếu chị có dự định gia hạn hoặc cần hỗ trợ thêm về thủ tục, chị vui lòng cho em biết nhé.

**Turn 4**
- **Câu hỏi**: "OK tôi sẽ cố gắng thu xếp. Bao giờ admin trả lời? Cho tôi xin xác nhận bằng văn bản qua Zalo hay SMS cũng được, có thông tin tổng nợ, hạn thanh toán và phí phạt (nếu có)."
- **Câu trả lời của AI**: Chào chị Lan, em đã kiểm tra thông tin hóa đơn tháng 06/2026 của chị như sau:

*   **Tổng nợ:** 4,465,000 VNĐ.
*   **Hạn thanh toán:** 2026-06-05 (đã quá hạn 10 ngày).
*   **Phí phạt:** Theo quy định, do chị đã trễ hạn từ 8-14 ngày, phí phạt là 100,000 VNĐ.

Tổng số tiền chị cần thanh toán là **4,565,000 VNĐ**.

Về yêu cầu xác nhận bằng văn bản, em sẽ gửi nội dung này qua Zalo cho chị ngay bây giờ để chị tiện theo dõi. Chị vui lòng thu xếp thanh toán sớm để tránh phát sinh thêm phí phạt hoặc ảnh hưởng đến hợp đồng nhé.

