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
*Chạy lúc: 2026-06-15 00:41:54*

**Turn 1**
- **Câu hỏi**: "Xin chào. Tôi muốn tìm phòng cho mẹ tôi ở, bà đã 70 tuổi rồi nên đi lại khó khăn. Bên mình có phòng nào tầng trệt không ạ? Tôi thấy có phòng 103 tầng 1, cho tôi hỏi phòng đó có gần nhà vệ sinh không? Có thoáng mát không? Khu vực có yên tĩnh cho người già nghỉ ngơi không? Giá 3tr có thêm phí gì không? Cảm ơn."
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến nhà trọ. Tôi xin giải đáp các thắc mắc của anh/chị về phòng 103 như sau:

**1. Về vị trí và không gian:**
*   **Tầng trệt:** Hiện tại chúng tôi có phòng 103 ở tầng 1 (tầng trệt), rất thuận tiện cho việc đi lại của người cao tuổi.
*   **Độ thoáng mát:** Phòng có diện tích 20m², được trang bị cửa sổ hướng Bắc, điều hòa Panasonic 9000BTU và hệ thống nóng lạnh gián tiếp, đảm bảo không gian nghỉ ngơi thoải mái.
*   **Sự yên tĩnh:** Nhà trọ có nội quy về sử dụng tiện ích và giữ gìn vệ sinh chung. Tuy nhiên, vì đây là khu vực nhà trọ, nếu anh/chị cần không gian đặc biệt yên tĩnh, anh/chị có thể ghé qua xem trực tiếp để cảm nhận thực tế môi trường xung quanh.

**2. Về chi phí:**
Ngoài giá thuê phòng là 3.000.000đ/tháng, các chi phí phát sinh bao gồm:
*   **Phí dịch vụ:** 50.000đ/tháng.
*   **Điện:** 3.500đ/kWh.
*   **Nước:** 100.000đ/m³.
*   **Phí gửi xe (nếu có):** Xe máy 100.000đ/tháng, xe đạp 50.000đ/tháng, xe điện 150.000đ/tháng.

**3. Về nhà vệ sinh:**
Phòng 103 được trang bị đầy đủ tiện nghi khép kín. Để biết chính xác vị trí nhà vệ sinh có gần khu vực sinh hoạt chung hay không, tôi mời anh/chị sắp xếp thời gian qua xem phòng trực tiếp.

Nếu anh/chị muốn đặt lịch xem phòng, vui lòng cho tôi biết thời gian cụ thể, tôi sẽ hỗ trợ anh/chị đặt lịch ạ.

