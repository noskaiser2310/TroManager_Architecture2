# Kịch bản: Đăng ký nhận nhắc nhở gia hạn hợp đồng

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Đỗ Văn Hùng |
| Tenant ID | 5 |
| Phòng | 302 (tầng 3, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2024-09-01 → 2026-09-01 (còn 2.5 tháng) |
| Lịch sử | Đã thanh toán đúng hạn suốt 22 tháng |
| Nhu cầu | Nhận thông báo nhắc trước khi hết hạn hợp đồng |

### Multi-turn conversation

**Turn 1** — Khách hỏi hợp đồng còn bao lâu, bày tỏ muốn gia hạn nhưng sợ quên.
> "Chào em, anh xem giúp hợp đồng của anh còn bao lâu nữa hết hạn vậy? Anh tính gia hạn tiếp nhưng sợ bận quá quên mất. Bên mình có nhắc trước không?"

**Hệ thống**: Tra cứu hợp đồng tenant_id=5 — hết hạn 2026-09-01, còn ~2.5 tháng. Thông báo còn hạn đến tháng 9.

**Turn 2** — Khách muốn đăng ký nhận nhắc qua SMS trước 1 tháng.
> "Vậy còn hơn 2 tháng nữa. Anh muốn đăng ký để được nhắc trước 1 tháng khi hết hạn. Cho anh nhắc qua SMS nhé, điện thoại anh để bàn nên dễ thấy hơn."

**Hệ thống**: Cập nhật preference contact_method=sms, ghi nhận yêu cầu nhắc trước 30 ngày.

**Turn 3** — Khách hỏi thủ tục gia hạn có gì thay đổi không.
> "À nếu gia hạn thì thủ tục có gì thay đổi không? Anh nghe nói mới có chính sách giữ phòng cho khách cũ. Có ưu đãi gì không?"

**Hệ thống**: Tra cứu policy về gia hạn và ưu đãi khách cũ. Thông tin chi tiết.

**Turn 4** — Khách yêu cầu ghi chú để khi nhắc gửi kèm thông tin ưu đãi.
> "OK tốt. Anh nhờ ghi chú là tới tháng 8 nhắc anh, gửi kèm các ưu đãi gia hạn nhé. Để anh còn so sánh với mấy chỗ khác."

**Hệ thống**: Ghi nhận yêu cầu vào behavior_log, xác nhận sẽ nhắc kèm thông tin ưu đãi.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status
- Turn 2: Router → System 2 → update_user_preference (contact_method=sms)
- Turn 3: Router → System 1 → query_policies (gia hạn, ưu đãi)
- Turn 4: Router → System 2 → update_user_preference (interaction_patterns)
### Kịch bản test
- File test: `existing_14_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:20:25*

**Turn 1**
- **Câu hỏi**: "Chào em, anh xem giúp hợp đồng của anh còn bao lâu nữa hết hạn vậy? Anh tính gia hạn tiếp nhưng sợ bận quá quên mất. Bên mình có nhắc trước không?"
- **Câu trả lời của AI**: Chào anh Hùng, em đã kiểm tra thông tin hợp đồng của mình ạ:

*   **Thời hạn hợp đồng:** Đến ngày **01/09/2026** mới hết hạn.
*   **Thời gian còn lại:** Hiện tại còn **78 ngày** nữa ạ.

Về việc nhắc nhở gia hạn, theo quy định của tòa nhà, bên em sẽ chủ động gửi thông báo qua Zalo cho anh trước **45 ngày** so với ngày hết hạn để anh kịp thời sắp xếp.

Anh yên tâm, khi đến thời điểm đó em sẽ nhắn tin nhắc anh nhé. Nếu anh muốn gia hạn sớm hơn để nhận các ưu đãi (như giảm 5% tiền phòng khi gia hạn 12 tháng), anh cứ nhắn em bất cứ lúc nào ạ!

**Turn 2**
- **Câu hỏi**: "Vậy còn hơn 2 tháng nữa. Anh muốn đăng ký để được nhắc trước 1 tháng khi hết hạn. Cho anh nhắc qua SMS nhé, điện thoại anh để bàn nên dễ thấy hơn."
- **Câu trả lời của AI**: Chào anh Hùng, em đã cập nhật thông tin để hệ thống gửi thông báo nhắc nhở gia hạn hợp đồng cho anh qua SMS trước 1 tháng khi hợp đồng hết hạn (ngày 01/08/2026) theo đúng yêu cầu của anh rồi ạ.

Anh cần hỗ trợ thêm thông tin gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "À nếu gia hạn thì thủ tục có gì thay đổi không? Anh nghe nói mới có chính sách giữ phòng cho khách cũ. Có ưu đãi gì không?"
- **Câu trả lời của AI**: Chào anh Hùng, về thắc mắc của anh, em xin thông tin chi tiết về chính sách gia hạn hợp đồng hiện tại như sau:

**1. Thủ tục gia hạn:**
Quy trình gia hạn không có thay đổi lớn, anh vẫn thực hiện theo các bước:
*   Phản hồi xác nhận gia hạn với quản lý.
*   Thảo luận về thời hạn và giá thuê mới.
*   Ký phụ lục gia hạn trước ngày hết hạn hợp đồng ít nhất 7 ngày.

**2. Ưu đãi dành cho khách hàng gia hạn:**
Hiện tại, tòa nhà có áp dụng các mức ưu đãi cụ thể dựa trên thời hạn anh đăng ký gia hạn thêm:
*   **Gia hạn 6 tháng:** Giữ nguyên giá thuê hiện tại.
*   **Gia hạn 12 tháng:** Giảm 5% tiền phòng.
*   **Gia hạn 24 tháng:** Giảm 10% tiền phòng và miễn phí 1 tháng cọc nếu tái ký.

**Lưu ý:** Điều kiện để được hưởng các ưu đãi này là anh đang thuê đúng hợp đồng, không có nợ tiền thuê/điện nước và phòng vẫn giữ nguyên trạng.

Anh dự định gia hạn thêm bao lâu để em tính toán mức ưu đãi chính xác cho anh nhé? Nếu anh cần hỗ trợ thêm thông tin gì, cứ nhắn em ạ!

**Turn 4**
- **Câu hỏi**: "OK tốt. Anh nhờ ghi chú là tới tháng 8 nhắc anh, gửi kèm các ưu đãi gia hạn nhé. Để anh còn so sánh với mấy chỗ khác."
- **Câu trả lời của AI**: Chào anh Hùng, em đã ghi chú lại yêu cầu của anh vào hệ thống để nhắc anh về việc gia hạn hợp đồng vào tháng 8 tới.

Khi đến thời điểm đó, em sẽ chủ động liên hệ và gửi kèm các chính sách ưu đãi gia hạn tốt nhất dành riêng cho anh để anh tham khảo và so sánh nhé. Anh yên tâm, với tư cách là khách hàng thân thiết, em sẽ hỗ trợ anh các phương án tối ưu nhất.

Anh còn cần em hỗ trợ thêm thông tin gì khác không ạ?

