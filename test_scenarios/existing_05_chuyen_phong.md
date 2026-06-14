# Kịch bản: Yêu cầu đổi phòng lên phòng có ban công

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Hoàng Tuấn |
| Tenant ID | 3 |
| Phòng hiện tại | 201 (tầng 2, 22m², 3.200.000đ/tháng) |
| Tone | friendly |
| Hợp đồng | 2024-06-01 → 2026-12-31 |
| Lịch sử | Thanh toán luôn đúng hạn, khách thân thiện |
| Behavior log | Đã đề nghị chuyển lên phòng có ban công (room_transfer) |
| Ghi chú | Khách nhiệt tình, tích cực, ở lâu dài |

### Multi-turn conversation

**Turn 1** — Khách nhắc lại yêu cầu đổi phòng có ban công.
> "Anh quản lý ơi, hồi trước em có nói muốn chuyển lên phòng có ban công, nay em hỏi lại lần nữa. Phòng 201 em ở thấy ổn nhưng thiếu ban công, quần áo phơi trong phòng ẩm quá. Bên mình còn phòng trống nào có ban công không em lên luôn?"

**Hệ thống**: Check available rooms có ban công — phòng 202 (tầng 2, 28m², 4.000.000đ, ban công rộng, hướng nam). Gợi ý phòng 202 là lựa chọn phù hợp nhất.

**Turn 2** — Khách hỏi chi tiết phòng 202.
> "Phòng 202 giá 4tr cao hơn phòng em đang ở 800k nhỉ. Nhưng 28m² rộng hơn, có ban công rộng, hướng nam thì chắc thoáng. Em hỏi tí: tiền chênh lệch tính thế nào? Em có phải đóng cọc thêm không? Có mất phí chuyển phòng không?"

**Hệ thống**: Hướng dẫn chính sách đổi phòng — phụ thu chênh lệch tiền phòng, không mất thêm cọc nếu đã đóng đủ, miễn phí chuyển phòng.

**Turn 3** — Khách muốn xem phòng trước.
> "Dạ em muốn qua xem phòng 202 một lần trước khi quyết định. Tầm chiều mai em rảnh sau 5h. Anh sắp xếp cho em xem được không ạ? Nếu ưng em chuyển luôn trong tuần."

**Hệ thống**: Xác nhận lịch xem phòng, ghi nhận request.

**Turn 4** — Khách hỏi thủ tục nếu đồng ý.
> "Cảm ơn anh. Nếu em ưng phòng 202 thì thủ tục chuyển ra sao? Em có cần ký hợp đồng mới không? Hay chỉ cần phụ lục điều chỉnh? Và chuyển xong trong ngày được không ạ?"

**Hệ thống**: Hướng dẫn chuyển phòng — ký phụ lục hợp đồng, bàn giao phòng cũ, nhận phòng mới. Có thể chuyển trong ngày.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 2 → fetch_available_rooms (filter: balcony, occupied=no)
- Turn 2: Router → System 2 → query_policies (chi phí chuyển phòng)
- Turn 3: Router → System 2 → schedule_room_viewing
- Turn 4: Router → System 2 → get_contract_status + query_policies
### Kịch bản test
- File test: `existing_05_test.py`




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:31:19*

**Turn 1**
- **Câu hỏi**: "Anh quản lý ơi, hồi trước em có nói muốn chuyển lên phòng có ban công, nay em hỏi lại lần nữa. Phòng 201 em ở thấy ổn nhưng thiếu ban công, quần áo phơi trong phòng ẩm quá. Bên mình còn phòng trống nào có ban công không em lên luôn?"
- **Câu trả lời của AI**: Chào anh Tuấn, em rất hiểu sự bất tiện của anh khi phòng không có ban công khiến việc phơi đồ khó khăn.

Dựa trên nhu cầu của anh, hiện tại bên em đang có 2 phòng trống có ban công phù hợp để anh chuyển sang đây ạ:

1.  **Phòng 203 (Tầng 2):** Diện tích 22m², giá thuê 3.200.000đ/tháng.
2.  **Phòng 202 (Tầng 2):** Diện tích 28m², giá thuê 4.000.000đ/tháng.

Anh xem qua thông tin này, nếu muốn ghé xem thực tế phòng nào thì báo em để em sắp xếp lịch cho anh nhé!

