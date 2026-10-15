---
name: review-week
description: Review Pull Request hằng tuần của học viên DocFlow. Kiểm tra CI, chạy gate test và các phép thử bổ sung trên chính phần bài nộp, đối chiếu từng tiêu chí Definition of Done của task, rồi soạn kết luận review. Dùng khi mentor gõ /review-week <số PR>, hoặc nhờ review / chấm PR của học viên.
---

# Review PR hằng tuần của học viên

Bạn đang giúp **mentor** review bài nộp của học viên trong repo DocFlow. Mục tiêu: đưa ra một kết luận có
bằng chứng, mentor đọc xong là quyết định được ngay. Viết mọi thứ bằng tiếng Việt, xưng "bạn" với học viên.

Đối số: số PR (ví dụ `/review-week 5`). Không có số PR thì liệt kê các PR đang mở và hỏi mentor chọn PR nào.

## Nguyên tắc

- **Chỉ đọc và chạy thử, không sửa bài của học viên.** Không push, không commit lên nhánh của học viên.
- **Không approve, không merge, không đăng bình luận** khi mentor chưa nói rõ. Soạn sẵn, trình mentor xem trước.
- **Mọi nhận định phải có bằng chứng**: lệnh đã chạy và kết quả, hoặc `file:dòng`. Không suy đoán là "chắc đạt".
- **Không đưa lời giải.** Góp ý chỉ ra *vấn đề* và *hướng tìm hiểu* (giống phần Mức 1 / Mức 2 của task),
  không viết sẵn code hoặc SQL đúng cho học viên chép.
- Không thêm chữ ký hay dòng tác giả Claude vào nội dung đăng lên GitHub.

## Bước 1: Thu thập

1. Đọc PR: tiêu đề, mô tả (theo mẫu `.github/pull_request_template.md`), danh sách file thay đổi, commit, tên nhánh.
2. Xác định **task** từ mục "Tuần / Task" trong mô tả PR. Không ghi rõ thì suy ra từ file thay đổi và nói rõ
   là suy ra.
3. Đọc file task tương ứng trong `tasks/week_XX/`, lấy danh sách tiêu chí **Definition of Done** và
   **Câu hỏi tư duy**.

## Bước 2: Cổng CI

Đọc trạng thái 3 check `hygiene`, `schema`, `secrets` trên commit mới nhất của PR.

- Có check **đỏ** → kết luận ngay **CẦN SỬA**. Liệt kê check đỏ và trích đúng thông báo lỗi (gate test
  được viết để thông báo lỗi tự giải thích). Bỏ qua bước 3–4, chuyển thẳng sang bước 5.
- Check **chưa chạy / đang chạy** → báo mentor và hỏi có đợi không.
- Học viên **sửa, xóa hay thêm `skip`** vào bất kỳ file nào trong `tests/gates/`, `scripts/`, `.github/`
  → nêu thành mục riêng, mức **nghiêm trọng**, kể cả khi CI xanh (vi phạm CONTRIBUTING.md mục 6).

## Bước 3: Kiểm tra ngầm trên bài nộp

Lấy code của PR vào một thư mục riêng, không làm bẩn nhánh đang đứng:

```bash
git fetch origin pull/<PR>/head:review/pr-<PR>
git worktree add ../review-pr-<PR> review/pr-<PR>
cd ../review-pr-<PR> && pip install -r requirements-dev.txt -q
```

Chạy gate test cơ bản: `pytest tests/gates -q`. Có Postgres + pgvector thì đặt thêm `DATABASE_URL`.
Không có Postgres thì ghi rõ "chưa chạy được test schema tại máy", **không** coi là đạt.

Sau đó chạy thêm các phép thử theo task:

