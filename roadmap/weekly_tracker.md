# Bảng Theo Dõi Tiến Độ Review Hàng Tuần

Bảng này dùng để theo dõi tiến độ hoàn thành các task của U và ghi nhận phản hồi trong các buổi review định kỳ hàng tuần.

---

## Quy Trình Review

1. **Trước buổi review (Thứ 6 hoặc Thứ 7):**
   - U cập nhật cột **Trạng thái** (`Chưa bắt đầu` / `Đang làm` / `Sẵn sàng Review` / `Hoàn thành`).
   - U ghi chú ngắn gọn những khó khăn đã gặp và giải pháp đã thử vào cột **Ghi chú của U**.
   - U tạo Pull Request (PR) tổng hợp code của tuần đó lên GitHub repo.
2. **Trong buổi review:**
   - U trình bày/demo kết quả dựa trên các tiêu chí **Definition of Done (DoD)** của từng task.
   - Trả lời các câu hỏi phản biện về các quyết định kỹ thuật.
3. **Sau buổi review:**
   - Cập nhật đánh giá từ Reviewer và các việc cần khắc phục (Action items) nếu có.

---

## Bảng Tiến Độ

| Tuần | Task | Trọng Tâm | Trạng Thái | Link PR / Bằng Chứng | Đánh Giá Của Reviewer |
|:---:|:---|:---|:---:|:---:|:---|
| **Tuần 1** | Task 0.1 | Cài đặt WSL2 (Ubuntu 22.04) & VS Code WSL | `Chưa bắt đầu` | | |
| **Tuần 1** | Task 0.2 | Docker Desktop trên Windows 11 & Cấu hình RAM .wslconfig | `Chưa bắt đầu` | | |
| **Tuần 2** | Task 0.3 | Docker Compose: MinIO + PostgreSQL + pgvector | `Chưa bắt đầu` | | |
| **Tuần 2** | Task 0.4 | Data Modeling (ERD) & Viết Schema init.sql | `Chưa bắt đầu` | | |
| **Tuần 2** | Task 0.5 | Chuẩn bị dữ liệu mẫu (Mock data & Edge cases) | `Chưa bắt đầu` | | |
| **Tuần 3** | Task 1.1 | Python Script: Kết nối MinIO & Trích xuất file (.txt, .md) | `Chưa bắt đầu` | | |
| **Tuần 3** | Task 1.2 | Xử lý chuỗi & Làm sạch văn bản (Clean text, Unicode) | `Chưa bắt đầu` | | |
| **Tuần 4** | Task 1.3 | Text Chunking Strategy & Metadata Injection | `Chưa bắt đầu` | | |
| **Tuần 4** | Task 1.4 | Idempotent Ingestion & File Hashing (SHA-256) | `Chưa bắt đầu` | | |
| **Tuần 5** | Task 1.5 | Database Writer & SCD Type 2 / Versioning cho Document | `Chưa bắt đầu` | | |
| **Tuần 6** | Task 2.1 | Vector Embedding với `sentence-transformers` (Local CPU) | `Chưa bắt đầu` | | |
| **Tuần 6** | Task 2.2 | Lưu trữ Vector & Query Cosine Distance trong pgvector | `Chưa bắt đầu` | | |
| **Tuần 7** | Task 2.3 | Multi-tenant Semantic Search Function | `Chưa bắt đầu` | | |
| **Tuần 7** | Task 2.4 | Đo lường chất lượng tìm kiếm (Recall@k) | `Chưa bắt đầu` | | |
