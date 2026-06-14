# Kịch bản: Tìm phòng trọ giá rẻ cho sinh viên mới ra trường

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Hoàng Văn Nam |
| Nghề nghiệp | Nhân viên văn phòng mới ra trường |
| Ngân sách | 2.5 - 3.5 triệu/tháng |
| Yêu cầu | Phòng rộng tối thiểu 20m², có cửa sổ thoáng |
| Tone | friendly |

### Kịch bản
Người mới đi làm, đang tìm phòng trọ giá rẻ, ưu tiên phòng thoáng, có chỗ để xe máy. Thực tế DB có 2 phòng phù hợp: 103 (20m², 3tr) và 203 (22m², 3.2tr).

### Câu hỏi mô phỏng
> "Chào anh chị. Em mới đi làm được vài tháng, đang tìm phòng trọ. Bên mình còn phòng nào giá tầm 2.5 đến 3.5 triệu không ạ? Phòng hơi rộng rộng tí, có cửa sổ là được. Với cho em hỏi khu vực đó có chỗ gửi xe máy không? Em cảm ơn."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (budget_max=3.5, min_area=20) + get_room_info + query_policies (cho dau xe)
- Gọi `fetch_available_rooms` với: budget_max=3.5, min_area=20
- Gọi `get_room_info` lấy thông tin các phòng khả dụng
- Gọi `query_policies` RAG về chỗ đậu xe
- Trả về: Danh sách phòng trống phù hợp (103 giá 3tr / 203 giá 3.2tr), thông tin về chỗ đậu xe (100.000đ/tháng), khuyến khích đến xem trực tiếp




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:39:56*

**Turn 1**
- **Câu hỏi**: "Chào anh chị. Em mới đi làm được vài tháng, đang tìm phòng trọ. Bên mình còn phòng nào giá tầm 2.5 đến 3.5 triệu không ạ? Phòng hơi rộng rộng tí, có cửa sổ là được. Với cho em hỏi khu vực đó có chỗ gửi xe máy không? Em cảm ơn."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến nhà trọ của bên mình.

Hiện tại, bên mình có 3 phòng trống phù hợp với ngân sách từ 2.5 đến 3.5 triệu đồng của bạn, tất cả đều có cửa sổ:

*   **Phòng 103 (Tầng 1):** Diện tích 20m², giá 3.000.000đ/tháng.
*   **Phòng 203 (Tầng 2):** Diện tích 22m², giá 3.200.000đ/tháng.
*   **Phòng 303 (Tầng 3):** Diện tích 25m², giá 3.500.000đ/tháng.

Về vấn đề gửi xe, tòa nhà có bãi để xe tại tầng hầm (khu A dành cho xe máy) với phí gửi là **100.000đ/tháng**. Khu vực để xe có camera giám sát và sử dụng thẻ từ ra vào 24/7. Khi ký hợp đồng, bạn chỉ cần cung cấp biển số xe, loại xe và bản photo CCCD của chủ xe để đăng ký là được ạ.

Bạn có muốn sắp xếp thời gian qua xem phòng trực tiếp không? Nếu có, bạn cho mình xin thông tin phòng muốn xem và thời gian cụ thể nhé!

