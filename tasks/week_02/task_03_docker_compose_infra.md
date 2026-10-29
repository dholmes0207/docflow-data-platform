# Task 0.3: Dựng Cụm Hạ Tầng MinIO & PostgreSQL (pgvector) Với Docker Compose

- **Giai đoạn:** Sprint 2 — Hạ tầng & Mô hình dữ liệu
- **Mục tiêu:** Hiểu cách dùng Docker Compose để điều phối nhiều dịch vụ chạy cùng nhau trong một mạng nội bộ; dựng thành công dịch vụ lưu trữ file MinIO (chuẩn S3) và cơ sở dữ liệu PostgreSQL có sẵn extension `pgvector`.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Bạn xây dựng được file `docker-compose.yml` định nghĩa 2 dịch vụ (`postgres` và `minio`), có cấu hình cổng (ports), biến môi trường (environment), và phân vùng lưu trữ lâu dài (named volumes).
2. Khi chạy lệnh khởi động Docker Compose, cả hai container cùng khởi chạy ngầm thành công.
3. Mở được giao diện Web Console của MinIO trên trình duyệt Windows (`localhost:9001`), đăng nhập được bằng tài khoản bạn đã cấu hình và tạo được bucket đầu tiên tên là `raw-documents`.
4. Dùng một công cụ quản lý cơ sở dữ liệu (như **DBeaver** hoặc VS Code Database Extension) kết nối thành công vào PostgreSQL tại `localhost:5432`.
5. Khi bạn tắt các container rồi bật lại, dữ liệu trong MinIO và PostgreSQL vẫn được giữ nguyên vẹn (nhờ cơ chế Docker Volume).

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Docker Compose:** Công cụ định nghĩa và chạy các ứng dụng Docker gồm nhiều container. Thay vì phải gõ nhiều câu lệnh `docker run` phức tạp với hàng tá tham số, toàn bộ kiến trúc được mô tả trong 1 file YAML.
- **Object Storage & Chuẩn S3 (MinIO):** Trong các hệ thống dữ liệu lớn, tại sao người ta không lưu file tài liệu thô trực tiếp vào ổ cứng cục bộ hay database, mà lại lưu vào kho đối tượng (Object Storage)? MinIO đóng vai trò giả lập AWS S3 như thế nào khi phát triển dưới máy local?
- **pgvector Extension:** PostgreSQL thuần túy vốn dành cho dữ liệu bảng quan hệ. Tại sao để làm ứng dụng RAG/AI, ta cần cài thêm extension `pgvector`?
- **Docker Volumes (Data Persistence):** Vòng đời dữ liệu của container là tạm thời (ephemeral). Làm thế nào để dữ liệu trong database và bucket không bị biến mất khi container bị tắt hoặc xóa?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `docker compose specification compose file reference`
- `docker compose environment variables .env file interpolation`
- `minio docker compose server console port configuration`
- `pgvector docker official image pgvector/pgvector`
- `docker compose named volumes persist postgres data`
- `dbeaver connect to postgresql docker local`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *MinIO có 2 cổng mặc định: cổng API (thường là 9000) và cổng Web Console (thường là 9001). Cổng nào sẽ dành cho code Python sau này gọi để upload/download file, và cổng nào dành cho con người mở trình duyệt xem trực quan?*
- *Nếu trong file compose bạn không định nghĩa mục `volumes:` cho PostgreSQL, điều gì sẽ xảy ra khi bạn gõ `docker compose down` rồi khởi động lại?*
- *Hai container trong cùng một file `docker-compose.yml` có thể giao tiếp với nhau bằng tên dịch vụ (service name) thay vì dùng địa chỉ IP không? Cơ chế đó gọi là gì?*
- *Bạn ngồi Wi-Fi trường, Postgres mở cổng `5432` và vẫn dùng mật khẩu mẫu trong `.env.example`. Một người lạ cùng mạng có kết nối được vào database của bạn không? Ghi cổng thế nào để chặn điều đó?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Cấu Trúc Tổng Quan Của Một File `docker-compose.yml`
Một file compose chuẩn thường bao gồm các khối chính:
- **`services:`** Định nghĩa danh sách các ứng dụng cần chạy.
  - **`postgres`:**
    - Nên chọn image có sẵn extension vector, ví dụ: `pgvector/pgvector:pg16` thay vì image Postgres gốc.
    - Cần khai báo các biến môi trường: user, password, tên database mặc định.
    - Chuyển tiếp cổng (thường là `"5432:5432"`). Mặc định Docker mở cổng cho **mọi** máy trong cùng mạng (ví dụ Wi-Fi trường) kết nối vào. Tìm hiểu cách chỉ mở cho chính máy bạn (từ khóa: `docker compose ports bind 127.0.0.1`), file mẫu đã làm như vậy.
    - Ánh xạ thư mục dữ liệu nội bộ của Postgres (`/var/lib/postgresql/data`) vào một Docker Volume để không bị mất dữ liệu.
  - **`minio`:**
    - Sử dụng image chính thức từ MinIO, nên **ghim cố định tag phiên bản** (như file mẫu `minio/minio:RELEASE.2024-05-10T01-41-38Z`) thay vì dùng `latest`. Các bản MinIO Community phát hành sau đó đã lược bớt nhiều chức năng quản trị trên Web Console, nên dùng bản mới có thể không thao tác được như hướng dẫn.
    - Cần truyền lệnh chạy (command) chỉ định cả thư mục dữ liệu và cổng cho giao diện Console (ví dụ: `server /data --console-address ":9001"`).
    - Biến môi trường quản trị viên (root user & root password).
    - Chuyển tiếp 2 cổng ra máy host: cổng 9000 (API) và cổng 9001 (Web UI).
