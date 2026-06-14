# Quy định và hướng dẫn sử dụng wifi toà nhà

> **Tài liệu nội bộ** – Áp dụng cho tất cả cư dân / khách thuê trọ  
> Phiên bản: 3.0 | Ngày hiệu lực: Tháng 6/2026

---

## Mục lục

1. [Tổng quan hệ thống wifi](#1-tổng-quan-hệ-thống-wifi)
2. [Hệ thống wifi chung toà nhà](#2-hệ-thống-wifi-chung-toà-nhà)
3. [Hệ thống wifi riêng từng phòng](#3-hệ-thống-wifi-riêng-từng-phòng)
4. [So sánh nhanh – Nên dùng loại nào?](#4-so-sánh-nhanh--nên-dùng-loại-nào)
5. [Xử lý sự cố chung](#5-xử-lý-sự-cố-chung)
6. [Lưu ý khi sử dụng](#6-lưu-ý-khi-sử-dụng)
7. [Bảo trì & hỗ trợ](#7-bảo-trì--hỗ-trợ)
8. [Liên hệ](#8-liên-hệ)

---

## 1. Tổng quan hệ thống wifi

Toà nhà cung cấp **hai hệ thống wifi song song**:

| Hệ thống | Đối tượng | Đặc điểm |
|----------|-----------|----------|
| **Wifi chung toà nhà** | Tất cả cư dân | Dùng chung, phủ sóng toà nhà, băng thông 200 Mbps chia sẻ |
| **Wifi riêng từng phòng** | Từng phòng riêng biệt | Mỗi phòng một router riêng, băng thông 200 Mbps riêng, bảo mật cao |

> 📌 **Nguyên tắc:**  
> - Wifi chung: dùng cho nhu cầu cơ bản, di chuyển nhiều, hoàn toàn miễn phí.  
> - Wifi riêng: dùng cho nhu cầu cao hơn ngay tại phòng, không ảnh hưởng đến phòng khác.

---

## 2. Hệ thống wifi chung toà nhà

### 2.1. Thông tin mạng

| Thông số | Chi tiết |
|----------|----------|
| Tên mạng 1 (5GHz) | `TROHAIDANG_5G` |
| Tên mạng 2 (2.4GHz) | `TROHAIDANG_2.4G` |
| Mật khẩu | `trohaidang` |
| Băng thông | 200 Mbps **chia sẻ toà nhà** |
| Nhà cung cấp | FPT Telecom |
| Phạm vi phủ sóng | Toàn bộ toà nhà (hành lang, cầu thang, khu vực chung) |

### 2.2. Hướng dẫn kết nối

1. Mở **Cài đặt → Wifi** trên thiết bị
2. Chọn `TROHAIDANG_5G` (nếu thiết bị hỗ trợ) hoặc `TROHAIDANG_2.4G`
3. Nhập mật khẩu: `trohaidang`
4. Kết nối thành công

### 2.3. Nên dùng mạng nào?

| Tần số | Ưu điểm | Nên dùng khi |
|--------|---------|---------------|
| **5GHz** | Tốc độ cao, ít nhiễu | Ở gần router (cùng tầng hoặc tầng liền kề) |
| **2.4GHz** | Sóng xa, xuyên tường tốt | Ở xa router, tầng khác, hoặc dùng thiết bị IoT |

---

## 3. Hệ thống wifi riêng từng phòng

### 3.1. Thông tin mạng

| Thông số | Chi tiết |
|----------|----------|
| Tên mạng (SSID) | `PHONG_[Số phòng]_Wifi` (VD: `PHONG_301_Wifi`) |
| Mật khẩu | Riêng từng phòng (in dưới đáy router) |
| Băng thông | 200 Mbps **riêng cho phòng** |
| Bảo mật | WPA2-PSK |
| Phạm vi phủ sóng | Trong phòng (không đảm bảo sóng ra hành lang) |

### 3.2. Hướng dẫn kết nối lần đầu

**Bước 1:** Đảm bảo router trong phòng đã cắm điện, đèn nguồn sáng

**Bước 2:** Trên thiết bị, chọn mạng có tên `PHONG_[Số phòng]_Wifi`

**Bước 3:** Nhập mật khẩu được cấp (xem dưới đáy router)

**Bước 4:** Kiểm tra tốc độ tại `speedtest.net` (phải đạt 150–200 Mbps)

### 3.3. Lưu ý riêng

- Mỗi phòng chỉ có một router, không mang sang phòng khác
- Báo hỏng ngay nếu đèn router không sáng hoặc chớp đỏ

---

## 4. So sánh nhanh – Nên dùng loại nào?

| Nhu cầu của bạn | Dùng wifi chung | Dùng wifi riêng |
|----------------|:---------------:|:---------------:|
| Lướt web nhẹ, nghe nhạc | ✅ Nên dùng | ⚠️ Dùng được nhưng hơi phí |
| Xem phim (Netflix, YouTube) | ✅ Được | ✅ Tốt hơn |
| Học online, họp Zoom | ⚠️ Có thể giật giờ cao điểm | ✅ Rất tốt |
| Tải game, phần mềm lớn | ✅ Vẫn dùng được (chậm hơn) | ✅ Thoải mái |
| Ở hành lang, khu vực chung | ✅ Dùng được | ❌ Sóng yếu hoặc không có |
| Cần bảo mật cao | ❌ Yếu (dùng chung) | ✅ Rất tốt |

> 📌 **Khuyến nghị:**  
> - Dùng **wifi chung** khi ở ngoài phòng hoặc nhu cầu nhẹ.  
> - Dùng **wifi riêng** khi ở trong phòng, đặc biệt khi cần tốc độ và ổn định.

---

## 5. Xử lý sự cố chung

### 5.1. Không kết nối được (cả hai mạng)

| Bước | Hành động |
|------|------------|
| 1 | Tắt/bật wifi trên thiết bị |
| 2 | Quên mạng cũ → kết nối lại với đúng mật khẩu |
| 3 | Khởi động lại router (nếu dùng wifi riêng) hoặc chờ 1 phút (nếu dùng wifi chung) |
| 4 | Liên hệ hotline nếu vẫn không được |

### 5.2. Mạng chậm

| Trường hợp | Xử lý |
|------------|--------|
| Wifi chung chậm | Chuyển sang 5GHz nếu đang dùng 2.4GHz, hoặc dùng wifi riêng trong phòng |
| Wifi riêng chậm | Kiểm tra tốc độ, reboot router, báo quản lý nếu dưới 50 Mbps |
| Giờ cao điểm (19h–22h) | Wifi chung có thể chậm do đông người dùng → nên chuyển sang wifi riêng |

### 5.3. Quên mật khẩu

| Loại wifi | Cách lấy lại mật khẩu |
|-----------|------------------------|
| Wifi chung | Mật khẩu là `trohaidang` (cố định) |
| Wifi riêng | Xem dưới đáy router, hoặc gọi **0901-234-567** (cung cấp số phòng) |

---

## 6. Lưu ý khi sử dụng

### 6.1. Với wifi chung (miễn phí)

- Wifi chung được cung cấp miễn phí cho toàn bộ cư dân.
- Không có giới hạn về dung lượng hay hình phạt khi sử dụng.
- Tốc độ có thể thay đổi tuỳ theo số người dùng cùng lúc.

### 6.2. Với wifi riêng (từng phòng)

- Bạn có thể thay đổi mật khẩu wifi riêng theo nhu cầu.
- **⚠️ Lưu ý quan trọng:** Nếu bạn tự ý đổi mật khẩu wifi riêng mà **không thông báo** cho ban quản lý, khi bạn cần hỗ trợ kỹ thuật (ví dụ: mất kết nối, router lỗi), chúng tôi sẽ **không thể** can thiệp được do không biết mật khẩu mới.
- **Khuyến nghị:** Sau khi đổi mật khẩu, vui lòng **thông báo qua hotline** để lưu lại. Hoặc giữ nguyên mật khẩu mặc định dưới đáy router để dễ dàng hỗ trợ.

---

## 7. Bảo trì & hỗ trợ

### 7.1. Lịch bảo trì định kỳ

| Hệ thống | Tần suất | Thời gian dự kiến |
|----------|----------|-------------------|
| Wifi chung toà nhà | Hàng tháng | 2h – 4h sáng (Chủ nhật tuần đầu tháng) |
| Wifi riêng từng phòng | Khi có báo hỏng | Trong vòng 24h |

> Trước khi bảo trì wifi chung, sẽ có thông báo trước 48h.

### 7.2. Các dịch vụ hỗ trợ

| Dịch vụ | Chi phí | Thời gian xử lý |
|---------|---------|----------------|
| Báo hỏng router (wifi riêng) | Miễn phí (bảo hành 12 tháng) | 24h |
| Hỗ trợ khi quên mật khẩu wifi riêng | Miễn phí | Trong giờ hành chính |
| Hỗ trợ kết nối tại phòng | Miễn phí | Theo lịch hẹn |

---

## 8. Liên hệ

**Ban quản lý toà nhà** – Bộ phận kỹ thuật & hỗ trợ wifi

📞 **Hotline kỹ thuật:** `0901-234-567`  
🕒 **Thời gian hỗ trợ:** 8h00 – 20h00 (Thứ 2 – Chủ nhật)  
📍 **Văn phòng quản lý:** Tầng 1 (cạnh sảnh chính)

> **Khi gọi, vui lòng cung cấp:**  
> - Số phòng của bạn  
> - Loại wifi gặp sự cố (chung / riêng)  
> - Mô tả ngắn gọn vấn đề

---

## Phụ lục: Hướng dẫn nhanh (treo tường)

### A. Dùng wifi chung toà nhà

```
Tên mạng: TROHAIDANG_5G hoặc TROHAIDANG_2.4G
Mật khẩu: trohaidang
```

### B. Dùng wifi riêng phòng mình

```
Tên mạng: PHONG_[số phòng]_Wifi
Mật khẩu: xem dưới đáy router
```

### C. Khi gặp sự cố

```
1. Tắt/bật wifi
2. Khởi động lại router (nếu là wifi riêng)
3. Gọi 0901-234-567
```

---

*Tài liệu này có thể được cập nhật mà không cần thông báo trước.  
Bản cập nhật mới nhất được niêm yết tại văn phòng quản lý tầng 1.*

**Ban quản lý toà nhà**  
📅 Ngày ban hành: Tháng 6/2026