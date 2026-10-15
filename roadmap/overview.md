# Lộ Trình Đào Tạo Thực Chiến Data Engineering (DocFlow Platform)

Lộ trình được thiết kế bám sát thực tế các hệ thống RAG doanh nghiệp hiện đại, chạy song song với lịch học trên trường:
**từ 02/11/2026 đến 30/05/2027**, chia thành **13 sprint**, mỗi sprint kéo dài 2 tuần (riêng Sprint 13 kéo dài 1 tuần).

## ⏱️ Nhịp Làm Việc

- **Sprint 2 tuần**, từ thứ Hai đến chủ nhật. Mỗi sprint có 1–2 task. Thời lượng dự kiến khoảng **8–10 giờ mỗi tuần**.
- **Cuối mỗi sprint** (chủ nhật cuối sprint): nộp PR, cập nhật [`weekly_tracker.md`](weekly_tracker.md), rồi review cùng mentor.
- **Giữa sprint:** tự cập nhật trạng thái trong tracker. Nếu bị tắc quá 2 buổi, nhắn mentor ngay, không đợi đến buổi review.
- Thư mục `tasks/week_XX/` tương ứng với **Sprint XX** (ví dụ `tasks/week_03/` là Sprint 3).
- Task được viết chi tiết trước 1–2 sprint (cuốn chiếu). Các sprint xa hơn chỉ có mô tả ngắn bên dưới và sẽ được bổ sung dần.
- Lịch nghỉ dưới đây là **dự kiến**. Hãy báo mentor lịch thi thật của bạn để điều chỉnh sớm.

## 🎯 Các Mốc Kiểm Tra

| Mốc | Thời điểm | Bạn cần chứng minh được |
|---|---|---|
| **M1: Hạ tầng sẵn sàng** | Hết Sprint 2 (29/11/2026) | Cụm MinIO + Postgres chạy ổn định; schema của bạn qua được gate test; dữ liệu mẫu đã lên MinIO |
| **M2: Demo giữa kỳ (MVP RAG)** | Hết Sprint 9 (11/04/2027) | Hỏi một câu trên giao diện Streamlit → nhận đoạn trích đúng tenant; có log truy vấn; có số Recall@k |
| **M3: Demo cuối kỳ** | Sprint 13 (24/05–30/05/2027) | Pipeline tự động bằng Airflow, Data Mart dbt có test, RLS chứng minh cách ly tenant, video demo 2–3 phút |

---

## 📅 GIAI ĐOẠN 1: CORE DATA PIPELINE & MVP RAG (Sprint 1 – Sprint 9)
*Mục tiêu: Xây dựng hệ thống nạp dữ liệu hoàn chỉnh từ File thô đến Vector Search và Event Logging.*

### Sprint 1 (02/11 – 15/11/2026): Thiết Lập Môi Trường Linux Chuẩn & Docker
- [Task 0.1: Cài đặt WSL2 (Ubuntu 24.04) & VS Code WSL trên Windows](../tasks/week_01/task_01_wsl_vscode.md)
- [Task 0.2: Cài đặt Docker Desktop & Cấu hình RAM .wslconfig](../tasks/week_01/task_02_docker_fundamentals.md)

### Sprint 2 (16/11 – 29/11/2026): Hạ Tầng Lưu Trữ & Data Modeling → 🎯 Mốc M1
- [Task 0.3: Dựng MinIO + PostgreSQL + pgvector với Docker Compose](../tasks/week_02/task_03_docker_compose_infra.md)
- [Task 0.4: Thiết kế ERD & tự viết schema `db/schema.sql`](../tasks/week_02/task_04_data_modeling.md)
- [Task 0.5: Chuẩn bị Mock Data & Edge Cases](../tasks/week_02/task_05_mock_data.md)

### Sprint 3 (30/11 – 13/12/2026): Khung Dự Án & Bộ Dữ Liệu Thật Sự
- [Task 0.6: Mở rộng bộ dữ liệu (corpus) & bộ câu hỏi đánh giá](../tasks/week_03/task_06_expand_corpus.md)
- [Task 1.0: Khung dự án Python & quy ước code](../tasks/week_03/task_07_project_skeleton.md)

