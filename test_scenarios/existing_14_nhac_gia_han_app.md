# Kịch bản: Đăng ký nhắc gia hạn hợp đồng trong app

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Đỗ Văn Hùng |
| Tenant ID | 5 |
| Phòng | 302 (tầng 3, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2024-09-01 → 2026-09-01 (còn 2.5 tháng) |
| Lịch sử | Thanh toán đúng hạn suốt 22 tháng |
| Nhu cầu | Được AI nhắc gia hạn trong app trước 1 tháng |

### Multi-turn conversation

**Turn 1** — Khách hỏi hợp đồng còn bao lâu và muốn được nhắc trong app.
> "Chào em, anh xem giúp hợp đồng của anh còn bao lâu nữa hết hạn vậy? Anh tính gia hạn nhưng sợ bận quên. Nếu được thì anh chat với em là em nhắc anh luôn nhé."

**Hệ thống**: Tra cứu hợp đồng tenant_id=5 — hết hạn 2026-09-01, còn ~2.5 tháng.

**Turn 2** — Khách muốn đăng ký nhắc trước 1 tháng.
> "Còn tới tháng 9, vậy tháng 8 anh nhắc anh nhé. Cứ tới tháng 8 anh hỏi em 'hợp đồng sắp hết chưa?' là em báo anh chi tiết luôn."

**Hệ thống**: Cập nhật preference reminder_contract_renewal=true, xác nhận sẽ nhắc trong app.

**Turn 3** — Khách hỏi thủ tục gia hạn và ưu đãi.
> "Nếu gia hạn thì thủ tục có gì thay đổi không? Anh nghe nói có ưu đãi giữ phòng cho khách cũ. Cho anh xin thông tin."

**Hệ thống**: Tra cứu policy về gia hạn hợp đồng và ưu đãi khách cũ. Trả lời chi tiết.

**Turn 4** — Khách muốn khi nhắc thì gửi kèm thông tin ưu đãi.
> "OK tốt. Anh nhờ lúc nhắc anh trong app thì gửi kèm luôn thông tin ưu đãi gia hạn nhé. Để anh so sánh với mấy chỗ khác luôn."

**Hệ thống**: Ghi nhận yêu cầu, xác nhận sẽ kèm ưu đãi khi nhắc.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status
- Turn 2: Router → System 2 → update_user_preference (reminder_contract_renewal=true)
- Turn 3: Router → System 2 → query_policies (gia hạn, ưu đãi)
- Turn 4: Router → System 2 → ghi nhận vào behavior_log
### Kịch bản test
- File test: `existing_14_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:19:28*

**Turn 1**
- **Câu hỏi**: "Chào em, anh xem giúp hợp đồng của anh còn bao lâu nữa hết hạn vậy? Anh tính gia hạn nhưng sợ bận quên. Nếu được thì anh chat với em là em nhắc anh luôn nhé."
- **Câu trả lời của AI**: Chào anh Hùng, em đã kiểm tra thông tin hợp đồng của anh trên hệ thống ạ:

*   **Ngày hết hạn:** 01/09/2026.
*   **Thời gian còn lại:** 78 ngày.

Anh yên tâm, em đã ghi chú lại yêu cầu của anh. Khi gần đến ngày gia hạn, em sẽ chủ động nhắn tin nhắc anh để mình kịp thời làm thủ tục nhé. Nếu anh cần thêm thông tin gì khác, anh cứ nhắn em ạ!

**Turn 2**
- **Câu hỏi**: "Còn tới tháng 9, vậy tháng 8 anh nhắc anh nhé. Cứ tới tháng 8 anh hỏi em 'hợp đồng sắp hết chưa?' là em báo anh chi tiết luôn."
- **Câu trả lời của AI**: Dạ vâng anh Hùng, em đã ghi chú lại yêu cầu của anh. Vào tháng 8 tới, em sẽ chủ động nhắn tin hỏi anh "hợp đồng sắp hết chưa?" để mình cùng kiểm tra và làm thủ tục gia hạn anh nhé. 

Anh cần hỗ trợ thêm thông tin gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "Nếu gia hạn thì thủ tục có gì thay đổi không? Anh nghe nói có ưu đãi giữ phòng cho khách cũ. Cho anh xin thông tin."
- **Câu trả lời của AI**: Chào anh Hùng, về việc gia hạn hợp đồng, em xin gửi anh thông tin chi tiết như sau:

**1. Thủ tục gia hạn:**
Hiện tại, quy trình gia hạn rất đơn giản, không có thay đổi đáng kể so với trước đây:
*   Anh chỉ cần phản hồi ý muốn gia hạn với em.
*   Chúng ta sẽ thảo luận về thời hạn và giá thuê mới (nếu có điều chỉnh).
*   Sau đó, anh ghé qua ký phụ lục gia hạn trước ngày hết hạn hợp đồng ít nhất 7 ngày là hoàn tất.

**2. Ưu đãi dành cho khách cũ:**
Đúng như anh nghe, tòa nhà có chính sách ưu đãi rất tốt cho khách hàng thân thiết khi gia hạn hợp đồng, cụ thể:
*   **Gia hạn 6 tháng:** Giữ nguyên giá cũ.
*   **Gia hạn 12 tháng:** Giảm **5%** tiền phòng.
*   **Gia hạn 24 tháng:** Giảm **10%** tiền phòng + miễn phí 1 tháng cọc nếu tái ký.

Vì anh là khách thuê lâu năm và luôn thanh toán đúng hạn, em sẽ ưu tiên hỗ trợ anh mức điều chỉnh giá tốt nhất theo chính sách. Khi nào anh sắp xếp được thời gian, anh nhắn em để mình chốt thời hạn gia hạn và chuẩn bị phụ lục nhé!

**Turn 4**
- **Câu hỏi**: "OK tốt. Anh nhờ lúc nhắc anh trong app thì gửi kèm luôn thông tin ưu đãi gia hạn nhé. Để anh so sánh với mấy chỗ khác luôn."
- **Câu trả lời của AI**: Chào anh Hùng, em đã ghi nhận yêu cầu của anh vào hệ thống. Từ nay, khi gửi thông báo nhắc nhở gia hạn, em sẽ đính kèm chi tiết các ưu đãi dành riêng cho anh để anh tiện so sánh và cân nhắc nhé.

Hiện tại, dựa trên lịch sử thuê phòng rất tốt của anh, hệ thống đang xếp anh vào nhóm khách hàng ưu tiên (Tier A). Khi anh tiến hành gia hạn, em sẽ đề xuất các phương án tối ưu nhất như giữ nguyên giá thuê cũ, hoặc các gói ưu đãi dịch vụ đi kèm.

Khi nào anh sẵn sàng ký phụ lục, anh cứ nhắn em nhé!

