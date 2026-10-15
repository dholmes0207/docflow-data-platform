# Task 0.1: Khởi Tạo Môi Trường Linux Trên Windows (WSL2 Ubuntu 24.04 & VS Code)

- **Giai đoạn:** Sprint 1 — Nền móng môi trường
- **Mục tiêu:** Máy của bạn chạy Windows, nhưng gần như mọi công cụ Data Engineering (Docker, Airflow, dbt, Postgres...) đều được thiết kế cho Linux. Task này giúp bạn có một môi trường Ubuntu 24.04 "thật" chạy ngay bên trong Windows thông qua WSL2, tích hợp mượt mà với VS Code để làm việc lâu dài cho toàn bộ khóa học.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Máy Windows của bạn (Windows 11, hoặc Windows 10 bản 2004 trở lên) chạy được **Ubuntu 24.04 LTS bên trong WSL2**. Lệnh `wsl -l -v` trên PowerShell hiển thị bản Ubuntu-24.04 với cột VERSION là `2`.
2. VS Code trên Windows mở và kết nối được vào bên trong môi trường Linux (hiển thị trạng thái kết nối WSL ở góc dưới cửa sổ).
3. Bên trong Ubuntu đã có Python 3.12 (đi kèm Ubuntu 24.04), `git`, và tạo được môi trường ảo bằng `python3 -m venv`. Cài được một thư viện bất kỳ bằng `pip` **bên trong môi trường ảo**.
4. Mã nguồn dự án được lưu trữ trong phân vùng file của Linux (thư mục home, ví dụ `~/projects/...`), tránh lưu trong các ổ đĩa mount từ Windows (`/mnt/c/...`).
5. Repo DocFlow được `git clone` và thao tác bằng **git bên trong Ubuntu** (không dùng Git for Windows cho repo này). Git đã cấu hình `user.name` và `user.email` trùng với tài khoản GitHub của bạn.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

Hãy thử tự nghiên cứu và giải quyết bài toán này trước thông qua tài liệu chính thức và các từ khóa định hướng dưới đây:

### 1. Khái Niệm Cốt Lõi
- **WSL (Windows Subsystem for Linux):** Là cơ chế cho phép chạy nhân Linux trực tiếp trên Windows mà không cần cài máy ảo cồng kềnh.
- **File System Performance:** Hiệu năng đọc/ghi file giữa hệ điều hành Windows (NTFS) và Linux (ext4). Việc để code trong phân vùng Linux tạo ra khác biệt gì về tốc độ so với để ở ổ C Windows?
- **Remote Development trong VS Code:** Cách VS Code chia làm 2 phần: Client chạy trên Windows UI và Server chạy bên trong Linux.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `install wsl2 ubuntu 24.04 windows official doc`
- `ubuntu 24.04 pip error externally-managed-environment PEP 668`
- `git line endings core.autocrlf wsl windows`
- `vscode wsl extension remote development tutorial`
- `wsl2 file system performance best practices /mnt/c vs home`
- `set up python virtual environment on ubuntu`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Tại sao các kỹ sư Data/Backend thường chọn làm việc trên môi trường Linux thay vì chạy trực tiếp trên Windows PowerShell/CMD?*
- *Extension "WSL" của VS Code giúp bạn làm việc như thế nào mà không cần mở một màn hình desktop ảo của Ubuntu?*
- *Vì sao Ubuntu 24.04 chặn lệnh `pip install` cài thẳng vào Python của hệ thống? Môi trường ảo (venv) giải quyết vấn đề đó thế nào?*
- *Windows và Linux dùng ký tự xuống dòng khác nhau (CRLF và LF). Nếu cùng một repo được sửa bằng cả Git for Windows lẫn git trong WSL, chuyện gì có thể xảy ra với mã băm của file?*

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
   - Thường sử dụng PowerShell (Run as Administrator) với lệnh dạng `wsl --install -d Ubuntu-24.04`. Dùng `wsl --list --online` để xem tên chính xác các bản Ubuntu có thể cài.
   - Nếu máy tính đã từng cài WSL cũ, hãy dùng `wsl --status` hoặc `wsl -l -v` để kiểm tra phiên bản WSL đang là version 1 hay version 2.
3. **Khởi tạo tài khoản trên Ubuntu:**
   - Thiết lập một username và password dễ nhớ cho môi trường Ubuntu (lưu ý rằng khi gõ mật khẩu trên Linux, màn hình sẽ không hiển thị ký tự để bảo mật).
4. **Cài đặt các gói công cụ cơ bản:**
   - Trên Ubuntu, công cụ quản lý gói là `apt`. Bạn nên cập nhật danh sách gói (`sudo apt update`) trước khi cài các gói cần thiết. Ubuntu 24.04 có sẵn Python 3.12, nhưng thường **thiếu** gói hỗ trợ tạo môi trường ảo và `pip` (tìm hiểu gói `python3-venv`, `python3-pip`).
5. **Kết nối qua VS Code:**
   - Cài extension có tên **WSL** (của Microsoft) trên ứng dụng VS Code Windows.
   - Khi đứng trong terminal Ubuntu, bạn có thể thử lệnh `code .` ngay tại thư mục muốn làm việc để VS Code tự động liên kết.

6. **Lấy mã nguồn về đúng chỗ:**
   - Mở terminal Ubuntu, tạo thư mục `~/projects`, rồi `git clone` repo DocFlow vào đó. Cấu hình `git config --global user.name` và `user.email` ngay trong Ubuntu (đây là cấu hình riêng, tách biệt với Git for Windows nếu máy bạn có cài).

### 2. Những Vấn Đề Thường Gặp Trên Windows
- **Lỗi ảo hóa (Virtualization Error / 0x80370102):** Do BIOS chưa bật ảo hóa phần cứng, hoặc tính năng "Virtual Machine Platform" của Windows chưa được bật trong Windows Features.
- **Tốc độ git/file rất chậm:** Hãy kiểm tra lại thư mục làm việc của bạn bằng lệnh `pwd`. Nếu đường dẫn bắt đầu bằng `/mnt/c/...`, điều đó có nghĩa là bạn đang đứng ở ổ C của Windows. Bạn nên chuyển vào thư mục home của Linux (`cd ~` hoặc `cd ~/projects/...`) để tận dụng tối đa tốc độ của hệ thống file Linux.
- **Lỗi không mở được VS Code từ WSL:** Đôi khi cần khởi động lại cả terminal hoặc đảm bảo VS Code trên Windows đã được thêm vào biến môi trường PATH.
- **`error: externally-managed-environment` khi chạy `pip install`:** Đây là cơ chế bảo vệ của Ubuntu 24.04 (PEP 668), không phải lỗi. Hãy tạo môi trường ảo trong thư mục dự án, kích hoạt nó, rồi mới `pip install`. Không dùng cờ `--break-system-packages`.
- **`python3 -m venv` báo thiếu `ensurepip`:** Chưa cài gói `python3-venv` (xem bước 4).
- **Git báo hàng loạt file "modified" dù bạn không sửa gì:** Thường do mở cùng repo bằng Git for Windows (tự đổi xuống dòng sang CRLF). Chỉ thao tác repo bằng git trong Ubuntu. Repo đã có file `.gitattributes` để giữ xuống dòng kiểu LF.

</details>
