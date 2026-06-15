# Kịch bản: Hỏi thủ tục đặt phòng và giấy tờ cần thiết

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Thị Phương |
| Nghề nghiệp | Sinh viên năm cuối |
| Ngân sách | 2 triệu |
| Yêu cầu | Phòng rẻ, thủ tục nhanh gọn, không rườm rà |
| Tone | friendly |

### Kịch bản
Khách nữ sinh viên sắp ra trường, muốn tìm phòng giá rẻ, cần biết thủ tục đặt phòng online trước khi đến xem.

### Câu hỏi mô phỏng
> "Em chào anh chị. Em sắp ra trường nên đang tìm phòng trọ. Em thấy bên mình có phòng giá 2 triệu, em muốn hỏi thủ tục đặt phòng như thế nào? Có đặt cọc online được không? Cần những giấy tờ gì? Có cần CMND/CCCD hay hợp đồng không ạ?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (budget_max=2.0) + query_policies (thu tuc thue phong, giay to can thiet)

### Kịch bản test
- File test: `new_18_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:33:13*

**Turn 1**
- **Câu hỏi**: "Em chào anh chị. Em sắp ra trường nên đang tìm phòng trọ. Em thấy bên mình có phòng giá 2 triệu, em muốn hỏi thủ tục đặt phòng như thế nào? Có đặt cọc online được không? Cần những giấy tờ gì? Có cần CMND/CCCD hay hợp đồng không ạ?"
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến dịch vụ thuê phòng tại nhà trọ của chúng tôi. Về quy trình đặt phòng và các thủ tục liên quan, mình xin giải đáp như sau:

### 1. Thủ tục đặt phòng và đặt cọc
*   **Đặt cọc:** Bạn cần đặt cọc **2 tháng tiền phòng**.
*   **Hình thức:** Bạn có thể thanh toán bằng tiền mặt hoặc chuyển khoản (đặt cọc online).
*   **Giữ phòng:** Sau khi đặt cọc, phòng sẽ được giữ cho bạn trong vòng **7 ngày**. Lưu ý, nếu sau 7 ngày bạn không tiến hành ký hợp đồng, bạn sẽ mất khoản tiền cọc này.

### 2. Giấy tờ cần chuẩn bị
Để ký hợp đồng thuê phòng, bạn cần chuẩn bị hồ sơ bao gồm:
*   **CCCD/CMND:** Bản gốc và 2 bản photo.
*   **Sổ hộ khẩu:** Bản photo.
*   **Ảnh 3x4:** 2 ảnh.
*   **Giấy xác nhận:** Vì bạn là sinh viên, bạn cần cung cấp **Thẻ sinh viên** và **Giấy xác nhận của trường**. (Nếu là hợp đồng dài hạn, có thể cần thêm CCCD của bố/mẹ để bảo lãnh).

### 3. Hợp đồng
Việc ký hợp đồng là bắt buộc để đảm bảo quyền lợi cho cả hai bên. Hợp đồng sẽ bao gồm các thông tin về giá phòng, diện tích, thời hạn thuê, mức cọc và các điều khoản về quyền/nghĩa vụ. Bạn sẽ cần đến trực tiếp văn phòng quản lý để thực hiện ký kết.

Nếu bạn muốn xem trực tiếp căn phòng 2 triệu đó, bạn có thể liên hệ với chúng tôi qua hotline **0901-234-567** (trong khung giờ 8h-20h) hoặc đặt lịch xem phòng vào các khung giờ: **9h-11h** hoặc **14h-17h** (từ thứ 2 đến thứ 7).

Bạn có cần mình hỗ trợ kiểm tra xem phòng 2 triệu đó hiện còn trống hay không không ạ? Nếu có, bạn cho mình xin số phòng hoặc tầng bạn đang quan tâm nhé!

