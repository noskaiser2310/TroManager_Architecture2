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
*Chạy lúc: 2026-06-15 09:29:17*

**Turn 1**
- **Câu hỏi**: "Chào anh chị. Em mới đi làm được vài tháng, đang tìm phòng trọ. Bên mình còn phòng nào giá tầm 2.5 đến 3.5 triệu không ạ? Phòng hơi rộng rộng tí, có cửa sổ là được. Với cho em hỏi khu vực đó có chỗ gửi xe máy không? Em cảm ơn."
- **Câu trả lời của AI**: Chào bạn, rất vui được hỗ trợ bạn tìm phòng. Hiện tại, bên mình đang có 3 phòng trống phù hợp với ngân sách từ 2.5 đến 3.5 triệu đồng của bạn như sau:

*   **Phòng 103 (Tầng 1):** Diện tích 20m², giá 3.000.000đ/tháng.
*   **Phòng 203 (Tầng 2):** Diện tích 22m², giá 3.200.000đ/tháng.
*   **Phòng 303 (Tầng 3):** Diện tích 25m², giá 3.500.000đ/tháng.

Các phòng này đều đảm bảo không gian rộng rãi và có cửa sổ thoáng mát.

Về vấn đề gửi xe, tòa nhà có khu vực để xe máy tại tầng hầm, hoạt động 24/7 với hệ thống camera giám sát và thẻ từ. Phí gửi xe máy là 100.000đ/tháng. Khi ký hợp đồng, bạn chỉ cần đăng ký biển số xe và loại xe với quản lý là được ạ.

Nếu bạn muốn ghé xem phòng trực tiếp, hãy cho mình biết thời gian thuận tiện nhé!

