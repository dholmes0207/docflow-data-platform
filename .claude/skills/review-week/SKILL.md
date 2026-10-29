---
name: review-week
description: Review Pull Request cuối mỗi sprint của học viên DocFlow. Kiểm tra CI, chạy gate test và các phép thử bổ sung trên chính phần bài nộp, đối chiếu từng tiêu chí Definition of Done của task, rồi soạn kết luận review. Dùng khi mentor gõ /review-week <số PR>, hoặc nhờ review / chấm PR của học viên.
---

# Review PR cuối sprint của học viên

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
   Đọc cả issue mà PR đóng (`Closes #N`): nhãn, người được assign, checklist DoD đã tick.
2. Xác định **task** từ mục "Sprint / Task" trong mô tả PR. Không ghi rõ thì suy ra từ file thay đổi và nói rõ
   là suy ra.
3. Đọc file task tương ứng trong `tasks/week_XX/` (thư mục `week_XX` = Sprint XX), lấy danh sách tiêu chí **Definition of Done** và
   **Câu hỏi tư duy**.

## Bước 2: Cổng CI

Đọc trạng thái 4 check `hygiene`, `schema`, `unit`, `secrets` trên commit mới nhất của PR.

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
| 0.0 (Quy trình Git) | Issue mà PR đóng: tạo bằng mẫu "Bắt đầu một task" (nhãn `task`), assign cho học viên, có checklist DoD. Nhánh tạo từ `main` gần nhất: `git merge-base origin/main review/pr-<PR>` trùng hoặc rất gần đỉnh `main`, `git diff --stat origin/main...review/pr-<PR>` chỉ chứa file của task. `git log --format='%an <%ae> %s' origin/main..review/pr-<PR>`: ≥ 3 commit, mỗi commit một ý (đọc `git show --stat` từng commit), email không phải email cá nhân lộ ra ngoài ý muốn, commit gắn được với tài khoản GitHub (trường `author.login` của commit qua API không rỗng). `docs/git_cheatsheet.md`: ≥ 12 lệnh viết bằng lời của học viên, có mục "Lỗi đã gặp", mục xung đột có dán nguyên văn 3 dấu `<<<<<<<` / `=======` / `>>>>>>>`, có thông báo bị từ chối push `main`. SSH (DoD 1): không kiểm chứng được từ repo → **CẦN DEMO** `ssh -T git@github.com` và `git remote -v`. DoD 8: **luôn** để lại ít nhất 1 góp ý cần sửa ở vòng đầu (kể cả khi bài tốt), vì vòng review là một tiêu chí. DoD 9: kiểm tra ở PR kế tiếp: nhánh Task 0.0 không còn trên GitHub, nhánh mới tạo từ `main` sau squash merge. |
| 0.1, 0.2 (môi trường máy học viên) | Không kiểm chứng được từ repo. Dựa vào ảnh chụp / output lệnh trong mô tả PR; tiêu chí nào thiếu bằng chứng thì đánh dấu **CẦN DEMO**. |
| 0.3 (Docker Compose) | Tìm file compose học viên nộp. `cp <thư mục>/.env.example <thư mục>/.env` (nếu có) rồi `docker compose -f <file> config --quiet`. Soát: 2 service `postgres` + `minio`, named volumes cho cả 2 (DoD 5), cổng 9000 + 9001 + 5432 chỉ mở cho `127.0.0.1` (không mở ra cả mạng), mật khẩu **không** ghi cứng trong YAML. |
| 0.4 (Data Modeling) | CI check `schema` đã tự chạy bộ gate test lên `db/schema.sql`, nên chỉ cần đọc kết quả. Nếu đỏ thì liệt kê đúng tình huống dữ liệu sai chưa bị chặn (tên test), **không** gợi ý cú pháp SQL để sửa. Soát thêm: `docs/erd.md` (DoD 1) và `docs/schema_decisions.md` (DoD 5) giải thích được **từng** ràng buộc, không chỉ liệt kê. Chống sao chép: `diff <(grep -v '^ *--' db/schema.sql) <(grep -v '^ *--' infra/sql/init.sql)`. Nếu gần như trùng khớp hoặc chỉ khác comment, đánh dấu **CẦN DEMO** và chuẩn bị 2–3 câu hỏi buộc học viên giải thích lại bằng lời (ví dụ: vì sao khóa ngoại phải gồm cả `tenant_id`, vì sao cần partial index thay vì UNIQUE thường). |
| 0.5 (Mock Data) | ≥ 2 tenant, mỗi tenant 2–3 tài liệu có nội dung; có file rỗng 0 byte; có tài liệu 2 phiên bản với mã băm khác nhau; có 3–5 câu hỏi kiểm thử kèm đáp án, trong đó ≥ 1 câu bẫy rò rỉ giữa các tenant. |
| 0.6 (Mở rộng corpus) | Đếm tài liệu và số từ theo từng tenant; kiểm tra có ≥ 2 cấp tiêu đề. Xác nhận bẫy làm sạch còn nguyên **trong repo**, không chỉ trên máy học viên: tìm byte BOM (`EF BB BF`), CRLF, ký tự U+200B, và chuỗi NFD (`unicodedata.is_normalized('NFC', s)` trả `False`). Với file câu hỏi: ≥ 20 câu, đủ số câu `leak` / `no_answer`, và viết script nhỏ xác nhận mọi `source_quote` thật sự có trong `source_file`. |
| 1.0 (Khung dự án) | Clone sạch sang thư mục tạm, tạo venv mới, `pip install -e .` rồi `python -c "import docflow"` từ thư mục khác. Xóa một biến bắt buộc khỏi môi trường và chạy: phải báo lỗi rõ ràng ngay lúc khởi động. Soát code: không có `print` thay log, không có DSN hay mật khẩu ghi cứng (`grep -rn "localhost\|password" src/`). |
| 1.1 (Client MinIO) | Đưa vào hàm phân loại object của học viên các key xấu: file ở gốc bucket, `../`, tenant viết hoa, tenant lạ, file 0 byte, đuôi `.pdf`. Mỗi key phải bị loại kèm lý do và không làm dừng cả lần quét. Có MinIO thì chạy thật trên bucket `raw-documents`. |
| 1.2 (Làm sạch văn bản) | Chạy hàm làm sạch trên toàn bộ corpus Task 0.6, kiểm tra 3 tính chất: kết quả ở dạng NFC; `clean(clean(x)) == clean(x)`; số dòng tiêu đề Markdown trước và sau làm sạch bằng nhau. Thử thêm một file không phải UTF-8: phải bị bỏ qua có log, không làm dừng cả lô. |
| 1.3 (Chunking) | Chạy hàm chunking của học viên trên toàn bộ corpus và tự kiểm các tính chất, không chỉ tin vào test của học viên: `text[char_start:char_end] == content` với mọi chunk; `chunk_index` liên tục từ 0; không chunk rỗng; chạy 2 lần cho kết quả giống hệt; tỷ lệ overlap thực tế nằm trong 15–20%; ranh giới chunk không rơi giữa một từ; mọi chunk có đường dẫn tiêu đề. Hỏi học viên chunk dài nhất ứng với bao nhiêu token của mô hình dự kiến dùng. Đọc `docs/chunking.md`: phần so sánh 2 cấu hình phải dựa trên đoạn văn cụ thể, không viết chung chung. |
| 1.4 (Idempotent) | Tự dựng kịch bản bằng bản in-memory của học viên: chạy lập kế hoạch 2 lần liên tiếp thì lần 2 phải toàn `UNCHANGED`; thay file bằng bản trong `sample_data/updates/` thì đúng 1 `CHANGED` với version 2; file chỉ đổi CRLF/NFD vẫn `UNCHANGED`; cùng đường dẫn ở 2 tenant không ảnh hưởng nhau. Kiểm tra mã băm là chuỗi hex 64 ký tự thường. Kiểm tra hàm lập kế hoạch **không** import thư viện database (tách quyết định khỏi thực thi, DoD 4). |
| 1.5 (Ghi DB & role) | Đăng nhập bằng `docflow_app` và tự thử: `DROP TABLE`, `ALTER TABLE`, `CREATE TABLE` phải bị từ chối; `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'docflow_app'` phải là `false, false`; `docflow_app` không sở hữu bảng nào (`pg_tables.tableowner`). `git diff` hàm lập kế hoạch của Task 1.4 phải rỗng. Chạy pipeline 2 lần, đếm số dòng 2 bảng: lần 2 không tăng. Tìm SQL ghép chuỗi: `grep -rn 'execute(f' src/`. Không có mật khẩu trong file `.sql` đã commit. |
| 1.6 (SCD2) | Chạy migration 2 lần liên tiếp: lần 2 không lỗi, không chạy lặp. Thử ghi `valid_to` khi `is_active = TRUE`, hoặc `valid_to <= valid_from`: database phải từ chối. Sau khi đổi tài liệu bằng bản trong `sample_data/updates/`: `valid_to` của bản cũ **bằng đúng** `valid_from` của bản mới; truy vấn as-of tại đúng mốc đó trả phiên bản mới. Chạy test tranh chấp của học viên vài lần liên tiếp, không được lúc đỏ lúc xanh. |
| 2.1 (Embedding) | Đọc code: mô hình là một trong hai mô hình đa ngôn ngữ của roadmap, **có ghim revision**, nạp một lần, encode theo lô, có chuẩn hóa. Nếu dùng `multilingual-e5-small`: kiểm tra có tiền tố `query: ` / `passage: ` đúng chỗ, vì quên tiền tố không báo lỗi mà chỉ làm kết quả kém. Chạy `pytest` không bật cờ mô hình thật: phải xanh, không tải gì từ mạng. Đọc báo cáo số chunk vượt giới hạn token: nếu nhiều, yêu cầu quay lại chỉnh Task 1.3. Thử tự 1–2 cặp câu hỏi / đoạn văn để xác nhận test ngữ nghĩa của học viên không phải chọn ví dụ "dễ". |
| 2.2 (Vector & cache) | Chạy bước điền embedding 2 lần liên tiếp, lần 2 phải 0 lần gọi mô hình. Đổi tài liệu bằng bản trong `sample_data/updates/` rồi chạy lại: số lần gọi phải bằng số chunk có nội dung mới. Kiểm tra khóa cache gồm cả **mô hình + revision**: đổi tên mô hình trong cấu hình, vector cũ không được dùng lại. Chạy câu SQL tìm kiếm của học viên: phải có điều kiện `tenant_id`. Hỏi câu tư duy về bộ nhớ đệm dùng chung giữa các tenant. |
| 2.3 (Tìm kiếm theo tenant) | Gọi `search` với `tenant_id` rỗng / `None` / tenant lạ: phải báo lỗi, không được trả kết quả của mọi tenant. Tự chèn một chunk có nội dung giống hệt ở tenant khác rồi tìm đúng nội dung đó: kết quả chỉ được thuộc tenant đang hỏi. Đổi tài liệu bằng bản trong `sample_data/updates/` rồi tìm lại: không còn chunk của phiên bản cũ. Chạy lại kịch bản "ít hơn `top_k`" của học viên **2 lần**: trước khi sửa phải thiếu kết quả, sau khi sửa phải đủ `min(top_k, số chunk)`, và cho cùng kết quả mỗi lần. Nếu dùng quét lặp `relaxed_order`: kiểm tra kết quả cuối vẫn đúng thứ tự khoảng cách. `grep -rn 'execute(f' src/`. Đọc `EXPLAIN` trong `docs/search.md`: có thật sự đo trên dữ liệu đủ lớn để index được dùng không. |
| 2.4 (Đo Recall@k) | Tự tính tay `Recall@k` và `MRR` cho 2–3 câu hỏi từ output thô của học viên, so với bảng trong `docs/retrieval_eval.md`. Chạy script đánh giá 2 lần: kết quả phải giống hệt. Đổi kích thước chunk trong cấu hình rồi chạy lại: script vẫn chạy được, không cần sửa bộ câu hỏi (định nghĩa "trúng" không phụ thuộc `chunk_id`). `EXPLAIN` một câu Full-Text Search: phải dùng index GIN. Thử câu hỏi gõ không dấu: vẫn khớp tài liệu có dấu. Soát ngưỡng "không tìm thấy": đọc từ cấu hình, có báo cáo cả số câu `normal` bị từ chối oan, và học viên có nhận ra rủi ro chọn ngưỡng trên chính bộ câu hỏi dùng để báo cáo. |
| Task chưa có trong bảng | Tự thiết kế 2–3 phép thử chạy được, bám sát từng tiêu chí DoD của task. Ghi rõ đã chạy lệnh gì. |

