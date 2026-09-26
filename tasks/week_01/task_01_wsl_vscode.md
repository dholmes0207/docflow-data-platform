# Task 0.1: Thiết Lập Môi Trường Linux Chuẩn Trên Windows 11 (WSL2 + VS Code)

- **Giai đoạn:** Giai đoạn 0 — Khởi tạo nền tảng
- **Thời lượng ước tính:** 1 – 2 ngày (3 – 5 giờ làm việc)
- **Mục tiêu:** U thiết lập được môi trường Ubuntu 22.04 LTS hoạt động mượt mà trên Windows 11 thông qua WSL2, tích hợp hoàn chỉnh với Visual Studio Code và cài sẵn môi trường Python.

---

## 🎯 Tiêu Chí Hoàn Thành (Definition of Done - DoD)
U được tính là hoàn thành task khi đạt đủ 3 tiêu chí sau trong buổi review:
1. Mở VS Code trên Windows, thanh trạng thái góc dưới bên trái có icon màu xanh hiện: `WSL: Ubuntu-22.04`.
2. Mở Terminal tích hợp của VS Code (Ctrl + `), chạy lệnh `python3 --version` hiển thị Python >= 3.10 và `git --version` hoạt động bình thường.
3. Thư mục code của U nằm hoàn toàn trong phân vùng Linux (ví dụ: `~/projects/docflow`), không nằm trong ổ `C:\` hay `/mnt/c/`.

---

## 🟢 MỨC 1: TỰ KHÁM PHÁ (U làm phần này trước)

### 1. Từ Khóa Tìm Kiếm (Search Keywords)
U hãy dùng các từ khóa này để tìm kiếm tài liệu chính thức hoặc bài viết hướng dẫn uy tín:
- `install wsl2 ubuntu 22.04 windows 11 powershell`
- `vscode wsl extension remote development`
- `why not to store files in /mnt/c in wsl2 performance`
- `create python virtual environment linux bash`

### 2. Câu Hỏi Định Hướng Tư Duy (U tự trả lời trước khi làm)
- *WSL2 khác gì so với việc cài một máy ảo VirtualBox hoặc VMware nặng nề?*
- *Tại sao khi làm việc với Git, Docker và Data Pipeline trên Windows, người ta luôn khuyên dùng WSL2 thay vì chạy trực tiếp trên CMD / PowerShell?*
- *Nếu U lưu project tại `/mnt/c/Users/...` thì tốc độ đọc ghi file (I/O) bị chậm đi như thế nào so với lưu tại `~/projects/...`?*

---

## 🟡 MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH (Chỉ mở khi bị tắc)

<details>
<summary>👉 <b>Bấm vào đây để xem hướng dẫn chi tiết từng bước</b></summary>

### Bước 1: Cài đặt WSL2 trên Windows 11
1. Nhấn phím `Windows`, gõ **PowerShell**, nhấp chuột phải chọn **Run as administrator**.
2. Chạy lệnh cài đặt Ubuntu 22.04:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```
3. Sau khi tải và cài xong, hệ thống có thể yêu cầu khởi động lại máy tính (Restart PC). U hãy khởi động lại.
4. Sau khi khởi động lại, một cửa sổ dòng lệnh màu đen của Ubuntu sẽ tự động bật lên. Hệ thống yêu cầu:
   - `Enter new UNIX username:` -> U nhập tên viết liền không dấu, ví dụ: `dholmes` hoặc tên của U.
   - `Enter new UNIX password:` -> U nhập mật khẩu (Lưu ý: trên Linux khi gõ mật khẩu con trỏ sẽ không di chuyển hay hiện dấu sao `*`, cứ gõ bình thường rồi Enter).

### Bước 2: Cập nhật hệ thống và cài đặt công cụ thiết yếu
Trong cửa sổ terminal của Ubuntu, gõ các lệnh sau:
```bash
# Cập nhật danh sách gói phần mềm
sudo apt update && sudo apt upgrade -y

# Cài đặt Python, Git, pip và công cụ biên dịch
sudo apt install -y python3-pip python3-venv git curl build-essential
```

### Bước 3: Cài đặt Visual Studio Code & Extension WSL
1. Tải và cài đặt VS Code trên Windows (nếu máy chưa có) từ trang chủ: `https://code.visualstudio.com/`.
2. Mở VS Code trên Windows, vào mục **Extensions** (phím tắt `Ctrl + Shift + X`).
3. Tìm kiếm extension tên là **WSL** (do Microsoft phát triển) và bấm **Install**.

### Bước 4: Tạo thư mục dự án và mở bằng VS Code
Trong terminal của Ubuntu (WSL), chạy các lệnh sau:
```bash
# 1. Tạo thư mục chứa các dự án bên trong phân vùng Linux (Home directory)
mkdir -p ~/projects/docflow

# 2. Di chuyển vào thư mục dự án
cd ~/projects/docflow

# 3. Mở VS Code trực tiếp từ Ubuntu
code .
```
*Lần đầu chạy lệnh `code .`, VS Code trên Windows sẽ tự động tải server WSL về cài đặt trong vài giây, sau đó cửa sổ VS Code sẽ hiện lên.*

### Bước 5: Kiểm tra môi trường (Verification)
1. Trong VS Code vừa mở, bấm `Ctrl + ` ` (phím dấu huyền cạnh số 1) để mở Terminal tích hợp.
2. Chạy các lệnh kiểm tra:
   ```bash
   whoami
   pwd
   python3 --version
   git --version
   ```
   Nếu `pwd` trả về đường dẫn dạng `/home/<username>/projects/docflow` là U đã làm chính xác!

### ⚠️ Bắt Lỗi Thường Gặp (Troubleshooting)
- **Lỗi 1: `WslRegisterDistribution failed with error: 0x80370102`**
  - *Nguyên nhân:* Tính năng ảo hóa (Virtualization) trong BIOS của máy tính chưa được bật.
  - *Cách xử lý:* Khởi động lại máy tính, vào BIOS (thường nhấn phím F2 hoặc Del lúc máy khởi động), tìm mục **Intel Virtualization Technology (Intel VT-x)** hoặc **AMD-V** và chuyển sang `Enabled`.
- **Lỗi 2: Gõ `code .` trong Ubuntu báo `command not found`**
  - *Cách xử lý:* Tắt cửa sổ Ubuntu đi mở lại, hoặc đảm bảo khi cài VS Code trên Windows U đã tích chọn ô *"Add to PATH"*.

</details>
