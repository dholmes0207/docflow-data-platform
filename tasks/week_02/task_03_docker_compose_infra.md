# Task 0.3: Dựng Hạ Tầng Lưu Trữ & Database Với Docker Compose (MinIO & PostgreSQL + pgvector)

- **Giai đoạn:** Giai đoạn 0 — Khởi tạo nền tảng
- **Thời lượng ước tính:** 3 – 4 ngày (6 – 8 giờ làm việc)
- **Mục tiêu:** U tạo file `docker-compose.yml` để tự động hóa việc khởi động cụm hạ tầng cốt lõi gồm: PostgreSQL phiên bản có sẵn extension `pgvector` và MinIO Object Storage (tương thích AWS S3 API).

---

## 🎯 Tiêu Chí Hoàn Thành (Definition of Done - DoD)
1. Chỉ cần gõ đúng 1 lệnh `docker compose -f infra/docker-compose.yml up -d` là cả 2 container `postgres` và `minio` cùng chạy ngầm thành công.
2. U truy cập được Web UI của MinIO tại `http://localhost:9001`, đăng nhập tạo được bucket tên là `raw-documents`.
3. Dùng tool quản lý DB (như **DBeaver** hoặc VS Code Database Client) kết nối thành công vào PostgreSQL tại `localhost:5432`, chạy lệnh `CREATE EXTENSION IF NOT EXISTS vector;` không báo lỗi.
4. Khi chạy `docker compose down` rồi `docker compose up -d` lại, dữ liệu trong bucket MinIO và trong Postgres không bị mất (nhờ cấu hình Docker Volume chuẩn).

---

## 🟢 MỨC 1: TỰ KHÁM PHÁ (U làm phần này trước)

### 1. Từ Khóa Tìm Kiếm (Search Keywords)
- `docker compose file format version 3 services`
- `pgvector docker compose example postgres:16`
- `minio docker compose minio server with console port 9001`
- `docker compose named volumes persist data`

### 2. Câu Hỏi Định Hướng Tư Duy
- *MinIO có 2 cổng: port `9000` và port `9001`. Cổng nào dùng cho code Python (API S3 Client) gọi tới, cổng nào dùng cho con người mở trình duyệt vào xem?*
- *Nếu trong `docker-compose.yml` không định nghĩa `volumes`, chuyện gì sẽ xảy ra với các bảng và dữ liệu trong Database khi U gõ `docker compose down`?*
- *Tại sao ta lại dùng image `pgvector/pgvector:pg16` thay vì image `postgres:16` nguyên bản của Docker Hub?*

---

## 🟡 MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH (Chỉ mở khi bị tắc)

<details>
<summary>👉 <b>Bấm vào đây để xem hướng dẫn chi tiết từng bước</b></summary>

### Bước 1: Tạo file cấu hình `infra/docker-compose.yml`
Tạo file tại đường dẫn chính xác: `infra/docker-compose.yml` với nội dung hoàn chỉnh:

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: docflow_postgres
    restart: always
    environment:
      POSTGRES_USER: docflow_admin
      POSTGRES_PASSWORD: docflow_secret_password
      POSTGRES_DB: docflow_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - docflow_network

  minio:
    image: minio/minio:RELEASE.2024-05-10T01-41-38Z
    container_name: docflow_minio
    restart: always
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin_secret
    ports:
      - "9000:9000"   # S3 API Port
      - "9001:9001"   # Web Console Port
    volumes:
      - minio_data:/data
    networks:
      - docflow_network

volumes:
  postgres_data:
    driver: local
  minio_data:
    driver: local

networks:
  docflow_network:
    driver: bridge
```

### Bước 2: Tạo file rỗng cho script khởi tạo SQL
Tạo file: `infra/sql/init.sql` (tạm thời để trống hoặc chỉ thêm lệnh kích hoạt extension vector):
```sql
-- Kích hoạt extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;
```

### Bước 3: Khởi chạy cụm dịch vụ
Từ thư mục gốc của dự án (`~/projects/docflow`), chạy lệnh:
```bash
docker compose -f infra/docker-compose.yml up -d
```

Kiểm tra trạng thái các container:
```bash
docker compose -f infra/docker-compose.yml ps
```
Cả 2 dịch vụ `docflow_postgres` và `docflow_minio` phải có trạng thái `Up` (Running).

### Bước 4: Kiểm tra MinIO qua Trình duyệt
1. Mở trình duyệt trên Windows 11 (Chrome/Edge), truy cập: `http://localhost:9001`.
2. Đăng nhập với thông tin đã khai báo trong docker-compose:
   - **Username:** `minioadmin`
   - **Password:** `minioadmin_secret`
3. Vào mục **Buckets** -> Bấm **Create Bucket** -> Đặt tên là `raw-documents` -> Bấm **Create**.

### Bước 5: Kết nối Database bằng DBeaver
1. Tải và cài đặt DBeaver Community trên Windows: `https://dbeaver.io/download/`.
2. Mở DBeaver -> Bấm nút **New Database Connection** (icon hình phích cắm) -> Chọn **PostgreSQL**.
3. Điền thông số kết nối:
   - **Host:** `localhost`
   - **Port:** `5432`
   - **Database:** `docflow_db`
   - **Username:** `docflow_admin`
   - **Password:** `docflow_secret_password`
4. Bấm **Test Connection**. Khi hiện thông báo *"Connected"* màu xanh, bấm **Finish**.
5. Mở một SQL Editor mới trong DBeaver và chạy:
   ```sql
   SELECT * FROM pg_extension;
   ```
   Kiểm tra xem dòng có `extname = 'vector'` đã tồn tại hay chưa.

### ⚠️ Bắt Lỗi Thường Gặp (Troubleshooting)
- **Lỗi: `Bind for 0.0.0.0:5432 failed: port is already allocated`**
  - *Nguyên nhân:* Trên máy tính của U trước đó đã từng cài đặt PostgreSQL chạy nền dạng Windows Service và đang chiếm cổng 5432.
  - *Cách xử lý:* Mở Task Manager hoặc Services của Windows, tìm dịch vụ `postgresql-x64-...`, click chuột phải chọn **Stop** và đổi chế độ sang **Manual**.
- **Lỗi: `docker compose command not found`**
  - *Cách xử lý:* Nếu lệnh `docker compose` (viết liền không gạch ngang) chưa nhận, thử lệnh cũ: `docker-compose` (có gạch ngang).

</details>
