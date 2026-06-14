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
*Chạy lúc: 2026-06-15 00:37:33*

**Turn 1**
- **Câu hỏi**: "Chào admin, tôi ở phòng 102. Gần đây tối nào cũng có tiếng nhạc ầm ĩ từ tầng trên, hình như từ phòng nào đó tầng 2. Tôi đã lên gõ cửa hỏi nhưng không ai mở. Tôi cần làm việc yên tĩnh vào buổi tối. Nhờ admin xử lý giúp."
- **Câu trả lời của AI**: Hệ thống đang xử lý yêu cầu phức tạp. Vui lòng liên hệ trực tiếp quản lý qua số ${LANDLORD_PHONE:-0901.234.567} để được hỗ trợ nhanh nhất.

**Turn 2**
- **Câu hỏi**: "Nội quy nhà trọ quy định thế nào về giờ yên tĩnh? Nếu họ tái phạm thì bên mình xử lý ra sao? Tôi muốn biết quy trình rõ ràng để nếu còn tái diễn thì tôi biết đường yêu cầu tiếp."
- **Câu trả lời của AI**: Chào chị Hoa, em rất hiểu sự phiền lòng của chị khi bị ảnh hưởng bởi tiếng ồn. Để chị nắm rõ quy trình và có cơ sở yêu cầu xử lý, em xin thông tin đến chị các quy định cụ thể như sau:

### 1. Quy định về giờ yên tĩnh
Theo nội quy tòa nhà, khung giờ yên tĩnh tuyệt đối được quy định như sau:
*   **Thứ 2 - Thứ 6:** Từ 22:00 đến 06:00 sáng hôm sau.
*   **Thứ 7 & Chủ nhật:** Từ 22:00 đến 07:00 sáng hôm sau.
*   **Yêu cầu:** Trong khung giờ này, cư dân không được hát karaoke, hội họp đông người hoặc mở loa lớn.

### 2. Quy trình xử lý vi phạm
Nếu tình trạng ồn ào tái diễn, Ban quản lý sẽ áp dụng các biện pháp xử lý theo mức độ vi phạm:
*   **Mức độ nhẹ (Nói chuyện ồn sau 22h):** Nhắc nhở trực tiếp.
*   **Mức độ trung bình (Hát karaoke, mở nhạc lớn):** Cảnh cáo và phạt 200.000đ/lần.
*   **Mức độ nặng (Gây mất trật tự nghiêm trọng):** Phối hợp với cơ quan công an địa phương để xử lý.

### 3. Cách thức chị có thể yêu cầu hỗ trợ
Nếu sự việc còn tái diễn, chị vui lòng thực hiện một trong các cách sau để Ban quản lý can thiệp kịp thời:
*   **Gửi khiếu nại qua App nhà trọ:** Đây là cách nhanh nhất để hệ thống ghi nhận và em sẽ xử lý ngay.
*   **Liên hệ trực tiếp qua Zalo:** Chị có thể nhắn tin cho quản lý qua số **0901-234-567**.
*   **Trường hợp khẩn cấp ban đêm:** Chị hãy gọi điện trực tiếp vào số hotline trên để được hỗ trợ ngay lập tức.

Chị cứ yên tâm, nếu có vấn đề phát sinh, chị hãy báo ngay cho em, em sẽ trực tiếp kiểm tra và xử lý nghiêm túc để đảm bảo không gian sống yên tĩnh cho chị ạ.

**Turn 3**
- **Câu hỏi**: "Tối qua họ vẫn ồn tới 1h sáng. Admin đã nhắc nhở họ chưa? Nếu chưa thì đề nghị gấp, tôi không thể tập trung làm việc được. Tôi yêu cầu phản hồi trong hôm nay."
- **Câu trả lời của AI**: Chào chị Hoa, em rất xin lỗi vì sự bất tiện này. Em hiểu rằng việc tiếng ồn kéo dài đến 1h sáng ảnh hưởng rất lớn đến công việc và sự nghỉ ngơi của chị.

Theo quy định về giờ giấc tại nhà trọ, khung giờ từ **22:00 đến 06:00** là thời gian yêu cầu **yên tĩnh tuyệt đối**. Việc gây ồn sau 22h được phân loại là vi phạm mức độ nhẹ và sẽ bị nhắc nhở.

Em xin ghi nhận phản hồi của chị ngay lập tức. Em sẽ kiểm tra lại lịch sử xử lý và tiến hành nhắc nhở phòng gây ồn theo đúng quy định. Em cam kết sẽ phản hồi lại kết quả xử lý cho chị trong hôm nay.

Cảm ơn chị đã thông tin kịp thời để em hỗ trợ giữ gìn không gian sống chung ạ.

**Turn 4**
- **Câu hỏi**: "Nếu tình trạng này kéo dài, tôi yêu cầu được đổi sang phòng yên tĩnh hơn, tầng cao hoặc cuối dãy. Tôi sẵn sàng trả thêm tiền nếu cần thiết. Hợp đồng của tôi còn 2 tháng nữa, tôi muốn ở tiếp nhưng cần yên tĩnh."
- **Câu trả lời của AI**: Chào chị Hoa, em rất hiểu và chia sẻ với mong muốn của chị về một không gian sống yên tĩnh. Vì chị là khách thuê ưu tiên sự yên tĩnh, em đã rà soát các phòng trống hiện có và xin đề xuất một số phương án phù hợp với yêu cầu của chị (tầng cao hơn hoặc cuối dãy) như sau:

*   **Phòng 203 (Tầng 2):** Diện tích 22m², giá 3,200,000đ/tháng.
*   **Phòng 303 (Tầng 3):** Diện tích 25m², giá 3,500,000đ/tháng.

Các phòng này đều nằm ở vị trí cuối dãy, hứa hẹn sẽ yên tĩnh hơn nhiều so với vị trí hiện tại của chị.

Về việc gia hạn hợp đồng, em rất trân trọng mong muốn tiếp tục gắn bó của chị. Nếu chị ưng ý với một trong các phòng trên, chị có muốn em sắp xếp lịch để mình qua xem trực tiếp không ạ? Sau khi chị chọn được phòng ưng ý, em sẽ hỗ trợ chị làm thủ tục chuyển phòng và gia hạn hợp đồng mới luôn ạ.

