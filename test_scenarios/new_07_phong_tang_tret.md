# Kịch bản: Yêu cầu phòng tầng trệt cho người già

## Loại nhân vật: Khách mới đang tìm hiểu (thuê cho người thân)

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lâm Văn Đông |
| Người thuê | Mẹ ruột (70 tuổi) |
| Yêu cầu | Phòng tầng trệt, không leo cầu thang |
| Ngân sách | 3 - 4 triệu |
| Phòng phù hợp | 103 (tầng 1, 20m², 3tr) — là phòng tầng trệt duy nhất còn trống |
| Tone | professional, lo lắng |

### Kịch bản
Khách muốn tìm phòng cho mẹ già ở, cần phòng tầng trệt để tiện đi lại. Chỉ có phòng 103 (tầng 1, 20m², 3.000.000đ) là phù hợp.

### Câu hỏi mô phỏng
> "Xin chào. Tôi muốn tìm phòng cho mẹ tôi ở, bà đã 70 tuổi rồi nên đi lại khó khăn. Bên mình có phòng nào tầng trệt không ạ? Tôi thấy có phòng 103 tầng 1, cho tôi hỏi phòng đó có gần nhà vệ sinh không? Có thoáng mát không? Khu vực có yên tĩnh cho người già nghỉ ngơi không? Giá 3tr có thêm phí gì không? Cảm ơn."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (floor=1) + get_room_info
- Gọi `fetch_available_rooms` với: floor=1
- Gọi `get_room_info` cho phòng 103 (20m², cửa sổ hướng bắc, amenities)
- Gọi `query_policies` về an ninh, giờ giấc
- Trả về: Thông tin phòng 103, an ninh (khoá cửa, camera), môi trường yên tĩnh


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:30:43*

**Turn 1**
- **Câu hỏi**: "Xin chào. Tôi muốn tìm phòng cho mẹ tôi ở, bà đã 70 tuổi rồi nên đi lại khó khăn. Bên mình có phòng nào tầng trệt không ạ? Tôi thấy có phòng 103 tầng 1, cho tôi hỏi phòng đó có gần nhà vệ sinh không? Có thoáng mát không? Khu vực có yên tĩnh cho người già nghỉ ngơi không? Giá 3tr có thêm phí gì không? Cảm ơn."
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến nhà trọ. Tôi xin giải đáp các thắc mắc của anh/chị về phòng 103 như sau:

**1. Về phòng 103 (Tầng 1):**
*   **Tiện lợi:** Phòng nằm ở tầng 1, rất thuận tiện cho người cao tuổi đi lại.
*   **Thông tin phòng:** Diện tích 20m², được trang bị sẵn giường, bàn bếp, cửa sổ, nóng lạnh, điều hòa và tủ quần áo.
*   **Không gian:** Phòng có cửa sổ nên khá thoáng mát. Về nhà vệ sinh, đây là phòng khép kín (có nhà vệ sinh riêng trong phòng), nên rất thuận tiện cho việc sinh hoạt cá nhân của mẹ anh/chị.

**2. Về sự yên tĩnh:**
*   Nhà trọ có quy định khung giờ yên tĩnh tuyệt đối từ **22:00 đến 06:00** (thứ 2 - thứ 6) và đến **07:00** (thứ 7, Chủ nhật). Trong khung giờ này, các hoạt động gây ồn như hát karaoke, mở nhạc lớn đều bị cấm.
*   Hệ thống an ninh bao gồm camera tại hành lang và đèn cảm biến chuyển động, đảm bảo môi trường sống an toàn và trật tự.

**3. Về chi phí:**
Ngoài giá thuê phòng là 3.000.000đ/tháng, các chi phí phát sinh hàng tháng bao gồm:
*   **Điện:** 3.500đ/kWh (có đồng hồ riêng).
*   **Nước:** 100.000đ/m³.
*   **Phí rác & Vệ sinh chung:** 50.000đ/phòng/tháng.
*   **Internet/Wifi:** Miễn phí.
*   **Gửi xe máy (nếu có):** 100.000đ/xe/tháng.

Nếu anh/chị muốn đưa mẹ đến xem trực tiếp phòng, anh/chị có thể cho tôi biết thời gian cụ thể, tôi sẽ hỗ trợ đặt lịch hẹn cho mình ạ.

