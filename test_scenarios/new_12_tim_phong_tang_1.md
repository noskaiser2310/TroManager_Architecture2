# Kịch bản: Tìm phòng tầng 1 (không leo cầu thang)

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Văn Đức |
| Nghề nghiệp | Bảo vệ văn phòng |
| Ngân sách | 3 - 4.5 triệu |
| Yêu cầu | Phòng tầng 1, không leo cầu thang, gần nhà xe |
| Phòng phù hợp | 101 (đã thuê), 102 (đã thuê), 103 (còn trống, 3tr) |
| Tone | direct |

### Kịch bản
Khách đứng tuổi, sức khỏe yếu, muốn phòng tầng trệt. Các phòng tầng 1: 101 (occupied), 102 (occupied), 103 (vacant, 20m², 3tr). Cần tư vấn phòng trống tầng 1.

### Câu hỏi mô phỏng
> "Tôi muốn thuê phòng tầng 1 vì chân yếu leo cầu thang không được. Bên mình còn phòng tầng 1 nào trống không? Cho tôi hỏi giá và diện tích. Với để xe ở đâu, có gần không?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (floor=1) + get_room_info + query_policies (gui xe)

### Kịch bản test
- File test: `new_12_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:31:51*

**Turn 1**
- **Câu hỏi**: "Tôi muốn thuê phòng tầng 1 vì chân yếu leo cầu thang không được. Bên mình còn phòng tầng 1 nào trống không? Cho tôi hỏi giá và diện tích. Với để xe ở đâu, có gần không?"
- **Câu trả lời của AI**: Chào anh/chị, rất cảm ơn anh/chị đã quan tâm đến nhà trọ của chúng tôi.

Để hỗ trợ anh/chị thuận tiện trong việc di chuyển, hiện tại bên em còn **phòng 103 ở tầng 1** đang trống. Thông tin chi tiết như sau:
*   **Diện tích:** 20m².
*   **Giá thuê:** 3.000.000đ/tháng.
*   **Sức chứa:** Tối đa 1 người.

Về vấn đề để xe, khu vực để xe của tòa nhà được bố trí tại **tầng hầm** (có camera giám sát và thẻ từ, hoạt động 24/7). Phí gửi xe hàng tháng cụ thể như sau:
*   Xe máy: 100.000đ/tháng.
*   Xe đạp: 50.000đ/tháng.
*   Xe điện: 150.000đ/tháng (đã bao gồm phí sạc tại khu vực quy định).

Anh/chị có muốn đặt lịch qua xem phòng trực tiếp không ạ? Nếu có, anh/chị vui lòng cho em biết thời gian mong muốn nhé!

