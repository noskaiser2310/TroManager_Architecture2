# Kịch bản: Hỏi các dịch vụ và tiện ích đi kèm

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Vũ Thị Mai Lan |
| Nghề nghiệp | Nhân viên ngân hàng |
| Ngân sách | 4-5 triệu |
| Yêu cầu | Phòng sạch sẽ, có dịch vụ giặt ủi/dọn vệ sinh, gửi xe máy |
| Tone | friendly |

### Kịch bản
Khách nữ làm ngân hàng bận rộn, muốn tìm phòng có dịch vụ tiện ích đi kèm để đỡ mất thời gian lo chuyện nhà.

### Câu hỏi mô phỏng
> "Chào anh chị, em đang tìm phòng trọ có sẵn tiện ích. Bên mình có dịch vụ giặt ủi không? Có dọn vệ sinh hàng tuần hay hàng tháng không? Chỗ để xe máy có mất phí không? Có wifi chung hay mỗi phòng tự đăng ký? Và có máy giặt chung không ạ?"

### Hệ thống kỳ vọng xử lý
- Router -> System 1 -> query_policies (dich vu tien ich, gui xe, wifi, may giat)

### Kịch bản test
- File test: `new_20_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:33:40*

**Turn 1**
- **Câu hỏi**: "Chào anh chị, em đang tìm phòng trọ có sẵn tiện ích. Bên mình có dịch vụ giặt ủi không? Có dọn vệ sinh hàng tuần hay hàng tháng không? Chỗ để xe máy có mất phí không? Có wifi chung hay mỗi phòng tự đăng ký? Và có máy giặt chung không ạ?"
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến dịch vụ tại nhà trọ. Dưới đây là thông tin chi tiết về các tiện ích bạn đang quan tâm:

*   **Dịch vụ giặt ủi:** Nhà trọ có trang bị máy giặt chung tại sân thượng để bạn tự phục vụ với phí 20.000đ/lần.
*   **Dọn vệ sinh:** Chúng tôi có dịch vụ dọn vệ sinh phòng hàng tuần (1 lần/tuần, 2 tiếng/lần) với chi phí 200.000đ/tháng. Đối với khu vực chung (hành lang, cầu thang), quản lý sẽ thực hiện vệ sinh hàng ngày.
*   **Chỗ để xe máy:** Có mất phí, mức phí là 100.000đ/tháng/xe.
*   **Wifi:** Internet đã bao gồm trong phí dịch vụ. Nếu bạn có nhu cầu sử dụng tốc độ cao hơn, bạn có thể liên hệ quản lý để đăng ký nâng cấp với mức phí riêng.

Nếu bạn cần tư vấn thêm về phòng trống hoặc muốn đặt lịch xem phòng, hãy cho mình biết nhé!

