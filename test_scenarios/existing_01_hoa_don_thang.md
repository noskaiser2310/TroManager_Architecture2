# Kịch bản: Tra cứu hoá đơn và thanh toán tháng gần nhất

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Văn Minh |
| Tenant ID | 1 |
| Phòng | 101 (tầng 1, 25m², 3.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-01-15 → 2026-12-31 |
| Lịch sử | Thanh toán luôn đúng hạn (Minh là khách gương mẫu) |
| Tình trạng hoá đơn | Đã thanh toán tháng 5 & 6 |

### Multi-turn conversation

**Turn 1** — Khách muốn kiểm tra hoá đơn tháng này.
> "Anh ơi cho em hỏi tháng này tiền phòng của em hết bao nhiêu vậy ạ? Em muốn kiểm tra lại xem đã đóng đủ chưa, còn hạn chót tới ngày nào?"

**Hệ thống**: Trả về chi tiết hoá đơn tháng 6 — base rent 3.500.000đ, điện 332.500đ (95kWh×3.500đ), nước 500.000đ (5m³×100.000đ), phí dịch vụ 50.000đ. Tổng 4.382.500đ, trạng thái: đã thanh toán.

**Turn 2** — Khách thấy đã thanh toán rồi, hỏi thêm lịch sử.
> "Dạ em thấy tháng này em đóng rồi mà quên mất. Anh cho em xem lịch sử 3 tháng gần nhất được không? Em muốn xem có tháng nào mình quên không ạ."

**Hệ thống**: Truy xuất lịch sử thanh toán 3 tháng (tháng 4-5-6), tất cả đều đã thanh toán đúng hạn. Ghi nhận Minh luôn thanh toán trước hạn 1 ngày.

**Turn 3** — Khách hỏi cách thanh toán cho tháng sau.
> "Dạ vậy tháng sau em chuyển khoản qua Vietcombank như mọi khi được không ạ? Anh cho em xin lại số tài khoản với nội dung chuyển tiền luôn để em lưu lại."

**Hệ thống**: Cung cấp số tài khoản Vietcombank, nội dung chuyển khoản mẫu: "Minh 101 T7".

**Turn 4** — Khách cảm ơn và hỏi thêm.
> "Cảm ơn anh. Mà anh ơi cho em hỏi luôn, nếu em muốn đóng tiền 3 tháng một lần có được không ạ? Hay bắt buộc phải đóng hàng tháng?"

**Hệ thống**: Tra chính sách thanh toán — có thể đóng 3 tháng/lần sau khi đặt cọc đủ.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_invoice_detail (tenant_id=1, month=6)
- Turn 2: Router → System 2 → get_payment_history (tenant_id=1, 3 months)
- Turn 3: Router → System 1 → query_policies (thông tin tài khoản)
- Turn 4: Router → System 2 → query_policies (chính sách đóng nhiều tháng)
### Kịch bản test
- File test: `existing_01_test.py`
- Endpoint: `POST /chat` với `tenant_id=1`
- Session ID cố định qua 4 turns


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:05:06*

**Turn 1**
- **Câu hỏi**: "Anh ơi cho em hỏi tháng này tiền phòng của em hết bao nhiêu vậy ạ? Em muốn kiểm tra lại xem đã đóng đủ chưa, còn hạn chót tới ngày nào?"
- **Câu trả lời của AI**: Dạ chào anh Minh, em đã kiểm tra thông tin hóa đơn tháng 06/2026 của anh như sau ạ:

*   **Tổng tiền phòng tháng 06/2026:** 555,555đ (Bao gồm tiền phòng, điện, nước và phí dịch vụ).
*   **Trạng thái:** Hiện tại hóa đơn này vẫn đang ở trạng thái **Chưa thanh toán**.
*   **Hạn thanh toán:** Hạn gốc là ngày 12/06/2026.

Như trao đổi trước đó, anh đã được chấp thuận gia hạn thêm 5 ngày, nên anh vui lòng hoàn tất thanh toán giúp em trước ngày **17/06/2026** để tránh ảnh hưởng đến lịch sử hợp đồng nhé.

Anh cần em hỗ trợ thêm thông tin gì khác không ạ?

**Turn 2**
- **Câu hỏi**: "Dạ em thấy tháng này em đóng rồi mà quên mất. Anh cho em xem lịch sử 3 tháng gần nhất được không? Em muốn xem có tháng nào mình quên không ạ."
- **Câu trả lời của AI**: Dạ chào anh Minh, em đã kiểm tra lịch sử thanh toán 3 tháng gần nhất của anh trên hệ thống đây ạ:

*   **Tháng 06/2026:** 555,555đ - **Chưa thanh toán** (Hạn thanh toán là 12/06/2026).
*   **Tháng 05/2026:** 4,382,500đ - Đã thanh toán đúng hạn vào ngày 04/05/2026.

Dữ liệu hệ thống cho thấy tháng 05 anh đã thanh toán đầy đủ và đúng hạn. Tuy nhiên, tháng 06 này anh vẫn chưa hoàn tất thanh toán. Như đã trao đổi trước đó, anh đang được gia hạn thêm 5 ngày (tính từ ngày 12/06), nên anh nhớ sắp xếp thanh toán sớm giúp em nhé.

Anh cần em hỗ trợ thêm thông tin gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "Dạ vậy tháng sau em chuyển khoản qua Vietcombank như mọi khi được không ạ? Anh cho em xin lại số tài khoản với nội dung chuyển tiền luôn để em lưu lại."
- **Câu trả lời của AI**: Dạ chào anh Minh, hoàn toàn được ạ. Anh có thể tiếp tục chuyển khoản qua Vietcombank như mọi khi nhé.

Dưới đây là thông tin chi tiết để anh lưu lại ạ:

*   **Ngân hàng:** Vietcombank
*   **Số tài khoản:** 1234567890
*   **Chủ tài khoản:** Đặng Văn Nhuận
*   **Nội dung chuyển khoản:** `TT phong [số phòng] thang [MM/YYYY]`
    *(Ví dụ: TT phong 101 thang 07/2026)*

Anh lưu ý điền đúng nội dung để hệ thống bên em xác nhận thanh toán nhanh chóng cho anh nhé. Anh cần hỗ trợ thêm thông tin gì nữa không ạ?

**Turn 4**
- **Câu hỏi**: "Cảm ơn anh. Mà anh ơi cho em hỏi luôn, nếu em muốn đóng tiền 3 tháng một lần có được không ạ? Hay bắt buộc phải đóng hàng tháng?"
- **Câu trả lời của AI**: Dạ chào anh Minh, cảm ơn anh đã quan tâm ạ.

Dựa trên chính sách thanh toán hiện tại của nhà trọ, quy định về kỳ hạn thanh toán như sau:

*   **Kỳ hạn:** Thanh toán theo **hàng tháng**, hạn chót là ngày **05** của tháng thuê.
*   **Chính sách:** Hiện tại, hệ thống quản lý và hóa đơn của chúng em được thiết lập để vận hành theo chu kỳ đóng tiền hàng tháng để đảm bảo việc ghi chỉ số điện nước và đối soát được chính xác nhất.

Vì vậy, hiện tại nhà trọ chưa áp dụng chính sách đóng tiền gộp 3 tháng một lần anh ạ. Anh vui lòng tiếp tục đóng tiền theo kỳ hàng tháng giúp em nhé.

Nếu anh có khó khăn gì về việc thanh toán hàng tháng, anh cứ trao đổi trực tiếp với em để chúng ta tìm phương án hỗ trợ phù hợp nhất ạ. Anh cần hỗ trợ thêm thông tin gì khác không ạ?

