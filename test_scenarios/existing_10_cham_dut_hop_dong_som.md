# Kịch bản: Đơn phương chấm dứt hợp đồng sớm

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Đỗ Văn Hùng |
| Tenant ID | 5 |
| Phòng | 302 (tầng 3, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2024-09-01 → 2026-09-01 (còn 3 tháng) |
| Lịch sử | Thanh toán luôn đúng hạn, khách mẫu mực |
| Ticket cũ | TKT-0009 (bàn làm việc ọp ẹp, open) |
| Lý do | Chuyển công tác vào Đà Nẵng |

### Multi-turn conversation

**Turn 1** — Khách báo chấm dứt hợp đồng sớm.
> "Chào admin, em có quyết định chuyển công tác vào Đà Nẵng gấp, phải đi trong tháng 7 này. Hợp đồng phòng 302 của em còn tới tháng 9, nhưng em không ở được nữa. Em muốn hỏi nếu chấm dứt sớm thì sẽ bị phạt thế nào? Có mất tiền cọc không ạ?"

**Hệ thống**: Kiểm tra hợp đồng (active, 2024-09-01 → 2026-09-01). Tra điều khoản chấm dứt sớm — thường mất 1 tháng tiền cọc nếu đơn phương chấm dứt.

**Turn 2** — Khách hỏi chi tiết điều khoản.
> "Cụ thể là mất 1 tháng tiền cọc (9 triệu) hay toàn bộ cọc? Và em cần báo trước bao nhiêu ngày? 30 ngày hay 45 ngày? Em muốn biết chính xác để sắp xếp tài chính."

**Hệ thống**: Cung cấp điều khoản — mất 1 tháng cọc (theo contract deposit_amount=9.000.000đ), cần báo trước 30 ngày. Tuy nhiên có thể thương lượng nếu tìm được người thế phòng.

**Turn 3** — Khách thương lượng và hỏi về giới thiệu người ở thế.
> "Em có thể tìm người vào ở thế được không? Có ông bạn đồng nghiệp cũng đang tìm phòng, em hỏi ổng coi. Nếu ổng chịu vào ở thì em có mất phí phạt không? Và thủ tục thế nào?"

**Hệ thống**: Xác nhận có thể giới thiệu người thế phòng, nếu được chấp thuận thì có thể miễn/giảm phí phạt. Hướng dẫn thủ tục — người mới ký hợp đồng mới, tiền cọc chuyển tiếp được.

**Turn 4** — Khách hỏi checklist bàn giao.
> "OK em sẽ hỏi bạn. Mà nếu đi thì em cần làm gì để bàn giao phòng? Có checklist gì không? Em còn cái bàn làm việc đã báo hỏng từ lâu (mã TKT-2026-0009), cái đó có ảnh hưởng gì tới việc trả phòng không?"

**Hệ thống**: Gửi checklist trả phòng — dọn dẹp, kiểm tra nội thất, tắt điện nước, bàn giao chìa khoá. Ghi nhận TKT-0009 (bàn ọp ẹp) là hao mòn tự nhiên, không ảnh hưởng.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → get_contract_status + query_policies
- Turn 2: Router → System 1 → query_policies (phí phạt)
- Turn 3: Router → System 2 → Approval Queue (thương lượng)
- Turn 4: Router → System 1 → checklist + update ticket TKT-0009
### Kịch bản test
- File test: `existing_10_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:14:22*

**Turn 1**
- **Câu hỏi**: "Chào admin, em có quyết định chuyển công tác vào Đà Nẵng gấp, phải đi trong tháng 7 này. Hợp đồng phòng 302 của em còn tới tháng 9, nhưng em không ở được nữa. Em muốn hỏi nếu chấm dứt sớm thì sẽ bị phạt thế nào? Có mất tiền cọc không ạ?"
- **Câu trả lời của AI**: Chào anh Hùng,

Về việc anh muốn chấm dứt hợp đồng sớm trước thời hạn (tháng 9/2026), theo quy định tại chính sách của tòa nhà, trường hợp anh đơn phương chấm dứt hợp đồng trước thời hạn cần đảm bảo các điều kiện sau:

1. **Thông báo trước:** Anh cần báo trước cho Ban quản lý tối thiểu **30 ngày**.
2. **Nghĩa vụ tài chính:** Anh cần thanh toán đầy đủ các khoản phí đến ngày chấm dứt hợp đồng.
3. **Tình trạng phòng:** Phòng cần được trả lại trong tình trạng ban đầu (không hư hỏng nặng).
4. **Tiền cọc:** Theo quy định, khi chấm dứt hợp đồng sớm, anh có thể mất một phần tiền cọc (tối đa 50%).

Để có phương án hỗ trợ tốt nhất cho anh, anh vui lòng nhắn lại cho em thời gian cụ thể anh dự kiến chuyển đi để em báo cáo với quản lý và làm thủ tục thanh lý hợp đồng cho anh nhé.

**Turn 2**
- **Câu hỏi**: "Cụ thể là mất 1 tháng tiền cọc (9 triệu) hay toàn bộ cọc? Và em cần báo trước bao nhiêu ngày? 30 ngày hay 45 ngày? Em muốn biết chính xác để sắp xếp tài chính."
- **Câu trả lời của AI**: Chào anh Hùng, về thắc mắc của anh liên quan đến quy định trả phòng và hoàn cọc, em xin phản hồi dựa trên chính sách của tòa nhà như sau:

1. **Về thời gian báo trước:** Theo quy định, anh cần báo trước **60 ngày** để đảm bảo quyền lợi hoàn cọc đầy đủ.
2. **Về tiền cọc:**
   - Anh sẽ được **hoàn 100% tiền cọc** nếu trả phòng đúng hạn (theo hợp đồng), phòng trong tình trạng ban đầu (không hư hỏng nặng), không nợ các khoản thanh toán và đã trả đủ chìa khóa.
   - Các trường hợp khấu trừ cọc sẽ xảy ra nếu phòng có hư hỏng nặng (khấu trừ 30-50%) hoặc có các vi phạm khác như nợ tiền thuê, cho người ở cùng không đăng ký, v.v.

Hiện tại, hợp đồng của anh đến ngày **2026-09-01** mới hết hạn. Nếu anh có dự định thay đổi kế hoạch, anh vui lòng nhắn sớm để em hỗ trợ anh làm thủ tục đúng quy định, tránh việc mất cọc không đáng có nhé.

Anh cần em hỗ trợ thêm thông tin gì khác không ạ?

**Turn 3**
- **Câu hỏi**: "Em có thể tìm người vào ở thế được không? Có ông bạn đồng nghiệp cũng đang tìm phòng, em hỏi ổng coi. Nếu ổng chịu vào ở thì em có mất phí phạt không? Và thủ tục thế nào?"
- **Câu trả lời của AI**: Chào anh Hùng, về việc anh muốn tìm người vào ở thay thế (chuyển nhượng hợp đồng), em xin thông tin đến anh như sau:

Theo quy định, nếu anh muốn chấm dứt hợp đồng sớm để người khác vào ở thay, anh cần lưu ý các điểm sau:

1.  **Thông báo:** Anh cần báo trước cho Ban quản lý tối thiểu **30 ngày**.
2.  **Điều kiện:** Anh cần đảm bảo đã thanh toán đầy đủ tiền thuê đến ngày chấm dứt và trả lại phòng trong tình trạng ban đầu.
3.  **Về phí phạt:** Theo chính sách chấm dứt hợp đồng sớm, nếu anh đơn phương chấm dứt hợp đồng, anh có thể mất một phần tiền cọc (tối đa 50%). Tuy nhiên, nếu anh tìm được người vào ở thay thế ngay lập tức và người đó ký hợp đồng mới với chúng em, chúng em sẽ xem xét để hỗ trợ anh tối đa về thủ tục và tiền cọc.

**Thủ tục thực hiện:**
*   Anh hãy trao đổi với bạn đồng nghiệp của mình. Nếu bạn anh đồng ý, anh hãy cho em xin thông tin liên hệ của bạn anh để em dẫn đi xem phòng và làm thủ tục đăng ký.
*   Sau đó, anh và bạn anh cùng qua gặp em để làm thủ tục thanh lý hợp đồng cũ và ký hợp đồng mới.

Anh cứ hỏi ý kiến bạn mình trước nhé, nếu cần hỗ trợ thêm thông tin gì anh cứ nhắn em ạ!

**Turn 4**
- **Câu hỏi**: "OK em sẽ hỏi bạn. Mà nếu đi thì em cần làm gì để bàn giao phòng? Có checklist gì không? Em còn cái bàn làm việc đã báo hỏng từ lâu (mã TKT-2026-0009), cái đó có ảnh hưởng gì tới việc trả phòng không?"
- **Câu trả lời của AI**: Chào anh Hùng, về thủ tục trả phòng và vấn đề bàn làm việc, em xin giải đáp như sau:

### 1. Thủ tục bàn giao phòng
Theo quy định, khi anh muốn trả phòng, anh cần thực hiện các bước sau:
*   **Thông báo:** Báo trước cho quản lý ít nhất 30 ngày qua Zalo hoặc ứng dụng.
*   **Thanh toán:** Hoàn tất đầy đủ tiền phòng, điện, nước và các dịch vụ phát sinh đến ngày trả phòng.
*   **Vệ sinh:** Dọn dẹp sạch sẽ, trả lại phòng về tình trạng ban đầu (lau sạch bếp, nhà vệ sinh, vứt hết rác).
*   **Kiểm tra & Bàn giao:**
    *   Anh và quản lý sẽ cùng kiểm tra tình trạng phòng và các thiết bị.
    *   Lập biên bản bàn giao (có ghi nhận tình trạng đồ đạc, thiết bị).
    *   Trả lại 2 chìa khóa phòng, thẻ gửi xe và remote điều hòa (nếu có).
*   **Hoàn cọc:** Sau khi ký biên bản bàn giao, tiền cọc sẽ được hoàn lại trong vòng 14 ngày làm việc.

### 2. Về bàn làm việc (TKT-2026-0009)
Vì hệ thống đang gặp lỗi nhỏ khi truy xuất chi tiết trạng thái bảo trì, em sẽ trực tiếp kiểm tra lại tình trạng phiếu TKT-2026-0009 của anh ngay. 

Thông thường, các hư hỏng do hao mòn tự nhiên hoặc lỗi kỹ thuật từ phía tòa nhà sẽ **không ảnh hưởng** đến việc trả phòng hay khấu trừ cọc của anh. Tuy nhiên, để đảm bảo quyền lợi, em sẽ ưu tiên xử lý dứt điểm phiếu này trước khi anh bàn giao phòng.

Anh yên tâm, em sẽ kiểm tra và thông báo lại cho anh ngay ạ!

