# Kịch bản: Hỏi về chính sách nuôi thú cưng và giới thiệu bạn ở

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Văn Minh |
| Tenant ID | 1 |
| Phòng | 101 (tầng 1, 25m², 3.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-01-15 → 2026-12-31 |
| Lịch sử | Luôn đúng hạn, thân thiện, thường xuyên tương tác |

### Multi-turn conversation

**Turn 1** — Khách hỏi về việc nuôi thú cưng.
> "Anh quản lý ơi, em ở phòng 101. Em đang tính nuôi một bé mèo, nhưng không rõ bên mình có cho phép nuôi thú cưng trong phòng không ạ? Có quy định gì về việc này không anh?"

**Hệ thống**: Tra policy về thú cưng. Trả lời có cho phép nuôi với điều kiện — không gây ồn, không ảnh hưởng phòng khác, đảm bảo vệ sinh.

**Turn 2** — Khách hỏi điều kiện cụ thể.
> "Nếu được thì có cần đóng thêm tiền cọc không anh? Hay ký giấy tờ gì thêm? Có giới hạn số lượng, chủng loại không ạ?"

**Hệ thống**: Cung cấp điều kiện — cọc thêm 500.000đ (hoàn lại), ký phụ lục hợp đồng, tối đa 2 con, chỉ nuôi mèo hoặc thú nhỏ, không nuôi chó.

**Turn 3** — Khách hỏi thêm về giới thiệu bạn vào ở.
> "Dạ em hiểu rồi. Mà anh ơi, em có thằng bạn đang tìm phòng trọ, em giới thiệu nó vào ở bên mình. Bên mình còn phòng trống nào không ạ? Nó cần phòng rộng rộng tí, tầm 3-4tr, có máy lạnh, thoáng mát."

**Hệ thống**: Kiểm tra available rooms — 103 (3tr, 20m²), 202 (4tr, 28m², máy lạnh Daikin, ban công rộng), 203 (3.2tr, 22m², máy lạnh Panasonic), 303 (3.5tr, 25m², máy lạnh LG). Đề xuất phòng 202 là phù hợp nhất.

**Turn 4** — Khách xin số điện thoại bạn để quản lý liên hệ.
> "Ok để em nói nó. Mà anh cho em xin số Zalo hay số điện thoại bên mình để nó liên hệ trực tiếp được không? Nó tên là Nam, làm IT, tính tháng sau chuyển qua. Em cảm ơn anh nhiều!"

**Hệ thống**: Cung cấp thông tin liên hệ quản lý hoặc đề nghị gửi số Nam để chủ động liên hệ.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 1 → query_policies (thú cưng)
- Turn 2: Router → System 1 → query_policies (chi tiết)
- Turn 3: Router → System 2 → fetch_available_rooms (budget 3-4tr, máy lạnh)
- Turn 4: Router → System 1 → cung cấp thông tin liên hệ
### Kịch bản test
- File test: `existing_07_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:11:23*

**Turn 1**
- **Câu hỏi**: "Anh quản lý ơi, em ở phòng 101. Em đang tính nuôi một bé mèo, nhưng không rõ bên mình có cho phép nuôi thú cưng trong phòng không ạ? Có quy định gì về việc này không anh?"
- **Câu trả lời của AI**: Dạ chào anh Minh, về thắc mắc của anh, em xin thông tin đến anh như sau ạ:

Hiện tại, theo quy định của nhà trọ, chúng ta **không cho phép nuôi thú cưng** trong phòng để đảm bảo vệ sinh, trật tự và sự thoải mái chung cho tất cả các khách thuê khác.

Nếu anh có nhu cầu đặc biệt hoặc muốn tìm nơi ở cho phép nuôi thú cưng, anh có thể liên hệ trực tiếp với em để em hỗ trợ tìm kiếm các phương án khác hoặc giới thiệu các khu vực phù hợp hơn ạ.

Anh lưu ý giúp em quy định này để tránh các trường hợp vi phạm không đáng có nhé. Anh cần em hỗ trợ thêm thông tin gì khác không ạ?

**Turn 2**
- **Câu hỏi**: "Nếu được thì có cần đóng thêm tiền cọc không anh? Hay ký giấy tờ gì thêm? Có giới hạn số lượng, chủng loại không ạ?"
- **Câu trả lời của AI**: Dạ chào anh Minh, về các thắc mắc của anh khi gia hạn hợp đồng, em xin giải đáp dựa trên quy định hiện hành như sau ạ:

1.  **Về tiền cọc:** Khi gia hạn hợp đồng, nếu anh vẫn tiếp tục thuê phòng cũ và không có thay đổi lớn về điều kiện thuê, thông thường anh **không cần đóng thêm tiền cọc**. Tiền cọc cũ của anh sẽ được bảo lưu cho hợp đồng mới.
2.  **Về giấy tờ:** Anh sẽ cần ký **Phụ lục gia hạn hợp đồng** hoặc làm hợp đồng mới để cập nhật thời hạn thuê và các điều khoản (nếu có thay đổi). Em sẽ chuẩn bị sẵn hồ sơ để anh ký khi đến thời điểm gia hạn.
3.  **Về giới hạn số lượng/chủng loại:** Nội quy nhà trọ quy định về việc đảm bảo an ninh, trật tự và vệ sinh chung. Nếu anh có ý định thay đổi về số lượng người ở hoặc các vấn đề liên quan đến vật nuôi, anh vui lòng thông báo trước để Ban quản lý xem xét và cập nhật vào phụ lục hợp đồng, đảm bảo đúng quy định tòa nhà anh nhé.

Hiện tại hợp đồng của anh còn hiệu lực đến ngày **31/12/2026**. Anh nên báo cho Ban quản lý trước ít nhất **30 ngày** (tức là khoảng cuối tháng 11/2026) để tiến hành thủ tục gia hạn và nhận các ưu đãi (nếu có) ạ.

Anh cần em hỗ trợ thêm thông tin nào khác không ạ?

**Turn 3**
- **Câu hỏi**: "Dạ em hiểu rồi. Mà anh ơi, em có thằng bạn đang tìm phòng trọ, em giới thiệu nó vào ở bên mình. Bên mình còn phòng trống nào không ạ? Nó cần phòng rộng rộng tí, tầm 3-4tr, có máy lạnh, thoáng mát."
- **Câu trả lời của AI**: Dạ chào anh Minh, cảm ơn anh đã giới thiệu bạn đến với nhà trọ mình nhé!

Hiện tại bên em đang có 4 phòng trống phù hợp với ngân sách từ 3-4 triệu của bạn anh đây ạ:

*   **Phòng 103 (Tầng 1):** 20m², giá 3.000.000đ/tháng.
*   **Phòng 203 (Tầng 2):** 22m², giá 3.200.000đ/tháng.
*   **Phòng 303 (Tầng 3):** 25m², giá 3.500.000đ/tháng.
*   **Phòng 202 (Tầng 2):** 28m², giá 4.000.000đ/tháng (phòng này rộng nhất ạ).

Tất cả các phòng này đều được trang bị máy lạnh và đảm bảo sự thoáng mát. Anh có thể gửi thông tin này cho bạn anh tham khảo nhé. Nếu bạn anh muốn qua xem phòng trực tiếp, anh cứ báo em hoặc bảo bạn anh liên hệ với em để em sắp xếp lịch ạ!

**Turn 4**
- **Câu hỏi**: "Ok để em nói nó. Mà anh cho em xin số Zalo hay số điện thoại bên mình để nó liên hệ trực tiếp được không? Nó tên là Nam, làm IT, tính tháng sau chuyển qua. Em cảm ơn anh nhiều!"
- **Câu trả lời của AI**: Dạ chào anh Minh, rất vui khi biết anh Nam có ý định chuyển đến nhà mình ạ.

Anh có thể bảo bạn Nam liên hệ với Ban quản lý qua các kênh sau để được hỗ trợ nhanh nhất nhé:

*   **Số điện thoại/Zalo:** `0901-234-567` (Đây là số hotline chính thức của Ban quản lý).
*   **Thời gian hỗ trợ:** 8h00 – 20h00 (Thứ 2 – Chủ nhật).

Nếu bạn Nam cần xem phòng trước, anh có thể nhắn em hoặc bảo bạn ấy liên hệ số trên để đặt lịch hẹn ạ. Chúc anh và bạn Nam một ngày tốt lành!

