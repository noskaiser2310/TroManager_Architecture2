# Kịch bản: Báo mất điện thoại và cập nhật số SMS mới

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Phạm Thị Lan |
| Tenant ID | 4 |
| Phòng | 301 (tầng 3, 32m², 5.000.000đ/tháng) |
| Tone | anxious |
| Hợp đồng | 2025-01-01 → 2026-12-31 |
| Lịch sử | Thanh toán đúng hạn bằng chuyển khoản, lo mất số nhận OTP |
| Nhu cầu | Cập nhật số điện thoại mới vì mất SIM, cần nhận lại SMS từ nhà trọ |

### Multi-turn conversation

**Turn 1** — Chị Lan báo mất điện thoại, lo không nhận được thông báo.
> "Anh ơi, em vừa mất điện thoại, mất luôn cái SIM đăng ký với bên mình. Giờ em lo quá, sắp tới ngày đóng phòng mà không thấy nhắc SMS. Bên mình còn cách nào liên lạc em không?"

**Hệ thống**: Xác nhận tình huống, kiểm tra profile có email/Zalo không. Đề xuất cập nhật số mới.

**Turn 2** — Chị muốn cập nhật số mới ngay.
> "Em mua SIM mới rồi, số 0911223344. Anh cập nhật giúp em với. Mà mấy cái thông báo gửi tới số cũ có đọc được không?"

**Hệ thống**: Cập nhật số mới vào profile. Giải thích không thể lấy lại tin nhắn cũ trên SIM cũ.

**Turn 3** — Chị lo có thông báo quan trọng đã gửi tới số cũ.
> "Hồi đầu tháng em có thấy sms báo gì đó mà chưa kịp đọc. Giờ mất số rồi có biết được không anh? Hay anh xem giúp em nội dung thông báo đó?"

**Hệ thống**: Kiểm tra behavior_logs, xem thông báo gần nhất đã gửi. Báo lại nội dung.

**Turn 4** — Chị yên tâm và xác nhận chỉ cần SMS.
> "Dạ vậy được rồi, SMS là chính thôi cũng được. Cảm ơn anh. Mà nay em đóng tiền luôn thể cho khỏi quên. Anh cho em xin số tài khoản."

**Hệ thống**: Xác nhận cập nhật. Hỗ trợ thông tin thanh toán.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status (kiểm tra profile có contact khác không)
- Turn 2: Router → System 2 → update_user_preference (phone_number=0911223344)
- Turn 3: Router → System 2 → get_payment_history (kiểm tra behavior_logs có thông báo gần nhất)
- Turn 4: Router → System 1 → query_policies (thông tin tài khoản thanh toán)
### Kịch bản test
- File test: `existing_18_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:27:09*

**Turn 1**
- **Câu hỏi**: "Anh ơi, em vừa mất điện thoại, mất luôn cái SIM đăng ký với bên mình. Giờ em lo quá, sắp tới ngày đóng phòng mà không thấy nhắc SMS. Bên mình còn cách nào liên lạc em không?"
- **Câu trả lời của AI**: Chào chị Lan, em rất tiếc khi biết chị gặp sự cố mất điện thoại. Chị đừng quá lo lắng về việc nhận thông báo nhé.

Hiện tại, hệ thống của chúng em có thể hỗ trợ liên lạc với chị qua các kênh sau:
1. **Zalo OA:** Nếu chị đã cài Zalo trên thiết bị mới, chị có thể nhắn tin trực tiếp cho Zalo OA của tòa nhà.
2. **Email:** Nếu chị có đăng ký email trong hồ sơ, chúng em có thể gửi thông báo qua đó.
3. **Trực tiếp:** Chị có thể ghé văn phòng quản lý để cập nhật số điện thoại mới ngay khi chị làm lại SIM.

Về tình hình thanh toán, hóa đơn tháng 06/2026 của chị (phòng 301) với tổng số tiền **4,465,000đ** đã quá hạn từ ngày 05/06/2026. Chị vui lòng sắp xếp thanh toán sớm giúp em.

Nếu chị cần cập nhật số điện thoại mới vào hệ thống ngay bây giờ, chị vui lòng cung cấp số mới để em cập nhật vào hồ sơ cho chị nhé.

**Turn 2**
- **Câu hỏi**: "Em mua SIM mới rồi, số 0911223344. Anh cập nhật giúp em với. Mà mấy cái thông báo gửi tới số cũ có đọc được không?"
- **Câu trả lời của AI**: Chào chị Lan, em đã cập nhật số điện thoại mới (0911223344) vào hệ thống liên lạc của chị rồi ạ.

Về các thông báo trước đây, hệ thống đã gửi đến số điện thoại cũ của chị. Vì các tin nhắn này đã được gửi đi thành công qua nhà mạng, nên chị sẽ không thể nhận lại hoặc đọc được các nội dung đó trên số SIM mới này. Từ nay về sau, mọi thông báo từ Ban quản lý sẽ được gửi trực tiếp đến số 0911223344 của chị ạ.

**Turn 3**
- **Câu hỏi**: "Hồi đầu tháng em có thấy sms báo gì đó mà chưa kịp đọc. Giờ mất số rồi có biết được không anh? Hay anh xem giúp em nội dung thông báo đó?"
- **Câu trả lời của AI**: Chào chị Lan,

Em đã kiểm tra lại hệ thống. Thông báo chị nhận được đầu tháng là hóa đơn tiền phòng tháng 06/2026. Nội dung chi tiết như sau:

*   **Tiền phòng:** 3,500,000đ
*   **Tiền điện (90 kWh):** 315,000đ
*   **Tiền nước (6 m³):** 600,000đ
*   **Phí dịch vụ:** 50,000đ
*   **Tổng cộng:** 4,465,000đ

Hạn thanh toán là ngày **05/06/2026**. Hiện tại hóa đơn này đã quá hạn thanh toán 10 ngày. Chị vui lòng sắp xếp thanh toán sớm giúp em nhé. Nếu cần hỗ trợ thêm thông tin gì, chị cứ nhắn em ạ.

**Turn 4**
- **Câu hỏi**: "Dạ vậy được rồi, SMS là chính thôi cũng được. Cảm ơn anh. Mà nay em đóng tiền luôn thể cho khỏi quên. Anh cho em xin số tài khoản."
- **Câu trả lời của AI**: Dạ, em đã ghi nhận yêu cầu ưu tiên liên lạc qua SMS của chị Lan.

Về việc thanh toán, chị vui lòng chuyển khoản theo thông tin sau:

*   **Ngân hàng:** Vietcombank
*   **Số tài khoản:** 1234567890
*   **Chủ tài khoản:** Đặng Văn Nhuận
*   **Nội dung chuyển khoản:** TT phong 301 thang 06/2026

Chị nhớ ghi đúng nội dung để hệ thống xác nhận thanh toán nhanh chóng giúp em nhé. Cảm ơn chị!

