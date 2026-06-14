# Kịch bản: Khách cũ từng ở trước đây muốn quay lại

## Loại nhân vật: Khách mới đang tìm hiểu (old tenant returning)

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trương Minh Tâm |
| Trước đây | Từng ở phòng 201 (dưới tên người thân — Lê Hoàng Tuấn), đã trả phòng sạch sẽ |
| Lý do rời | Chuyển việc tạm thời |
| Bây giờ | Trở lại thành phố, muốn thuê phòng riêng |
| Ngân sách | 3 - 4 triệu |
| Phòng phù hợp | 203 (22m², 3.2tr, máy lạnh) hoặc 303 (25m², 3.5tr, yên tĩnh) |
| Tone | friendly, quen thuộc |

### Kịch bản
Khách từng ở đây dưới tên người thân, nay trở lại muốn thuê phòng riêng. Nên gợi ý phòng tầng 2-3 vì khách có thể quen khu vực tầng 2 (từng ở 201).

### Câu hỏi mô phỏng
> "Anh chị quản lý còn nhớ em không? Em Tâm, hồi trước em ở phòng 201 với ông Tuấn (Lê Hoàng Tuấn) hồi năm ngoái ý. Nay em quay lại thành phố làm việc, muốn thuê phòng riêng bên mình tiếp. Còn phòng nào đẹp không ạ? Ưu tiên phòng tầng 2-3, có máy lạnh, giá tốt. Khách cũ như em có được giảm chút đỉnh không ạ? Em hồi trước trả phòng sạch sẽ mà đúng hạn nữa."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> get_contract_status + get_invoice_detail + fetch_available_rooms
- Gọi `fetch_available_rooms` tìm phòng phù hợp (tầng 2-3, máy lạnh)
- Tra cứu lịch sử (Tâm có trong DB không? Có thể không có user profile riêng, nhưng có thể tìm qua tên)
- Gọi `recommend_renewal` kiểm tra profile
- Gọi `query_policies` về ưu đãi khách cũ
- Trả về: Chào mừng khách cũ, danh sách phòng trống (203, 303), ưu đãi cho khách quay lại



---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:43:00*

**Turn 1**
- **Câu hỏi**: "Anh chị quản lý còn nhớ em không? Em Tâm, hồi trước em ở phòng 201 với ông Tuấn (Lê Hoàng Tuấn) hồi năm ngoái ý. Nay em quay lại thành phố làm việc, muốn thuê phòng riêng bên mình tiếp. Còn phòng nào đẹp không ạ? Ưu tiên phòng tầng 2-3, có máy lạnh, giá tốt. Khách cũ như em có được giảm chút đỉnh không ạ? Em hồi trước trả phòng sạch sẽ mà đúng hạn nữa."
- **Câu trả lời của AI**: Chào bạn Tâm, rất vui được gặp lại bạn! Ban quản lý vẫn lưu giữ thông tin khách hàng cũ, rất cảm ơn bạn đã tin tưởng quay lại thuê phòng bên mình.

Hiện tại, bên mình đang có một số phòng trống ở tầng 2 và tầng 3 phù hợp với yêu cầu của bạn:

*   **Phòng 202 (Tầng 2):** Diện tích 28m², giá 4.000.000đ/tháng.
*   **Phòng 203 (Tầng 2):** Diện tích 22m², giá 3.200.000đ/tháng.
*   **Phòng 303 (Tầng 3):** Diện tích 25m², giá 3.500.000đ/tháng.

Tất cả các phòng đều được trang bị máy lạnh đầy đủ.

Về vấn đề ưu đãi cho khách cũ, chính sách bên mình hiện tập trung vào các ưu đãi gia hạn hợp đồng dài hạn (giảm 5% cho hợp đồng 12 tháng và 10% cho hợp đồng 24 tháng). Tuy nhiên, vì bạn là khách hàng cũ từng có lịch sử trả phòng sạch sẽ và đúng hạn, mình sẽ ghi nhận thông tin này và trao đổi thêm với quản lý để xem xét có hỗ trợ thêm cho bạn khi làm hợp đồng mới nhé.

Bạn có muốn ghé qua xem trực tiếp phòng nào không? Nếu có, hãy cho mình biết thời gian cụ thể, mình sẽ đặt lịch hẹn cho bạn nhé!

