# Task 0.4: Thiết Kế Mô Hình Dữ Liệu (Data Modeling) Cho Hệ Thống Multi-Tenant RAG

- **Giai đoạn:** Tuần 2 — Hạ tầng & Mô hình dữ liệu
- **Mục tiêu:** Hiểu tư duy thiết kế cơ sở dữ liệu quan hệ kết hợp lưu trữ vector cho một bài toán đa doanh nghiệp (Multi-tenant), xây dựng sơ đồ ERD và chuẩn bị kịch bản SQL khởi tạo cấu trúc bảng.

---

## 🎯 Mục Tiêu Cần Đạt (Definition of Done)

Sau khi hoàn thành task này, bạn có thể tự tin xác nhận:
1. Bạn vẽ được sơ đồ thực thể liên kết (ERD) mô tả mối quan hệ giữa 2 bảng chính: `documents` (Tài liệu gốc) và `document_chunks` (Các đoạn văn bản đã cắt để tìm kiếm).
2. Thiết kế bảng đảm bảo được tính **cách ly theo doanh nghiệp (Multi-tenancy)**: bất kỳ bảng nào chứa dữ liệu nghiệp vụ cũng phải có định danh `tenant_id`.
3. Có cơ chế nhận diện trùng lặp/sửa đổi file dựa trên mã băm nội dung (Hash-based Idempotency) và quản lý phiên bản (Versioning) trong bảng `documents`.
4. Bảng `document_chunks` có trường lưu vector đặc trưng (độ dài vector phù hợp với mô hình embedding sẽ dùng, ví dụ: 384 chiều) và ràng buộc khóa ngoại (Foreign Key) chặt chẽ với bảng `documents`.
5. Tạo thành công các bảng trên cơ sở dữ liệu PostgreSQL thực tế thông qua kịch bản SQL.

---

## 🟢 MỨC 1: ĐỊNH HƯỚNG TỰ TÌM HIỂU

### 1. Khái Niệm Cốt Lõi
- **Kiến trúc Multi-tenancy ở tầng dữ liệu:** Làm thế nào để đảm bảo dữ liệu của công ty A không bao giờ bị lẫn sang công ty B? Việc đánh chỉ mục (Index) trên cột `tenant_id` mang lại lợi ích gì cho hiệu năng tìm kiếm?
- **Tính Bất Biến (Data Idempotency) & Hashing:** Trong kỹ nghệ dữ liệu, nếu một pipeline bị chạy lại nhiều lần cho cùng một file tài liệu, làm thế nào để hệ thống không sinh ra dữ liệu trùng lặp? Mã băm SHA-256 của nội dung file được áp dụng ra sao trong trường hợp này?
- **Phân rã tài liệu (Document Splitting / Chunking):** Tại sao trong các ứng dụng AI/RAG, người ta không nhúng nguyên cả một cuốn tài liệu 50 trang thành 1 vector, mà phải chia nhỏ thành các đoạn (chunks)? Mối quan hệ giữa Document và Document Chunk là gì (1-1, 1-N hay N-N)?
- **Chỉ mục Vector (Vector Indexing):** Tìm hiểu khái quát về chỉ mục HNSW (Hierarchical Navigable Small World) hoặc IVFFlat trong `pgvector`. Tại sao khi dữ liệu vector lớn, việc quét toàn bộ bảng (Sequential Scan) lại rất chậm?

### 2. Từ Khóa Tra Cứu (Search Keywords)
- `rag database schema design postgresql best practices`
- `multi tenant data architecture shared database shared schema`
- `pgvector vector column definition and hnsw index`
- `idempotent data pipeline file hash sha256 sql`
- `database relationship on delete cascade explanation`

### 3. Câu Hỏi Tư Duy Để Bạn Tự Kiểm Tra Bản Thân
- *Nếu một tài liệu bị xóa khỏi hệ thống, các đoạn văn bản (chunks) thuộc về tài liệu đó nên được xử lý thế nào? Thuộc tính nào trong SQL (`ON DELETE ...`) giúp tự động giải quyết việc này?*
- *Nếu nhân viên của công ty A sửa một câu trong tài liệu quy chế và tải lên lại, hệ thống nên ghi đè hoàn toàn hay nên tăng số phiên bản (version = version + 1)? Ưu và nhược điểm của mỗi cách là gì?*
- *Vector embedding bản chất là gì? Tại sao kích thước vector lại cố định (ví dụ 384 hoặc 768 hoặc 1536 chiều) đối với một mô hình nhất định?*

---

## 🟡 MỨC 2: GỢI Ý LUỒNG XỬ LÝ & LƯU Ý KHI GẶP LỖI

*(Nếu bạn đã tự tìm hiểu từ 1–2 tiếng mà vẫn vướng mắc, hãy tham khảo các gợi ý dưới đây)*

<details>
<summary>👉 <b>Bấm vào đây để xem gợi ý luồng thực hiện</b></summary>