**Turn 2**
- **Câu hỏi**: "Phòng 202 giá 4tr cao hơn phòng em đang ở 800k nhỉ. Nhưng 28m² rộng hơn, có ban công rộng, hướng nam thì chắc thoáng. Em hỏi tí: tiền chênh lệch tính thế nào? Em có phải đóng cọc thêm không? Có mất phí chuyển phòng không?"
- **Câu trả lời của AI**: Chào anh Tuấn, em xin giải đáp các thắc mắc của anh về việc chuyển sang phòng 202 như sau ạ:

1. **Về tiền chênh lệch:**
   - Theo quy định, khi anh chuyển phòng, tiền chênh lệch giá thuê sẽ được tính bắt đầu từ ngày anh chính thức chuyển sang phòng mới. Vì phòng 202 có giá 4.000.000đ/tháng, phần chênh lệch sẽ được điều chỉnh trong hóa đơn tháng đó dựa trên số ngày thực tế anh ở tại phòng mới.

2. **Về phí chuyển phòng:**
   - Nếu đây là lần đầu tiên anh thực hiện chuyển phòng trong thời hạn hợp đồng, bên em sẽ **MIỄN PHÍ** chuyển phòng cho anh ạ. (Từ lần thứ 2 trở đi mới phát sinh phí 200.000đ/lần).

3. **Về tiền cọc:**
   - Khi chuyển phòng, chúng ta sẽ thực hiện ký phụ lục hợp đồng. Vì giá thuê phòng 202 cao hơn, thông thường sẽ cần điều chỉnh khoản tiền cọc để đảm bảo đúng với giá trị hợp đồng mới. Em sẽ kiểm tra lại số tiền cọc hiện tại của anh và thông báo cụ thể xem anh có cần đóng thêm phần chênh lệch hay không ngay khi anh quyết định chuyển ạ.

Phòng 202 đúng là rất thoáng và rộng rãi, rất phù hợp nếu anh muốn không gian thoải mái hơn. Nếu anh muốn chốt chuyển, anh cho em biết để em làm thủ tục phụ lục hợp đồng cho mình nhé!

**Turn 3**
- **Câu hỏi**: "Dạ em muốn qua xem phòng 202 một lần trước khi quyết định. Tầm chiều mai em rảnh sau 5h. Anh sắp xếp cho em xem được không ạ? Nếu ưng em chuyển luôn trong tuần."
- **Câu trả lời của AI**: Hệ thống đang xử lý yêu cầu phức tạp. Vui lòng liên hệ trực tiếp quản lý qua số ${LANDLORD_PHONE:-0901.234.567} để được hỗ trợ nhanh nhất.

**Turn 4**
- **Câu hỏi**: "Cảm ơn anh. Nếu em ưng phòng 202 thì thủ tục chuyển ra sao? Em có cần ký hợp đồng mới không? Hay chỉ cần phụ lục điều chỉnh? Và chuyển xong trong ngày được không ạ?"
- **Câu trả lời của AI**: Chào anh Tuấn, em đã kiểm tra thông tin phòng 202 và quy định về việc chuyển phòng để hỗ trợ anh đây ạ.

Về các thắc mắc của anh, em xin giải đáp như sau:

1. **Thủ tục chuyển phòng:** Anh chỉ cần gửi yêu cầu xác nhận chuyển phòng cho em. Sau đó, chúng ta sẽ thực hiện ký **Phụ lục hợp đồng** để cập nhật thông tin phòng mới và giá thuê mới, thay vì phải ký lại toàn bộ hợp đồng từ đầu.
2. **Chi phí:** Vì đây là lần đầu anh chuyển phòng, nên anh sẽ được **MIỄN PHÍ** chuyển phòng ạ.
3. **Thời gian chuyển:** Theo quy trình, chúng ta cần chốt ngày chuyển (thường ưu tiên vào đầu tháng để thuận tiện cho việc tính toán hóa đơn). Việc chuyển trong ngày hoàn toàn có thể thực hiện được sau khi đã hoàn tất ký phụ lục và bàn giao chìa khóa.

**Thông tin phòng 202 để anh tham khảo:**
*   **Diện tích:** 28m²
*   **Giá thuê:** 4,000,000đ/tháng
*   **Tiện nghi:** Ban công, Giường, Bàn bếp, Cửa sổ, Nóng lạnh, Điều hòa, Tủ quần áo.

Nếu anh ưng ý phòng 202, anh cho em biết để em làm thủ tục chuẩn bị phụ lục cho mình nhé!

