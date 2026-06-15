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
*Chạy lúc: 2026-06-15 09:29:47*

**Turn 1**
- **Câu hỏi**: "Xin chào. Tôi đang quan tâm phòng 202 bên anh chị. Cho tôi hỏi vài vấn đề: Thứ nhất, tiền cọc bao nhiêu tháng? Có được hoàn lại không nếu tôi ở hết hợp đồng? Hợp đồng tối thiểu bao nhiêu tháng? Ngoài 4tr tiền phòng còn phí quản lý, phí rác, phí gửi xe gì không? Tổng tất cả mỗi tháng khoảng bao nhiêu? Xin cảm ơn."
- **Câu trả lời của AI**: Chào Quý khách, cảm ơn Quý khách đã quan tâm đến phòng 202. TroBot xin giải đáp các thắc mắc của Quý khách như sau:

**1. Tiền cọc và hoàn cọc:**
*   **Tiền cọc:** Quý khách cần đặt cọc **2 tháng tiền phòng**.
*   **Hoàn cọc:** Tiền cọc sẽ được hoàn trả 100% khi kết thúc hợp đồng nếu không có các khoản khấu trừ (như hư hỏng nội thất, nợ phí dịch vụ, vi phạm hợp đồng...). Quý khách cần báo trước 30 ngày để thực hiện thủ tục hoàn cọc.

**2. Thời hạn hợp đồng:**
*   Hợp đồng tối thiểu là **1 tháng** (cho thuê ngắn hạn). Ngoài ra, chúng tôi có các gói dài hạn (6-12 tháng hoặc 13-24 tháng) với ưu đãi giảm giá tiền phòng từ 5-10%.

**3. Chi phí hàng tháng:**
Ngoài tiền phòng 4.000.000đ, các chi phí hàng tháng bao gồm:
*   **Phí dịch vụ (Rác & Vệ sinh chung):** 50.000đ/phòng/tháng.
*   **Phí gửi xe máy:** 100.000đ/xe/tháng.
*   **Điện:** 3.500đ/kWh (theo đồng hồ riêng).
*   **Nước:** 100.000đ/m³.
*   **Internet/Wifi:** Miễn phí tốc độ cao.

**Tổng chi phí:**
Tổng tiền mỗi tháng sẽ bao gồm tiền phòng (4tr) + phí dịch vụ (50k) + phí gửi xe (nếu có) + tiền điện/nước thực tế sử dụng.

Nếu Quý khách muốn đến xem phòng trực tiếp, hãy cho tôi biết thời gian mong muốn, tôi sẽ hỗ trợ đặt lịch cho Quý khách ạ!

