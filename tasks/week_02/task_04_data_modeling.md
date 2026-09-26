# Task 0.4: Thiết Kế Mô Hình Dữ Liệu (Data Modeling) & Tạo Schema Ban Đầu

- **Giai đoạn:** Giai đoạn 0 — Khởi tạo nền tảng
- **Thời lượng ước tính:** 2 – 3 ngày (4 – 6 giờ làm việc)
- **Mục tiêu:** U thiết kế sơ đồ thực thể liên kết (ERD) cho bài toán Multi-tenant RAG và viết script SQL hoàn chỉnh để khởi tạo bảng dữ liệu cùng các ràng buộc tính toàn vẹn dữ liệu (Data Integrity).

---

## 🎯 Tiêu Chí Hoàn Thành (Definition of Done - DoD)
1. Có file sơ đồ thiết kế ERD dạng ảnh lưu tại `docs/architecture/erd.png` (hoặc file markdown có diagram Mermaid).
2. File script `infra/sql/init.sql` được viết hoàn chỉnh, bao gồm 2 bảng nghiệp vụ chính: `documents` và `document_chunks`.
3. Bảng `documents` có cột `file_hash` (dùng để kiểm tra tính Idempotent) và cơ chế đánh dấu version.
4. Bảng `document_chunks` có trường `embedding` lưu vector 384 chiều (`vector(384)`) và liên kết khóa ngoại (Foreign Key) chặt chẽ với bảng `documents`.
5. Tạo thành công các Index: Index trên `tenant_id`, Index tìm kiếm vector (HNSW hoặc IVFFlat).

---

## 🟢 MỨC 1: TỰ KHÁM PHÁ (U làm phần này trước)

### 1. Từ Khóa Tìm Kiếm (Search Keywords)
- `rag database schema postgres best practices`
- `pgvector create table with vector type and ivfflat index`
- `multi tenant data modeling foreign key cascade`
- `sha256 file hash deduplication sql schema`

### 2. Câu Hỏi Định Hướng Tư Duy
- *Tại sao một tài liệu dài không nên lưu toàn bộ vào 1 dòng vector mà phải chia thành nhiều chunks (đoạn nhỏ)?*
- *Nếu một tài liệu bị xóa ở bảng `documents`, các chunks tương ứng trong bảng `document_chunks` có nên bị xóa theo không? Dùng cú pháp SQL nào để làm việc này (`ON DELETE ...`)?*
- *Cột `tenant_id` có bắt buộc phải xuất hiện ở cả bảng `documents` lẫn bảng `document_chunks` không? Tại sao (nghĩ về tốc độ truy vấn lọc theo tenant)?*
- *Vector 384 chiều là gì? Tại sao lại là con số 384 mà không phải 1536 hay 768?*

---

## 🟡 MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH (Chỉ mở khi bị tắc)

<details>
<summary>👉 <b>Bấm vào đây để xem hướng dẫn chi tiết từng bước</b></summary>

### Bước 1: Tư duy thiết kế thực thể
- **Thực thể 1: `documents` (Tài liệu gốc)**
  - Quản lý metadata của từng file được tải lên MinIO.
  - Mỗi file của 1 tenant được xác định qua `tenant_id` và `file_path`.
  - Cột `file_hash` (mã băm SHA-256) giúp nhận diện: nếu nội dung file không đổi -> không cần chạy lại pipeline tốn tài nguyên.
  - Cột `version` (INT) tăng dần nếu cùng 1 file được sửa đổi nội dung.

- **Thực thể 2: `document_chunks` (Các đoạn văn bản đã cắt)**
  - Một tài liệu (`documents`) sinh ra nhiều đoạn nhỏ (`chunks`).
  - Mỗi đoạn lưu nội dung thô (`content`), vị trí đoạn trong file (`chunk_index`).
  - Cột `embedding` lưu biểu diễn số học của đoạn văn bản (độ dài 384 phù hợp với model local siêu nhẹ `all-MiniLM-L6-v2`).
  - Cột `metadata` dạng `JSONB` để lưu linh hoạt các thông tin phụ (tiêu đề mục, số trang, ngày tạo...).

### Bước 2: Cập nhật nội dung file `infra/sql/init.sql`
Mở file `infra/sql/init.sql` và điền nội dung sau:

```sql
-- 1. Kích hoạt tiện ích mở rộng pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Bảng quản lý Tài liệu gốc (Documents)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,          -- SHA-256 hash của nội dung file
    version INT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- Đánh dấu bản mới nhất đang sử dụng
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_tenant_file_version UNIQUE (tenant_id, file_path, version)
);

-- Index phục vụ lọc tài liệu theo Tenant
CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);

-- 3. Bảng quản lý Các đoạn cắt (Document Chunks)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,          -- Lưu tenant_id ở đây để tăng tốc filter
    chunk_index INT NOT NULL,                -- Thứ tự đoạn trong file (0, 1, 2, ...)
    content TEXT NOT NULL,                   -- Nội dung văn bản của đoạn
    embedding vector(384),                   -- Vector đặc trưng 384 chiều
    metadata JSONB DEFAULT '{}'::jsonb,      -- Metadata phụ trợ (page, section, ...)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE                    -- Xóa document thì tự động dọn sạch chunks
);

-- Index tăng tốc truy vấn lọc
CREATE INDEX IF NOT EXISTS idx_chunks_tenant ON document_chunks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks(document_id);

-- Index tìm kiếm tương đồng vector (Cosine Distance) sử dụng HNSW
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops);
```

### Bước 3: Thực thi Schema trên Database
U có 2 cách để nạp schema này vào Postgres:
- **Cách 1 (Tái tạo lại DB):** Chạy `docker compose -f infra/docker-compose.yml down -v` rồi `docker compose -f infra/docker-compose.yml up -d` (Lưu ý: cờ `-v` sẽ xóa sạch data cũ để Docker chạy lại file `init.sql`).
- **Cách 2 (Chạy trực tiếp trên DBeaver):** Mở DBeaver, mở file `infra/sql/init.sql` và nhấn tổ hợp phím `Alt + X` để thực thi toàn bộ script.

### Bước 4: Kiểm tra kết quả
Trong DBeaver, kiểm tra xem hai bảng `documents` và `document_chunks` đã hiển thị trong Schema `public` chưa. Thử insert 1 dòng test để kiểm tra ràng buộc khóa ngoại.

</details>
