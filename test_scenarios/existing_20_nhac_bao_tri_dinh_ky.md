# Kịch bản: Đăng ký nhận thông báo bảo trì định kỳ

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Thị Hoa |
| Tenant ID | 2 |
| Phòng | 102 (tầng 1, 30m², 4.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2025-03-01 → 2026-08-31 |
| Lịch sử | Từng gặp sự cố hỏng điều hòa giữa mùa hè, muốn chủ động bảo trì |
| Nhu cầu | Đăng ký nhận thông báo khi có lịch bảo trì định kỳ và kiểm tra thiết bị |

### Multi-turn conversation

**Turn 1** — Chị Hoa hỏi về lịch bảo trì định kỳ.
> "Chào em, chị nhớ hồi tháng 4 điều hòa phòng 102 bị hỏng giữa mùa nóng, chờ sửa mệt quá. Bên mình có lịch bảo trì định kỳ không? Cho chị xin lịch để chị còn biết trước mà sắp xếp."

**Hệ thống**: Tra cứu policy về bảo trì. Thông báo lịch bảo trì định kỳ (nếu có).

**Turn 2** — Chị muốn đăng ký được báo trước nếu có lịch bảo trì.
> "Vậy nếu có lịch bảo trì, em báo chị trước qua app nhé. Chị muốn được báo trước ít nhất 1 tuần để chị thu xếp công việc."

**Hệ thống**: Cập nhật preference notice_for_maintenance=7days, channel=app.

**Turn 3** — Chị hỏi những hạng mục nào được bảo trì.
> "Cảm ơn em. Mà bảo trì gồm những gì? Có kiểm tra hết máy lạnh, tủ lạnh, bình nóng lạnh không? Hay chỉ có mấy cái chung như thang máy thôi?"

**Hệ thống**: Tra cứu danh sách hạng mục bảo trì định kỳ từ policy. Giải thích chi tiết.

**Turn 4** — Chị yêu cầu kiểm tra thêm bình nóng lạnh vì gần đây hơi yếu.
> "Dạ vậy tiện thể lần tới bảo trì, em cho thợ kiểm tra giúp chị bình nóng lạnh phòng 102 luôn nhé. Nước ấm yếu quá mà chưa tiện báo hỏng riêng."

**Hệ thống**: Ghi nhận yêu cầu. Tạo ticket kiểm tra bình nóng lạnh, hẹn lịch với bảo trì định kỳ.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 1 → query_policies (lịch bảo trì định kỳ)
- Turn 2: Router → System 2 → update_user_preference (maintenance_notice_days=7)
- Turn 3: Router → System 1 → query_policies (hạng mục bảo trì)
- Turn 4: Router → System 2 → create_maintenance_ticket (bình nóng lạnh, ưu tiên thường)
### Kịch bản test
- File test: `existing_20_test.py`






---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:55:32*

**Turn 1**
- **Câu hỏi**: "Chào em, chị nhớ hồi tháng 4 điều hòa phòng 102 bị hỏng giữa mùa nóng, chờ sửa mệt quá. Bên mình có lịch bảo trì định kỳ không? Cho chị xin lịch để chị còn biết trước mà sắp xếp."
- **Câu trả lời của AI**: Chào chị Hoa ạ, em rất hiểu sự bất tiện của chị khi thiết bị hỏng hóc trong mùa nóng.

Về lịch bảo trì định kỳ, theo nội quy tòa nhà, điều hòa tại các phòng sẽ được **vệ sinh định kỳ 6 tháng/lần** (chi phí này do nhà trọ chi trả).

Hiện tại, hệ thống không có một lịch cố định theo ngày cụ thể cho từng phòng mà sẽ được Ban quản lý chủ động lên kế hoạch và thông báo trước cho cư dân để chị sắp xếp thời gian. Để em kiểm tra lại lịch bảo trì gần nhất của phòng 102 và thông báo cho chị sớm nhất nhé.

Nếu chị thấy điều hòa có dấu hiệu hoạt động không tốt (kém lạnh, kêu to...), chị đừng ngần ngại báo ngay cho em qua đây để em tạo phiếu bảo trì, kỹ thuật sẽ đến kiểm tra sớm cho chị thay vì phải chờ đến đợt định kỳ ạ.

Chị cần em hỗ trợ kiểm tra thêm thông tin gì khác không ạ?

**Turn 2**
- **Câu hỏi**: "Vậy nếu có lịch bảo trì, em báo chị trước qua app nhé. Chị muốn được báo trước ít nhất 1 tuần để chị thu xếp công việc."
- **Câu trả lời của AI**: Dạ vâng chị Hoa, em đã ghi nhận yêu cầu của chị vào hệ thống rồi ạ. Từ nay, khi có lịch bảo trì, em sẽ ưu tiên thông báo qua app cho chị trước ít nhất 1 tuần để chị chủ động sắp xếp công việc nhé.

Chị cần em hỗ trợ thêm vấn đề gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "Cảm ơn em. Mà bảo trì gồm những gì? Có kiểm tra hết máy lạnh, tủ lạnh, bình nóng lạnh không? Hay chỉ có mấy cái chung như thang máy thôi?"
- **Câu trả lời của AI**: Chào chị Hoa, em xin giải đáp thắc mắc của chị về vấn đề bảo trì như sau ạ:

Theo quy định của tòa nhà, công tác bảo trì không chỉ giới hạn ở các khu vực chung (như thang máy, hành lang) mà bao gồm cả các thiết bị trong phòng của chị. Cụ thể:

*   **Thiết bị trong phòng:** Các thiết bị như **điều hòa, bình nóng lạnh** đều nằm trong danh mục được bảo trì định kỳ. Nhà trọ sẽ chịu 100% chi phí cho việc bảo trì định kỳ này.
*   **Thiết bị khác (tủ lạnh, v.v.):** Nếu thiết bị hỏng hóc do sử dụng lâu ngày hoặc lỗi kỹ thuật (không phải do tác động từ phía khách thuê), nhà trọ cũng sẽ chịu chi phí sửa chữa hoặc thay thế.
*   **Thời gian xử lý:**
    *   Các sự cố khẩn cấp (điện, nước, khóa cửa) sẽ được xử lý trong vòng 2 giờ.
    *   Các sự cố thông thường (vòi nước rỉ, bóng đèn cháy, ổ cắm lỏng) sẽ được xử lý trong vòng 24 giờ.
    *   Bảo trì định kỳ thường được thực hiện trong vòng 3-5 ngày sau khi tiếp nhận yêu cầu.

Chị hoàn toàn yên tâm là các thiết bị quan trọng trong phòng như điều hòa, bình nóng lạnh luôn được chú trọng bảo trì để đảm bảo chị có không gian sống thoải mái nhất ạ. Nếu chị thấy thiết bị nào có dấu hiệu hoạt động không ổn định, chị cứ báo em để em lên lịch kiểm tra ngay nhé!

**Turn 4**
- **Câu hỏi**: "Dạ vậy tiện thể lần tới bảo trì, em cho thợ kiểm tra giúp chị bình nóng lạnh phòng 102 luôn nhé. Nước ấm yếu quá mà chưa tiện báo hỏng riêng."
- **Câu trả lời của AI**: Chào chị Hoa ạ,

Em đã ghi nhận yêu cầu của chị và tạo phiếu bảo trì cho bình nóng lạnh phòng 102 rồi ạ.

*   **Mã phiếu:** TKT-2026-25F571
*   **Nội dung:** Kiểm tra bình nóng lạnh nước ấm yếu.
*   **Trạng thái:** Mới tiếp nhận.

Thợ kỹ thuật sẽ kiểm tra và xử lý sớm nhất cho chị trong vòng 24-48h tới ạ. Em cảm ơn chị đã thông báo nhé! Chị còn cần em hỗ trợ thêm vấn đề gì nữa không ạ?