| Task | Phép thử thêm |
|---|---|
| 0.1, 0.2 (môi trường máy học viên) | Không kiểm chứng được từ repo. Dựa vào ảnh chụp / output lệnh trong mô tả PR; tiêu chí nào thiếu bằng chứng thì đánh dấu **CẦN DEMO**. |
| 0.3 (Docker Compose) | Tìm file compose học viên nộp. `cp <thư mục>/.env.example <thư mục>/.env` (nếu có) rồi `docker compose -f <file> config --quiet`. Soát: 2 service `postgres` + `minio`, named volumes cho cả 2 (DoD 5), cổng 9000 + 9001 + 5432, mật khẩu **không** ghi cứng trong YAML. |
| 0.4 (Data Modeling) | Nếu học viên nộp file schema riêng: `INIT_SQL_PATH=<file> DATABASE_URL=... pytest tests/gates/test_schema_constraints.py -q`. Test đỏ vì **khác tên bảng / tên cột** thì không tính là lỗi thiết kế: đọc schema và đánh giá thủ công theo từng ý của test. Test đỏ vì **thiếu ràng buộc** thì là phát hiện thật. Soát thêm: có file ERD trong `docs/` (DoD 1). |
| 0.5 (Mock Data) | ≥ 2 tenant, mỗi tenant 2–3 tài liệu có nội dung; có file rỗng 0 byte; có tài liệu 2 phiên bản với mã băm khác nhau; có 3–5 câu hỏi kiểm thử kèm đáp án, trong đó ≥ 1 câu bẫy rò rỉ giữa các tenant. |
| Task chưa có trong bảng | Tự thiết kế 2–3 phép thử chạy được, bám sát từng tiêu chí DoD của task. Ghi rõ đã chạy lệnh gì. |

Làm xong thì dọn: `git worktree remove ../review-pr-<PR> && git branch -D review/pr-<PR>`.

## Bước 4: Quy trình

- Tên nhánh có đúng dạng `week-XX/task-X.Y-...` không.
- Commit message có theo Conventional Commits không.
- `roadmap/weekly_tracker.md` đã đổi trạng thái task thành `Sẵn sàng Review` và có link PR chưa.
- Mô tả PR có điền đủ các mục của mẫu không.

Lỗi quy trình chỉ là **ghi chú**, không tự nó làm bài thành CẦN SỬA, trừ khi lặp lại sau khi đã được nhắc.

## Bước 5: Kết luận

Chọn đúng một mức:
- **ĐẠT:** CI xanh và mọi tiêu chí DoD có bằng chứng.
- **ĐẠT KÈM GHI CHÚ:** CI xanh, DoD đạt, còn góp ý không chặn (chất lượng, quy trình).
- **CẦN SỬA:** CI đỏ, hoặc có tiêu chí DoD chưa đạt, hoặc chạm vào gate test.

Trình bày cho mentor theo đúng khung sau:

```markdown
## Kết luận review PR #<số>: <ĐẠT | ĐẠT KÈM GHI CHÚ | CẦN SỬA>
Task: <X.Y> · Commit: <sha ngắn> · CI: hygiene <✅/❌> · schema <✅/❌> · secrets <✅/❌>

### Definition of Done
| # | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | ... | ✅ ĐẠT / ❌ CHƯA ĐẠT / 🎤 CẦN DEMO | lệnh + kết quả, hoặc file:dòng |

### Kiểm tra ngầm đã chạy
- `<lệnh>` → <kết quả>

### Cần sửa (chặn merge)
- ...

### Góp ý (không chặn)
- ...

### Câu hỏi cho buổi review
- 2–3 câu lấy từ "Câu hỏi tư duy" của task, ưu tiên câu chạm đúng chỗ bài nộp còn yếu.
```

Sau đó hỏi mentor muốn làm gì tiếp:
1. Đăng kết luận lên PR dưới dạng review (`REQUEST_CHANGES` nếu CẦN SỬA, ngược lại `COMMENT`).
2. Approve và merge. Chỉ làm khi mentor nói rõ, và chỉ khi kết luận không phải CẦN SỬA.
3. Chỉ giữ ở đây, không đăng.
