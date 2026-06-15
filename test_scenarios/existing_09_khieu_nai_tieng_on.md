# Kịch bản: Khiếu nại tiếng ồn từ hàng xóm

## Loại nhân vật: Khách đã thuê trọ

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Thị Hoa |
| Tenant ID | 2 |
| Phòng | 102 (tầng 1, 30m², 4.500.000đ/tháng) |
| Tone | professional |
| Hợp đồng | 2025-03-01 → 2026-08-31 |
| Hồ sơ ngầm | "Khách thích phòng yên tĩnh, nhạy cảm về tiếng ồn" |
| Ticket | TKT-0002 (wifi, in_progress) |

### Multi-turn conversation

**Turn 1** — Khách phàn nàn về tiếng ồn, giọng bức xúc.
> "Chào admin, tôi ở phòng 102. Gần đây tối nào cũng có tiếng nhạc ầm ĩ từ tầng trên, hình như từ phòng nào đó tầng 2. Tôi đã lên gõ cửa hỏi nhưng không ai mở. Tôi cần làm việc yên tĩnh vào buổi tối. Nhờ admin xử lý giúp."

**Hệ thống**: Tra nội quy giờ yên tĩnh (22h-6h), hứa liên hệ kiểm tra và nhắc nhở phòng gây ồn.

**Turn 2** — Khách hỏi quy định cụ thể và cách xử lý.
> "Nội quy nhà trọ quy định thế nào về giờ yên tĩnh? Nếu họ tái phạm thì bên mình xử lý ra sao? Tôi muốn biết quy trình rõ ràng để nếu còn tái diễn thì tôi biết đường yêu cầu tiếp."

**Hệ thống**: Cung cấp nội quy — giờ yên tĩnh 22h-6h, mức cảnh cáo: lần 1 nhắc nhở, lần 2 cảnh cáo bằng văn bản, lần 3 phạt tiền hoặc chấm dứt hợp đồng.

**Turn 3** — Khách báo vẫn chưa hết ồn.
> "Tối qua họ vẫn ồn tới 1h sáng. Admin đã nhắc nhở họ chưa? Nếu chưa thì đề nghị gấp, tôi không thể tập trung làm việc được. Tôi yêu cầu phản hồi trong hôm nay."

**Hệ thống**: Xác nhận đã gửi cảnh báo, hứa tăng cường biện pháp nếu còn tái phạm. Đề nghị tenant ghi lại bằng chứng (video/thời gian) nếu cần.

**Turn 4** — Khách yêu cầu đổi phòng nếu không giải quyết được.
> "Nếu tình trạng này kéo dài, tôi yêu cầu được đổi sang phòng yên tĩnh hơn, tầng cao hoặc cuối dãy. Tôi sẵn sàng trả thêm tiền nếu cần thiết. Hợp đồng của tôi còn 2 tháng nữa, tôi muốn ở tiếp nhưng cần yên tĩnh."

**Hệ thống**: Ghi nhận yêu cầu đổi phòng. Kiểm tra available rooms (202, 203, 303), gợi ý phòng tầng cao (303 tầng 3, 3.5tr) hoặc phòng cuối dãy.

