# Kịch bản: Tính tổng chi phí một tháng

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Đoàn Văn Khải |
| Nghề nghiệp | Sinh viên làm thêm |
| Ngân sách | Tối đa 3.5 triệu/tháng (tổng) |
| Phòng quan tâm | 103 (20m², 3.000.000đ/tháng) |
| Tone | friendly, thực tế |

### Kịch bản
Khách là sinh viên muốn biết tổng chi phí một tháng (bao gồm cả điện nước) cho phòng 103 giá rẻ nhất (3tr) để xem có đủ khả năng chi trả không.

### Câu hỏi mô phỏng
> "Anh chị ơi, em là sinh viên muốn thuê phòng. Em thấy phòng 103 giá 3 triệu nhưng chưa biết tổng một tháng hết bao nhiêu. Cho em hỏi thêm tiền điện bao nhiêu 1 số? Nước bao nhiêu 1 khối? Phí wifi, phí rác, phí gửi xe mỗi tháng là bao nhiêu? Giả sử em dùng tầm 50 số điện và 5 khối nước thì tổng hết tầm bao nhiêu ạ? Em tính trước xem có đủ tiền không."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> get_room_info (phong 103) + calc_rent (uoc tinh) + query_policies (bieu gia)
- Gọi `get_room_info` phòng 103
- Gọi `calc_rent` với ước tính: điện 50kWh×3.500đ=175.000đ, nước 5m³×100.000đ=500.000đ, service 50.000đ, gửi xe 100.000đ
- Gọi `query_policies` tra biểu giá
- Trả về: Bảng chi phí chi tiết, tổng ~3.825.000đ/tháng


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:30:14*

**Turn 1**
- **Câu hỏi**: "Anh chị ơi, em là sinh viên muốn thuê phòng. Em thấy phòng 103 giá 3 triệu nhưng chưa biết tổng một tháng hết bao nhiêu. Cho em hỏi thêm tiền điện bao nhiêu 1 số? Nước bao nhiêu 1 khối? Phí wifi, phí rác, phí gửi xe mỗi tháng là bao nhiêu? Giả sử em dùng tầm 50 số điện và 5 khối nước thì tổng hết tầm bao nhiêu ạ? Em tính trước xem có đủ tiền không."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ. Dưới đây là thông tin chi tiết về chi phí cho phòng 103 để bạn tham khảo:

### 1. Các khoản phí hàng tháng
*   **Giá thuê phòng:** 3.000.000đ/tháng.
*   **Tiền điện:** 3.500đ/kWh.
*   **Tiền nước:** 100.000đ/m³.
*   **Phí dịch vụ (Rác, vệ sinh chung, Wifi):** 50.000đ/tháng (Wifi tốc độ cao được miễn phí).
*   **Phí gửi xe máy:** 100.000đ/xe/tháng.

### 2. Dự tính chi phí hàng tháng (với mức sử dụng bạn nêu)
Nếu bạn sử dụng 50 số điện và 5 khối nước, tổng chi phí dự kiến như sau:

| Khoản mục | Cách tính | Thành tiền |
| :--- | :--- | :--- |
| Tiền phòng | Cố định | 3.000.000đ |
| Tiền điện | 50 kWh × 3.500đ | 175.000đ |
| Tiền nước | 5 m³ × 100.000đ | 500.000đ |
| Phí dịch vụ | Rác, vệ sinh, wifi | 50.000đ |
| **Tổng cộng** | | **3.725.000đ** |

*(Lưu ý: Nếu bạn có xe máy, bạn cộng thêm 100.000đ phí gửi xe vào tổng chi phí trên).*

Hy vọng thông tin này giúp bạn lập kế hoạch tài chính phù hợp. Nếu cần hỗ trợ thêm hoặc muốn đặt lịch xem phòng, bạn cứ cho mình biết nhé!

