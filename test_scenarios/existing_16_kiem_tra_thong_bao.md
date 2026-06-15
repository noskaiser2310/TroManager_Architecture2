# Kịch bản: Kiểm tra lịch sử thông báo đã nhận

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Văn Minh |
| Tenant ID | 1 |
| Phòng | 101 (tầng 1, 25m², 3.500.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-01-15 → 2026-12-31 |
| Lịch sử | Thanh toán đều, thỉnh thoảng thấy app báo mà không đọc kịp |
| Nhu cầu | Xem lại các thông báo đã nhận và yêu cầu gửi lại nếu cần |

### Multi-turn conversation

**Turn 1** — Khách muốn xem lịch sử các thông báo đã gửi cho mình.
> "Anh ơi, dạo này em thấy app có báo mấy cái gì đó mà em lỡ tay gạt mất không đọc. Anh coi giúp em gần đây có thông báo gì gửi cho em không?"

**Hệ thống**: Kiểm tra behavior_logs của tenant_id=1. Liệt kê các thông báo đã gửi gần đây (nhắc thanh toán, bảo trì, v.v.).

**Turn 2** — Khách thấy có thông báo bảo trì, muốn xem chi tiết.
> "Em thấy có thông báo bảo trì hồi đầu tháng. Kỹ thuật đã qua sửa chưa anh? Em sợ bỏ lỡ lịch bảo trì thang máy."

**Hệ thống**: Tra cứu lịch bảo trì và ticket liên quan. Thông báo tình trạng.

**Turn 3** — Khách muốn đăng ký nhận lại các thông báo đã lỡ.
> "Có cách nào em xem lại mấy cái thông báo cũ không hay mất hút luôn rồi? Hay anh gửi lại cho em cái thông báo bảo trì đó được không?"

**Hệ thống**: Xác nhận không xem lại được thông báo cũ đã gửi, nhưng ghi nhận yêu cầu và hướng dẫn check thông báo trong app.

**Turn 4** — Khách yêu cầu gửi thông báo quan trọng qua cả Zalo.
> "Dạ thôi cũng được. Mà anh cho em xin được nhận thông báo qua Zalo luôn nhé, chứ em hay lỡ mấy cái trong app lắm. Mấy cái quan trọng như bảo trì với nhắc nợ thôi cũng được."

**Hệ thống**: Cập nhật preference notification_channel=app+zalo cho các loại quan trọng.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status (kiểm tra profile + behavior_logs)
- Turn 2: Router → System 2 → get_maintenance_status (tra lịch bảo trì)
- Turn 3: Router → System 1 → query_policies (chính sách lưu trữ thông báo)
- Turn 4: Router → System 2 → update_user_preference (notification_channel=["app","zalo"])
### Kịch bản test
- File test: `existing_16_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:24:29*

**Turn 1**
- **Câu hỏi**: "Anh ơi, dạo này em thấy app có báo mấy cái gì đó mà em lỡ tay gạt mất không đọc. Anh coi giúp em gần đây có thông báo gì gửi cho em không?"
- **Câu trả lời của AI**: Chào anh Minh, em đã kiểm tra hệ thống cho anh.

Hiện tại, thông báo quan trọng nhất gửi đến anh là về **hóa đơn tháng 06/2026**. Hóa đơn này có tổng số tiền là **555,555đ** và hạn thanh toán là ngày **12/06/2026**.

Vì anh có trao đổi về việc xin gia hạn thanh toán 5 ngày (đến ngày 17/06/2026) do đang đi công tác, nên anh cứ yên tâm thực hiện theo lịch trình đã được chấp thuận nhé.

Ngoài ra, về yêu cầu sửa chữa bóng đèn hành lang (phiếu TKT-2026-1C8CFB), hiện trạng vẫn đang được đội ngũ kỹ thuật xử lý. Anh có cần em kiểm tra thêm thông tin nào khác không ạ?

**Turn 2**
- **Câu hỏi**: "Em thấy có thông báo bảo trì hồi đầu tháng. Kỹ thuật đã qua sửa chưa anh? Em sợ bỏ lỡ lịch bảo trì thang máy."
- **Câu trả lời của AI**: Dạ chào anh Minh,

Về yêu cầu bảo trì bóng đèn hành lang (phiếu TKT-2026-1C8CFB) mà anh đã báo trước đó, em xin lỗi vì sự bất tiện này. Em sẽ kiểm tra lại ngay với đội kỹ thuật để đôn đốc xử lý sớm cho anh ạ.

Còn về lịch bảo trì thang máy, hiện tại trong hệ thống thông báo chung của tòa nhà chưa có lịch bảo trì cụ thể cho tháng 6/2026. Các thông báo bảo trì định kỳ thường được dán tại bảng tin ở tầng 1 hoặc gửi qua Zalo OA của tòa nhà. Anh cứ yên tâm, nếu có lịch bảo trì thang máy, Ban quản lý sẽ thông báo trước đến anh để không ảnh hưởng đến việc đi lại của mình ạ.

Anh cần em hỗ trợ kiểm tra thêm thông tin nào khác không ạ?

**Turn 3**
- **Câu hỏi**: "Có cách nào em xem lại mấy cái thông báo cũ không hay mất hút luôn rồi? Hay anh gửi lại cho em cái thông báo bảo trì đó được không?"
- **Câu trả lời của AI**: Dạ chào anh Minh, rất xin lỗi anh vì sự bất tiện này. Hiện tại, hệ thống tra cứu trạng thái bảo trì đang gặp chút sự cố kỹ thuật nhỏ, nên em chưa thể trích xuất lại lịch sử các phiếu bảo trì cũ ngay lúc này được ạ.

Tuy nhiên, em vẫn nhớ yêu cầu gần nhất của anh là về việc **thay bóng đèn ngoài hành lang** (Mã phiếu: **TKT-2026-1C8CFB**). Em sẽ báo ngay với bộ phận kỹ thuật kiểm tra lại tiến độ của phiếu này và cập nhật cho anh sớm nhất có thể nhé.

Về việc xem lại các thông báo cũ, hiện tại hệ thống chưa có tính năng để anh tự truy cập xem lại lịch sử thông báo. Em sẽ ghi nhận ý kiến này của anh để đề xuất với Ban quản lý nâng cấp tính năng trong thời gian tới ạ.

Anh cần em hỗ trợ thêm thông tin gì khác không ạ?

**Turn 4**
- **Câu hỏi**: "Dạ thôi cũng được. Mà anh cho em xin được nhận thông báo qua Zalo luôn nhé, chứ em hay lỡ mấy cái trong app lắm. Mấy cái quan trọng như bảo trì với nhắc nợ thôi cũng được."
- **Câu trả lời của AI**: Dạ vâng anh Minh, em đã cập nhật sở thích nhận thông báo qua Zalo cho anh rồi ạ. Từ nay, các thông báo quan trọng về bảo trì và nhắc nợ sẽ được gửi trực tiếp qua Zalo để anh tiện theo dõi nhé.

Anh còn cần em hỗ trợ thêm thông tin gì khác không ạ?

