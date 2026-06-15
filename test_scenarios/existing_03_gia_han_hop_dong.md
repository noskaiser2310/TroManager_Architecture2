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
*Chạy lúc: 2026-06-15 09:07:06*

**Turn 1**
- **Câu hỏi**: "Chào anh, hợp đồng của em ở phòng 302 sắp hết hạn vào tháng 9 này. Em muốn ở tiếp nhưng muốn hỏi bên mình có chính sách ưu đãi cho khách ở lâu như em không? Em ở đây gần 2 năm rồi, chưa từng đóng trễ ngày nào."
- **Câu trả lời của AI**: Chào anh Hùng, em đã kiểm tra thông tin hợp đồng của anh tại phòng 302. Hợp đồng của anh sẽ hết hạn vào ngày 01/09/2026.

Rất cảm ơn anh vì đã luôn tuân thủ tốt các quy định và thanh toán đúng hạn trong suốt thời gian qua. Về chính sách ưu đãi gia hạn, bên em có các mức ưu đãi cụ thể như sau:

*   **Gia hạn 6 tháng:** Giữ nguyên giá thuê cũ.
*   **Gia hạn 12 tháng:** Giảm 5% tiền phòng.
*   **Gia hạn 24 tháng:** Giảm 10% tiền phòng và miễn phí 1 tháng cọc nếu tái ký.

Vì anh đã ở đây gần 2 năm và là khách hàng thân thiết, khi gia hạn, bên em sẽ ưu tiên áp dụng mức điều chỉnh giá tốt nhất cho anh.

Để tiến hành gia hạn, anh chỉ cần phản hồi lại thời hạn anh muốn tiếp tục thuê (6, 12 hay 24 tháng), sau đó chúng ta sẽ sắp xếp thời gian ký phụ lục hợp đồng trước ngày 25/08/2026 (trước 7 ngày so với ngày hết hạn) anh nhé.

Anh xem qua các mức ưu đãi trên rồi cho em biết ý định của mình nhé!

**Turn 2**
- **Câu hỏi**: "Anh xem bên mình có thể giảm cho em 200-300k/tháng được không? Nếu ok em ký tiếp 12 tháng luôn, không cần đắn đo. Với cho em hỏi nếu em đóng 6 tháng một lần có được giảm thêm không?"
- **Câu trả lời của AI**: Chào anh Hùng, về yêu cầu của anh, em xin phản hồi dựa trên chính sách hiện hành của tòa nhà như sau:

1. **Về việc giảm giá 200-300k/tháng:** Theo quy định, khi anh gia hạn hợp đồng 12 tháng, anh sẽ được hưởng ưu đãi **giảm 5% tiền phòng** thay vì giảm theo số tiền cố định như anh đề xuất. Em sẽ tính toán cụ thể mức giảm 5% này dựa trên giá phòng hiện tại của anh để anh cân nhắc nhé.

2. **Về việc đóng 6 tháng một lần:** Chính sách hiện tại của bên em đối với việc gia hạn 6 tháng là **giữ nguyên giá cũ**. Hiện tại, hệ thống chưa có chương trình giảm giá thêm khi thanh toán trước 6 tháng.

Anh thấy phương án gia hạn 12 tháng với ưu đãi giảm 5% tiền phòng có phù hợp với mong muốn của anh không ạ? Nếu anh đồng ý, em sẽ chuẩn bị phụ lục hợp đồng để mình sớm hoàn tất thủ tục nhé.

**Turn 3**
- **Câu hỏi**: "Nếu ký tiếp thì em có phải đóng cọc lại không? Các điều khoản khác giữ nguyên hay có gì thay đổi? Em cũng muốn sửa lại cái bàn làm việc đang ọp ẹp trong phòng (em báo lâu rồi mà chưa thấy ai qua)."
- **Câu trả lời của AI**: Chào anh Hùng, em xin giải đáp các thắc mắc của anh như sau:

**1. Về việc gia hạn hợp đồng:**
*   **Tiền cọc:** Theo quy định, khi gia hạn hợp đồng, anh không cần đóng thêm tiền cọc nếu các điều khoản không thay đổi và anh vẫn đảm bảo các nghĩa vụ hiện tại.
*   **Điều khoản và giá thuê:** Nếu anh ký tiếp hợp đồng mới, giá thuê có thể được điều chỉnh nhẹ (tăng khoảng 5-10% tùy theo thị trường) để phù hợp với tình hình thực tế. Nếu anh giữ nguyên hợp đồng cũ (nếu còn thời hạn hoặc gia hạn theo phụ lục), giá thuê thường sẽ không đổi. Em sẽ chuẩn bị sẵn các phương án này để anh xem xét khi mình gặp nhau ký phụ lục nhé.

**2. Về bàn làm việc:**
Em rất xin lỗi anh vì sự chậm trễ trong việc xử lý yêu cầu bảo trì bàn làm việc của anh. Em đã tạo một phiếu yêu cầu sửa chữa mới để ưu tiên xử lý ngay cho anh:
*   **Mã phiếu:** TKT-2026-2FE8DA
*   **Trạng thái:** Mới tiếp nhận
*   **Thời gian dự kiến:** Thợ sẽ liên hệ và qua kiểm tra/sửa chữa cho anh trong vòng 24-48 giờ tới.

Anh yên tâm, em sẽ theo sát để đảm bảo bàn làm việc của anh được xử lý sớm nhất ạ. Anh còn cần hỗ trợ gì thêm không ạ?

**Turn 4**
- **Câu hỏi**: "OK vậy em chờ admin duyệt giảm giá. Khoảng bao lâu có kết quả? Và nếu được giảm thì em ký hợp đồng mới từ 1/9 luôn nhé."
- **Câu trả lời của AI**: Chào anh Hùng, về yêu cầu gia hạn và giảm giá thuê, em xin phản hồi như sau:

Theo quy định hiện hành, các yêu cầu về gia hạn và điều chỉnh giá thuê thường được quản lý xem xét và phản hồi trong khoảng **3 đến 5 ngày làm việc**.

Em đã ghi nhận thông tin anh muốn ký hợp đồng mới từ ngày 01/09/2026 nếu được duyệt giảm giá. Ngay khi có kết quả từ quản lý, em sẽ thông báo ngay cho anh để mình sắp xếp thời gian ký phụ lục hợp đồng nhé.

Anh cần hỗ trợ thêm thông tin gì khác không ạ?

