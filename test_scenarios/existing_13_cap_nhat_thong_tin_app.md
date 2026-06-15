# Kịch bản: Cập nhật thông tin liên lạc trong app

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Thị Hoa |
| Tenant ID | 2 |
| Phòng | 102 (tầng 1, 30m², 4.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2025-03-01 → 2026-08-31 |
| Lịch sử | Đã dùng app chat, muốn cập nhật thêm số điện thoại dự phòng |
| Nhu cầu | Cập nhật thông tin liên lạc qua app |

### Multi-turn conversation

**Turn 1** — Chị Hoa muốn kiểm tra và cập nhật số điện thoại trong app.
> "Chào em. Chị quên số điện thoại chị đăng ký với bên mình là số nào rồi. Em check giúp chị với. Chị mới đổi số, cần cập nhật lại."

**Hệ thống**: Tra cứu số điện thoại từ profile và hiển thị. Xác nhận có thể cập nhật số mới.

**Turn 2** — Chị cập nhật số mới và hỏi thêm số dự phòng.
> "Số cũ đúng rồi, số mới của chị là 0909888999. Em cập nhật giúp chị nhé. Mà cho chị hỏi có thêm được số dự phòng không?"

**Hệ thống**: Cập nhật số điện thoại mới. Giải thích profile chỉ lưu 1 số chính, ghi nhận nhu cầu.

**Turn 3** — Chị đồng ý và muốn dùng app là kênh liên lạc chính.
> "Thôi 1 số cũng được. Chị thích chat trong app hơn, tiện hơn gọi điện. Có chuyện gì em nhắn trong app cho chị nhé."

**Hệ thống**: Cập nhật preference contact_method=app, xác nhận sẽ liên lạc qua app.

**Turn 4** — Chị hỏi thay đổi có hiệu lực ngay không.
> "OK vậy từ giờ có gì em nhắn trong app cho chị nha. Cập nhật này có hiệu lực liền chưa em?"

**Hệ thống**: Xác nhận đã cập nhật xong, có hiệu lực ngay.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status (lấy số ĐT từ profile)
- Turn 2: Router → System 2 → update_user_preference (phone_number=0909888999)
- Turn 3: Router → System 2 → update_user_preference (contact_method=app)
- Turn 4: Router → System 1 → xác nhận thay đổi
### Kịch bản test
- File test: `existing_13_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:17:30*

**Turn 1**
- **Câu hỏi**: "Chào em. Chị quên số điện thoại chị đăng ký với bên mình là số nào rồi. Em check giúp chị với. Chị mới đổi số, cần cập nhật lại."
- **Câu trả lời của AI**: Chào chị Hoa ạ,

Em xin lỗi vì sự bất tiện này. Hiện tại, trong hệ thống quản lý thông tin cá nhân của chị, em không hiển thị trực tiếp số điện thoại đăng ký mà chỉ quản lý các tùy chọn liên lạc.

Để em có thể hỗ trợ chị cập nhật số điện thoại mới vào hồ sơ, chị vui lòng cung cấp giúp em **số điện thoại mới** mà chị muốn sử dụng nhé. Sau khi nhận được thông tin từ chị, em sẽ cập nhật ngay vào hệ thống để đảm bảo việc liên lạc giữa Ban quản lý và chị được thông suốt ạ.

Em cảm ơn chị!

**Turn 2**
- **Câu hỏi**: "Số cũ đúng rồi, số mới của chị là 0909888999. Em cập nhật giúp chị nhé. Mà cho chị hỏi có thêm được số dự phòng không?"
- **Câu trả lời của AI**: Chào chị Hoa, em đã ghi nhận yêu cầu cập nhật số điện thoại mới của chị. Tuy nhiên, vì hệ thống hiện tại chỉ cho phép cập nhật các tùy chọn về phương thức liên lạc và sở thích, em sẽ ghi chú lại số điện thoại **0909888999** này vào hồ sơ cá nhân của chị để Ban quản lý liên hệ khi cần thiết ạ.

Về việc thêm số điện thoại dự phòng, theo quy định hiện hành của tòa nhà, chúng em chủ yếu liên lạc qua số điện thoại chính đã đăng ký trong hợp đồng. Nếu chị muốn bổ sung thêm thông tin liên lạc, chị có thể nhắn tin trực tiếp cho em qua Zalo hoặc gọi đến số hotline quản lý **0901-234-567** để được hỗ trợ ghi chú thêm vào hồ sơ cư dân chị nhé.

Chị cần em hỗ trợ thêm thông tin nào khác không ạ?

**Turn 3**
- **Câu hỏi**: "Thôi 1 số cũng được. Chị thích chat trong app hơn, tiện hơn gọi điện. Có chuyện gì em nhắn trong app cho chị nhé."
- **Câu trả lời của AI**: Dạ vâng chị Hoa, em đã ghi nhận sở thích của chị là ưu tiên trao đổi qua tin nhắn trong app thay vì gọi điện thoại ạ. Từ nay, khi có bất kỳ thông tin gì cần trao đổi, em sẽ nhắn tin trực tiếp cho chị qua đây để chị tiện theo dõi nhé.

Chị cần em hỗ trợ thêm vấn đề gì khác không ạ?

**Turn 4**
- **Câu hỏi**: "OK vậy từ giờ có gì em nhắn trong app cho chị nha. Cập nhật này có hiệu lực liền chưa em?"
- **Câu trả lời của AI**: Dạ vâng chị Hoa, em đã cập nhật phương thức liên lạc ưu tiên của chị sang "nhắn tin trong app" vào hệ thống rồi ạ.

Cập nhật này có hiệu lực ngay lập tức chị nhé. Từ giờ, em sẽ ưu tiên gửi các thông báo và phản hồi cho chị qua kênh này ạ. Chị cần em hỗ trợ thêm vấn đề gì nữa không ạ?

