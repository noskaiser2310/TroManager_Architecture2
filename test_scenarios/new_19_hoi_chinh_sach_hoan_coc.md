# Kịch bản: Hỏi chính sách hoàn cọc và hủy phòng

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Nguyễn Văn Tùng |
| Nghề nghiệp | Kỹ sư xây dựng |
| Ngân sách | 4-5 triệu |
| Yêu cầu | Phòng rộng, nhưng sợ bị mất cọc nếu công việc đột xuất phải chuyển |
| Tone | cautious |

### Kịch bản
Khách nam làm kỹ sư có thể bị điều động công tác bất ngờ. Cần hiểu rõ chính sách hoàn cọc trước khi quyết định.

### Câu hỏi mô phỏng
> "Tôi muốn thuê phòng tầm 4-5 triệu, phòng rộng một chút. Nhưng tôi làm xây dựng hay bị điều động đột xuất, lỡ phải chuyển đi sớm thì tiền cọc có được hoàn lại không? Hợp đồng tối thiểu bao lâu? Có phí phạt nếu hủy trước hạn không?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> fetch_available_rooms (budget_min=4.0, budget_max=5.0) + query_policies (chinh sach coc, huy phong, phi phat)

### Kịch bản test
- File test: `new_19_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:33:27*

**Turn 1**
- **Câu hỏi**: "Tôi muốn thuê phòng tầm 4-5 triệu, phòng rộng một chút. Nhưng tôi làm xây dựng hay bị điều động đột xuất, lỡ phải chuyển đi sớm thì tiền cọc có được hoàn lại không? Hợp đồng tối thiểu bao lâu? Có phí phạt nếu hủy trước hạn không?"
- **Câu trả lời của AI**: Chào anh/chị, cảm ơn anh/chị đã quan tâm đến dịch vụ thuê phòng tại tòa nhà. Dựa trên yêu cầu của anh/chị, tôi xin cung cấp thông tin như sau:

### 1. Về phòng trống
Hiện tại, tòa nhà có phòng **202** (tầng 2) với diện tích **28m²**, giá thuê **4.000.000đ/tháng**, rất phù hợp với ngân sách và mong muốn không gian rộng rãi của anh/chị.

### 2. Về hợp đồng và tiền cọc
Theo chính sách của tòa nhà:
*   **Hợp đồng:** Thông tin về thời hạn tối thiểu không được quy định cụ thể là bao nhiêu tháng trong cơ sở dữ liệu, anh/chị vui lòng trao đổi trực tiếp với quản lý khi làm hợp đồng để có thỏa thuận phù hợp nhất với tính chất công việc của mình.
*   **Hoàn cọc:** 
    *   Tiền cọc sẽ được hoàn lại trong vòng **14 ngày làm việc** sau khi trả phòng, sau khi quản lý đã xác nhận tình trạng phòng và các khoản thanh toán.
    *   **Điều kiện hoàn cọc 100%:** Trả phòng đúng hạn, phòng không hư hỏng nặng, không nợ các khoản phí, đã trả đủ chìa khóa và thanh toán mọi hóa đơn đến ngày trả phòng.
*   **Phí phạt:** 
    *   Nếu vi phạm hợp đồng, mức khấu trừ có thể lên đến **tối đa 50% tiền cọc**.
    *   Các khoản khấu trừ khác bao gồm: hư hỏng nội thất (tùy mức độ), mất chìa khóa, chi phí vệ sinh phòng hoặc nợ tiền điện/nước/dịch vụ.

Vì tính chất công việc của anh/chị hay có sự điều động đột xuất, tôi khuyên anh/chị nên trao đổi rõ ràng với quản lý về điều khoản "chấm dứt hợp đồng trước hạn" ngay khi ký kết để có phương án bảo vệ quyền lợi tốt nhất.

Nếu anh/chị muốn xem phòng 202, vui lòng cho tôi biết thời gian cụ thể, tôi sẽ hỗ trợ đặt lịch cho anh/chị.

