# Bảng Theo Dõi Tiến Độ & Đánh Giá Theo Sprint

Bảng này là không gian trao đổi và ghi nhận tiến độ học tập giữa bạn và người hướng dẫn. Mỗi sprint kéo dài 2 tuần
(lịch chi tiết và các đợt nghỉ: xem [`overview.md`](overview.md)).

---

## 📌 Quy Trình Mỗi Sprint

1. **Trong sprint:**
   - Bắt đầu task nào thì mở issue cho task đó bằng mẫu **"Bắt đầu một task"** và tạo nhánh theo quy tắc trong [`CONTRIBUTING.md`](../CONTRIBUTING.md) mục 2.
   - Cập nhật cột **Trạng thái** ngay khi bắt đầu một task (`Đang thực hiện`). Chỉ dùng đúng 4 giá trị:
     `Chưa bắt đầu` / `Đang thực hiện` / `Sẵn sàng Review` / `Hoàn thành` (CI sẽ báo lỗi nếu ghi khác).
   - Ghi lại kiến thức mới, lỗi đã gặp và cách bạn giải quyết vào file `docs/learning_log.md` của bạn (gợi ý cách ghi: [`docs/README.md`](../docs/README.md)).
   - Bị tắc quá 2 buổi thì mở issue mẫu **"Hỏi mentor / Bị tắc"** rồi nhắn link cho mentor ngay, không đợi đến buổi review.
2. **Cuối sprint (trước cột Hạn):**
   - Mở Pull Request cho task (mô tả có `Closes #<số issue>`), đợi CI xanh, đổi trạng thái thành `Sẵn sàng Review` và dán link PR vào cột **Link PR**.
3. **Buổi review:**
   - Bạn demo nhanh kết quả theo các tiêu chí **Definition of Done (DoD)** của từng task.
   - Cùng người hướng dẫn trao đổi về các câu hỏi tư duy trong Mức 1 để củng cố bản chất kỹ thuật.
4. **Sau buổi review:**
   - Người hướng dẫn ghi nhận đánh giá vào cột **Đánh Giá & Góp Ý**; task đạt thì chuyển sang `Hoàn thành`.

---

## 📋 Bảng Tiến Độ Chi Tiết

| Sprint | Task | Trọng Tâm Bài Toán | Trạng Thái | Link PR / Bằng Chứng | Đánh Giá & Góp Ý Của Reviewer | Hạn |
|:---:|:---|:---|:---:|:---:|:---|:---:|
| **S1** | Task 0.0 | Quy trình Git & GitHub: issue, nhánh, commit, Pull Request, review | `Chưa bắt đầu` | | | 15/11/2026 |
| **S1** | Task 0.1 | Môi trường Linux chuẩn trên Windows (WSL2 Ubuntu 24.04 & VS Code) | `Chưa bắt đầu` | | | 15/11/2026 |
| **S1** | Task 0.2 | Cài đặt Docker Desktop & Tối ưu RAM qua `.wslconfig` | `Chưa bắt đầu` | | | 15/11/2026 |
| **S2** | Task 0.3 | Dựng cụm MinIO + PostgreSQL (pgvector) với Docker Compose | `Chưa bắt đầu` | | | 29/11/2026 |
| **S2** | Task 0.4 | Data Modeling (ERD) & Viết Schema khởi tạo Database | `Chưa bắt đầu` | | | 29/11/2026 |
| **S2** | Task 0.5 | Chuẩn bị dữ liệu mẫu và các trường hợp biên (Edge Cases) | `Chưa bắt đầu` | | | 29/11/2026 |
| **S3** | Task 0.6 | Mở rộng bộ dữ liệu (corpus) & bộ câu hỏi đánh giá | `Chưa bắt đầu` | | | 13/12/2026 |
| **S3** | Task 1.0 | Khung dự án Python & quy ước code | `Chưa bắt đầu` | | | 13/12/2026 |
| **S4** | Task 1.1 | Python Client kết nối MinIO & quét file theo Tenant | `Chưa bắt đầu` | | | 27/12/2026 |
| **S4** | Task 1.2 | Trích xuất & làm sạch văn bản (Unicode NFC, giữ cấu trúc tiêu đề) | `Chưa bắt đầu` | | | 27/12/2026 |
| **S5** | Task 1.3 | Kỹ thuật cắt đoạn (Chunking) & Đính kèm Metadata | `Chưa bắt đầu` | | | 24/01/2027 |
| **S5** | Task 1.4 | Nạp dữ liệu bất biến (Idempotent) qua mã băm SHA-256 | `Chưa bắt đầu` | | | 24/01/2027 |
| **S6** | Task 1.5 | Database Writer & tách role `docflow_owner` / `docflow_app` | `Chưa bắt đầu` | | | 28/02/2027 |
| **S6** | Task 1.6 | Xử lý phiên bản tài liệu (SCD Type 2: `valid_from` / `valid_to`) | `Chưa bắt đầu` | | | 28/02/2027 |
| **S7** | Task 2.1 | Vector Embedding đa ngôn ngữ chạy local (CPU) | `Chưa bắt đầu` | | | 14/03/2027 |
| **S7** | Task 2.2 | Lưu trữ Vector & cache embedding theo mã băm chunk | `Chưa bắt đầu` | | | 14/03/2027 |
| **S8** | Task 2.3 | Hàm tìm kiếm ngữ nghĩa cách ly theo tenant | `Chưa bắt đầu` | | | 28/03/2027 |
| **S8** | Task 2.4 | Đo chất lượng tìm kiếm bằng Recall@k (FTS vs Vector) | `Chưa bắt đầu` | | | 28/03/2027 |
| **S9** | Task 3.1 | Giao diện Chat/Search demo bằng Streamlit | `Chưa bắt đầu` | | | 11/04/2027 |
| **S9** | Task 3.2 | Ghi log truy vấn vào `query_events` (đã che PII) | `Chưa bắt đầu` | | | 11/04/2027 |
| **S10** | Task 4.1 | Dựng Airflow (LocalExecutor) trên Docker | `Chưa bắt đầu` | | | 25/04/2027 |
| **S10** | Task 4.2 | Viết DAG tự động hóa toàn bộ luồng nạp dữ liệu (có retries) | `Chưa bắt đầu` | | | 25/04/2027 |
| **S11** | Task 5.1 | Cài đặt dbt-core kết nối PostgreSQL | `Chưa bắt đầu` | | | 09/05/2027 |
| **S11** | Task 5.2 | Xây dựng Data Mart từ `query_events` (dim/fct/agg) | `Chưa bắt đầu` | | | 09/05/2027 |
| **S12** | Task 5.3 | dbt tests (`unique`, `not_null`, `accepted_values`) chạy trong CI | `Chưa bắt đầu` | | | 23/05/2027 |
| **S12** | Task 6.1 | Row Level Security & test cách ly Tenant | `Chưa bắt đầu` | | | 23/05/2027 |
| **S13** | Task 7.2 | Hoàn thiện README, kiến trúc & video demo | `Chưa bắt đầu` | | | 30/05/2027 |
| **Tùy chọn** | Task 4.3 | Alert khi gặp file lỗi & retry nâng cao trong Airflow | `Chưa bắt đầu` | | | — |
| **Tùy chọn** | Task 5.4 | Dashboard phân tích vận hành từ các bảng dbt | `Chưa bắt đầu` | | | — |
| **Tùy chọn** | Task 6.3 | Data Retention: dọn dẹp/archive log cũ | `Chưa bắt đầu` | | | — |
