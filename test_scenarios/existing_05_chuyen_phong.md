# Kịch bản: Yêu cầu đổi phòng lên phòng có ban công

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Hoàng Tuấn |
| Tenant ID | 3 |
| Phòng hiện tại | 201 (tầng 2, 22m², 3.200.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-06-01 → 2026-12-31 |
| Lịch sử | Thanh toán luôn đúng hạn, khách thân thiện |
| Behavior log | Đã đề nghị chuyển lên phòng có ban công (room_transfer) |
| Ghi chú | Khách nhiệt tình, tích cực, ở lâu dài |

### Multi-turn conversation

**Turn 1** — Khách nhắc lại yêu cầu đổi phòng có ban công.
> "Anh quản lý ơi, hồi trước em có nói muốn chuyển lên phòng có ban công, nay em hỏi lại lần nữa. Phòng 201 em ở thấy ổn nhưng thiếu ban công, quần áo phơi trong phòng ẩm quá. Bên mình còn phòng trống nào có ban công không em lên luôn?"

**Hệ thống**: Check available rooms có ban công — phòng 202 (tầng 2, 28m², 4.000.000đ, ban công rộng, hướng nam). Gợi ý phòng 202 là lựa chọn phù hợp nhất.

**Turn 2** — Khách hỏi chi tiết phòng 202.
> "Phòng 202 giá 4tr cao hơn phòng em đang ở 800k nhỉ. Nhưng 28m² rộng hơn, có ban công rộng, hướng nam thì chắc thoáng. Em hỏi tí: tiền chênh lệch tính thế nào? Em có phải đóng cọc thêm không? Có mất phí chuyển phòng không?"

**Hệ thống**: Hướng dẫn chính sách đổi phòng — phụ thu chênh lệch tiền phòng, không mất thêm cọc nếu đã đóng đủ, miễn phí chuyển phòng.

**Turn 3** — Khách muốn xem phòng trước.
> "Dạ em muốn qua xem phòng 202 một lần trước khi quyết định. Tầm chiều mai em rảnh sau 5h. Anh sắp xếp cho em xem được không ạ? Nếu ưng em chuyển luôn trong tuần."

**Hệ thống**: Xác nhận lịch xem phòng, ghi nhận request.

**Turn 4** — Khách hỏi thủ tục nếu đồng ý.
> "Cảm ơn anh. Nếu em ưng phòng 202 thì thủ tục chuyển ra sao? Em có cần ký hợp đồng mới không? Hay chỉ cần phụ lục điều chỉnh? Và chuyển xong trong ngày được không ạ?"

**Hệ thống**: Hướng dẫn chuyển phòng — ký phụ lục hợp đồng, bàn giao phòng cũ, nhận phòng mới. Có thể chuyển trong ngày.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → fetch_available_rooms (filter: balcony, occupied=no)
- Turn 2: Router → System 2 → query_policies (chi phí chuyển phòng)
- Turn 3: Router → System 2 → schedule_room_viewing
- Turn 4: Router → System 2 → get_contract_status + query_policies
### Kịch bản test
- File test: `existing_05_test.py`






---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:54:35*

**Turn 1**
- **Câu hỏi**: "Anh quản lý ơi, hồi trước em có nói muốn chuyển lên phòng có ban công, nay em hỏi lại lần nữa. Phòng 201 em ở thấy ổn nhưng thiếu ban công, quần áo phơi trong phòng ẩm quá. Bên mình còn phòng trống nào có ban công không em lên luôn?"
- **Câu trả lời của AI**: Chào anh Tuấn, em rất hiểu sự bất tiện khi phòng thiếu ban công khiến quần áo bị ẩm.

Em vừa kiểm tra danh sách phòng trống hiện tại, hiện chỉ có **phòng 202** là có ban công thôi ạ. Thông tin chi tiết phòng 202 như sau:
*   **Tầng:** 2
*   **Diện tích:** 28m²
*   **Giá thuê:** 4,000,000đ/tháng
*   **Tiện nghi:** Có ban công, giường, bàn bếp, cửa sổ, nóng lạnh, điều hòa, tủ quần áo.

Các phòng còn lại (103, 203, 303) hiện tại không có ban công anh ạ. Nếu anh quan tâm đến phòng 202, anh có muốn qua xem trực tiếp không ạ? Em sẽ sắp xếp lịch cho anh nhé!

**Turn 2**
- **Câu hỏi**: "Phòng 202 giá 4tr cao hơn phòng em đang ở 800k nhỉ. Nhưng 28m² rộng hơn, có ban công rộng, hướng nam thì chắc thoáng. Em hỏi tí: tiền chênh lệch tính thế nào? Em có phải đóng cọc thêm không? Có mất phí chuyển phòng không?"
- **Câu trả lời của AI**: Chào anh Tuấn, em đã kiểm tra thông tin về phòng 202 và chính sách chuyển phòng để giải đáp thắc mắc cho anh đây ạ:

1. **Về tiền chênh lệch:** Đúng là phòng 202 có giá 4.000.000đ/tháng, cao hơn phòng 201 anh đang ở là 800.000đ. Theo quy định, giá phòng mới sẽ được áp dụng từ ngày anh chính thức chuyển sang phòng 202.
2. **Về tiền cọc:** Khi chuyển sang phòng có giá thuê cao hơn, anh sẽ cần thực hiện bù trừ chênh lệch tiền cọc (nếu có) để đảm bảo đúng với giá trị cọc của phòng mới theo hợp đồng.
3. **Về phí chuyển phòng:** 
   - Nếu đây là lần đầu tiên anh chuyển phòng trong hợp đồng, bên em sẽ **miễn phí** hoàn toàn phí chuyển phòng.
   - Từ lần thứ 2 trở đi, phí chuyển sẽ là 200.000đ/lần (bao gồm chi phí vệ sinh và sửa chữa nhỏ).

Vì phòng 202 có diện tích 28m² và có ban công hướng Nam như anh nhận xét thì rất thoáng mát, rất phù hợp nếu anh muốn nâng cấp không gian sống. Anh cần lưu ý báo trước cho bên em **tối thiểu 7 ngày** trước khi chuyển để em làm thủ tục và chuẩn bị phòng cho anh nhé.

Anh có muốn em đặt lịch cho anh qua xem trực tiếp phòng 202 không ạ?

**Turn 3**
- **Câu hỏi**: "Dạ em muốn qua xem phòng 202 một lần trước khi quyết định. Tầm chiều mai em rảnh sau 5h. Anh sắp xếp cho em xem được không ạ? Nếu ưng em chuyển luôn trong tuần."
- **Câu trả lời của AI**: Chào anh Tuấn, em đã ghi nhận yêu cầu xem phòng 202 của anh vào lúc 17:00 chiều mai (16/06/2026) rồi ạ.

Hiện tại, lịch hẹn đã được gửi đến bộ phận quản lý để xác nhận. Quản lý sẽ liên hệ với anh sớm để chốt lịch chính thức nhé. Anh yên tâm, nếu anh ưng ý và muốn chuyển phòng, bên em sẽ hỗ trợ thủ tục nhanh gọn nhất cho anh ạ.

Anh cần hỗ trợ thêm thông tin gì về phòng 202 không ạ?

**Turn 4**
- **Câu hỏi**: "Cảm ơn anh. Nếu em ưng phòng 202 thì thủ tục chuyển ra sao? Em có cần ký hợp đồng mới không? Hay chỉ cần phụ lục điều chỉnh? Và chuyển xong trong ngày được không ạ?"
- **Câu trả lời của AI**: Chào anh Tuấn, em đã kiểm tra thông tin về phòng 202 và quy định chuyển phòng để hỗ trợ anh đây ạ:

**1. Về thủ tục chuyển phòng:**
Theo quy định của tòa nhà, khi anh muốn chuyển sang phòng 202, quy trình sẽ bao gồm các bước sau:
*   Anh gửi yêu cầu chính thức (em đã ghi nhận yêu cầu của anh).
*   Chúng ta sẽ chốt ngày chuyển và thực hiện **ký phụ lục hợp đồng** (không cần ký lại hợp đồng mới hoàn toàn) để cập nhật thông tin phòng và giá thuê mới.
*   Anh sẽ thực hiện bàn giao phòng cũ và nhận chìa khóa phòng 202.

**2. Về thời gian chuyển:**
*   Theo quy định, anh cần báo trước tối thiểu **7 ngày** để Ban quản lý chuẩn bị phòng và làm thủ tục.
*   Việc chuyển trong ngày thường chỉ áp dụng cho các trường hợp khẩn cấp. Do đó, để thuận tiện nhất cho anh, chúng ta nên lên kế hoạch chuyển sau 7 ngày kể từ khi chốt lịch anh nhé.

**Thông tin phòng 202 cho anh tham khảo:**
*   **Diện tích:** 28m²
*   **Giá thuê:** 4,000,000đ/tháng
*   **Tiện nghi:** Ban công, Giường, Bàn bếp, Cửa sổ, Nóng lạnh, Điều hòa, Tủ quần áo.

Anh xem xét thời gian dự kiến chuyển rồi báo lại để em làm thủ tục phụ lục hợp đồng cho mình nhé! Nếu cần xem trực tiếp phòng 202 trước khi chốt, anh cho em biết khung giờ, em sẽ sắp xếp ạ.

