# DocFlow — Nền Tảng Dữ Liệu Cho Trợ Lý AI Nội Bộ

Dự án này là bài toán thực chiến giúp bạn tiếp cận và làm quen với công việc của một **Data Engineer (DE)** thông qua việc xây dựng nền tảng dữ liệu phục vụ trợ lý AI đa doanh nghiệp (Multi-tenant RAG Data Platform).

Hệ thống xoay quanh 2 luồng dữ liệu chính:
1. **Luồng tài liệu (Document Ingestion & Retrieval):** Tiếp nhận file, làm sạch, cắt đoạn (chunking), tạo vector embedding và tìm kiếm ngữ nghĩa theo từng doanh nghiệp.
2. **Luồng sự kiện (Analytics & Logging):** Ghi nhận log truy vấn, mô hình hóa dữ liệu (Data Modeling với dbt) và trực quan hóa số liệu vận hành.

---

## 💡 Phương Pháp Học & Cách Dùng Tài Liệu

Tài liệu trong repo này được thiết kế không phải để bạn "copy-paste lệnh có sẵn", mà để rèn luyện kỹ năng quan trọng nhất của kỹ sư phần mềm: **tự tra cứu, hiểu bản chất vấn đề và giải quyết lỗi phát sinh**.

Mỗi bài toán trong thư mục `tasks/` được chia thành 2 mức độ hỗ trợ:

### 🟢 Mức 1: Định Hướng Tự Học (Hãy luôn bắt đầu từ đây)
- **Mục tiêu & Tiêu chuẩn hoàn thành (DoD):** Giúp bạn biết rõ kết quả cần đạt được là gì.
- **Từ khóa tra cứu (Keywords):** Gợi ý những cụm từ chính xác để bạn tự tìm tài liệu chính thức hoặc thảo luận kỹ thuật.
- **Câu hỏi tư duy:** Những câu hỏi giúp bạn hiểu lý do "tại sao lại làm như vậy" thay vì chỉ học vẹt.

### 🟡 Mức 2: Gợi Ý Luồng Xử Lý (Mở ra khi bạn bị tắc quá lâu)
- Khi bạn đã chủ động tìm kiếm 1–2 tiếng mà vẫn chưa rõ hướng đi, hãy mở phần này.
- Mức này sẽ chỉ ra **luồng tư duy (workflow)**, các tài liệu tham khảo chính thống và các lưu ý đặc thù (nhất là khi chạy trên môi trường Windows 11/WSL2), chứ không áp đặt các câu lệnh cứng nhắc. Máy tính của mỗi người có thể khác nhau, việc hiểu luồng quan trọng hơn việc chạy đúng 1 lệnh copy.

---

## 🧭 Cơ Chế Theo Dõi Tiến Độ Hàng Tuần

- **Tần suất review:** Mỗi tuần một lần, người hướng dẫn sẽ ngồi lại cùng bạn để review tiến độ.
- **Cách thức:**
  1. Bạn tự cập nhật trạng thái các task và ghi chú những điều mình đã học được vào file [`roadmap/weekly_tracker.md`](roadmap/weekly_tracker.md).
  2. Tạo Pull Request (PR) cho những nội dung đã làm trong tuần.
  3. Trong buổi review, bạn sẽ demo nhanh kết quả hoặc giải thích cách bạn đã giải quyết bài toán theo tiêu chí của task.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
docflow-data-platform/
├── README.md                 # Giới thiệu bài toán & hướng dẫn chung
├── roadmap/
│   ├── overview.md           # Lộ trình tổng thể dự án
│   └── weekly_tracker.md     # Bảng theo dõi tiến độ review hàng tuần
├── tasks/                    # Danh sách các task chi tiết theo tuần
│   ├── week_01/              # Tuần 1: Môi trường làm việc chuẩn (WSL2, Docker)
│   └── week_02/              # Tuần 2: Hạ tầng lưu trữ, Database & Data Modeling
├── infra/                    # Thư mục cấu hình hạ tầng mẫu (tham khảo)
│   ├── docker-compose.yml
│   └── sql/init.sql
├── sample_data/              # Dữ liệu tài liệu giả lập phục vụ kiểm thử
└── docs/                     # Ghi chép thiết kế, sơ đồ ERD, nhật ký học tập
```

Hãy bắt đầu tuần đầu tiên tại thư mục [`tasks/week_01/`](tasks/week_01/) nhé! Chúc bạn có trải nghiệm học tập thú vị.
