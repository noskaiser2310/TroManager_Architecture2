# Kịch bản: Xác nhận thanh toán trong app

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Phạm Thị Lan |
| Tenant ID | 4 |
| Phòng | 301 (tầng 3, 25m², 3.500.000đ/tháng) |
| Tone | strict |
| Hợp đồng | 2025-01-10 → 2026-07-10 |
| Lịch sử | Nợ tháng 5 và 6, đã chuyển khoản trả nợ |
| Nhu cầu | Xác nhận thanh toán và nhận biên nhận trong app |

### Multi-turn conversation

**Turn 1** — Khách báo đã chuyển khoản và muốn kiểm tra ngay trong app.
> "Tôi đã chuyển 8.930.000đ trả nợ 2 tháng rồi. Anh kiểm tra giúp tôi xem đã nhận được chưa. Cho tôi xác nhận luôn trong app, khỏi gửi SMS hay Zalo gì hết."

**Hệ thống**: Kiểm tra invoice tháng 5 và 6, xác nhận giao dịch. Trả kết quả trong app.

**Turn 2** — Khách muốn xem chi tiết số tiền khớp chưa.
> "Tôi chuyển đúng 8.930.000đ — 4.465.000đ tháng 5 + 4.465.000đ tháng 6. Khớp không? Cho tôi xem chi tiết từng tháng trong app."

**Hệ thống**: Tra cứu chi tiết hóa đơn tháng 5 và 6. Xác nhận đã khớp.

**Turn 3** — Khách muốn biết còn nợ gì khác không.
> "Đã hết nợ chưa? Tôi còn phải đóng thêm gì nữa không? Cho tôi xem tổng kết trong app."

**Hệ thống**: Kiểm tra tổng nợ hiện tại, thông báo đã hết nợ (hoặc còn nếu có).

**Turn 4** — Khách hỏi thủ tục bàn giao phòng vì sắp hết hợp đồng.
> "Hợp đồng hết 10/7, tôi tính về quê. Cho tôi hỏi thủ tục bàn giao phòng luôn. Mấy giờ làm việc để ra văn phòng?"