### Sprint 4 (14/12 – 27/12/2026): Trích Xuất & Làm Sạch Văn Bản (Data Cleaning)
- [Task 1.1: Python Client kết nối MinIO & quét file theo Tenant](../tasks/week_04/task_08_minio_client.md)
- [Task 1.2: Text Extractor & Normalizer (Unicode NFC, làm sạch, giữ cấu trúc tiêu đề)](../tasks/week_04/task_09_text_cleaning.md)

> 🏖️ **Nghỉ thi học kỳ 1 & Tết Dương lịch (28/12/2026 – 10/01/2027):** không giao task mới. Dùng để ôn thi, hoặc làm nốt phần còn dở nếu có thời gian.

### Sprint 5 (11/01 – 24/01/2027): Semantic Chunking & Idempotent Ingestion
- **Task 1.3:** Thiết kế thuật toán cắt đoạn (Chunking Strategy: Recursive Character Splitter với overlap 15-20%), đính kèm Metadata (`tenant_id`, `chunk_index`, tiêu đề mục chứa đoạn).
- **Task 1.4:** Tính mã băm nội dung (SHA-256) **sau khi đã chuẩn hóa ở Task 1.2** và thiết kế logic nạp Idempotent (chạy lại nhiều lần không trùng dữ liệu).

> 🧘 **Tuần đệm (25/01 – 31/01/2027):** làm nốt task còn dở của Sprint 1–5. Không có task mới.
>
> 🧧 **Nghỉ Tết Nguyên Đán (01/02 – 14/02/2027, mùng 1 Tết: 06/02/2027).**

### Sprint 6 (15/02 – 28/02/2027): Database Writer & Versioning
- **Task 1.5:** Viết module ghi PostgreSQL qua `psycopg` / `SQLAlchemy`. **Tách 2 role database:** `docflow_owner` (tạo và sở hữu bảng) và `docflow_app` (ứng dụng dùng hằng ngày, chỉ có quyền đọc/ghi dữ liệu). Superuser và chủ sở hữu bảng mặc định **bỏ qua Row Level Security**. Tách role từ bây giờ để đến Task 6.1 bật RLS là có tác dụng ngay.
- **Task 1.6:** Xử lý file bị sửa nội dung theo kiểu **SCD Type 2**: viết migration bổ sung `valid_from` / `valid_to`, đóng phiên bản cũ (`is_active = FALSE`, `valid_to = now()`) và mở phiên bản mới trong **cùng một transaction**.

