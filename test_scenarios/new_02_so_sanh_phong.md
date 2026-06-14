# Kịch bản: So sánh chi tiết 2 phòng để quyết định

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Trần Thị Hạnh |
| Nghề nghiệp | Giáo viên |
| Ngân sách | 3 - 4 triệu |
| Đặc biệt | Cần phòng yên tĩnh để soạn bài |
| Phân vân giữa | Phòng 202 (4tr, 28m², ban công) và phòng 303 (3.5tr, 25m², tầng 3) |
| Tone | cẩn thận, chi tiết |

### Kịch bản
Khách đã xem sơ qua web và thấy 2 phòng ưng ý (202 và 303). Muốn so sánh chi tiết về giá, diện tích, hướng phòng, tiện nghi trước khi quyết định đến xem.

### Câu hỏi mô phỏng
> "Dạ em chào anh chị. Em đang phân vân giữa phòng 202 và 303. Anh chị cho em hỏi chi tiết 2 phòng này khác nhau thế nào ạ? Phòng nào rộng hơn? Có máy lạnh không? Hướng phòng có bị nắng chiều không? Phòng 202 thấy có ban công, ban công rộng không? Giá cả chênh lệch nhiều không ạ? Em ở một mình nên cần phòng yên tĩnh tí."

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> compare_rooms (room 202 vs 303) + get_room_info
- Gọi `compare_rooms` với room 202 vs 303
- Gọi `get_room_info` cho cả 2 phòng
- Trả về: Bảng so sánh side-by-side — 202 (28m², 4tr, ban công rộng, hướng nam, máy lạnh Daikin) vs 303 (25m², 3.5tr, không ban công, hướng bắc, máy lạnh LG)




---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 00:40:20*

**Turn 1**
- **Câu hỏi**: "Dạ em chào anh chị. Em đang phân vân giữa phòng 202 và 303. Anh chị cho em hỏi chi tiết 2 phòng này khác nhau thế nào ạ? Phòng nào rộng hơn? Có máy lạnh không? Hướng phòng có bị nắng chiều không? Phòng 202 thấy có ban công, ban công rộng không? Giá cả chênh lệch nhiều không ạ? Em ở một mình nên cần phòng yên tĩnh tí."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ. Dưới đây là thông tin chi tiết so sánh giữa phòng 202 và 303 để bạn dễ dàng lựa chọn:

### So sánh chi tiết

| Tiêu chí | Phòng 202 | Phòng 303 |
| :--- | :--- | :--- |
| **Diện tích** | 28.00 m² | 25.00 m² |
| **Giá thuê** | 4,000,000đ/tháng | 3,500,000đ/tháng |
| **Ban công** | Có (rộng) | Không |
| **Hướng cửa sổ** | Hướng Nam | Hướng Bắc |
| **Điều hòa** | Daikin 12000BTU | LG 9000BTU |
| **Tủ quần áo** | 4 cánh | 3 cánh |

### Giải đáp các thắc mắc của bạn:
*   **Độ rộng:** Phòng 202 rộng hơn (28m² so với 25m² của phòng 303).
*   **Máy lạnh:** Cả hai phòng đều được trang bị máy lạnh (Phòng 202 dùng Daikin 12000BTU, phòng 303 dùng LG 9000BTU).
*   **Hướng phòng & Nắng chiều:** Phòng 202 có cửa sổ hướng Nam và phòng 303 có cửa sổ hướng Bắc. Với hướng này, cả hai phòng đều không bị nắng chiều trực tiếp chiếu vào, giúp không gian mát mẻ hơn.
*   **Ban công:** Phòng 202 có ban công rộng, rất thuận tiện để phơi đồ hoặc thư giãn. Phòng 303 không có ban công.
*   **Sự yên tĩnh:** Vì bạn ở một mình và ưu tiên sự yên tĩnh, cả hai phòng đều là lựa chọn tốt. Tuy nhiên, phòng 303 nằm ở tầng cao hơn (tầng 3) nên thường sẽ có lưu lượng người qua lại ít hơn so với tầng 2.

**Chi phí khác:** Cả hai phòng đều có chung mức phí dịch vụ là 50,000đ/tháng, phí điện 3,500đ/kWh và phí nước 100,000đ/m³.

Nếu bạn muốn ghé xem trực tiếp, hãy cho mình biết thời gian thuận tiện, mình sẽ hỗ trợ đặt lịch cho bạn nhé!

