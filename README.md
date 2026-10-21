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

## 🧭 Cơ Chế Theo Dõi Tiến Độ Theo Sprint

- **Lịch học:** từ 02/11/2026 đến 30/05/2027, chia thành 13 sprint (mỗi sprint 2 tuần), đã trừ các đợt thi và nghỉ Tết. Lịch chi tiết: [`roadmap/overview.md`](roadmap/overview.md).
- **Tần suất review:** Cuối mỗi sprint, người hướng dẫn sẽ ngồi lại cùng bạn để review tiến độ.
- **Cách thức:**
  1. Bắt đầu mỗi task bằng một issue và một nhánh riêng, theo quy trình ở [`CONTRIBUTING.md`](CONTRIBUTING.md) mục 2.
  2. Bạn tự cập nhật trạng thái các task và ghi chú những điều mình đã học được vào file [`roadmap/weekly_tracker.md`](roadmap/weekly_tracker.md).
  3. Tạo Pull Request (PR) cho từng task, có dòng `Closes #<số issue>`. CI sẽ tự kiểm tra PR, cần xanh trước khi review.
  4. Trong buổi review, bạn sẽ demo nhanh kết quả hoặc giải thích cách bạn đã giải quyết bài toán theo tiêu chí của task.

> 📏 **Trước khi bắt đầu, hãy đọc [`CONTRIBUTING.md`](CONTRIBUTING.md)**: cách dùng issue, quy tắc đặt tên nhánh, commit, các file bị cấm, các kiểm tra tự động (pre-commit, CI) và quy trình review mỗi sprint.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
docflow-data-platform/
├── README.md                 # Giới thiệu bài toán & hướng dẫn chung
├── CONTRIBUTING.md           # Quy tắc làm việc: nhánh, commit, file bị cấm, CI, quy trình review
├── .github/                  # CODEOWNERS, mẫu issue & mẫu mô tả PR, CI (ci.yml), phát hành task theo lịch (release-tasks.yml)
├── .claude/skills/           # Skill /review-week cho mentor review PR bằng Claude Code
├── roadmap/
│   ├── overview.md           # Lộ trình tổng thể dự án
│   └── weekly_tracker.md     # Bảng theo dõi tiến độ & hạn nộp từng task
├── tasks/                    # Task chi tiết, thư mục week_XX = Sprint XX
│   ├── release_schedule.toml # Lịch mở các task đang khóa
│   ├── _locked/              # Task của sprint sau, đang mã hóa (🔒), tự mở theo lịch
│   ├── week_01/              # Sprint 1: Môi trường làm việc chuẩn (WSL2, quy trình Git & GitHub, Docker)
│   ├── week_02/              # Sprint 2: Hạ tầng lưu trữ, Database & Data Modeling
│   ├── week_03/              # Sprint 3: Khung dự án Python & mở rộng bộ dữ liệu (🔒 mở theo lịch)
│   ├── week_04/              # Sprint 4: Kết nối MinIO & làm sạch văn bản (🔒 mở theo lịch)
│   ├── week_05/              # Sprint 5: Chunking & nạp dữ liệu không trùng lặp (🔒 mở theo lịch)
│   ├── week_06/              # Sprint 6: Ghi database, tách role & SCD Type 2 (🔒 mở theo lịch)
│   └── week_07/              # Sprint 7: Embedding đa ngôn ngữ & lưu vector có bộ nhớ đệm (🔒 mở theo lịch)
├── infra/                    # Thư mục cấu hình hạ tầng mẫu (tham khảo)
│   ├── docker-compose.yml
│   ├── .env.example          # Mẫu biến môi trường (copy thành .env, không commit .env)
│   └── sql/init.sql
├── sample_data/              # Dữ liệu tài liệu giả lập phục vụ kiểm thử
│   ├── tenant_retail/        # Doanh nghiệp bán lẻ (có 1 file rỗng làm bẫy)
│   ├── tenant_tech/          # Doanh nghiệp công nghệ
│   └── updates/              # Phiên bản sửa đổi của tài liệu (kiểm thử Versioning)
├── tests/gates/              # Gate test do mentor đặt ra (CI chạy trên mọi PR, không được sửa để lách)
├── scripts/                  # Script kiểm tra dùng chung cho pre-commit và CI
└── docs/                     # Ghi chép thiết kế, sơ đồ ERD, nhật ký học tập, git cheatsheet
```

Hãy bắt đầu Sprint 1 tại thư mục [`tasks/week_01/`](tasks/week_01/) theo thứ tự Task 0.1 → 0.0 → 0.2 nhé! Chúc bạn có trải nghiệm học tập thú vị.
