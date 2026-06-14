# Kịch bản: Hỏi về tiện nghi và chất lượng internet

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trịnh Hoàng Long |
| Nghề nghiệp | IT remote |
| Ngân sách | 4 - 5 triệu |
| Yêu cầu | Internet tốc độ cao, yên tĩnh, máy lạnh |
| Phòng phù hợp | 202 (28m², 4tr, ban công, máy lạnh Daikin) |
| Tone | direct, technical |

### Kịch bản
Khách làm IT remote cần internet mạnh, phòng yên tĩnh để làm việc. Phòng 202 có amenities tốt nhất (máy lạnh Daikin 12000BTU, nóng lạnh năng lượng mặt trời, ban công rộng, hướng nam thoáng mát). TKT-0002 (wifi chập chờn ở phòng 102) có thể được nhắc đến nếu khách hỏi về độ ổn định.

### Câu hỏi mô phỏng
> "Hi. Tôi làm remote IT nên cần internet ổn định, tốc độ cao. Bên bạn dùng mạng gì? Bao nhiêu Mbps? Có dây LAN trong phòng không? Có thường mất mạng không? Ngoài ra phòng cần yên tĩnh, có máy lạnh. Tôi thấy phòng 202 có vẻ phù hợp — ban công rộng, máy lạnh, hướng nam. Cho tôi hỏi giá 4tr đã gồm những gì? Còn phòng 202 không?"

### Hệ thống kỳ vọng xử lý
- Router -> System 1 -> query_policies (thong tin wifi/internet)
- Gọi `fetch_available_rooms` kiểm tra 202 còn trống không
- Gọi `get_room_info` phòng 202 (amenities: máy lạnh Daikin, nóng lạnh NLMT, ban công)
- Gọi `query_policies` RAG về gói internet (nhà mạng, băng thông)
- Trả về: Thông tin internet, phòng 202 chi tiết, tổng chi phí



---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:42:14*

**Turn 1**
- **Câu hỏi**: "Hi. Tôi làm remote IT nên cần internet ổn định, tốc độ cao. Bên bạn dùng mạng gì? Bao nhiêu Mbps? Có dây LAN trong phòng không? Có thường mất mạng không? Ngoài ra phòng cần yên tĩnh, có máy lạnh. Tôi thấy phòng 202 có vẻ phù hợp — ban công rộng, máy lạnh, hướng nam. Cho tôi hỏi giá 4tr đã gồm những gì? Còn phòng 202 không?"
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến dịch vụ tại nhà trọ. Tôi xin giải đáp các thắc mắc của anh/chị như sau:

### 1. Về Internet
*   **Nhà cung cấp:** FPT Telecom.
*   **Băng thông:** 200Mbps (chia sẻ toàn tòa nhà).
*   **Kết nối:** Tòa nhà sử dụng hệ thống Wifi với 2 băng tần là `TROHAIDANG_5G` và `TROHAIDANG_2.4G`. Hiện tại, các phòng không trang bị sẵn dây LAN.
*   **Độ ổn định:** Hệ thống hoạt động ổn định cho các nhu cầu làm việc thông thường. Nếu gặp sự cố, anh/chị có thể liên hệ quản lý để được hỗ trợ kiểm tra hoặc khởi động lại router.

### 2. Về phòng 202
*   **Tình trạng:** Hiện tại phòng 202 đang **trống (available)**.
*   **Giá thuê:** 4,000,000đ/tháng.
*   **Chi tiết chi phí:** Giá thuê 4tr chưa bao gồm các khoản phí tiêu thụ và dịch vụ. Cụ thể:
    *   **Điện:** 3,500đ/kWh.
    *   **Nước:** 100,000đ/m³.
    *   **Phí dịch vụ:** 50,000đ/tháng.
*   **Tiện nghi:** Phòng có diện tích 28m², bao gồm ban công, điều hòa, nóng lạnh, giường, bàn bếp và tủ quần áo, rất phù hợp với nhu cầu của anh/chị.

Nếu anh/chị muốn xem phòng trực tiếp, vui lòng cho tôi biết thời gian cụ thể, tôi sẽ hỗ trợ đặt lịch hẹn cho anh/chị nhé!

