# Kịch bản: Báo hỏng và nhận cập nhật tiến độ trong app

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Hoàng Tuấn |
| Tenant ID | 3 |
| Phòng | 201 (tầng 2, 22m², 3.200.000đ/tháng) |
| Tone | direct |
| Hợp đồng | 2024-06-01 → 2026-12-31 |
| Lịch sử | Đã báo tủ lạnh kêu to (TKT-2026-0003), chưa sửa |
| Nhu cầu | Báo thêm hỏng ống nước, muốn AI cập nhật tiến độ ngay trong app |

### Multi-turn conversation

**Turn 1** — Khách báo hỏng ống nước và hỏi tiến độ tủ lạnh.
> "Hôm qua em phát hiện ống nước dưới bồn rửa chén bị rò rỉ. Anh tạo phiếu bảo trì giúp em với. Mà tủ lạnh báo từ đợt trước có mã TKT-2026-0003, sửa chưa vậy anh?"

**Hệ thống**: Gọi get_maintenance_status(TKT-2026-0003) kiểm tra ticket cũ + create_maintenance_ticket tạo ticket mới cho ống nước.

**Turn 2** — Khách muốn AI báo tiến độ ngay trong app.
> "Anh cho em hỏi, mai mốt có gì mới về 2 cái phiếu này thì anh báo em luôn trong app được không? Chứ em ít check Zalo lắm."

**Hệ thống**: Cập nhật preference, xác nhận sẽ thông báo qua app khi có cập nhật.

**Turn 3** — Khách hỏi dự kiến bao lâu có thợ.
> "Vậy 2 cái này bao lâu có thợ anh? Cái tủ lạnh lâu quá rồi, cái ống nước thì gấp vì nó chảy xuống gạch."

**Hệ thống**: Tra cứu policy thời gian xử lý. Thông báo ETA: ống nước ưu tiên cao → trong 24h, tủ lạnh trong 48h.

**Turn 4** — Khách dặn lịch và muốn AI nhắc lại trong app.
> "OK em chờ. Sáng chủ nhật em ở nhà, nếu thợ tới thì anh nhắc em trong app trước 1 tiếng nhé. Em cám ơn."

**Hệ thống**: Ghi nhận yêu cầu, xác nhận sẽ nhắc trong app trước khi thợ tới.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_maintenance_status + create_maintenance_ticket
- Turn 2: Router → System 2 → update_user_preference (thông báo trong app)
- Turn 3: Router → System 2 → get_maintenance_status + query_policies
- Turn 4: Router → System 2 → lưu ghi chú vào ticket
### Kịch bản test
- File test: `existing_12_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:16:31*

**Turn 1**
- **Câu hỏi**: "Hôm qua em phát hiện ống nước dưới bồn rửa chén bị rò rỉ. Anh tạo phiếu bảo trì giúp em với. Mà tủ lạnh báo từ đợt trước có mã TKT-2026-0003, sửa chưa vậy anh?"
- **Câu trả lời của AI**: Chào anh Tuấn,

Em đã ghi nhận sự cố rò rỉ ống nước dưới bồn rửa chén của anh. Mã phiếu bảo trì mới của anh là **TKT-2026-F72D57**. Bộ phận kỹ thuật sẽ sớm liên hệ để qua kiểm tra và xử lý cho anh trong vòng 24-48 giờ tới ạ.

Về tình trạng tủ lạnh (mã TKT-2026-0003), do hệ thống đang gặp lỗi kỹ thuật nhỏ khi truy xuất chi tiết trạng thái, em sẽ trực tiếp kiểm tra lại với đội ngũ kỹ thuật ngay bây giờ và cập nhật thông tin cho anh sớm nhất có thể nhé. Anh thông cảm giúp em ạ!

**Turn 2**
- **Câu hỏi**: "Anh cho em hỏi, mai mốt có gì mới về 2 cái phiếu này thì anh báo em luôn trong app được không? Chứ em ít check Zalo lắm."
- **Câu trả lời của AI**: Chào anh Tuấn, em đã ghi nhận yêu cầu của anh rồi ạ. Từ nay, em sẽ ưu tiên cập nhật thông tin về các phiếu yêu cầu bảo trì trực tiếp cho anh tại đây thay vì qua Zalo như trước nhé.

Em đã cập nhật phương thức liên lạc ưu tiên của anh vào hệ thống. Khi có bất kỳ cập nhật mới nào về các phiếu yêu cầu, em sẽ báo ngay cho anh ạ!

**Turn 3**
- **Câu hỏi**: "Vậy 2 cái này bao lâu có thợ anh? Cái tủ lạnh lâu quá rồi, cái ống nước thì gấp vì nó chảy xuống gạch."
- **Câu trả lời của AI**: Chào anh Tuấn, em rất xin lỗi vì sự bất tiện này, đặc biệt là tình trạng rò rỉ nước gây ảnh hưởng đến sàn nhà.

Em đã ghi nhận và tạo phiếu yêu cầu sửa chữa khẩn cấp cho anh rồi ạ:
- **Mã phiếu:** TKT-2026-FDA8AD
- **Nội dung:** Tủ lạnh hỏng và ống nước rò rỉ.
- **Mức độ:** Khẩn cấp.

Theo quy định, thời gian xử lý dự kiến là từ **24-48 giờ**. Tuy nhiên, vì ống nước đang bị rò rỉ gây ẩm ướt, em đã đánh dấu là **Khẩn cấp** để bộ phận kỹ thuật ưu tiên xử lý sớm nhất cho anh. Thợ sẽ liên hệ với anh ngay khi đến nơi ạ.

Anh yên tâm, em sẽ theo dõi sát sao tiến độ này cho mình!

**Turn 4**
- **Câu hỏi**: "OK em chờ. Sáng chủ nhật em ở nhà, nếu thợ tới thì anh nhắc em trong app trước 1 tiếng nhé. Em cám ơn."
- **Câu trả lời của AI**: Dạ vâng anh Tuấn, em đã ghi chú lại yêu cầu của anh vào hệ thống rồi ạ. Từ nay, khi có thợ qua bảo trì, bên em sẽ chủ động nhắn tin báo trước cho anh 1 tiếng như anh mong muốn nhé.

Chúc anh một ngày cuối tuần thật vui vẻ và thoải mái ạ!

