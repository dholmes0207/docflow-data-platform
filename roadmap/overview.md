# Lộ Trình Đào Tạo Thực Chiến Data Engineering (DocFlow Platform)

Lộ trình được thiết kế bám sát thực tế các hệ thống RAG doanh nghiệp hiện đại, chia làm 2 giai đoạn chính:

---

## 📅 GIAI ĐOẠN 1: CORE DATA PIPELINE & MVP RAG (Tuần 1 – Tuần 8)
*Mục tiêu: Xây dựng hệ thống nạp dữ liệu hoàn chỉnh từ File thô đến Vector Search và Event Logging.*

### Tuần 1: Thiết Lập Môi Trường Linux Chuẩn & Docker
- [Task 0.1: Cài đặt WSL2 (Ubuntu 22.04) & VS Code WSL](../tasks/week_01/task_01_wsl_vscode.md)
- [Task 0.2: Cài đặt Docker Desktop & Cấu hình RAM .wslconfig](../tasks/week_01/task_02_docker_fundamentals.md)

### Tuần 2: Hạ Tầng Lưu Trữ & Data Modeling
- [Task 0.3: Dựng MinIO + PostgreSQL + pgvector với Docker Compose](../tasks/week_02/task_03_docker_compose_infra.md)
- [Task 0.4: Thiết kế ERD & Viết Schema init.sql](../tasks/week_02/task_04_data_modeling.md)
- [Task 0.5: Chuẩn bị Mock Data & Edge Cases](../tasks/week_02/task_05_mock_data.md)

### Tuần 3: Trích Xuất & Làm Sạch Văn Bản (Data Cleaning)
- **Task 1.1:** Viết Python Client kết nối MinIO và quét danh sách file theo Tenant.
- **Task 1.2:** Text Extractor & Normalizer: Xử lý định dạng file (`.txt`, `.md`), chuẩn hóa Unicode (NFC), xóa ký tự rác, bảo toàn cấu trúc tiêu đề.

### Tuần 4: Semantic Chunking & Idempotent Ingestion
- **Task 1.3:** Thiết kế thuật toán cắt đoạn (Chunking Strategy: Recursive Character Splitter với overlap 15-20%), đính kèm Metadata (`tenant_id`, `chunk_index`).
- **Task 1.4:** Tính toán mã băm nội dung file (SHA-256) và thiết kế logic nạp Idempotent (chạy lại nhiều lần không trùng dữ liệu).

### Tuần 5: Database Writer & Versioning (SCD Type 2)
- **Task 1.5:** Viết module kết nối PostgreSQL qua `psycopg` / `SQLAlchemy`.
- **Task 1.6:** Xử lý tình huống file bị sửa đổi nội dung: Đánh dấu version cũ `is_active = FALSE` và tạo version mới.

### Tuần 6: Local Vector Embedding & pgvector Storage
- **Task 2.1:** Tích hợp mô hình nhúng cục bộ siêu nhẹ `sentence-transformers/all-MiniLM-L6-v2` (chạy trên CPU, chi phí $0).
- **Task 2.2:** Lưu trữ vector vào bảng `document_chunks` và cấu hình bộ nhớ đệm (Cache) tránh tính toán lại.

### Tuần 7: Multi-tenant Semantic Search & Đánh Giá
- **Task 2.3:** Viết hàm tìm kiếm ngữ nghĩa `search(query, tenant_id, top_k)` sử dụng Cosine Distance (`<=>`), bắt buộc cách ly dữ liệu theo Tenant.
- **Task 2.4:** Thiết kế bộ 20 câu hỏi đánh giá và tính chỉ số `Recall@k` so sánh giữa Full-Text Search và Vector Search.

### Tuần 8: UI Demo (Streamlit) & Event Logging
- **Task 3.1:** Dựng giao diện Chat/Search đơn giản bằng Streamlit: Chọn Tenant, nhập câu hỏi, xem các đoạn trích dẫn được trả về.
- **Task 3.2:** Ghi log sự kiện sử dụng: Mỗi truy vấn ghi lại 1 dòng sự kiện vào bảng `query_events` (tenant_id, question, retrieved_chunks, latency, cost).

---

## 📅 GIAI ĐOẠN 2: ORCHESTRATION, ANALYTICS & GOVERNANCE (Tuần 9 – Tuần 16)
*Mục tiêu: Đưa hệ thống lên chuẩn Production với Airflow, dbt, Row Level Security và CI/CD.*

### Tuần 9 – 10: Tự Động Hóa Với Apache Airflow
- **Task 4.1:** Dựng Airflow LocalExecutor nhẹ nhàng trên Docker.
- **Task 4.2:** Viết Airflow DAG tự động hóa toàn bộ luồng: Quét MinIO -> Xử lý text -> Chunking -> Vectorizing -> Load vào Postgres.
- **Task 4.3:** Xử lý cơ chế Retry khi lỗi mạng và cấu hình Alert khi gặp file lỗi (Empty/Corrupted).

### Tuần 11 – 12: Analytics Engineering Với dbt
- **Task 5.1:** Cài đặt dbt-core kết nối vào PostgreSQL.
- **Task 5.2:** Xây dựng Data Mart từ bảng `query_events`:
  - `dim_tenants`, `dim_documents`
  - `fct_queries`
  - `agg_daily_tenant_usage` (Tổng hợp lượng dùng, chi phí ước tính, tỷ lệ trả lời thành công).
- **Task 5.3:** Viết dbt tests (`unique`, `not_null`, `accepted_values`).

### Tuần 13: Dashboard Phân Tích Vận Hành
- **Task 5.4:** Dựng Dashboard phân tích vận hành ngay trên Streamlit (hoặc Metabase) đọc trực tiếp từ các bảng tổng hợp của dbt.

### Tuần 14 – 15: Quản Trị & Bảo Mật Dữ Liệu (Governance & Security)
- **Task 6.1:** Bật tính năng Row Level Security (RLS) trên PostgreSQL; viết test tự động chứng minh Tenant A không thể đọc trộm dữ liệu của Tenant B.
- **Task 6.2:** PII Masking: Che các thông tin nhạy cảm (Email, Số điện thoại) trong log câu hỏi trước khi đưa vào kho phân tích.
- **Task 6.3:** Data Retention: Thiết lập job tự động dọn dẹp hoặc archive log cũ hơn N ngày.

### Tuần 16: Hoàn Thiện Repo, CI/CD & Portfolio Showcase
- **Task 7.1:** Thiết lập GitHub Actions tự động chạy `pytest` và `dbt test` trên mỗi Pull Request.
- **Task 7.2:** Hoàn thiện README, kiến trúc tổng thể, ghi chép thiết kế và quay video demo 2–3 phút.
