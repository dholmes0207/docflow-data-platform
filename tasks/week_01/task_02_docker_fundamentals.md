# Task 0.2: Làm Quen Với Docker & Thiết Lập Cấu Hình Tối Ưu RAM Trên Windows 11

- **Giai đoạn:** Tuần 1 — Nền móng môi trường
- **Mục tiêu:** Hiểu bản chất của công nghệ đóng gói (Containerization), cài đặt Docker Desktop tích hợp với WSL2 và cấu hình giới hạn tài nguyên hợp lý để máy tính 16GB RAM hoạt động mượt mà.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Docker Desktop đã được cài đặt và đang chạy bình thường trên Windows 11 với engine là WSL2 backend.
2. Từ terminal của Ubuntu (WSL2), bạn thực hiện được các lệnh kiểm tra trạng thái Docker (như `docker ps`, `docker version`) mà không bị lỗi giao tiếp với Docker daemon.
3. Chạy thử nghiệm thành công một container mẫu (như `hello-world` hoặc `nginx`) và hiểu rõ vòng đời từ lúc kéo Image đến khi Container chạy và dừng lại.
4. Đã tạo file cấu hình `.wslconfig` trong thư mục người dùng Windows để đặt mức trần bộ nhớ RAM hợp lý (khoảng 8GB - 10GB cho WSL2), tránh hiện tượng WSL chiếm hết RAM gây treo máy.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Docker Image vs Container:** Phân biệt "bản vẽ/khuôn mẫu" (Image) và "ngôi nhà/thể hiện thực tế đang chạy" (Container).
- **WSL 2 Backend trong Docker Desktop:** Cơ chế Docker Desktop chạy một Linux VM nhẹ bên trong WSL để chia sẻ daemon trực tiếp với các bản phân phối Linux như Ubuntu.
- **Port Mapping (`-p host_port:container_port`):** Tại sao ứng dụng chạy bên trong một container bị cô lập mạng lại có thể truy cập được từ trình duyệt bên ngoài máy Windows?
- **Tài nguyên bộ nhớ WSL2:** Cách Windows cấp phát động RAM cho máy ảo vEthernet/WSL và lý do cần đặt giới hạn thông qua `.wslconfig`.

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `docker desktop install windows 11 wsl2 integration`
- `docker get started understand images and containers`
- `limit wsl2 memory consumption .wslconfig windows 11`
- `docker port publishing explained`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu bạn xóa một container đang chạy, những file được tạo ra bên trong container đó có còn tồn tại không?*
- *Nếu hai container cùng muốn mở cổng 8080 ra ngoài máy Windows thì có được không? Cần giải quyết việc trùng cổng này như thế nào?*
- *Tại sao việc chạy Docker thông qua WSL2 lại tối ưu hơn việc bật Hyper-V truyền thống trên Windows?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Các Bước Cần Thực Hiện
1. **Thiết lập giới hạn RAM cho WSL2 (`.wslconfig`):**
   - Tài liệu tham khảo: [Microsoft Learn - Advanced settings configuration in WSL](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#configure-global-options-with-wslconfig).
   - Trên Windows, file `.wslconfig` nằm tại thư mục người dùng (`%USERPROFILE%\.wslconfig`, tức là `C:\Users\<Tên_Của_Bạn>\.wslconfig`).
   - Các thuộc tính chính cần cấu hình trong phần `[wsl2]` bao gồm `memory` (khuyên đặt `8GB` hoặc `10GB` với máy 16GB RAM) và `processors`.
   - Mỗi lần sửa file này, bạn cần chạy lệnh tắt hoàn toàn WSL (`wsl --shutdown` trên PowerShell) rồi mở lại để cấu hình có hiệu lực.
2. **Cài đặt và thiết lập Docker Desktop:**
   - Tải bộ cài chính thức từ trang chủ [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/).
   - Khi cài đặt, hãy đảm bảo tùy chọn sử dụng **WSL 2 based engine** đã được tích chọn.
   - Sau khi cài xong, mở Docker Settings -> tìm phần **WSL Integration** (thường nằm ở `Settings > Resources > WSL integration`) -> bật cho phép tích hợp với bản Ubuntu mà bạn đang dùng.
3. **Thử nghiệm trên dòng lệnh:**
   - Mở terminal Ubuntu trong VS Code.
   - Thử chạy một container kiểm tra đơn giản: `docker run hello-world`.
   - Thử tìm hiểu các cờ lệnh phổ biến khi chạy container:
     - `-d` (chạy ngầm - detached mode)
     - `--name` (đặt tên cho container dễ quản lý)
     - `-p` (chuyển tiếp cổng)
     - `--rm` (tự dọn dẹp xóa container khi nó dừng chạy)

### 2. Những Vấn Đề Thường Gặp
- **Lỗi Docker daemon không chạy (`Cannot connect to the Docker daemon`):**
  - Hãy kiểm tra xem ứng dụng Docker Desktop trên thanh Taskbar Windows đã khởi động xong chưa (biểu tượng cá voi màu xanh ổn định).
  - Kiểm tra xem trong Settings của Docker Desktop đã bật công tắc cho bản Ubuntu tương ứng chưa.
- **Máy bị chậm hoặc giật khi chạy nhiều ứng dụng:**
  - Mở Task Manager trên Windows kiểm tra tiến trình `Vmmem`. Tiến trình này đại diện cho toàn bộ tài nguyên mà WSL2 và Docker đang sử dụng. Nếu `Vmmem` ăn quá nhiều RAM, hãy xem lại file `.wslconfig`.

</details>
