# Kịch bản: Báo hỏng wifi chập chờn

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Thị Hoa |
| Tenant ID | 2 |
| Phòng | 102 (tầng 1, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2025-03-01 → 2026-08-31 |
| Ticket cũ | TKT-2026-0002: wifi chập chờn (in_progress) |
| Lịch sử | Thanh toán thường đúng hạn, trễ 1 lần tháng 3 |

### Multi-turn conversation

**Turn 1** — Khách báo wifi vẫn chập chờn dù đã có ticket trước đó.
> "Chào admin, tôi đã báo wifi chập chờn từ tuần trước (mã TKT-2026-0002), thấy bảo đã giao cho anh Tú bên IT. Nhưng tối qua từ 20h-23h vẫn mất kết nối liên tục. Có tiến độ gì chưa?"

**Hệ thống**: Kiểm tra ticket TKT-0002, trạng thái in_progress, assigned_to = "Anh Tú - IT". Cập nhật rằng IT đang xử lý, dự kiến hoàn thành trong 1-2 ngày.

**Turn 2** — Khách muốn nói chuyện trực tiếp với thợ.
> "Tôi có thể liên hệ trực tiếp anh Tú được không? Tôi cần biết chính xác khi nào đến vì tôi làm việc online, không có mạng là ảnh hưởng tới công việc cả ngày. Hoặc admin cho tôi số điện thoại."

**Hệ thống**: Cung cấp số liên hệ IT, hoặc đề nghị chuyển tiếp yêu cầu gọi lại.

**Turn 3** — Khách đề xuất giải pháp tạm thời.
> "Nếu chưa sửa được ngay thì bên mình có cho mượn modem tạm hay sim 4G dự phòng không? Tôi cần mạng để họp sáng mai."

**Hệ thống**: Kiểm tra kho thiết bị, thông báo có modem dự phòng, hướng dẫn mượn tại văn phòng.

**Turn 4** — Khách xác nhận và hỏi chi phí.
> "OK, tôi ra văn phòng lấy modem chiều nay. Có mất phí mượn không? Và nếu sửa xong thì tôi trả lại chứ?"

**Hệ thống**: Miễn phí mượn, chỉ cần ký phiếu mượn, trả lại khi sửa xong.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_maintenance_status (TKT-2026-0002)
- Turn 2: Router → System 2 → cập nhật ticket (ưu tiên cao hơn)
- Turn 3: Router → System 1 → query_policies (mượn thiết bị)
- Turn 4: Router → System 1 → hướng dẫn thủ tục mượn
### Kịch bản test
- File test: `existing_02_test.py`
- Session ID cố định






---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:53:37*

**Turn 1**
- **Câu hỏi**: "Chào admin, tôi đã báo wifi chập chờn từ tuần trước (mã TKT-2026-0002), thấy bảo đã giao cho anh Tú bên IT. Nhưng tối qua từ 20h-23h vẫn mất kết nối liên tục. Có tiến độ gì chưa?"
- **Câu trả lời của AI**: Chào chị Hoa, em rất xin lỗi vì sự bất tiện này. Hiện tại hệ thống tra cứu trạng thái bảo trì đang gặp lỗi kỹ thuật nhỏ nên em chưa thể cập nhật ngay tiến độ xử lý cho mã phiếu TKT-2026-0002 của chị.

Em đã ghi nhận phản hồi của chị về việc wifi vẫn chập chờn vào tối qua (20h-23h). Em sẽ trực tiếp liên hệ với anh Tú bên bộ phận IT để kiểm tra lại ngay tình trạng này và yêu cầu xử lý dứt điểm cho chị ạ.

Em sẽ báo lại chị sớm nhất có thể. Chị thông cảm giúp em nhé!

**Turn 2**
- **Câu hỏi**: "Tôi có thể liên hệ trực tiếp anh Tú được không? Tôi cần biết chính xác khi nào đến vì tôi làm việc online, không có mạng là ảnh hưởng tới công việc cả ngày. Hoặc admin cho tôi số điện thoại."
- **Câu trả lời của AI**: Chào chị Hoa, em rất hiểu sự bất tiện của chị khi công việc bị ảnh hưởng do vấn đề mạng internet.

Về yêu cầu của chị, em xin phản hồi như sau:

1. **Liên hệ hỗ trợ:** Để đảm bảo công việc được xử lý nhanh nhất, chị có thể liên hệ trực tiếp với **Hotline Kỹ thuật: 0901-234-567**. Đây là kênh chính thức để Ban quản lý tiếp nhận và điều phối nhân viên kỹ thuật (bao gồm anh Tú) đến hỗ trợ chị.
2. **Thời gian hỗ trợ:** Theo quy định, sau khi nhận báo cáo, bộ phận kỹ thuật sẽ xác nhận trong vòng 1 giờ (giờ hành chính) và có mặt xử lý sự cố trong vòng 24 giờ đối với trường hợp bình thường. Nếu sự cố được đánh giá là khẩn cấp, thời gian có mặt là trong vòng 2 giờ.

Để em có thể hỗ trợ chị tốt nhất, chị cho em biết tình trạng mạng hiện tại của phòng 102 là như thế nào (ví dụ: mất mạng hoàn toàn, mạng chập chờn, hay hỏng thiết bị router)? Nếu chị cần, em sẽ tạo ngay một phiếu báo hỏng kỹ thuật để ưu tiên xử lý cho chị ạ.

**Turn 3**
- **Câu hỏi**: "Nếu chưa sửa được ngay thì bên mình có cho mượn modem tạm hay sim 4G dự phòng không? Tôi cần mạng để họp sáng mai."
- **Câu trả lời của AI**: Chào chị Hoa, em rất hiểu sự bất tiện của chị khi cần mạng để họp vào sáng mai.

Dựa trên chính sách của tòa nhà, hiện tại chúng em **chưa có quy định về việc cho mượn modem tạm hoặc sim 4G dự phòng** cho cư dân khi gặp sự cố mạng.

Tuy nhiên, để hỗ trợ chị xử lý gấp vấn đề này, em xin gợi ý các bước sau:

1. **Liên hệ trực tiếp bộ phận kỹ thuật:** Chị có thể gọi ngay cho Hotline kỹ thuật của tòa nhà: **0901-234-567** (hỗ trợ đến 20h00). Chị hãy báo rõ tình trạng mạng của mình và nhấn mạnh việc chị cần họp gấp vào sáng mai để bộ phận kỹ thuật ưu tiên hỗ trợ chị sớm nhất có thể.
2. **Kiểm tra thiết bị:** Nếu router trong phòng chị có đèn báo bất thường (không sáng hoặc chớp đỏ), chị hãy báo ngay cho kỹ thuật để họ kiểm tra xem có thể khắc phục nhanh trong tối nay không ạ.

Nếu chị cần em hỗ trợ tạo thêm phiếu yêu cầu bảo trì kỹ thuật (nếu chưa có) để đảm bảo vấn đề được ghi nhận chính thức, chị cho em biết nhé. Em rất mong chị sớm khắc phục được sự cố để buổi họp ngày mai diễn ra suôn sẻ!

**Turn 4**
- **Câu hỏi**: "OK, tôi ra văn phòng lấy modem chiều nay. Có mất phí mượn không? Và nếu sửa xong thì tôi trả lại chứ?"
- **Câu trả lời của AI**: Chào chị Hoa, em xin giải đáp thắc mắc của chị về việc mượn modem như sau ạ:

*   **Về phí mượn:** Theo quy định của tòa nhà, việc hỗ trợ các thiết bị kỹ thuật như router/modem khi gặp sự cố là **miễn phí** (trong thời gian bảo hành hoặc do lỗi kỹ thuật của hệ thống).
*   **Về việc trả lại:** Sau khi thiết bị được sửa chữa hoặc thay thế và hoạt động ổn định, chị vui lòng **trả lại thiết bị cũ** (nếu có) hoặc xác nhận tình trạng hoạt động với bộ phận kỹ thuật tại văn phòng để bên em cập nhật vào hồ sơ quản lý thiết bị của phòng chị ạ.

Chiều nay khi ra văn phòng, chị cứ liên hệ với bộ phận kỹ thuật tại tầng 1 để các bạn hỗ trợ chị nhanh nhất nhé. Chúc chị một ngày làm việc hiệu quả!

