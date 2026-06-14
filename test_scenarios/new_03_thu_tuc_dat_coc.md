# Kịch bản: Hỏi về thủ tục đặt cọc và hợp đồng

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lý Văn Phát |
| Nghề nghiệp | Kỹ sư xây dựng |
| Ngân sách | 4 - 5 triệu |
| Phòng quan tâm | 202 (28m², 4tr, ban công rộng) |
| Lần đầu thuê trọ | Có |
| Tone | professional, dè dặt |

### Kịch bản
Khách lần đầu thuê trọ, muốn tìm hiểu kỹ thủ tục trước khi cam kết. Phòng 202 rộng 28m² giá 4tr/tháng là lựa chọn hàng đầu.

### Câu hỏi mô phỏng
> "Xin chào. Tôi đang quan tâm phòng 202 bên anh chị. Cho tôi hỏi vài vấn đề: Thứ nhất, tiền cọc bao nhiêu tháng? Có được hoàn lại không nếu tôi ở hết hợp đồng? Hợp đồng tối thiểu bao nhiêu tháng? Ngoài 4tr tiền phòng còn phí quản lý, phí rác, phí gửi xe gì không? Tổng tất cả mỗi tháng khoảng bao nhiêu? Xin cảm ơn."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> get_room_info (phong 202) + query_policies (coc, hop dong, phi) + calc_rent uoc tinh
- Gọi `query_policies` RAG về chính sách đặt cọc, hợp đồng, phí
- Gọi `get_room_info` cho phòng 202
- Gọi `calc_rent` ước tính: 4.000.000đ (rent) + ước tính điện/nước/dịch vụ
- Trả về: Chi tiết tiền cọc, điều kiện hoàn cọc, thời hạn hợp đồng, các loại phí kèm




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:40:37*

**Turn 1**
- **Câu hỏi**: "Xin chào. Tôi đang quan tâm phòng 202 bên anh chị. Cho tôi hỏi vài vấn đề: Thứ nhất, tiền cọc bao nhiêu tháng? Có được hoàn lại không nếu tôi ở hết hợp đồng? Hợp đồng tối thiểu bao nhiêu tháng? Ngoài 4tr tiền phòng còn phí quản lý, phí rác, phí gửi xe gì không? Tổng tất cả mỗi tháng khoảng bao nhiêu? Xin cảm ơn."
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến phòng 202. Tôi xin giải đáp các thắc mắc của anh/chị như sau:

**1. Về đặt cọc và hợp đồng:**
*   **Tiền cọc:** Anh/chị cần đặt cọc **2 tháng tiền phòng** (bao gồm 1 tháng cọc và 1 tháng trả trước).
*   **Hoàn cọc:** Tiền cọc sẽ được hoàn lại khi anh/chị kết thúc hợp đồng đúng hạn, đã thanh toán đầy đủ các khoản phí và trả phòng trong tình trạng ban đầu.
*   **Thời hạn hợp đồng:** Hợp đồng có các mốc từ 1-5 tháng (ngắn hạn) hoặc 6-24 tháng (dài hạn). Anh/chị có thể linh hoạt chọn thời hạn phù hợp với nhu cầu.

**2. Về chi phí hàng tháng:**
Ngoài tiền phòng là **4,000,000đ/tháng**, các chi phí dịch vụ tại phòng 202 bao gồm:
*   **Phí dịch vụ:** 50,000đ/tháng.
*   **Điện:** 3,500đ/kWh.
*   **Nước:** 100,000đ/m³.
*   **Phí khác:** Các khoản phí như phí rác, phí gửi xe (nếu có) sẽ được quy định chi tiết trong phụ lục hợp đồng.

**Tổng chi phí hàng tháng:** Sẽ bao gồm tiền phòng, phí dịch vụ và tiền điện, nước thực tế sử dụng. Do đó, tổng số tiền sẽ thay đổi tùy thuộc vào mức tiêu thụ điện, nước của anh/chị mỗi tháng.

Nếu anh/chị muốn đến xem phòng trực tiếp, hãy cho tôi biết thời gian cụ thể, tôi sẽ hỗ trợ đặt lịch cho anh/chị nhé!