### Hệ thống kỳ vọng xử lý
- Turn 1: Router → System 1 → query_policies (giờ yên tĩnh)
- Turn 2: Router → System 1 → query_policies (mức phạt)
- Turn 3: Router → System 2 → cập nhật warning cho phòng gây ồn
- Turn 4: Router → System 2 → fetch_available_rooms + recommend_transfer
### Kịch bản test
- File test: `existing_09_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:13:17*

**Turn 1**
- **Câu hỏi**: "Chào admin, tôi ở phòng 102. Gần đây tối nào cũng có tiếng nhạc ầm ĩ từ tầng trên, hình như từ phòng nào đó tầng 2. Tôi đã lên gõ cửa hỏi nhưng không ai mở. Tôi cần làm việc yên tĩnh vào buổi tối. Nhờ admin xử lý giúp."
- **Câu trả lời của AI**: Chào chị Hoa, em rất xin lỗi vì chị đã phải chịu đựng tiếng ồn làm ảnh hưởng đến công việc của mình. Em hiểu chị cần không gian yên tĩnh, đặc biệt là vào buổi tối.

Em đã ghi nhận sự việc và tạo phiếu phản ánh khẩn cấp để Ban quản lý kiểm tra các phòng ở tầng 2 ngay lập tức:

*   **Mã phiếu phản ánh:** TKT-2026-428D25
*   **Mức độ:** Cao
*   **Trạng thái:** Đã tiếp nhận

Ban quản lý sẽ trực tiếp kiểm tra và làm việc với các phòng ở tầng 2 để đảm bảo quy định về tiếng ồn được tuân thủ nghiêm ngặt. Nếu tình trạng này vẫn tiếp diễn ngay tối nay, chị vui lòng báo lại cho em hoặc liên hệ trực tiếp với bảo vệ tòa nhà để được hỗ trợ xử lý ngay lập tức chị nhé.

Em cảm ơn chị đã thông báo để Ban quản lý kịp thời xử lý ạ!

**Turn 2**
- **Câu hỏi**: "Nội quy nhà trọ quy định thế nào về giờ yên tĩnh? Nếu họ tái phạm thì bên mình xử lý ra sao? Tôi muốn biết quy trình rõ ràng để nếu còn tái diễn thì tôi biết đường yêu cầu tiếp."
- **Câu trả lời của AI**: Chào chị Hoa, em hiểu sự phiền lòng của chị khi bị ảnh hưởng bởi tiếng ồn. Dưới đây là thông tin chi tiết về quy định giờ yên tĩnh và quy trình xử lý vi phạm của tòa nhà để chị nắm rõ ạ:

### 1. Quy định về giờ yên tĩnh
Tòa nhà quy định khung giờ yên tĩnh tuyệt đối như sau:
*   **Thứ 2 - Thứ 6:** Từ 22:00 đến 06:00 sáng hôm sau.
*   **Thứ 7 & Chủ nhật:** Từ 22:00 đến 07:00 sáng hôm sau.

Trong khung giờ này, cư dân không được hát karaoke, mở nhạc lớn, hội họp đông người hoặc gây tiếng ồn ảnh hưởng đến người khác.

### 2. Quy trình xử lý vi phạm
Tùy theo mức độ vi phạm, Ban quản lý sẽ áp dụng các hình thức xử lý sau:
*   **Vi phạm nhẹ (nói chuyện ồn sau 22h):** Nhắc nhở trực tiếp.
*   **Vi phạm trung bình (hát karaoke, mở nhạc lớn):** Cảnh cáo và phạt 200.000đ.
*   **Vi phạm nặng (gây mất trật tự nghiêm trọng):** Phối hợp với cơ quan công an địa phương để xử lý.

### 3. Cách thức chị yêu cầu hỗ trợ nếu tái diễn
Nếu tình trạng này còn tiếp diễn, chị có thể thực hiện một trong các cách sau để Ban quản lý can thiệp kịp thời:
*   **Báo trực tiếp qua khung chat này:** Em sẽ ghi nhận và gửi thông báo nhắc nhở ngay lập tức.
*   **Đăng ký khiếu nại qua App nhà trọ.**
*   **Liên hệ trực tiếp Quản lý:** 0901-234-567 (Zalo).
*   **Trường hợp khẩn cấp ban đêm:** Chị có thể gọi trực tiếp cho số điện thoại trên.

Chị cứ yên tâm, em đã ghi nhận yêu cầu của chị và sẽ theo sát vấn đề này. Nếu có bất kỳ sự cố nào xảy ra, chị hãy báo ngay cho em nhé!

**Turn 3**
- **Câu hỏi**: "Tối qua họ vẫn ồn tới 1h sáng. Admin đã nhắc nhở họ chưa? Nếu chưa thì đề nghị gấp, tôi không thể tập trung làm việc được. Tôi yêu cầu phản hồi trong hôm nay."
- **Câu trả lời của AI**: Chào chị Hoa, em rất xin lỗi vì sự bất tiện này vẫn tiếp diễn khiến chị không thể tập trung làm việc.

Em đã ghi nhận phản ánh của chị và tạo phiếu yêu cầu xử lý khẩn cấp với mã **TKT-2026-F13E5A**. Ban quản lý sẽ trực tiếp làm việc với cư dân phòng gây ồn ngay trong hôm nay để đảm bảo không gian yên tĩnh cho chị.

Em sẽ theo sát và cập nhật kết quả xử lý cho chị sớm nhất có thể. Chị yên tâm nhé!

**Turn 4**
- **Câu hỏi**: "Nếu tình trạng này kéo dài, tôi yêu cầu được đổi sang phòng yên tĩnh hơn, tầng cao hoặc cuối dãy. Tôi sẵn sàng trả thêm tiền nếu cần thiết. Hợp đồng của tôi còn 2 tháng nữa, tôi muốn ở tiếp nhưng cần yên tĩnh."
- **Câu trả lời của AI**: Chào chị Hoa, em rất chia sẻ với mong muốn được ở trong không gian yên tĩnh của chị.

Dựa trên lịch sử yêu cầu và nhu cầu của chị, em đã tìm được một số phòng trống phù hợp với tiêu chí tầng cao và cuối dãy (thường yên tĩnh hơn) để chị cân nhắc chuyển đổi:

*   **Phòng 203 (Tầng 2):** Diện tích 22m², giá 3,200,000đ/tháng.
*   **Phòng 303 (Tầng 3):** Diện tích 25m², giá 3,500,000đ/tháng.

Các phòng này đều nằm ở cuối dãy, đảm bảo sự riêng tư và yên tĩnh hơn so với vị trí hiện tại của chị.

Về việc gia hạn hợp đồng, em đã ghi nhận mong muốn của chị. Với tình trạng hiện tại, em sẽ hỗ trợ chị ưu tiên xử lý dứt điểm vấn đề tiếng ồn. Nếu chị muốn xem trực tiếp các phòng trên để quyết định chuyển đổi, chị cho em biết thời gian thuận tiện, em sẽ sắp xếp lịch xem phòng cho chị nhé.

Chị có cần em hỗ trợ thêm thông tin gì về các phòng này không ạ?

