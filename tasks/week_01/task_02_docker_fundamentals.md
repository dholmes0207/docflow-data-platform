# Task 0.2: Cài Đặt Docker Desktop & Cấu Hình Tối Ưu RAM Trên Windows 11

- **Giai đoạn:** Giai đoạn 0 — Khởi tạo nền tảng
- **Thời lượng ước tính:** 2 – 3 ngày (4 – 6 giờ làm việc)
- **Mục tiêu:** U cài đặt được Docker Desktop liên kết với WSL2, cấu hình giới hạn RAM an toàn cho hệ thống (16GB RAM) để tránh treo máy, và làm chủ các lệnh Docker CLI cơ bản.

---

## 🎯 Tiêu Chí Hoàn Thành (Definition of Done - DoD)
1. Trong terminal Ubuntu (WSL2), U chạy được lệnh `docker ps` mà không cần dùng quyền `sudo` và không bị báo lỗi kết nối Docker daemon.
2. File cấu hình `.wslconfig` được tạo chuẩn trong thư mục Windows User, giới hạn RAM tối đa cho WSL2 không vượt quá 10GB.
3. Chạy thành công container thử nghiệm `docker run --rm hello-world` từ terminal WSL và hiểu được đầu ra hiển thị.

---

## 🟢 MỨC 1: TỰ KHÁM PHÁ (U làm phần này trước)

### 1. Từ Khóa Tìm Kiếm (Search Keywords)
- `install docker desktop windows 11 wsl2 backend`
- `configure .wslconfig limit memory windows 11`
- `docker basic commands: run, ps, stop, rm, images`
- `difference between docker image and docker container`

### 2. Câu Hỏi Định Hướng Tư Duy
- *Container khác gì với Image? Nếu so sánh với lập trình hướng đối tượng (OOP), cái nào tương đương với Class, cái nào tương đương với Object/Instance?*
- *WSL2 trên Windows 11 mặc định có thể tự động ngốn đến 50% hoặc 80% dung lượng RAM của máy nếu không kiểm soát. Làm sao để đặt trần (limit) RAM cho nó?*
- *Lệnh `docker run -d -p 8080:80 nginx` có ý nghĩa gì? Số 8080 là gì, số 80 là gì?*

---

## 🟡 MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH (Chỉ mở khi bị tắc)

<details>
<summary>👉 <b>Bấm vào đây để xem hướng dẫn chi tiết từng bước</b></summary>

### Bước 1: Giới hạn RAM cho WSL2 qua file `.wslconfig`
*Máy của U có 16GB RAM. Nếu chạy song song Windows + Chrome + VS Code + Docker (Postgres, MinIO, Python), ta cần cố định mức RAM cho WSL2 là 10GB để máy luôn mượt.*

1. Mở PowerShell trên Windows (không cần quyền Admin).
2. Tạo hoặc chỉnh sửa file `.wslconfig` tại thư mục người dùng Windows bằng lệnh sau:
   ```powershell
   notepad $env:USERPROFILE\.wslconfig
   ```
3. Khi Notepad mở ra, dán nội dung sau vào:
   ```ini
   [wsl2]
   memory=10GB
   processors=4
   swap=2GB
   ```
4. Bấm `Ctrl + S` để lưu lại và tắt Notepad.
5. Chạy lệnh tắt hẳn WSL để áp dụng cấu hình:
   ```powershell
   wsl --shutdown
   ```

### Bước 2: Cài đặt Docker Desktop trên Windows 11
1. Tải bộ cài đặt chính thức từ: `https://www.docker.com/products/docker-desktop/`.
2. Chạy file cài đặt `Docker Desktop Installer.exe`.
3. Trong màn hình cài đặt, **bắt buộc tích chọn:**
   - `Use WSL 2 instead of Hyper-V (recommended)`.
4. Bấm **OK** và chờ cài đặt hoàn tất. Khởi động lại máy nếu được yêu cầu.

### Bước 3: Kích hoạt WSL2 Integration trong Docker Desktop
1. Mở ứng dụng **Docker Desktop** trên Windows.
2. Bấm vào icon bánh răng **Settings** ở góc trên bên phải.
3. Chọn mục **General** -> Đảm bảo đã tích chọn: `Use the WSL 2 based engine`.
4. Chọn mục **Resources** -> **WSL integration**:
   - Bật công tắc `Enable integration with my default WSL distro`.
   - Bật thêm công tắc ở dòng `Ubuntu-22.04`.
5. Bấm nút **Apply & restart** ở góc dưới cùng bên phải.

### Bước 4: Kiểm tra và chạy thử container từ Terminal Ubuntu
1. Mở VS Code (đang ở môi trường WSL Ubuntu).
2. Mở Terminal và kiểm tra:
   ```bash
   docker --version
   docker ps
   ```
3. Chạy thử container `hello-world`:
   ```bash
   docker run --rm hello-world
   ```
   Nếu màn hình hiển thị:
   > `Hello from Docker! This message shows that your installation appears to be working correctly.`
   thì xin chúc mừng, toàn bộ môi trường Docker đã sẵn sàng!

### ⚠️ Bắt Lỗi Thường Gặp (Troubleshooting)
- **Lỗi: `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`**
  - *Nguyên nhân:* Ứng dụng Docker Desktop trên Windows chưa được bật hoặc đang khởi động dở.
  - *Cách xử lý:* Bật Docker Desktop trên Windows lên, chờ đến khi icon cá voi ở góc dưới thanh taskbar Windows chuyển sang trạng thái màu xanh lá cây ("Engine running").
- **Lỗi: Máy tính bị đơ, quạt hú to khi chạy Docker**
  - *Cách xử lý:* Kiểm tra lại file `C:\Users\<TênUser>\.wslconfig` xem đã tạo đúng chưa và đã chạy `wsl --shutdown` chưa.

</details>
