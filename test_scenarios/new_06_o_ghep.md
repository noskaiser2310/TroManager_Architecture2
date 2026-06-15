# Kịch bản: Hỏi về chính sách ở ghép

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Mai Thị Yến |
| Nghề nghiệp | Nhân viên spa |
| Ở cùng | Bạn thân (2 người) |
| Ngân sách | 4 - 5 triệu (tổng 2 người) |
| Phòng phù hợp | 202 (28m², 4tr, rộng nhất, ban công) |
| Tone | friendly |

### Kịch bản
Khách muốn thuê cùng bạn, cần phòng đủ rộng cho 2 người. Phòng 202 (28m²) là rộng nhất trong các phòng trống. Tuy nhiên max_occupants default là 1, cần check policy cho phép ở ghép không.

### Câu hỏi mô phỏng
> "Chào anh chị, em với bạn em định thuê chung một phòng. Bên mình có cho thuê 2 người ở chung một phòng không ạ? Bọn em cần phòng hơi rộng rộng tí, thấy phòng 202 có 28m², ban công rộng, giá 4tr có vẻ ok. Có bị tính thêm phí người không ạ? Và mình có thể xem phòng được không?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (phong rong >25m2) + query_policies (quy dinh o ghep)
- Gọi `query_policies` tra chính sách số người/phòng, phụ phí
- Gọi `fetch_available_rooms` với min_area=25, max_budget=5
- Gọi `get_room_info` xem phòng 202
- Trả về: Chính sách ở ghép, phòng 202 phù hợp, hướng dẫn thủ tục


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:30:27*

**Turn 1**
- **Câu hỏi**: "Chào anh chị, em với bạn em định thuê chung một phòng. Bên mình có cho thuê 2 người ở chung một phòng không ạ? Bọn em cần phòng hơi rộng rộng tí, thấy phòng 202 có 28m², ban công rộng, giá 4tr có vẻ ok. Có bị tính thêm phí người không ạ? Và mình có thể xem phòng được không?"
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ của chúng mình.

Về các thắc mắc của bạn, mình xin được giải đáp như sau:

1. **Về việc ở ghép:** Theo thông tin hệ thống, phòng 202 hiện được quy định số người tối đa là 1 người. Do đó, phòng này không phù hợp để ở 2 người.
2. **Về phí người ở chung:** Hiện tại, chính sách của tòa nhà quy định số người tối đa cho từng phòng. Việc ở quá số người quy định là không đúng nội quy.
3. **Về việc xem phòng:** Bạn hoàn toàn có thể qua xem phòng trực tiếp. Để thuận tiện, bạn vui lòng cho mình biết thời gian cụ thể (ngày, giờ) bạn muốn đến, mình sẽ hỗ trợ đặt lịch hẹn cho bạn nhé.

Nếu bạn cần tìm phòng có diện tích rộng hơn cho 2 người ở, hãy cho mình biết ngân sách dự kiến, mình sẽ hỗ trợ tìm các phòng phù hợp hơn cho bạn và bạn của bạn.

