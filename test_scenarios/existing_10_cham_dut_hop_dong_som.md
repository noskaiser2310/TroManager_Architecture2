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
*Chạy lúc: 2026-06-15 00:39:40*

**Turn 1**
- **Câu hỏi**: "Chào admin, em có quyết định chuyển công tác vào Đà Nẵng gấp, phải đi trong tháng 7 này. Hợp đồng phòng 302 của em còn tới tháng 9, nhưng em không ở được nữa. Em muốn hỏi nếu chấm dứt sớm thì sẽ bị phạt thế nào? Có mất tiền cọc không ạ?"
- **Câu trả lời của AI**: Chào anh Hùng, rất tiếc khi nghe tin anh phải chuyển công tác gấp.

Về việc chấm dứt hợp đồng sớm tại phòng 302, theo quy định trong chính sách hợp đồng của tòa nhà, trường hợp bên thuê đơn phương chấm dứt hợp đồng sớm cần đảm bảo các điều kiện sau:

1. **Thông báo trước:** Anh cần báo trước cho Ban quản lý tối thiểu **30 ngày**.
2. **Nghĩa vụ tài chính:** Anh cần thanh toán đầy đủ các khoản phí đến ngày chấm dứt hợp đồng.
3. **Tình trạng phòng:** Phòng phải được trả lại trong tình trạng ban đầu.

**Về vấn đề tiền cọc:** Theo quy định, khi chấm dứt hợp đồng sớm, khách thuê có thể sẽ bị khấu trừ một phần tiền cọc (tối đa 50%).

Để có phương án hỗ trợ tốt nhất cho anh, anh vui lòng cho em biết chính xác ngày anh dự định chuyển đi (trong tháng 7) để em báo cáo lại với Ban quản lý và kiểm tra chi tiết hợp đồng của anh nhé. Anh có thể nhắn lại cho em hoặc ghé qua gặp trực tiếp em để làm thủ tục ạ.

**Turn 2**
- **Câu hỏi**: "Cụ thể là mất 1 tháng tiền cọc (9 triệu) hay toàn bộ cọc? Và em cần báo trước bao nhiêu ngày? 30 ngày hay 45 ngày? Em muốn biết chính xác để sắp xếp tài chính."
- **Câu trả lời của AI**: Chào anh Hùng, về thắc mắc của anh liên quan đến việc chấm dứt hợp đồng và tiền cọc, em xin phản hồi dựa trên chính sách của tòa nhà như sau:

1. **Thời gian báo trước:** Theo quy định, nếu anh đơn phương chấm dứt hợp đồng, anh cần báo trước cho Ban quản lý tối thiểu **30 ngày**.
2. **Về tiền cọc:** 
   - Nếu anh chấm dứt hợp đồng đúng hạn và tuân thủ các điều kiện (phòng không hư hỏng nặng, không nợ phí, trả phòng đúng tình trạng ban đầu), anh sẽ được hoàn lại 100% tiền cọc.
   - Trong trường hợp anh đơn phương chấm dứt hợp đồng sớm (khi chưa đến hạn), theo chính sách, anh có thể bị khấu trừ một phần tiền cọc (tối đa là 50%).

Việc khấu trừ cụ thể (nếu có) sẽ phụ thuộc vào tình trạng thực tế của phòng và các khoản phí còn lại tại thời điểm anh bàn giao phòng. Sau khi anh trả phòng, Ban quản lý sẽ kiểm tra và hoàn cọc trong vòng 14 ngày làm việc.

Để đảm bảo quyền lợi, khi anh có kế hoạch cụ thể, anh hãy thông báo sớm cho em để em hỗ trợ làm thủ tục bàn giao phòng đúng quy trình nhé. Nếu cần hỗ trợ thêm thông tin gì, anh cứ nhắn em ạ!

**Turn 3**
- **Câu hỏi**: "Em có thể tìm người vào ở thế được không? Có ông bạn đồng nghiệp cũng đang tìm phòng, em hỏi ổng coi. Nếu ổng chịu vào ở thì em có mất phí phạt không? Và thủ tục thế nào?"
- **Câu trả lời của AI**: Chào anh Hùng, về việc anh muốn giới thiệu bạn vào ở thay thế, em xin giải đáp như sau:

