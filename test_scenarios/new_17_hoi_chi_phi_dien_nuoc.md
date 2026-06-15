# Kịch bản: Hỏi chi phí điện nước và dịch vụ

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Văn Đạt |
| Nghề nghiệp | Thợ hồ tự do |
| Ngân sách | 2.5-3 triệu |
| Yêu cầu | Phòng giá rẻ, muốn biết tổng chi phí mỗi tháng gồm những gì |
| Tone | straightforward |

### Kịch bản
Khách nam muốn thuê phòng giá rẻ, quan tâm đến các khoản phí phát sinh ngoài tiền phòng.

### Câu hỏi mô phỏng
> "Tôi muốn thuê phòng giá tầm 2.5-3 triệu. Nhưng ngoài tiền phòng ra còn đóng những gì nữa? Điện nước tính riêng đúng không? Bao nhiêu một số? Có phí dịch vụ, phí gửi xe gì không? Tổng mỗi tháng hết bao nhiêu?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (budget_max=3.0) + query_policies (chi phi dien nuoc, phi dich vu)

### Kịch bản test
- File test: `new_17_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:32:59*

**Turn 1**
- **Câu hỏi**: "Tôi muốn thuê phòng giá tầm 2.5-3 triệu. Nhưng ngoài tiền phòng ra còn đóng những gì nữa? Điện nước tính riêng đúng không? Bao nhiêu một số? Có phí dịch vụ, phí gửi xe gì không? Tổng mỗi tháng hết bao nhiêu?"
- **Câu trả lời của AI**: Chào anh/chị, hiện tại bên em có phòng 103 (tầng 1, diện tích 20m²) với giá thuê 3.000.000đ/tháng đang trống.

Về các khoản chi phí ngoài tiền phòng, em xin thông tin chi tiết đến anh/chị như sau:

**1. Các khoản phí hàng tháng:**
*   **Tiền điện:** 3.500đ/kWh (có đồng hồ riêng cho từng phòng).
*   **Tiền nước:** 100.000đ/m³.
*   **Phí dịch vụ (rác, vệ sinh chung):** 50.000đ/phòng/tháng.
*   **Phí gửi xe máy:** 100.000đ/xe/tháng (nếu có).
*   **Internet/Wifi:** Miễn phí.

**2. Tổng chi phí mỗi tháng:**
Tổng tiền hàng tháng sẽ bằng: **Tiền phòng (3.000.000đ) + Phí dịch vụ (50.000đ) + Phí gửi xe (nếu có) + (Số điện × 3.500đ) + (Số nước × 100.000đ)**. Do tiền điện và nước phụ thuộc vào mức sử dụng thực tế của anh/chị, nên tổng số tiền sẽ thay đổi tùy theo nhu cầu dùng hàng tháng ạ.

Anh/chị có muốn đặt lịch qua xem phòng trực tiếp không ạ? Nếu có, anh/chị cho em xin thời gian dự kiến nhé!

