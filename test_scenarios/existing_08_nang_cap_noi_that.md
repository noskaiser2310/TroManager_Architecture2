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
*Chạy lúc: 2026-06-15 09:12:18*

**Turn 1**
- **Câu hỏi**: "Anh quản lý ơi, em có báo cái tủ lạnh phòng 201 kêu to từ lâu rồi (mã TKT-2026-0003) mà chưa thấy ai qua kiểm tra. Tủ kêu ồn cả đêm, em mất ngủ mấy bữa rồi. Anh cho thợ qua xem sớm giúp em với ạ."
- **Câu trả lời của AI**: Hệ thống đang xử lý yêu cầu phức tạp. Vui lòng liên hệ trực tiếp quản lý qua số ${LANDLORD_PHONE:-0901.234.567} để được hỗ trợ nhanh nhất.

**Turn 2**
- **Câu hỏi**: "Mà hôm qua em còn phát hiện ống nước dưới bồn rửa chén bị rò rỉ, nước chảy ra sàn. Em thấy bên mình có thợ đang sửa rồi (hồi trước có báo), anh cho em hỏi tiến độ tới đâu rồi? Có qua luôn thể sửa cả tủ lạnh với ống nước được không?"
- **Câu trả lời của AI**: Chào anh Tuấn, em rất xin lỗi vì sự bất tiện này ạ.

Về yêu cầu của anh, em đã lập phiếu bảo trì mới (Mã phiếu: **TKT-2026-573A5A**) để đội ngũ kỹ thuật kiểm tra và xử lý dứt điểm tình trạng rò rỉ ống nước bồn rửa chén cũng như kiểm tra tủ lạnh cho mình luôn ạ.

Trạng thái hiện tại của phiếu là "Mới tiếp nhận", thời gian xử lý dự kiến trong vòng 24-48 giờ tới. Thợ sẽ liên hệ trực tiếp với anh trước khi qua kiểm tra ạ. Anh yên tâm nhé, em sẽ theo sát tiến độ để đảm bảo thợ xử lý sớm nhất cho mình ạ!

**Turn 3**
- **Câu hỏi**: "Dạ nếu được thì cuối tuần này thứ 7 em ở nhà cả ngày. Anh sắp xếp thợ qua sáng thứ 7 được không? Cả 2 cái một thể. Em ở nhà đón thợ."
- **Câu trả lời của AI**: Chào anh Tuấn ạ,

Em đã ghi nhận yêu cầu của anh vào hệ thống. Phiếu bảo trì cho sự cố điều hòa và kiểm tra các vấn đề khác đã được tạo với mã **TKT-2026-DF1806**.

Em đã lưu chú ý là anh sẽ ở nhà vào sáng thứ 7 (20/06/2026) để đón thợ. Em sẽ báo bộ phận kỹ thuật sắp xếp thợ qua kiểm tra cho anh vào khung giờ đó nhé. Nếu có thay đổi gì, em sẽ nhắn tin báo anh ngay ạ!

**Turn 4**
- **Câu hỏi**: "Cảm ơn anh nhiều. Mà cho em hỏi luôn, sửa tủ lạnh với ống nước có mất phí không anh? Hay bên mình lo hết? Em nghe nói sửa đồ trong phòng có khi tính phí."
- **Câu trả lời của AI**: Chào anh Tuấn, em xin giải đáp thắc mắc của anh về chi phí sửa chữa như sau ạ:

Theo quy định của tòa nhà, chi phí sửa chữa sẽ được áp dụng dựa trên nguyên nhân gây ra hỏng hóc:

*   **Nhà trọ chịu 100% chi phí:** Đối với các trường hợp hỏng hóc tự nhiên do quá trình sử dụng lâu ngày, lỗi kỹ thuật của thiết bị hoặc các hạng mục bảo trì định kỳ.
*   **Khách thuê chịu 100% chi phí:** Đối với các trường hợp hỏng hóc do lỗi chủ quan của khách thuê trong quá trình sử dụng.

Vì vậy, nếu tủ lạnh hay ống nước nhà mình gặp sự cố do hao mòn tự nhiên, anh hoàn toàn yên tâm là bên em sẽ chịu trách nhiệm sửa chữa và không tính phí của anh ạ.

Nếu hiện tại anh đang gặp vấn đề với tủ lạnh hoặc ống nước, anh cứ báo lại để em tạo phiếu bảo trì cho thợ qua kiểm tra ngay nhé!

