# Task 0.1: Khởi Tạo Môi Trường Linux Trên Windows 11 (WSL2 & VS Code)

- **Giai đoạn:** Tuần 1 — Nền móng môi trường
- **Mục tiêu:** Giúp bạn làm quen với môi trường dòng lệnh Linux (Ubuntu) ngay trên Windows thông qua WSL2, tích hợp mượt mà với VS Code để phục vụ việc lập trình Data/Backend lâu dài.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Bạn đã có một môi trường Linux (khuyên dùng Ubuntu 22.04 LTS) chạy ổn định trên máy Windows 11.
2. VS Code trên Windows mở và kết nối được vào bên trong môi trường Linux (hiển thị trạng thái kết nối WSL ở góc dưới cửa sổ).
3. Môi trường Linux đã cài đặt sẵn Python (phiên bản 3.10+), trình quản lý gói `pip`, `venv` và `git`.
4. Mã nguồn dự án được lưu trữ trong phân vùng file của Linux (thư mục home, ví dụ `~/projects/...`), tránh lưu trong các ổ đĩa mount từ Windows (`/mnt/c/...`).

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

Hãy thử tự nghiên cứu và giải quyết bài toán này trước thông qua tài liệu chính thức và các từ khóa định hướng dưới đây:

### 1. Khái Niệm Cốt Lõi
- **WSL (Windows Subsystem for Linux):** Là cơ chế cho phép chạy nhân Linux trực tiếp trên Windows mà không cần cài máy ảo cồng kềnh.
- **File System Performance:** Hiệu năng đọc/ghi file giữa hệ điều hành Windows (NTFS) và Linux (ext4). Việc để code trong phân vùng Linux tạo ra khác biệt gì về tốc độ so với để ở ổ C Windows?
- **Remote Development trong VS Code:** Cách VS Code chia làm 2 phần: Client chạy trên Windows UI và Server chạy bên trong Linux.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `install wsl2 ubuntu 22.04 windows 11 official doc`
- `vscode wsl extension remote development tutorial`
- `wsl2 file system performance best practices /mnt/c vs home`
- `set up python virtual environment on ubuntu`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Tại sao các kỹ sư Data/Backend thường chọn làm việc trên môi trường Linux thay vì chạy trực tiếp trên Windows PowerShell/CMD?*
- *Extension "WSL" của VS Code giúp bạn làm việc như thế nào mà không cần mở một màn hình desktop ảo của Ubuntu?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Cần Thực Hiện
1. **Kiểm tra tính năng ảo hóa (Virtualization):**
   - Mở Task Manager trên Windows (`Ctrl + Shift + Esc`) -> chọn tab **Performance** -> mục **CPU**. Kiểm tra dòng **Virtualization** xem đã là `Enabled` chưa. Nếu là `Disabled`, bạn sẽ cần bật tính năng này trong BIOS của máy (Intel VT-x hoặc AMD-V).
2. **Cài đặt WSL qua dòng lệnh:**
   - Tài liệu tham khảo chính thức: [Microsoft Learn - Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
   - Thường sử dụng PowerShell (Run as Administrator) với lệnh dạng `wsl --install -d Ubuntu-22.04`.
   - Nếu máy tính đã từng cài WSL cũ, hãy dùng `wsl --status` hoặc `wsl -l -v` để kiểm tra phiên bản WSL đang là version 1 hay version 2.
3. **Khởi tạo tài khoản trên Ubuntu:**
   - Thiết lập một username và password dễ nhớ cho môi trường Ubuntu (lưu ý rằng khi gõ mật khẩu trên Linux, màn hình sẽ không hiển thị ký tự để bảo mật).
4. **Cài đặt các gói công cụ cơ bản:**
   - Trên Ubuntu, công cụ quản lý gói là `apt`. Bạn nên cập nhật danh sách gói (`sudo apt update`) trước khi cài Python, Git và các thư viện cần thiết.
5. **Kết nối qua VS Code:**
   - Cài extension có tên **WSL** (của Microsoft) trên ứng dụng VS Code Windows.
   - Khi đứng trong terminal Ubuntu, bạn có thể thử lệnh `code .` ngay tại thư mục muốn làm việc để VS Code tự động liên kết.

### 2. Những Vấn Đề Thường Gặp Trên Windows 11
- **Lỗi ảo hóa (Virtualization Error / 0x80370102):** Do BIOS chưa bật ảo hóa phần cứng, hoặc tính năng "Virtual Machine Platform" của Windows chưa được bật trong Windows Features.
- **Tốc độ git/file rất chậm:** Hãy kiểm tra lại thư mục làm việc của bạn bằng lệnh `pwd`. Nếu đường dẫn bắt đầu bằng `/mnt/c/...`, điều đó có nghĩa là bạn đang đứng ở ổ C của Windows. Bạn nên chuyển vào thư mục home của Linux (`cd ~` hoặc `cd ~/projects/...`) để tận dụng tối đa tốc độ của hệ thống file Linux.
- **Lỗi không mở được VS Code từ WSL:** Đôi khi cần khởi động lại cả terminal hoặc đảm bảo VS Code trên Windows đã được thêm vào biến môi trường PATH.

</details>