### Sprint 7 (01/03 – 14/03/2027): Local Vector Embedding & pgvector Storage
- **Task 2.1:** Tích hợp mô hình nhúng chạy cục bộ **hỗ trợ tiếng Việt**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` hoặc `intfloat/multilingual-e5-small` (đều sinh vector **384 chiều**, chạy trên CPU, chi phí $0). *Không dùng `all-MiniLM-L6-v2`: mô hình này chỉ được huấn luyện trên tiếng Anh, sẽ cho kết quả kém với tài liệu tiếng Việt.*
- **Task 2.2:** Lưu vector vào bảng `document_chunks`, kèm **mã băm nội dung từng chunk** làm khóa bộ nhớ đệm (cache), để chunk không đổi thì không phải tính lại embedding.

### Sprint 8 (15/03 – 28/03/2027): Multi-tenant Semantic Search & Đánh Giá
- **Task 2.3:** Viết hàm tìm kiếm ngữ nghĩa `search(query, tenant_id, top_k)` dùng Cosine Distance (`<=>`), bắt buộc cách ly dữ liệu theo tenant. Tìm hiểu vì sao lọc `WHERE tenant_id = ...` kết hợp index HNSW có thể trả về **ít hơn `top_k`** kết quả (từ khóa: `pgvector filtering iterative index scans`).
- **Task 2.4:** Dùng bộ câu hỏi của Task 0.6 để tính `Recall@k`, so sánh Full-Text Search với Vector Search. Lưu ý: PostgreSQL không có cấu hình full-text search cho tiếng Việt, hãy tìm hiểu cấu hình `simple` kết hợp extension `unaccent`.

### Sprint 9 (29/03 – 11/04/2027): UI Demo (Streamlit) & Event Logging → 🎯 Mốc M2
- **Task 3.1:** Dựng giao diện Chat/Search đơn giản bằng Streamlit: chọn tenant, nhập câu hỏi, xem các đoạn trích dẫn được trả về.
- **Task 3.2:** Ghi log sự kiện sử dụng: mỗi truy vấn ghi 1 dòng vào bảng `query_events` (tenant_id, câu hỏi **đã che PII** như email và số điện thoại, retrieved_chunks, latency, số token). Che PII **ngay khi ghi log**, trước khi dữ liệu chảy sang kho phân tích.

---

## 📅 GIAI ĐOẠN 2: ORCHESTRATION, ANALYTICS & GOVERNANCE (Sprint 10 – Sprint 13)
*Mục tiêu: Đưa hệ thống lên chuẩn Production với Airflow, dbt, Row Level Security và CI/CD.*

### Sprint 10 (12/04 – 25/04/2027): Tự Động Hóa Với Apache Airflow
- **Task 4.1:** Dựng Airflow (LocalExecutor) trên Docker, **ghim cố định phiên bản**. Tính trước ngân sách RAM: Airflow chạy cùng Postgres + MinIO phải nằm gọn trong giới hạn `.wslconfig` của Task 0.2.
- **Task 4.2:** Viết Airflow DAG tự động hóa toàn bộ luồng: Quét MinIO → Xử lý text → Chunking → Vectorizing → Load vào Postgres. Cấu hình `retries` cho các task có gọi mạng.

### Sprint 11 (26/04 – 09/05/2027): Analytics Engineering Với dbt
- **Task 5.1:** Cài đặt dbt-core kết nối vào PostgreSQL.
- **Task 5.2:** Xây dựng Data Mart từ bảng `query_events`:
  - `dim_tenants`, `dim_documents`
  - `fct_queries`
  - `agg_daily_tenant_usage` (lượng dùng, độ trễ, tỷ lệ trả lời thành công theo ngày)

### Sprint 12 (10/05 – 23/05/2027): Chất Lượng Dữ Liệu & Cách Ly Tenant
- **Task 5.3:** Viết dbt tests (`unique`, `not_null`, `accepted_values`) và cho CI sẵn có của repo (`.github/workflows/ci.yml`) chạy `dbt test` trên mỗi Pull Request.
- **Task 6.1:** Bật Row Level Security (RLS) trên PostgreSQL với role `docflow_app` của Task 1.5; viết test tự động chứng minh Tenant A không đọc được dữ liệu của Tenant B.

### Sprint 13 (24/05 – 30/05/2027, 1 tuần): Hoàn Thiện & Demo Cuối Kỳ → 🎯 Mốc M3
- **Task 7.2:** Hoàn thiện README, sơ đồ kiến trúc tổng thể, ghi chép thiết kế và quay video demo 2–3 phút.

---

## ➕ Mở Rộng (Tùy Chọn, Làm Nếu Còn Thời Gian)

- **Task 4.3:** Alert khi gặp file lỗi (rỗng / hỏng) và retry nâng cao (backoff, giới hạn số lần thử) trong Airflow.
- **Task 5.4:** Dashboard phân tích vận hành (Streamlit hoặc Metabase) đọc từ các bảng tổng hợp của dbt.
- **Task 6.3:** Data Retention: job tự động dọn dẹp hoặc archive log cũ hơn N ngày.
- Nạp thêm định dạng `.pdf` / `.docx` ở Task 1.2. *Lưu ý: khi đó mentor cần mở quy tắc chặn file trong `scripts/check_forbidden_files.py` để cho phép file mẫu trong `sample_data/`.*