**Hệ thống**: Tra cứu policy về trả phòng, giờ làm việc. Cung cấp thông tin trong app.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_invoice_detail + get_payment_history
- Turn 2: Router → System 2 → get_invoice_detail (tháng 5 + tháng 6)
- Turn 3: Router → System 2 → get_payment_history (kiểm tra tổng nợ)
- Turn 4: Router → System 1 → query_policies (trả phòng, giờ làm việc)
### Kịch bản test
- File test: `existing_15_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:21:53*

**Turn 1**
- **Câu hỏi**: "Tôi đã chuyển 8.930.000đ trả nợ 2 tháng rồi. Anh kiểm tra giúp tôi xem đã nhận được chưa. Cho tôi xác nhận luôn trong app, khỏi gửi SMS hay Zalo gì hết."
- **Câu trả lời của AI**: Chào chị Lan,

Dựa trên hệ thống quản lý tài chính, hiện tại tôi chưa ghi nhận khoản thanh toán 8.930.000đ cho hai tháng 05/2026 và 06/2026 của chị.

Để tôi có thể hỗ trợ kiểm tra chính xác, chị vui lòng cung cấp ảnh chụp màn hình giao dịch chuyển khoản thành công (có hiển thị mã giao dịch/biên lai) để tôi đối chiếu với bộ phận kế toán.

Đúng như yêu cầu của chị, tôi sẽ xác nhận trực tiếp tại đây ngay khi nhận được thông tin từ chị và xác minh thành công.

**Turn 2**
- **Câu hỏi**: "Tôi chuyển đúng 8.930.000đ — 4.465.000đ tháng 5 + 4.465.000đ tháng 6. Khớp không? Cho tôi xem chi tiết từng tháng trong app."
- **Câu trả lời của AI**: Chào chị Lan,

Em đã kiểm tra chi tiết hóa đơn tháng 05/2026 và 06/2026 của phòng 301 như sau:

**1. Chi tiết hóa đơn:**
*   **Tháng 05/2026:** 4.465.000đ (Tiền phòng 3.500.000đ + Điện 315.000đ + Nước 600.000đ + Dịch vụ 50.000đ).
*   **Tháng 06/2026:** 4.465.000đ (Tiền phòng 3.500.000đ + Điện 315.000đ + Nước 600.000đ + Dịch vụ 50.000đ).
*   **Tổng cộng:** 8.930.000đ.

Số tiền chị chuyển hoàn toàn khớp với tổng hóa đơn của hai tháng này.

**2. Lưu ý về trạng thái:**
Hiện tại, hệ thống vẫn ghi nhận cả hai hóa đơn này ở trạng thái **"Quá hạn"**. Có thể do giao dịch của chị cần thời gian để ngân hàng đối soát hoặc cập nhật vào hệ thống quản lý.

Chị vui lòng cung cấp giúp em **ảnh chụp màn hình giao dịch chuyển khoản** để em xác nhận và cập nhật trạng thái thanh toán cho chị ngay nhé.

**Turn 3**
- **Câu hỏi**: "Đã hết nợ chưa? Tôi còn phải đóng thêm gì nữa không? Cho tôi xem tổng kết trong app."
- **Câu trả lời của AI**: Chào chị Lan,

Em xin thông tin chi tiết về tình trạng thanh toán của chị như sau:

Hiện tại, chị vẫn còn nợ tiền thuê phòng của **2 tháng** gần nhất, tổng cộng là **8,930,000đ**:

1.  **Tháng 05/2026:** 4,465,000đ (Đã quá hạn)
2.  **Tháng 06/2026:** 4,465,000đ (Hạn thanh toán: 2026-06-05, hiện đã quá hạn 10 ngày)

**Chi tiết hóa đơn tháng 06/2026:**
*   Tiền phòng: 3,500,000đ
*   Tiền điện (90 kWh): 315,000đ
*   Tiền nước (6 m³): 600,000đ
*   Phí dịch vụ: 50,000đ
*   **Tổng cộng:** 4,465,000đ

Chị vui lòng thanh toán sớm các khoản nợ này để tránh bị tính phí phạt trễ hạn theo quy định của nhà trọ ạ. Nếu chị cần hỗ trợ phương thức thanh toán, hãy cho em biết nhé.

**Turn 4**
- **Câu hỏi**: "Hợp đồng hết 10/7, tôi tính về quê. Cho tôi hỏi thủ tục bàn giao phòng luôn. Mấy giờ làm việc để ra văn phòng?"
- **Câu trả lời của AI**: Chào chị Lan, về việc chị dự định trả phòng vào ngày 10/7, em xin thông tin đến chị quy trình bàn giao như sau:

**1. Thủ tục bàn giao phòng:**
Theo quy định, chị cần thực hiện các bước sau:
*   **Báo trước:** Chị cần báo trước ít nhất 30 ngày (nếu chưa báo, chị vui lòng xác nhận lại với em ngay để em cập nhật hệ thống).
*   **Thanh toán:** Chị cần thanh toán đầy đủ tiền phòng, điện, nước và các chi phí phát sinh đến ngày trả phòng.
*   **Vệ sinh phòng:** Chị vui lòng dọn dẹp phòng sạch sẽ, trả lại tình trạng ban đầu, giặt ga trải giường/khăn tắm (nếu có) và đảm bảo không còn rác trong phòng.
*   **Kiểm tra:** Sau khi chị dọn dẹp xong, quản lý sẽ qua kiểm tra trực tiếp cùng chị để chốt bàn giao.

**2. Giờ làm việc:**
Hiện tại, các thông tin về giờ làm việc hành chính cụ thể tại văn phòng không được quy định chi tiết trong nội quy, tuy nhiên chị có thể liên hệ trực tiếp với em qua Zalo này để đặt lịch hẹn cụ thể. Em sẽ sắp xếp thời gian để hỗ trợ chị làm thủ tục bàn giao nhanh chóng nhất.

Chị cần em hỗ trợ thêm thông tin gì khác không ạ?

