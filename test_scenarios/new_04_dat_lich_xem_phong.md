# Kịch bản: Đặt lịch xem phòng trực tiếp

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Phạm Thị Nhung |
| Nghề nghiệp | Nhân viên ngân hàng |
| Ngân sách | 3 - 4.5 triệu |
| Phòng muốn xem | 303 (tầng 3, 25m², 3.500.000đ/tháng) |
| Thời gian rảnh | Cuối tuần (CN) hoặc sau 18h |
| Tone | friendly, gấp |

### Kịch bản
Khách đã xem ảnh phòng trên web và ưng phòng 303. Muốn đặt lịch đến xem trực tiếp vào Chủ Nhật.

### Câu hỏi mô phỏng
> "Em chào anh chị. Em có xem phòng 303 trên web và thấy cũng ưng. Cuối tuần này em rảnh Chủ Nhật, không biết bên mình có thể sắp xếp cho em qua xem phòng được không ạ? Khoảng 10h sáng em qua được. Em ở gần đó nên đi lại cũng tiện."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms kiem tra 303 con trong + get_room_info + schedule_room_viewing
- Gọi `fetch_available_rooms` kiểm tra 303 còn trống không
- Gọi `get_room_info` lấy thông tin
- Gọi `schedule_room_viewing` tạo appointment (room_id=303, scheduled_at=Chủ nhật 10h)
- Trả về: Xác nhận lịch hẹn, địa chỉ, số điện thoại liên hệ khi đến




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:40:54*

**Turn 1**
- **Câu hỏi**: "Em chào anh chị. Em có xem phòng 303 trên web và thấy cũng ưng. Cuối tuần này em rảnh Chủ Nhật, không biết bên mình có thể sắp xếp cho em qua xem phòng được không ạ? Khoảng 10h sáng em qua được. Em ở gần đó nên đi lại cũng tiện."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng 303 tại nhà trọ của chúng tôi.

Tôi đã kiểm tra thông tin, phòng 303 hiện đang trống. Tôi rất vui lòng sắp xếp lịch hẹn để bạn qua xem phòng vào **10:00 sáng Chủ Nhật, ngày 21/06/2026** như bạn mong muốn.

Để hoàn tất việc đặt lịch, bạn vui lòng cung cấp cho tôi **họ tên và số điện thoại liên hệ** của bạn nhé. Sau khi nhận được thông tin, tôi sẽ xác nhận lịch hẹn chính thức với bạn.

