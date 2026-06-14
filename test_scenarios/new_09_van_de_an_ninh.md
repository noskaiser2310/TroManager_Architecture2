# Kịch bản: Hỏi về an ninh, khoá cửa, camera

## Loại nhân vật: Khách mới đang tìm hiểu (nữ)

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Hoàng Thị Thanh |
| Nghề nghiệp | Y tá |
| Ngân sách | 3 - 4.5 triệu |
| Ưu tiên | An ninh, an toàn |
| Phòng hướng đến | 203 (3.2tr, 22m²) hoặc 303 (3.5tr, 25m²) |
| Tone | cẩn thận |

### Kịch bản
Khách là nữ ở một mình, ưu tiên an ninh hàng đầu. Hay trực đêm nên đi về khuya, cần phòng an toàn.

### Câu hỏi mô phỏng
> "Em chào anh chị. Em là nữ ở một mình nên hơi lo về an ninh. Bên mình có khoá vân tay hay khoá thẻ từ không? Có camera hành lang không? Có bảo vệ trực không ạ? Khu vực xung quanh an ninh tốt không? Em làm y tá hay trực đêm, về khuya nên sợ. Anh chị tư vấn giúp em phòng nào an toàn nhất với ạ."

### Hệ thống kỳ vọng xử lý
- Router -> System 1 -> query_policies (an ninh, camera, kiem soat)
- Gọi `get_room_info` xem amenities
- Gọi `query_policies` về an ninh (khoá cửa, camera, bảo vệ)
- Gọi `fetch_available_rooms` tìm phòng phù hợp
- Trả về: Thông tin an ninh, loại khoá, camera, tư vấn phòng tầng cao (303) hoặc gần cửa chính



---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:42:40*

**Turn 1**
- **Câu hỏi**: "Em chào anh chị. Em là nữ ở một mình nên hơi lo về an ninh. Bên mình có khoá vân tay hay khoá thẻ từ không? Có camera hành lang không? Có bảo vệ trực không ạ? Khu vực xung quanh an ninh tốt không? Em làm y tá hay trực đêm, về khuya nên sợ. Anh chị tư vấn giúp em phòng nào an toàn nhất với ạ."
- **Câu trả lời của AI**: Chào bạn, rất vui được hỗ trợ bạn. Về vấn đề an ninh mà bạn quan tâm, mình xin giải đáp các thông tin như sau:

**1. Hệ thống an ninh tòa nhà:**
*   **Camera:** Hệ thống camera được lắp đặt tại cổng chính, hành lang các tầng, khu vực để xe và sân thượng, dữ liệu được lưu trữ trong 30 ngày.
*   **Bảo vệ:** Tòa nhà có bảo vệ trực 24/7 (Số điện thoại liên hệ: 0901-234-568).
*   **Khóa cửa:** Hiện tại tòa nhà sử dụng hệ thống khóa cơ truyền thống (mỗi phòng được cấp 2 chìa khóa khi ký hợp đồng). Theo quy định, bạn không được tự ý đổi ổ khóa hoặc lắp thêm khóa phụ.
*   **An ninh khu vực:** Tòa nhà nằm trong khu vực an ninh ổn định, tuy nhiên để đảm bảo an toàn tuyệt đối, bạn nên tuân thủ các quy định ra vào.

**2. Lưu ý cho công việc của bạn:**
Vì bạn làm y tá và thường xuyên về khuya, bạn cần lưu ý:
*   Cổng chính sẽ tự động đóng từ 23h đêm đến 5h30 sáng hôm sau. Bạn nên liên hệ trước với bảo vệ để được hỗ trợ mở cửa khi về muộn.
*   Tòa nhà có đèn cảm biến chuyển động tại hành lang tầng 1 và tầng trên cùng giúp chiếu sáng khi bạn di chuyển vào ban đêm.

**3. Tư vấn chọn phòng:**
Để đảm bảo an toàn và thuận tiện nhất cho bạn, mình gợi ý bạn nên ưu tiên các phòng ở **tầng 1 hoặc tầng 2** (gần khu vực có đèn cảm biến hành lang và dễ dàng di chuyển ra vào). 

Để kiểm tra chính xác các phòng trống hiện có và tư vấn chi tiết hơn, bạn có thể cho mình biết **ngân sách dự kiến** hoặc **diện tích phòng mong muốn** không? Mình sẽ tra cứu danh sách phòng trống phù hợp nhất cho bạn ngay.