Làm xong thì dọn: `git worktree remove ../review-pr-<PR> && git branch -D review/pr-<PR>`.

## Bước 4: Quy trình

CI (bước "Quy ước Git" của `hygiene`) đã kiểm tra tên nhánh, tiêu đề PR, commit message và dòng `Closes #`. Ở đây chỉ soát
những gì máy không bắt được:

- Nhánh bắt đầu bằng `sprint-`: học viên **không** dùng tiền tố của mentor/bot (`claude/`, `mentor/`, `release/tasks-`)
  để né kiểm tra. Có thì nêu thành mục riêng.
- Issue được đóng là đúng issue của task này, checklist DoD trong issue khớp với những gì PR thực sự làm.
- Commit có **nội dung** đúng với message (không phải `fix: sửa` cho một commit đổi 20 file), mỗi commit một ý.
- PR chỉ chứa thay đổi của một task, nhánh tạo từ `main` mới (không kéo theo file của task trước).
- `roadmap/weekly_tracker.md` đã đổi trạng thái task thành `Sẵn sàng Review` và có link PR chưa.
- Mô tả PR có điền đủ các mục của mẫu không.
- Từ vòng review thứ 2: học viên đã trả lời từng thread góp ý và sửa trên cùng nhánh, không mở PR mới.

