# SƠ ĐỒ DFD CẤP 3 - HỆ THỐNG QUẢN LÝ RẠP CHIẾU PHIM

## 📋 Tổng quan

DFD cấp 3 mô tả chi tiết các quy trình con trong từng chức năng chính của hệ thống quản lý rạp chiếu phim.

---

## 🎯 1. QUY TRÌNH QUẢN LÝ PHIM (Process 1.0)

### 1.1. Cập nhật thông tin phim

```
External Entity: Nhân viên quản lý
    |
    | Thông tin phim mới
    v
[1.1 Kiểm tra thông tin phim]
    |
    | Thông tin hợp lệ
    v
[1.2 Lưu thông tin phim] --> D1: PHIM
    |
    | Xác nhận
    v
External Entity: Nhân viên quản lý
```

**Data Stores:**

-   D1: PHIM (MaPhim, TenPhim, TheLoai, ThoiLuong, DaoDien, NgayKhoiChieu, MoTa)

**Inputs:**

-   Thông tin phim (từ Nhân viên quản lý)

**Outputs:**

-   Xác nhận cập nhật
-   Thông báo lỗi (nếu có)

---

### 1.2. Xóa phim

```
External Entity: Nhân viên quản lý
    |
    | Mã phim cần xóa
    v
[1.3 Kiểm tra ràng buộc] <-- D2: SUATCHIEU
    |                          D3: VECHIEU
    | Không có ràng buộc
    v
[1.4 Xóa phim] --> D1: PHIM
    |
    | Xác nhận xóa
    v
External Entity: Nhân viên quản lý
```

---

## 🎬 2. QUY TRÌNH QUẢN LÝ SUẤT CHIẾU (Process 2.0)

### 2.1. Thêm suất chiếu mới

```
External Entity: Nhân viên lập lịch
    |
    | Thông tin suất chiếu
    v
[2.1 Kiểm tra phòng chiếu] <-- D4: PHONGCHIEU
    |
    | Phòng trống
    v
[2.2 Kiểm tra phim] <-- D1: PHIM
    |
    | Phim hợp lệ
    v
[2.3 Tạo suất chiếu] --> D2: SUATCHIEU
    |
    | Xác nhận
    v
External Entity: Nhân viên lập lịch
```

**Data Stores:**

-   D1: PHIM
-   D2: SUATCHIEU (MaSuatChieu, MaPhim, MaPhongChieu, GioChieu, NgayChieu, GiaVe)
-   D4: PHONGCHIEU

**Business Rules:**

-   Không trùng lịch phòng chiếu
-   Khoảng cách giữa 2 suất ≥ thời lượng phim + 30 phút

---

### 2.2. Hủy suất chiếu

```
External Entity: Nhân viên quản lý
    |
    | Mã suất chiếu
    v
[2.4 Kiểm tra vé đã bán] <-- D3: VECHIEU
    |
    | Danh sách vé
    v
[2.5 Hoàn tiền khách hàng] --> D5: KHACHHANG
    |                            D6: HOADON
    | Hoàn tiền xong
    v
[2.6 Hủy suất chiếu] --> D2: SUATCHIEU
    |
    | Thông báo
    v
External Entity: Khách hàng (qua email/SMS)
```

---

## 🎫 3. QUY TRÌNH ĐẶT VÉ VÀ BÁN VÉ (Process 3.0)

### 3.1. Đặt vé online

```
External Entity: Khách hàng
    |
    | Chọn phim + suất chiếu
    v
[3.1 Hiển thị sơ đồ ghế] <-- D4: PHONGCHIEU
    |                          D3: VECHIEU
    | Chọn ghế
    v
[3.2 Kiểm tra ghế trống]
    |
    | Ghế khả dụng
    v
[3.3 Tính tiền] <-- D2: SUATCHIEU (GiaVe)
    |
    | Tổng tiền
    v
[3.4 Xử lý thanh toán] <-- D7: THANHTOAN
    |
    | Thanh toán thành công
    v
[3.5 Tạo vé] --> D3: VECHIEU
    |          --> D6: HOADON
    |
    | Mã vé + QR Code
    v
External Entity: Khách hàng (qua email)
```

**Data Flow:**

-   Input: Thông tin đặt vé (MaSuatChieu, DanhSachGhe, ThongTinKH)
-   Output: Vé điện tử (MaVe, QRCode, ThongTinSuatChieu)

---

### 3.2. Bán vé tại quầy

```
External Entity: Khách hàng
    |
    | Yêu cầu mua vé
    v
[3.6 Tra cứu suất chiếu] <-- D2: SUATCHIEU
    |
    | Thông tin suất chiếu
    v
External Entity: Nhân viên bán vé
    |
    | Chọn ghế
    v
[3.7 Kiểm tra ghế] <-- D3: VECHIEU
    |
    | Ghế trống
    v
[3.8 In vé] --> D3: VECHIEU
    |         --> D6: HOADON
    |
    | Vé giấy
    v
External Entity: Khách hàng
```

---

## 💳 4. QUY TRÌNH THANH TOÁN (Process 4.0)

### 4.1. Thanh toán online

