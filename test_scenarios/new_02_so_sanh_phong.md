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
*Chạy lúc: 2026-06-15 09:29:34*

**Turn 1**
- **Câu hỏi**: "Dạ em chào anh chị. Em đang phân vân giữa phòng 202 và 303. Anh chị cho em hỏi chi tiết 2 phòng này khác nhau thế nào ạ? Phòng nào rộng hơn? Có máy lạnh không? Hướng phòng có bị nắng chiều không? Phòng 202 thấy có ban công, ban công rộng không? Giá cả chênh lệch nhiều không ạ? Em ở một mình nên cần phòng yên tĩnh tí."
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến các phòng tại nhà mình. Dưới đây là thông tin chi tiết để bạn so sánh giữa phòng 202 và 303:

### So sánh thông số kỹ thuật
| Đặc điểm | Phòng 202 | Phòng 303 |
| :--- | :--- | :--- |
| **Diện tích** | 28.00m² | 25.00m² |
| **Giá thuê** | 4,000,000đ/tháng | 3,500,000đ/tháng |
| **Tầng** | Tầng 2 | Tầng 3 |
| **Tiện nghi nổi bật** | Ban công rộng, Tủ 4 cánh | Tủ 3 cánh |
| **Hướng cửa sổ** | Hướng Nam | Hướng Bắc |
| **Điều hòa** | Daikin 12000BTU | LG 9000BTU |

### Giải đáp thắc mắc của bạn:
*   **Diện tích:** Phòng 202 rộng hơn (28m² so với 25m² của phòng 303).
*   **Máy lạnh:** Cả hai phòng đều được trang bị sẵn máy lạnh.
*   **Hướng nắng:** 
    *   Phòng 202 có cửa sổ hướng Nam, thường mát mẻ và đón gió tốt.
    *   Phòng 303 có cửa sổ hướng Bắc, tránh được nắng chiều trực tiếp.
*   **Ban công:** Phòng 202 có ban công rộng, rất thuận tiện nếu bạn muốn có không gian thoáng đãng. Phòng 303 không có ban công.
*   **Giá cả:** Chênh lệch 500,000đ/tháng giữa hai phòng.
*   **Độ yên tĩnh:** Cả hai phòng đều nằm ở khu vực yên tĩnh. Tuy nhiên, vì phòng 303 ở tầng cao hơn (tầng 3), nên thường sẽ hạn chế tiếng ồn từ khu vực sinh hoạt chung hoặc đường phố tốt hơn một chút so với tầng 2.

Nếu bạn muốn ghé xem thực tế để cảm nhận không gian, hãy cho mình biết thời gian thuận tiện, mình sẽ hỗ trợ đặt lịch xem phòng cho bạn nhé!

