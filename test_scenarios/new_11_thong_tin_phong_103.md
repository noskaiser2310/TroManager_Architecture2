# Kịch bản: Hỏi thông tin chi tiết phòng 103

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Thị Mai |
| Nghề nghiệp | Nhân viên kế toán |
| Ngân sách | 3 triệu |
| Yêu cầu | Phòng nhỏ, đủ ở 1 mình, có cửa sổ, gần mặt tiền |
| Tone | friendly |

### Kịch bản
Khách nữ muốn thuê phòng giá 3tr, thấy phòng 103 có giá phù hợp. Hỏi chi tiết về diện tích, tiện nghi, và xem còn trống không.

### Câu hỏi mô phỏng
> "Anh chị ơi, em thấy phòng 103 có giá 3 triệu đúng không ạ? Cho em hỏi phòng còn trống không, diện tích bao nhiêu, có cửa sổ không? Có chỗ phơi đồ riêng không ạ? Em định qua xem cuối tuần."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> get_room_by_number (room_number=103) + query_policies (tien nghi)

### Kịch bản test
- File test: `new_11_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:31:38*

**Turn 1**
- **Câu hỏi**: "Anh chị ơi, em thấy phòng 103 có giá 3 triệu đúng không ạ? Cho em hỏi phòng còn trống không, diện tích bao nhiêu, có cửa sổ không? Có chỗ phơi đồ riêng không ạ? Em định qua xem cuối tuần."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ. Mình xin giải đáp các thắc mắc của bạn về phòng 103 như sau:

*   **Tình trạng:** Phòng 103 hiện đang **còn trống**.
*   **Giá thuê:** 3.000.000đ/tháng.
*   **Diện tích:** 20m².
*   **Tiện nghi:** Phòng có **cửa sổ**, cùng các nội thất cơ bản như: giường, bàn bếp, nóng lạnh, điều hòa và tủ quần áo.
*   **Chỗ phơi đồ:** Nhà trọ có khu vực sân phơi đồ rộng rãi tại sân thượng (dùng chung cho cư dân tòa nhà).

Về việc bạn muốn qua xem phòng vào cuối tuần này, bạn vui lòng cho mình biết thời gian cụ thể (ngày và giờ) để mình đặt lịch hẹn cho bạn nhé!