Việc anh giới thiệu người vào ở thay thế là hoàn toàn được phép. Để thực hiện, anh cần lưu ý các quy định sau:

1. **Về phí phạt:** Theo chính sách hiện tại, việc chuyển nhượng hợp đồng hoặc thay đổi người thuê không bị tính phí phạt, miễn là anh đảm bảo các điều kiện về thanh toán và thông báo.
2. **Thủ tục thực hiện:**
   - **Bước 1:** Anh vui lòng thông báo cho em thông tin của bạn anh (tên, số điện thoại) để em hỗ trợ tư vấn và dẫn bạn anh đi xem phòng.
   - **Bước 2:** Sau khi bạn anh đồng ý thuê, chúng ta sẽ tiến hành làm thủ tục chấm dứt hợp đồng cũ của anh và ký hợp đồng mới cho bạn anh.
   - **Bước 3:** Cập nhật lại thông tin cư trú và bàn giao phòng.

**Lưu ý:** Để quá trình diễn ra thuận lợi, anh nên báo trước cho em ít nhất 30 ngày (theo quy định chấm dứt/thay đổi hợp đồng) để bên em có thời gian chuẩn bị thủ tục giấy tờ cần thiết.

Anh cứ hỏi ý kiến bạn đồng nghiệp xem sao, nếu bạn anh quan tâm thì cứ nhắn em nhé!

**Turn 4**
- **Câu hỏi**: "OK em sẽ hỏi bạn. Mà nếu đi thì em cần làm gì để bàn giao phòng? Có checklist gì không? Em còn cái bàn làm việc đã báo hỏng từ lâu (mã TKT-2026-0009), cái đó có ảnh hưởng gì tới việc trả phòng không?"
- **Câu trả lời của AI**: Chào anh Hùng, về quy trình bàn giao phòng khi anh chuyển đi, anh vui lòng thực hiện theo các bước sau đây để đảm bảo quyền lợi của mình nhé:

### 1. Checklist bàn giao phòng
*   **Thông báo:** Anh cần báo trước cho Ban quản lý ít nhất **30 ngày** qua Zalo hoặc app, ghi rõ ngày dự kiến trả phòng.
*   **Thanh toán:** Hoàn tất đầy đủ các khoản phí (tiền phòng, điện, nước, dịch vụ) tính đến ngày trả phòng.
*   **Vệ sinh:** Dọn dẹp phòng sạch sẽ, trả lại tình trạng ban đầu (bao gồm giặt ga giường, khăn tắm, lau sạch bếp/nhà vệ sinh và vứt bỏ rác).
*   **Kiểm tra:** Ban quản lý sẽ đến kiểm tra phòng theo lịch hẹn, lập biên bản ghi nhận tình trạng phòng và đồ đạc.
*   **Trả vật dụng:** Bàn giao lại 2 chìa khóa phòng, thẻ gửi xe và remote điều hòa (nếu có).
*   **Ký biên bản & Hoàn cọc:** Ký biên bản bàn giao xác nhận tình trạng phòng và số tiền cọc được hoàn. Tiền cọc sẽ được hoàn lại trong vòng **14 ngày làm việc**.

### 2. Về phiếu bảo trì TKT-2026-0009 (Bàn làm việc)
Việc anh có phiếu bảo trì chưa xử lý **có thể ảnh hưởng** đến quá trình bàn giao nếu bàn làm việc bị hư hỏng do lỗi người dùng hoặc không được bảo trì kịp thời dẫn đến hư hỏng nặng. 

Vì hệ thống đang gặp lỗi nhỏ khi truy xuất chi tiết phiếu này, em sẽ trực tiếp kiểm tra lại tình trạng của phiếu TKT-2026-0009 và báo lại cho anh sớm nhất. Anh yên tâm, em sẽ hỗ trợ anh xử lý dứt điểm vấn đề này trước khi anh làm thủ tục trả phòng để tránh ảnh hưởng đến việc hoàn cọc nhé.

Anh còn cần em hỗ trợ thêm thông tin nào khác không ạ?

