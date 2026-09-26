# DocFlow — Nền Tảng Dữ Liệu Cho Trợ Lý AI Nội Bộ (Multi-Tenant RAG Data Platform)

Hệ thống Data Platform phục vụ trợ lý AI doanh nghiệp đa khách hàng (Multi-tenant), kết hợp hai luồng dữ liệu chính:
1. **Luồng tài liệu (Unstructured Data Pipeline):** Ingestion, Document Cleaning, Semantic Chunking, pgvector Storage, Semantic Search.
2. **Luồng sự kiện (Analytics & Logging Pipeline):** Event Tracking, Dimensional Modeling với dbt, Operational Dashboard.

---

## 🧭 Hướng Dẫn & Quy Định Cho U

Chào U! Repo này là dự án thực chiến giúp U làm quen và làm chủ tư duy của một **Data Engineer**.

### 1. Nguyên Tắc 2 Mức Hướng Dẫn (Level 1 & Level 2)
Mỗi task trong thư mục `tasks/` được chia làm 2 mức độ:
- 🟢 **MỨC 1: TỰ KHÁM PHÁ (Bắt buộc làm trước)**
  - U đọc kỹ **Mục tiêu** và **Definition of Done (DoD)**.
  - Sử dụng **Search Keywords** được cung cấp để tự tra cứu tài liệu, Google, hoặc đọc Official Docs.
  - Trả lời các **Câu hỏi định hướng tư duy** trước khi bắt tay vào gõ lệnh.
- 🟡 **MỨC 2: HƯỚNG DẪN CHI TIẾT & PHAO CỨU SINH**
  - **Chỉ mở ra khi U đã tự tìm hiểu và bị tắc quá 1 – 2 tiếng.**
  - Cung cấp đường dẫn file chính xác, cú pháp câu lệnh chi tiết từng bước, và các lỗi thường gặp (troubleshooting).

### 2. Chu Kỳ Review & Họp Đánh Giá
- **Review 1 tuần / 1 lần:** U tạo Pull Request (PR) hoặc cập nhật tiến độ vào file [`roadmap/weekly_tracker.md`](roadmap/weekly_tracker.md).
- U cần chuẩn bị demo ngắn hoặc trả lời các câu hỏi phản biện liên quan đến các quyết định kỹ thuật của task trong tuần.

---

## 📂 Cấu Trúc Thư Mục

```text
docflow/
├── README.md                 # Giới thiệu dự án & hướng dẫn tổng quát
├── roadmap/
│   ├── overview.md           # Lộ trình tổng thể các tuần
│   └── weekly_tracker.md     # Bảng theo dõi tiến độ review hàng tuần
├── tasks/                    # Kế hoạch chi tiết từng tuần chia 2 mức
│   ├── week_01/
│   │   ├── task_01_wsl_vscode.md
│   │   └── task_02_docker_fundamentals.md
│   └── week_02/
│       ├── task_03_docker_compose_infra.md
│       ├── task_04_data_modeling.md
│       └── task_05_mock_data.md
├── infra/                    # Hạ tầng Docker & Database
│   ├── docker-compose.yml
│   └── sql/
│       └── init.sql
├── sample_data/              # Dữ liệu tài liệu giả lập cho các Tenant
│   ├── tenant_retail/
│   └── tenant_tech/
└── docs/                     # Tài liệu thiết kế ERD, Architecture, Quyết định thiết kế
    └── architecture/
```

---

## 🚀 Bắt Đầu Từ Đâu?

U hãy mở ngay thư mục [`tasks/week_01/`](tasks/week_01/) và bắt đầu với [Task 0.1: Thiết lập môi trường Linux chuẩn trên Windows 11 (WSL2 + VS Code)](tasks/week_01/task_01_wsl_vscode.md)!
