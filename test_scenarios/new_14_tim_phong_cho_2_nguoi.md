# Kịch bản: Tìm phòng cho 2 người ở

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Võ Hoàng Nam |
| Nghề nghiệp | Sinh viên ĐH Công Nghệ |
| Ngân sách | 3 - 4.5 triệu |
| Yêu cầu | Phòng trên 25m², đủ cho 2 người, có ban công hoặc cửa sổ |
| Phòng phù hợp | 202 (28m², 4tr, ban công rộng), 303 (25m², 3.5tr) |
| Tone | friendly |

### Kịch bản
Khách là sinh viên muốn ở ghép với bạn, cần phòng rộng tầm 25-30m², giá cả phải chăng, có chỗ học tập riêng.

### Câu hỏi mô phỏng
> "Tụi em 2 đứa ở chung, đang tìm phòng khoảng hơn 25m², có chỗ để 2 cái bàn học với cửa sổ cho thoáng. Tụi em cần tầm 2 cái giường riêng, không ngủ chung. Bên mình có phòng nào như vậy không ạ? Giá tụi em lo được tầm 4tr đổ lại."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (min_area=25, budget_max=4.5) + get_room_by_number (202, 303) + query_policies (o ghep)

### Kịch bản test
- File test: `new_14_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:32:18*

**Turn 1**
- **Câu hỏi**: "Tụi em 2 đứa ở chung, đang tìm phòng khoảng hơn 25m², có chỗ để 2 cái bàn học với cửa sổ cho thoáng. Tụi em cần tầm 2 cái giường riêng, không ngủ chung. Bên mình có phòng nào như vậy không ạ? Giá tụi em lo được tầm 4tr đổ lại."
- **Câu trả lời của AI**: Chào hai bạn, cảm ơn các bạn đã quan tâm đến nhà trọ.

Dựa trên yêu cầu của hai bạn (diện tích trên 25m², giá dưới 4 triệu), mình đã kiểm tra và hiện có 2 phòng trống là **phòng 202 (28m²)** và **phòng 303 (25m²)**.

Tuy nhiên, mình cần lưu ý với hai bạn một số điểm quan trọng sau:
1. **Số lượng người ở:** Theo dữ liệu hệ thống, các phòng này hiện được quy định tối đa cho 1 người ở.
2. **Tiện nghi:** Các phòng này được trang bị cơ bản, mình cần kiểm tra lại xem có đủ diện tích và cho phép bố trí 2 giường đơn hay không.

Để đảm bảo quyền lợi và sự thoải mái cho hai bạn, mình khuyên hai bạn nên đến xem trực tiếp để kiểm tra không gian thực tế xem có phù hợp để kê 2 bàn học và 2 giường đơn như mong muốn không.

Hai bạn có muốn đặt lịch hẹn để mình dẫn đi xem phòng trực tiếp không ạ? Nếu có, các bạn cho mình xin thời gian cụ thể nhé!

