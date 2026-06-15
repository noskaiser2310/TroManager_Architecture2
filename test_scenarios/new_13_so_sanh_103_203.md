# Kịch bản: So sánh hai phòng 103 và 203

## Loại nhân vật: Khách mới đang tìm hiểu

### Thông tin nhân vật
| Field | Giá trị |
|-------|---------|
| Họ tên | Lê Thị Hương |
| Nghề nghiệp | Giáo viên mầm non |
| Ngân sách | 3 - 3.5 triệu |
| Yêu cầu | Phòng yên tĩnh, có máy lạnh, thoáng mát |
| Phòng cần so sánh | 103 (tầng 1, 3tr) và 203 (tầng 2, 3.2tr) |
| Tone | friendly |

### Kịch bản
Khách phân vân giữa 2 phòng 103 và 203, cần AI so sánh chi tiết về giá, diện tích, tầng, tiện nghi để quyết định.

### Câu hỏi mô phỏng
> "Em chào anh chị, em đang phân vân giữa phòng 103 giá 3tr và phòng 203 giá 3.2tr. Anh chị cho em hỏi phòng nào rộng hơn, thoáng hơn? Phòng nào yên tĩnh hơn? Em làm giáo viên nên tối cần soạn giáo án, cần yên tĩnh. Với phòng nào có máy lạnh tốt hơn ạ?"

### Hệ thống kỳ vọng xử lý
- Router -> System 2 -> compare_rooms (103, 203) + query_policies (tien nghi phong)

### Kịch bản test
- File test: `new_13_test.py`


---

## Kết quả hội thoại thực tế
*Chạy lúc: 2026-06-15 09:32:05*

**Turn 1**
- **Câu hỏi**: "Em chào anh chị, em đang phân vân giữa phòng 103 giá 3tr và phòng 203 giá 3.2tr. Anh chị cho em hỏi phòng nào rộng hơn, thoáng hơn? Phòng nào yên tĩnh hơn? Em làm giáo viên nên tối cần soạn giáo án, cần yên tĩnh. Với phòng nào có máy lạnh tốt hơn ạ?"
- **Câu trả lời của AI**: Chào bạn, cảm ơn bạn đã quan tâm đến phòng tại nhà trọ. Dựa trên thông tin từ hệ thống, mình xin cung cấp thông tin chi tiết về hai phòng 103 và 203 để bạn dễ dàng lựa chọn:

**Thông tin so sánh:**

| Đặc điểm | Phòng 103 | Phòng 203 |
| :--- | :--- | :--- |
| **Giá thuê** | 3,000,000đ/tháng | 3,200,000đ/tháng |
| **Diện tích** | 20.00 m² | 22.00 m² |
| **Tầng** | Tầng 1 | Tầng 2 |
| **Tiện nghi** | Giường, Bàn bếp, Cửa sổ, Nóng lạnh, Điều hòa, Tủ quần áo | Giường, Bàn bếp, Cửa sổ, Nóng lạnh, Điều hòa, Tủ quần áo |

**Giải đáp thắc mắc của bạn:**

*   **Về diện tích:** Phòng 203 rộng hơn phòng 103 (22m² so với 20m²).
*   **Về độ thoáng và yên tĩnh:** Thông thường, các phòng ở tầng cao hơn như tầng 2 sẽ thoáng đãng hơn và ít chịu ảnh hưởng bởi tiếng ồn từ khu vực để xe hoặc người qua lại ở tầng trệt. Vì bạn là giáo viên và cần không gian yên tĩnh để soạn giáo án vào buổi tối, phòng 203 có thể là lựa chọn phù hợp hơn.
*   **Về điều hòa:** Cả hai phòng đều được trang bị điều hòa tiêu chuẩn như nhau. Hệ thống chưa ghi nhận sự khác biệt về chất lượng máy lạnh giữa hai phòng này.

Nếu bạn muốn kiểm tra thực tế, mình có thể hỗ trợ đặt lịch hẹn để bạn qua xem trực tiếp cả hai phòng. Bạn thấy sao ạ?