```
External Entity: Khách hàng
    |
    | Thông tin thẻ/ví điện tử
    v
[4.1 Xác thực thanh toán] <-- External: Cổng thanh toán
    |
    | Xác thực thành công
    v
[4.2 Ghi nhận giao dịch] --> D7: THANHTOAN
    |                       --> D6: HOADON
    |
    | Hóa đơn điện tử
    v
External Entity: Khách hàng
```

---

### 4.2. Thanh toán tại quầy

```
External Entity: Khách hàng
    |
    | Tiền mặt/Thẻ
    v
[4.3 Nhận tiền]
    |
    v
[4.4 In hóa đơn] --> D6: HOADON
    |              --> D8: DOANHTHU
    |
    | Hóa đơn + Tiền thừa
    v
External Entity: Khách hàng
```

---

## 👤 5. QUY TRÌNH QUẢN LÝ KHÁCH HÀNG (Process 5.0)

### 5.1. Đăng ký thành viên

```
External Entity: Khách hàng
    |
    | Thông tin đăng ký
    v
[5.1 Kiểm tra email trùng] <-- D5: KHACHHANG
    |
    | Email chưa tồn tại
    v
[5.2 Tạo tài khoản] --> D5: KHACHHANG
    |
    | Tài khoản + Mật khẩu
    v
[5.3 Gửi email xác nhận] --> External Entity: Email Service
    |
    | Thông báo đăng ký thành công
    v
External Entity: Khách hàng
```

---

### 5.2. Tích điểm thành viên

```
[3.5 Tạo vé]
    |
    | Thông tin giao dịch
    v
[5.4 Tính điểm] <-- D5: KHACHHANG (BacThanhVien)
    |
    | Điểm tích lũy
    v
[5.5 Cập nhật điểm] --> D5: KHACHHANG
    |
    | Thông báo điểm thưởng
    v
External Entity: Khách hàng (qua app/email)
```

**Business Rule:**

-   10.000 VNĐ = 1 điểm
-   Thành viên Vàng: x1.5 điểm
-   Thành viên Kim Cương: x2 điểm

---

## 📊 6. QUY TRÌNH BÁO CÁO THỐNG KÊ (Process 6.0)

### 6.1. Báo cáo doanh thu

```
External Entity: Quản lý
    |
    | Yêu cầu báo cáo (Thời gian)
    v
[6.1 Truy vấn dữ liệu] <-- D6: HOADON
    |                       D8: DOANHTHU
    | Dữ liệu thống kê
    v
[6.2 Tính toán tổng hợp]
    |
    | Số liệu doanh thu
    v
[6.3 Tạo biểu đồ]
    |
    | Báo cáo PDF/Excel
    v
External Entity: Quản lý
```

---

### 6.2. Thống kê phim hot

```
External Entity: Quản lý
    |
    | Yêu cầu thống kê
    v
[6.4 Đếm số vé bán] <-- D3: VECHIEU
    |                    D1: PHIM
    | Danh sách phim
    v
[6.5 Sắp xếp theo doanh thu]
    |
    | Top phim hot
    v
[6.6 Xuất báo cáo] --> External Entity: Quản lý
```

---

## 📦 DATA STORES

| Ký hiệu | Tên Data Store | Mô tả                           |
| ------- | -------------- | ------------------------------- |
| D1      | PHIM           | Thông tin phim                  |
| D2      | SUATCHIEU      | Lịch chiếu phim                 |
| D3      | VECHIEU        | Vé đã bán                       |
| D4      | PHONGCHIEU     | Thông tin phòng chiếu           |
| D5      | KHACHHANG      | Thông tin khách hàng/thành viên |
| D6      | HOADON         | Hóa đơn thanh toán              |
| D7      | THANHTOAN      | Lịch sử giao dịch               |
| D8      | DOANHTHU       | Thống kê doanh thu              |

---

## 👥 EXTERNAL ENTITIES

1. **Khách hàng**: Người đặt/mua vé
2. **Nhân viên bán vé**: Xử lý giao dịch tại quầy
3. **Nhân viên quản lý**: Quản lý phim, suất chiếu
4. **Nhân viên lập lịch**: Sắp xếp lịch chiếu
5. **Quản lý**: Xem báo cáo, thống kê
6. **Cổng thanh toán**: VNPay, MoMo, ZaloPay
7. **Email Service**: Gửi xác nhận, thông báo

---

## 🔐 BUSINESS RULES

1. **Đặt vé:**

    - Chỉ được chọn ghế trống
    - Thanh toán trong 10 phút, nếu không tự động hủy

2. **Hủy vé:**

    - Trước 2 giờ chiếu: Hoàn 100%
    - Trong 2 giờ: Hoàn 50%
    - Sau giờ chiếu: Không hoàn

3. **Suất chiếu:**

    - Khoảng cách tối thiểu 30 phút giữa các suất
    - Tự động khóa đặt vé sau 15 phút bắt đầu chiếu

4. **Thành viên:**
    - Bạc: 0-999 điểm
    - Vàng: 1000-4999 điểm
    - Kim Cương: ≥5000 điểm

---

## 📝 GHI CHÚ

-   DFD cấp 3 này có thể mở rộng thêm các quy trình:
    -   Quản lý đồ ăn/đồ uống
    -   Quản lý khuyến mãi
    -   Quản lý nhân viên
    -   Bảo trì phòng chiếu
-   Mỗi process có thể có sub-process riêng tùy yêu cầu chi tiết