Lỗi quy trình chỉ là **ghi chú**, không tự nó làm bài thành CẦN SỬA, trừ khi lặp lại sau khi đã được nhắc.

## Bước 5: Kết luận

Chọn đúng một mức:
- **ĐẠT:** CI xanh và mọi tiêu chí DoD có bằng chứng.
- **ĐẠT KÈM GHI CHÚ:** CI xanh, DoD đạt, còn góp ý không chặn (chất lượng, quy trình).
- **CẦN SỬA:** CI đỏ, hoặc có tiêu chí DoD chưa đạt, hoặc chạm vào gate test.

Trình bày cho mentor theo đúng khung sau:

```markdown
## Kết luận review PR #<số>: <ĐẠT | ĐẠT KÈM GHI CHÚ | CẦN SỬA>
Task: <X.Y> · Commit: <sha ngắn> · CI: hygiene <✅/❌> · schema <✅/❌> · unit <✅/❌> · secrets <✅/❌>

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
2. Approve và merge bằng **squash merge** (tiêu đề PR thành commit trên `main`). Chỉ làm khi mentor nói rõ, và chỉ khi
   kết luận không phải CẦN SỬA.
3. Với ĐẠT KÈM GHI CHÚ: mở issue `[Góp ý PR #<số>] ...` liệt kê các góp ý không chặn để học viên làm ở sprint sau.
   Chỉ làm khi mentor nói rõ.
4. Chỉ giữ ở đây, không đăng.
