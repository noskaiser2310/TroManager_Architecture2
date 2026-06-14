# Kịch bản: Gia hạn hợp đồng và thương lượng giá

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Đỗ Văn Hùng |
| Tenant ID | 5 |
| Phòng | 302 (tầng 3, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2024-09-01 → 2026-09-01 |
| Lịch sử | Thanh toán luôn đúng hạn, chưa từng trễ |
| Ticket | TKT-0008 (công tơ điện, resolved), TKT-0009 (bàn làm việc ọp ẹp, open) |
| Ghi chú | Khách mẫu mực, có kế hoạch, đề xuất gia hạn từ sớm |

### Multi-turn conversation

**Turn 1** — Khách hỏi hạn hợp đồng và muốn thương lượng gia hạn.
> "Chào anh, hợp đồng của em ở phòng 302 sắp hết hạn vào tháng 9 này. Em muốn ở tiếp nhưng muốn hỏi bên mình có chính sách ưu đãi cho khách ở lâu như em không? Em ở đây gần 2 năm rồi, chưa từng đóng trễ ngày nào."

**Hệ thống**: Kiểm tra hợp đồng — active, hết hạn 2026-09-01. Ghi nhận lịch sử thanh toán tốt. Thông báo chính sách ưu đãi cho khách giữ phòng (composite score tốt).

**Turn 2** — Khách hỏi cụ thể giảm giá.
> "Anh xem bên mình có thể giảm cho em 200-300k/tháng được không? Nếu ok em ký tiếp 12 tháng luôn, không cần đắn đo. Với cho em hỏi nếu em đóng 6 tháng một lần có được giảm thêm không?"

**Hệ thống**: Tra policy, tạo approval request cho admin duyệt giảm giá. Trả lời tạm thời đang chờ duyệt từ chủ nhà.

**Turn 3** — Khách hỏi thêm về điều khoản gia hạn.
> "Nếu ký tiếp thì em có phải đóng cọc lại không? Các điều khoản khác giữ nguyên hay có gì thay đổi? Em cũng muốn sửa lại cái bàn làm việc đang ọp ẹp trong phòng (em báo lâu rồi mà chưa thấy ai qua)."

**Hệ thống**: Giải thích chính sách gia hạn — không cần cọc lại. Cập nhật ticket TKT-0009 (bàn làm việc) lên priority cao hơn.

**Turn 4** — Khách quyết định chờ duyệt.
> "OK vậy em chờ admin duyệt giảm giá. Khoảng bao lâu có kết quả? Và nếu được giảm thì em ký hợp đồng mới từ 1/9 luôn nhé."

**Hệ thống**: Thông báo thời gian duyệt dự kiến 3-5 ngày, hẹn phản hồi qua Zalo.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status + recommend_renewal
- Turn 2: Router → System 2 → Approval Queue (giảm giá)
- Turn 3: Router → System 2 → query_policies + update ticket priority
- Turn 4: Router → System 1 → thông báo ETA duyệt
### Kịch bản test
- File test: `existing_03_test.py`




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:28:37*

**Turn 1**
- **Câu hỏi**: "Chào anh, hợp đồng của em ở phòng 302 sắp hết hạn vào tháng 9 này. Em muốn ở tiếp nhưng muốn hỏi bên mình có chính sách ưu đãi cho khách ở lâu như em không? Em ở đây gần 2 năm rồi, chưa từng đóng trễ ngày nào."
- **Câu trả lời của AI**: Chào anh Hùng, rất cảm ơn anh đã tin tưởng và gắn bó với tòa nhà trong suốt gần 2 năm qua.

Về việc gia hạn hợp đồng cho phòng 302, em xin thông tin đến anh các chính sách ưu đãi hiện hành như sau:

Theo quy định gia hạn của tòa nhà, với khách hàng thuê lâu năm và có lịch sử thanh toán tốt như anh, khi anh ký gia hạn hợp đồng mới, anh sẽ được hưởng các ưu đãi dựa trên thời hạn gia hạn như sau:
*   **Gia hạn 6 tháng:** Giữ nguyên giá thuê hiện tại.
*   **Gia hạn 12 tháng:** Giảm 5% tiền phòng.
*   **Gia hạn 24 tháng:** Giảm 10% tiền phòng và miễn phí 1 tháng cọc nếu tái ký.

Vì hợp đồng của anh sẽ hết hạn vào ngày 01/09/2026, anh hoàn toàn đủ điều kiện để thực hiện gia hạn. Để nhận được các ưu đãi này, anh vui lòng nhắn lại cho em thời gian anh dự định gia hạn (6, 12 hay 24 tháng) để em chuẩn bị phụ lục hợp đồng nhé.

Nếu anh cần hỗ trợ thêm thông tin gì, anh cứ nhắn em ạ!

**Turn 2**
- **Câu hỏi**: "Anh xem bên mình có thể giảm cho em 200-300k/tháng được không? Nếu ok em ký tiếp 12 tháng luôn, không cần đắn đo. Với cho em hỏi nếu em đóng 6 tháng một lần có được giảm thêm không?"
- **Câu trả lời của AI**: Chào anh Hùng, về yêu cầu của anh, em xin thông tin cụ thể như sau:

Theo chính sách gia hạn hợp đồng của bên em, khi anh gia hạn hợp đồng với thời hạn 12 tháng, anh sẽ được hưởng ưu đãi **giảm 5% tiền phòng**. Đây là mức ưu đãi cố định áp dụng cho các hợp đồng gia hạn dài hạn thay vì giảm theo số tiền cụ thể như anh đề xuất.

Về việc đóng tiền 6 tháng một lần, chính sách hiện tại của tòa nhà tập trung vào ưu đãi theo thời hạn hợp đồng (như mức giảm 5% cho 12 tháng nêu trên) chứ không có chính sách giảm thêm khi đóng tiền theo kỳ 6 tháng.

Anh xem xét mức ưu đãi giảm 5% cho hợp đồng 12 tháng này có phù hợp với anh không ạ? Nếu anh đồng ý, em sẽ chuẩn bị phụ lục hợp đồng để mình sớm hoàn tất thủ tục nhé.

**Turn 3**
- **Câu hỏi**: "Nếu ký tiếp thì em có phải đóng cọc lại không? Các điều khoản khác giữ nguyên hay có gì thay đổi? Em cũng muốn sửa lại cái bàn làm việc đang ọp ẹp trong phòng (em báo lâu rồi mà chưa thấy ai qua)."
- **Câu trả lời của AI**: Chào anh Hùng, em xin giải đáp các thắc mắc của anh về việc gia hạn hợp đồng như sau:

### 1. Về thủ tục gia hạn và tiền cọc:
Theo chính sách gia hạn của tòa nhà, anh **không cần đóng thêm tiền cọc** nếu hợp đồng hiện tại của anh vẫn đảm bảo các điều kiện (không nợ tiền thuê, không vi phạm nội quy). 

### 2. Về các điều khoản hợp đồng:
*   **Giá thuê:** Khi gia hạn, có thể sẽ có sự điều chỉnh giá mới dựa trên thị trường (thường tăng từ 5-10%). 
*   **Ưu đãi:** Để hỗ trợ anh, tòa nhà có các chương trình ưu đãi khi tái ký:
    *   Gia hạn 6 tháng: Giữ nguyên giá cũ.
    *   Gia hạn 12 tháng: Giảm 5% tiền phòng.
    *   Gia hạn 24 tháng: Giảm 10% tiền phòng + miễn phí 1 tháng cọc.
*   Các điều khoản khác về quyền và nghĩa vụ sẽ được cập nhật trong phụ lục hợp đồng mới khi anh ghé qua ký kết.

### 3. Về bàn làm việc:
Em rất xin lỗi anh vì sự bất tiện này. Em đã kiểm tra và tạo ngay một phiếu yêu cầu sửa chữa mới để ưu tiên xử lý dứt điểm cho anh:
*   **Mã phiếu:** TKT-2026-0AC42B
*   **Trạng thái:** Mới tiếp nhận
*   **Thời gian xử lý dự kiến:** Trong vòng 24-48h tới, thợ kỹ thuật sẽ liên hệ trực tiếp với anh để qua kiểm tra và sửa bàn làm việc nhé.

Anh còn cần em hỗ trợ thêm thông tin gì không ạ?

**Turn 4**
- **Câu hỏi**: "OK vậy em chờ admin duyệt giảm giá. Khoảng bao lâu có kết quả? Và nếu được giảm thì em ký hợp đồng mới từ 1/9 luôn nhé."
- **Câu trả lời của AI**: Chào anh Hùng, về yêu cầu gia hạn và đề xuất giảm giá của anh, em xin phản hồi như sau:

Thông thường, các yêu cầu về chính sách giá sẽ được Ban quản lý xem xét và phản hồi trong vòng **3-5 ngày làm việc**. Em sẽ theo sát tiến độ và báo ngay cho anh khi có kết quả từ bộ phận quản lý nhé.

Nếu đề xuất được thông qua, chúng ta sẽ tiến hành ký phụ lục hợp đồng mới với hiệu lực từ ngày 01/09/2026 như anh mong muốn. Anh cứ yên tâm ạ!

Anh cần hỗ trợ thêm thông tin gì khác không ạ?