### 1. Luồng Tư Duy Thiết Kế Thực Thể
- **Bảng `documents` (Quản lý tài liệu gốc):**
  - Cần các trường để xác định: Tài liệu này của ai (`tenant_id`), tên file là gì (`file_name`), vị trí lưu trên MinIO (`file_path`).
  - Cần trường `file_hash`: Lưu mã băm (SHA-256) của nội dung file. Khi quét file mới, pipeline chỉ cần so sánh chuỗi hash này với database để biết file có thay đổi hay không.
  - Cần trường `version` (INT): Mặc định là 1. Nếu hash thay đổi nhưng đường dẫn file giữ nguyên, ta có thể lưu một bản ghi mới với version tăng lên.
  - Cần trường `is_active` (BOOLEAN): Để đánh dấu phiên bản nào đang có hiệu lực phục vụ tìm kiếm.
- **Bảng `document_chunks` (Quản lý các đoạn cắt):**
  - Cần trường `document_id`: Khóa ngoại trỏ về `documents(id)`. Nên gắn kèm `ON DELETE CASCADE` để khi xóa tài liệu gốc, database tự động dọn dẹp các chunk liên quan mà không để lại dữ liệu rác.
  - Cần trường `tenant_id`: Mặc dù đã có `document_id`, việc lưu thêm `tenant_id` tại bảng chunk giúp câu lệnh tìm kiếm ngữ nghĩa có thể lọc trực tiếp `WHERE tenant_id = '...'` mà không bắt buộc phải JOIN sang bảng document, tăng tốc độ truy vấn đáng kể.
  - Cần trường `chunk_index`: Vị trí của đoạn trong văn bản (đoạn 0, đoạn 1, đoạn 2,...).
  - Cần trường `content` (TEXT): Chứa nội dung chữ thực tế của đoạn đó để trả về cho người dùng đọc.
  - Cần trường `embedding` (`vector(384)`): Lưu vector đặc trưng (độ dài 384 tương ứng với mô hình phổ biến và nhẹ nhất là `all-MiniLM-L6-v2`).
  - Cần trường `metadata` (`JSONB`): Giúp lưu trữ linh hoạt các thông tin phụ trợ (số trang, tên chương mục, ngày tạo,...).

### 2. Ràng Buộc Toàn Vẹn (Constraints): Để Database Tự Chặn Dữ Liệu Sai
Code pipeline có thể có bug, nhưng ràng buộc trong database thì luôn được kiểm tra. Hãy tự hỏi: *"Nếu code ghi sai, database có tự chặn được không?"*
- **Chunk phải cùng tenant với document cha:** Khóa ngoại thông thường chỉ kiểm tra `document_id` có tồn tại. Hãy tìm hiểu **khóa ngoại ghép (composite foreign key)** trên cặp `(document_id, tenant_id)` để một chunk không thể mang `tenant_id` khác với tài liệu gốc của nó.
- **Không trùng chunk khi chạy lại pipeline:** Ràng buộc `UNIQUE` trên cặp nào sẽ khiến lần chạy thứ hai không thể chèn thêm "đoạn 0" lần nữa cho cùng một tài liệu?
- **Chỉ một phiên bản đang hiệu lực:** Tìm hiểu **partial unique index** (`CREATE UNIQUE INDEX ... WHERE is_active`) để mỗi file của một tenant chỉ có tối đa 1 bản ghi `is_active = TRUE`.
- **Cột `updated_at`:** `DEFAULT CURRENT_TIMESTAMP` chỉ có tác dụng lúc INSERT. Muốn cột này tự cập nhật khi UPDATE, bạn cần tìm hiểu về **trigger** trong PostgreSQL.

### 3. Thiết Kế Chỉ Mục (Indexes)
- Bảng nào cũng nên đánh Index trên `tenant_id` vì hầu hết các câu truy vấn nghiệp vụ đều lọc theo công ty.
- Với cột `embedding`, sau khi kích hoạt extension `vector`, bạn có thể tìm hiểu cú pháp tạo Index loại `hnsw` với toán tử khoảng cách `vector_cosine_ops` (Cosine Distance) để tối ưu tốc độ tìm kiếm tương đồng.

*(Bạn có thể tham khảo file mẫu gợi ý tại [`infra/sql/init.sql`](../../infra/sql/init.sql) trong thư mục dự án để đối chiếu với thiết kế của mình).*

### 4. Những Vấn Đề Thường Gặp
- **Lỗi kiểu dữ liệu `vector` không tồn tại (`type "vector" does not exist`):**
  - Nguyên nhân: Bạn chưa chạy lệnh `CREATE EXTENSION IF NOT EXISTS vector;` trước khi tạo bảng.
- **Tạo Index HNSW bị báo lỗi hoặc tốn nhiều thời gian:**
  - HNSW là giải pháp tìm kiếm láng giềng gần đúng rất nhanh. Nếu chưa quen với HNSW, ở giai đoạn đầu bạn hoàn toàn có thể chạy query trực tiếp mà chưa cần tạo vector index, sau đó bổ sung index khi số lượng bản ghi lớn hơn.

</details>
