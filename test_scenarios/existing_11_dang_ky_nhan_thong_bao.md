# Kịch bản: Đăng ký nhận thông báo nhắc nợ trong app

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Văn Minh |
| Tenant ID | 1 |
| Phòng | 101 (tầng 1, 25m², 3.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-01-15 → 2026-12-31 |
| Lịch sử | Thanh toán đúng hạn, muốn đăng ký nhắc nợ trong app |
| Nhu cầu | Được AI nhắc nợ trực tiếp khi chat |

### Multi-turn conversation

**Turn 1** — Khách hỏi có được nhắc nợ trong app không.
> "Anh ơi, em hay quên ngày đóng phòng quá. Bên mình có nhắc nợ ngay trong app không? Ví dụ em chat với anh thì anh nhắc em luôn ấy."

**Hệ thống**: Xác nhận có thể nhắc nợ qua chat app. Hướng dẫn cách đăng ký.

**Turn 2** — Khách muốn đăng ký.
> "Vậy anh đăng ký cho em nhé. Cứ tới gần ngày đóng là anh nhắc em luôn khi em hỏi chuyện. Có cần em làm gì không?"

**Hệ thống**: Cập nhật preference notification_via_app=true, xác nhận đã đăng ký.

**Turn 3** — Khách hỏi khi nào thì được nhắc.
> "Cảm ơn anh. Mà khi nào anh nhắc em? Kiểu mùng mấy hàng tháng vậy? Và nhắc những gì?"

**Hệ thống**: Tra cứu policy về lịch thanh toán. Giải thích sẽ nhắc trước ngày 05 hàng tháng khi khách chat.

**Turn 4** — Khách chỉ muốn nhắc nợ, không cần các thông báo khác.
> "Dạ vậy anh chỉ nhắc nợ thôi nhé, còn mấy cái khác như khuyến mãi hay sinh nhật thì thôi. Em ngại lắm."

**Hệ thống**: Ghi nhận, xác nhận chỉ nhắc nợ trong app.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 1 → query_policies (nhắc nợ)
- Turn 2: Router → System 2 → update_user_preference (notification_via_app=true)
- Turn 3: Router → System 2 → query_policies (lịch thanh toán)
- Turn 4: Router → System 2 → update_user_preference (notification_types=chỉ nhắc nợ)
### Kịch bản test
- File test: `existing_11_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:15:30*

**Turn 1**
- **Câu hỏi**: "Anh ơi, em hay quên ngày đóng phòng quá. Bên mình có nhắc nợ ngay trong app không? Ví dụ em chat với anh thì anh nhắc em luôn ấy."
- **Câu trả lời của AI**: Dạ chào anh Minh, em rất hiểu sự bất tiện này.

Theo quy định của tòa nhà, quy trình thông báo thanh toán hiện tại như sau ạ:

*   **Ngày 25 hàng tháng:** Quản lý sẽ ghi chỉ số điện nước.
*   **Ngày 27-28:** Hệ thống sẽ gửi thông báo chi tiết hóa đơn qua Zalo cho anh.
*   **Ngày 30:** Hóa đơn chính thức sẽ được gửi qua app.

Về việc anh muốn được nhắc nhở trực tiếp qua chat, em hoàn toàn có thể hỗ trợ anh việc này! Anh có muốn em ghi chú lại vào hồ sơ cá nhân để mỗi khi đến kỳ thanh toán, em sẽ chủ động nhắn tin nhắc anh không ạ? Nếu anh đồng ý, em sẽ cập nhật vào hệ thống ngay để anh không phải lo lắng về việc quên ngày nữa nhé.

**Turn 2**
- **Câu hỏi**: "Vậy anh đăng ký cho em nhé. Cứ tới gần ngày đóng là anh nhắc em luôn khi em hỏi chuyện. Có cần em làm gì không?"
- **Câu trả lời của AI**: Dạ vâng anh Minh, em đã ghi nhận yêu cầu của anh vào hệ thống rồi ạ. Từ nay, cứ gần đến ngày đóng tiền phòng, anh chỉ cần nhắn tin hỏi em, em sẽ chủ động nhắc nhở anh ngay nhé.

Anh không cần phải làm gì thêm đâu ạ, mọi việc cứ để em lo. Chúc anh có một ngày làm việc thật hiệu quả và vui vẻ nhé! Anh còn cần em hỗ trợ thêm vấn đề gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "Cảm ơn anh. Mà khi nào anh nhắc em? Kiểu mùng mấy hàng tháng vậy? Và nhắc những gì?"
- **Câu trả lời của AI**: Dạ chào anh Minh, về quy trình nhắc nhở thanh toán, em xin thông tin đến anh như sau:

Theo quy định của nhà trọ, quy trình thông báo hóa đơn và nhắc nhở được thực hiện như sau:

*   **Ngày 25 hàng tháng:** Quản lý sẽ tiến hành ghi chỉ số điện, nước.
*   **Ngày 27-28 hàng tháng:** Em sẽ gửi thông báo chi tiết hóa đơn qua Zalo để anh kiểm tra.
*   **Ngày 30 hàng tháng:** Hóa đơn chính thức sẽ được gửi qua ứng dụng.
*   **Thời hạn thanh toán:** Anh vui lòng hoàn tất thanh toán trước ngày **05 hàng tháng**.

**Về việc nhắc nhở:**
*   Nếu đến hạn (ngày 05) mà anh chưa thanh toán, hệ thống sẽ bắt đầu nhắc nhở anh qua Zalo.
*   Nếu anh trễ hạn từ 1-3 ngày, em sẽ gửi tin nhắn nhắc nhở nhẹ nhàng.
*   Từ ngày thứ 4 trở đi, sẽ có phát sinh phí phạt theo quy định (50.000đ cho 4-7 ngày trễ).

Vì anh thường hay quên đóng tiền vào ngày 05, nếu anh muốn, em có thể lưu ý để nhắc anh sớm hơn một chút qua Zalo vào ngày 27-28 khi gửi hóa đơn. Anh thấy thế nào ạ?

**Turn 4**
- **Câu hỏi**: "Dạ vậy anh chỉ nhắc nợ thôi nhé, còn mấy cái khác như khuyến mãi hay sinh nhật thì thôi. Em ngại lắm."
- **Câu trả lời của AI**: Dạ vâng anh Minh, em đã ghi nhận yêu cầu của anh rồi ạ. Từ nay, em sẽ chỉ gửi thông báo cho anh khi có nhắc nhở về việc thanh toán tiền phòng thôi, còn các thông tin về khuyến mãi hay sinh nhật em sẽ không gửi nữa để anh được thoải mái ạ.

Anh cần hỗ trợ thêm gì khác không ạ?

