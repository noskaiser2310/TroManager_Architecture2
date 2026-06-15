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
*Chạy lúc: 2026-06-15 09:31:10*

**Turn 1**
- **Câu hỏi**: "Em chào anh chị. Em là nữ ở một mình nên hơi lo về an ninh. Bên mình có khoá vân tay hay khoá thẻ từ không? Có camera hành lang không? Có bảo vệ trực không ạ? Khu vực xung quanh an ninh tốt không? Em làm y tá hay trực đêm, về khuya nên sợ. Anh chị tư vấn giúp em phòng nào an toàn nhất với ạ."
- **Câu trả lời của AI**: Chào bạn, rất cảm ơn bạn đã quan tâm đến nhà trọ. Với đặc thù công việc y tá và thường xuyên về khuya, mình xin giải đáp các thắc mắc về an ninh để bạn yên tâm hơn như sau:

**Về hệ thống an ninh:**
*   **Camera:** Hệ thống camera an ninh được lắp đặt tại cổng chính, hành lang các tầng, khu để xe và sân thượng, dữ liệu được lưu trữ trong 30 ngày.
*   **Bảo vệ:** Nhà trọ có nhân viên trông xe vào ban đêm và có số điện thoại hỗ trợ bảo vệ 24/7 (0901-234-568).
*   **Khóa cửa:** Hiện tại các phòng sử dụng chìa khóa cơ truyền thống (mỗi phòng được cấp 2 chìa khi ký hợp đồng). Theo quy định, bạn không được tự ý đổi ổ khóa hoặc lắp thêm khóa phụ.
*   **Khu vực:** Nhà trọ có cổng chính tự đóng từ 23h đến 5h30 sáng hôm sau để đảm bảo an ninh chung.

**Lời khuyên cho bạn:**
Vì bạn thường xuyên về khuya, bạn nên lưu lại số điện thoại của quản lý (0901-234-567) và bảo vệ để liên hệ khi cần hỗ trợ mở cửa hoặc gặp vấn đề an ninh.

Để tư vấn phòng phù hợp nhất, bạn có thể cho mình biết **ngân sách thuê phòng dự kiến** của bạn là bao nhiêu không ạ? Mình sẽ kiểm tra danh sách phòng trống hiện có để ưu tiên các phòng ở vị trí thuận tiện, gần cầu thang hoặc có tầm nhìn tốt ra khu vực hành lang có camera cho bạn nhé.