- **`volumes:`** Khai báo danh sách các volume để Docker quản lý bộ nhớ lâu dài.

*(Bạn có thể tham khảo một file mẫu sẵn có tại thư mục [`infra/docker-compose.yml`](../../infra/docker-compose.yml) trong dự án để đối chiếu với cấu hình bạn tự viết).*

### 2. Các Lệnh Thao Tác Thường Dùng Với Docker Compose
- Chuẩn bị biến môi trường (chỉ làm 1 lần): copy file mẫu `infra/.env.example` thành `infra/.env` rồi đổi mật khẩu. File compose mẫu đọc mật khẩu từ `.env` thay vì ghi cứng trong YAML, và `.env` đã được đưa vào `.gitignore` để không lộ mật khẩu lên Git.
- Khởi động cụm dịch vụ và cho chạy ngầm: `docker compose up -d`
- Xem trạng thái các container đang chạy: `docker compose ps` (file mẫu có cấu hình `healthcheck` cho Postgres: khi cột STATUS hiện `healthy` nghĩa là database đã sẵn sàng nhận kết nối)
- Xem log hiển thị của các dịch vụ để debug khi gặp lỗi: `docker compose logs -f` (hoặc chỉ định tên dịch vụ: `docker compose logs -f postgres`)
- Dừng toàn bộ dịch vụ một cách an toàn: `docker compose down`

### 3. Những Vấn Đề Thường Gặp
- **Trùng cổng 5432 (Port is already allocated):**
  - Rất nhiều bạn học ngành CNTT từng cài đặt PostgreSQL trực tiếp lên Windows trong các môn học cơ sở dữ liệu trước đó, khiến cổng 5432 trên Windows luôn bị chiếm dụng bởi Windows Service.
  - *Cách xử lý:* Bạn có thể mở ứng dụng `Services` trên Windows, tìm dịch vụ PostgreSQL local và bấm Stop; hoặc đổi cổng ánh xạ bên ngoài máy host trong file compose thành cổng khác (ví dụ `"5433:5432"`).
- **Sửa file `init.sql` nhưng database không thay đổi:**
  - Postgres chỉ chạy các script trong `/docker-entrypoint-initdb.d` khi volume dữ liệu còn trống (lần khởi tạo đầu tiên). Muốn chạy lại, bạn cần xóa volume bằng `docker compose down -v` (lưu ý: thao tác này xóa sạch dữ liệu cũ) rồi `docker compose up -d`.
- **Lỗi `required variable POSTGRES_PASSWORD is missing a value`:**
  - Bạn chưa tạo file `.env` trong thư mục `infra/`, hoặc đang chạy lệnh compose ở thư mục khác. Hãy kiểm tra lại bước chuẩn bị biến môi trường ở trên.
- **Dữ liệu trong MinIO bị reset mỗi lần restart:**
  - Kiểm tra xem đường dẫn ánh xạ volume của MinIO đã trỏ đúng vào thư mục `/data` bên trong container hay chưa.

</details>
