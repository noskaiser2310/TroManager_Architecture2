# Kịch bản: Báo hỏng tủ lạnh và rò rỉ nước

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Hoàng Tuấn |
| Tenant ID | 3 |
| Phòng | 201 (tầng 2, 22m², 3.200.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-06-01 → 2026-12-31 |
| Ticket cũ | TKT-0003 (tủ lạnh kêu to, open), TKT-0007 (rò rỉ ống nước, in_progress) |
| Ghi chú | Khách thân thiện, tích cực, ở lâu dài |

### Multi-turn conversation

**Turn 1** — Khách nhắc về tủ lạnh vẫn kêu to.
> "Anh quản lý ơi, em có báo cái tủ lạnh phòng 201 kêu to từ lâu rồi (mã TKT-2026-0003) mà chưa thấy ai qua kiểm tra. Tủ kêu ồn cả đêm, em mất ngủ mấy bữa rồi. Anh cho thợ qua xem sớm giúp em với ạ."

**Hệ thống**: Kiểm tra TKT-0003 — trạng thái open, chưa assigned. Xác nhận đã nhận, hứa sắp xếp thợ trong 1-2 ngày.

**Turn 2** — Khách báo thêm ống nước rò rỉ.
> "Mà hôm qua em còn phát hiện ống nước dưới bồn rửa chén bị rò rỉ, nước chảy ra sàn. Em thấy bên mình có thợ đang sửa rồi (hồi trước có báo), anh cho em hỏi tiến độ tới đâu rồi? Có qua luôn thể sửa cả tủ lạnh với ống nước được không?"

**Hệ thống**: Kiểm tra TKT-0007 (rò rỉ ống nước, in_progress, assigned = "Anh Tài - thợ nước", priority=high). Xác nhận thợ đang xử lý. Đề xuất kết hợp 2 ticket — sửa cùng lúc cho tiện.

**Turn 3** — Khách đề xuất lịch sửa.
> "Dạ nếu được thì cuối tuần này thứ 7 em ở nhà cả ngày. Anh sắp xếp thợ qua sáng thứ 7 được không? Cả 2 cái một thể. Em ở nhà đón thợ."

**Hệ thống**: Xác nhận lịch thứ 7, cập nhật schedule cho cả 2 ticket.

**Turn 4** — Khách cảm ơn và hỏi thêm.
> "Cảm ơn anh nhiều. Mà cho em hỏi luôn, sửa tủ lạnh với ống nước có mất phí không anh? Hay bên mình lo hết? Em nghe nói sửa đồ trong phòng có khi tính phí."

**Hệ thống**: Trả lời chính sách bảo trì — miễn phí nếu do hao mòn tự nhiên, có phí nếu do người dùng gây hư. Trường hợp này thuộc hao mòn nên miễn phí.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_maintenance_status (TKT-0003)
- Turn 2: Router → System 2 → get_maintenance_status (TKT-0007)
- Turn 3: Router → System 2 → update ticket schedule
- Turn 4: Router → System 1 → query_policies (chi phí bảo trì)
### Kịch bản test
- File test: `existing_08_test.py`




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:36:04*

**Turn 1**
- **Câu hỏi**: "Anh quản lý ơi, em có báo cái tủ lạnh phòng 201 kêu to từ lâu rồi (mã TKT-2026-0003) mà chưa thấy ai qua kiểm tra. Tủ kêu ồn cả đêm, em mất ngủ mấy bữa rồi. Anh cho thợ qua xem sớm giúp em với ạ."
- **Câu trả lời của AI**: Hệ thống đang xử lý yêu cầu phức tạp. Vui lòng liên hệ trực tiếp quản lý qua số ${LANDLORD_PHONE:-0901.234.567} để được hỗ trợ nhanh nhất.

**Turn 2**
- **Câu hỏi**: "Mà hôm qua em còn phát hiện ống nước dưới bồn rửa chén bị rò rỉ, nước chảy ra sàn. Em thấy bên mình có thợ đang sửa rồi (hồi trước có báo), anh cho em hỏi tiến độ tới đâu rồi? Có qua luôn thể sửa cả tủ lạnh với ống nước được không?"
- **Câu trả lời của AI**: Chào anh Tuấn, em rất xin lỗi vì sự bất tiện này ạ.

Để đảm bảo vấn đề rò rỉ nước và tủ lạnh được xử lý dứt điểm, em đã tạo phiếu yêu cầu bảo trì mới cho anh với thông tin cụ thể như sau:

*   **Mã phiếu:** TKT-2026-E88214
*   **Nội dung:** Sửa ống nước dưới bồn rửa chén bị rò rỉ và kiểm tra tủ lạnh.
*   **Trạng thái:** Mới tiếp nhận
*   **Thời gian xử lý dự kiến:** Trong vòng 24-48 giờ tới.

Em sẽ đôn đốc bộ phận kỹ thuật ưu tiên xử lý sớm cho mình. Khi thợ chuẩn bị qua, họ sẽ liên hệ trực tiếp với anh ạ. Anh yên tâm nhé!

**Turn 3**
- **Câu hỏi**: "Dạ nếu được thì cuối tuần này thứ 7 em ở nhà cả ngày. Anh sắp xếp thợ qua sáng thứ 7 được không? Cả 2 cái một thể. Em ở nhà đón thợ."
- **Câu trả lời của AI**: Chào anh Tuấn, em đã ghi nhận yêu cầu của anh vào hệ thống rồi ạ.

Mã phiếu bảo trì của anh là **TKT-2026-10F81A**. Em đã lưu lưu ý là anh sẽ ở nhà vào sáng thứ 7 (20/06/2026) để thợ qua kiểm tra và xử lý sự cố điều hòa chảy nước cho mình.

Bộ phận kỹ thuật sẽ sắp xếp thợ qua vào khung giờ đó và liên hệ trước với anh ạ. Anh yên tâm nhé!

**Turn 4**
- **Câu hỏi**: "Cảm ơn anh nhiều. Mà cho em hỏi luôn, sửa tủ lạnh với ống nước có mất phí không anh? Hay bên mình lo hết? Em nghe nói sửa đồ trong phòng có khi tính phí."
- **Câu trả lời của AI**: Chào anh Tuấn, em xin giải đáp thắc mắc của anh về chi phí sửa chữa như sau ạ:

Theo quy định của tòa nhà, chi phí sửa chữa sẽ được xác định dựa trên nguyên nhân gây ra hỏng hóc:

*   **Nhà trọ chịu 100% chi phí:** Đối với các trường hợp thiết bị hỏng do hao mòn tự nhiên (sử dụng lâu ngày), lỗi kỹ thuật của thiết bị hoặc trong các đợt bảo trì định kỳ.
*   **Khách thuê chịu 100% chi phí:** Đối với các trường hợp hỏng hóc do lỗi sử dụng hoặc tác động từ phía khách thuê.

Vì vậy, nếu tủ lạnh hoặc ống nước nhà mình gặp sự cố do hao mòn tự nhiên, anh hoàn toàn yên tâm là bên em sẽ chịu trách nhiệm sửa chữa mà không tính phí cho anh ạ.

Nếu anh đang gặp vấn đề cụ thể với tủ lạnh hay ống nước, anh cứ báo lại để em ghi nhận và cử thợ qua kiểm tra sớm cho mình nhé!

