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
*Chạy lúc: 2026-06-15 00:41:11*

**Turn 1**
- **Câu hỏi**: "Anh chị ơi, em là sinh viên muốn thuê phòng. Em thấy phòng 103 giá 3 triệu nhưng chưa biết tổng một tháng hết bao nhiêu. Cho em hỏi thêm tiền điện bao nhiêu 1 số? Nước bao nhiêu 1 khối? Phí wifi, phí rác, phí gửi xe mỗi tháng là bao nhiêu? Giả sử em dùng tầm 50 số điện và 5 khối nước thì tổng hết tầm bao nhiêu ạ? Em tính trước xem có đủ tiền không."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ. Dưới đây là thông tin chi tiết về chi phí cho phòng 103 để bạn tham khảo:

### 1. Các khoản phí hàng tháng
*   **Tiền phòng:** 3.000.000đ/tháng.
*   **Tiền điện:** 3.500đ/kWh.
*   **Tiền nước:** 100.000đ/m³.
*   **Phí dịch vụ:** 50.000đ/tháng (bao gồm rác, wifi, vệ sinh chung).
*   **Phí gửi xe máy:** 100.000đ/tháng (nếu bạn có xe máy).

### 2. Ước tính tổng chi phí hàng tháng
Với giả định bạn sử dụng 50 số điện và 5 khối nước, tổng chi phí dự kiến như sau:

| Khoản mục | Cách tính | Thành tiền |
| :--- | :--- | :--- |
| Tiền phòng | Cố định | 3.000.000đ |
| Tiền điện | 50 số × 3.500đ | 175.000đ |
| Tiền nước | 5 khối × 100.000đ | 500.000đ |
| Phí dịch vụ | Cố định | 50.000đ |
| Phí gửi xe | Cố định (nếu có) | 100.000đ |
| **Tổng cộng** | | **3.825.000đ** (chưa bao gồm phí xe) |

Như vậy, tổng chi phí hàng tháng của bạn sẽ rơi vào khoảng **3.725.000đ** (nếu không gửi xe) hoặc **3.825.000đ** (nếu có gửi 1 xe máy).

Hy vọng thông tin này giúp bạn lập kế hoạch tài chính phù hợp. Nếu bạn cần xem phòng thực tế, hãy cho mình biết thời gian thuận tiện nhé!

