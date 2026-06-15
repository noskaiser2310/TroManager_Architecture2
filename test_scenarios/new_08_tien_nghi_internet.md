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
*Chạy lúc: 2026-06-15 09:30:57*

**Turn 1**
- **Câu hỏi**: "Hi. Tôi làm remote IT nên cần internet ổn định, tốc độ cao. Bên bạn dùng mạng gì? Bao nhiêu Mbps? Có dây LAN trong phòng không? Có thường mất mạng không? Ngoài ra phòng cần yên tĩnh, có máy lạnh. Tôi thấy phòng 202 có vẻ phù hợp — ban công rộng, máy lạnh, hướng nam. Cho tôi hỏi giá 4tr đã gồm những gì? Còn phòng 202 không?"
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến căn hộ của chúng tôi. Tôi xin giải đáp các thắc mắc của anh/chị như sau:

### 1. Về Internet
Để phục vụ tốt nhất cho nhu cầu làm việc remote, mỗi phòng tại tòa nhà đều được trang bị hệ thống internet riêng biệt:
*   **Tốc độ:** Băng thông riêng **200 Mbps** cho mỗi phòng (không chia sẻ với các phòng khác).
*   **Kết nối:** Mỗi phòng được trang bị 1 router riêng (tên mạng: `PHONG_202_Wifi`). Anh/chị có thể kết nối qua Wi-Fi hoặc sử dụng trực tiếp **dây LAN** cắm từ router trong phòng.
*   **Độ ổn định:** Hệ thống được cung cấp bởi FPT Telecom. Nếu gặp sự cố về tốc độ (dưới 50 Mbps) hoặc đèn router không sáng, anh/chị có thể báo ngay cho Ban quản lý để được hỗ trợ kỹ thuật kịp thời.

### 2. Về phòng 202
Hiện tại **phòng 202 vẫn còn trống**. Đây là lựa chọn rất phù hợp với nhu cầu của anh/chị:
*   **Diện tích:** 28m² (rộng rãi, thoáng mát).
*   **Tiện nghi:** Có sẵn ban công, điều hòa, nóng lạnh, giường, bàn bếp, tủ quần áo.
*   **Giá thuê:** 4,000,000đ/tháng.

**Lưu ý về chi phí:** Giá 4,000,000đ là giá thuê phòng hàng tháng. Các chi phí sử dụng thực tế bao gồm:
*   **Điện:** 3,500đ/kWh.
*   **Nước:** 100,000đ/m³.
*   **Phí dịch vụ:** 50,000đ/tháng.

Nếu anh/chị muốn xem phòng trực tiếp, vui lòng cho tôi biết thời gian cụ thể, tôi sẽ đặt lịch hẹn cho anh/chị nhé!

