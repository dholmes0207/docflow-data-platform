# Quy Tắc Làm Việc Trên Repo DocFlow

Tài liệu này là "luật chơi" chung giữa bạn (học viên) và người hướng dẫn (mentor). Phần lớn các quy tắc
dưới đây **được máy kiểm tra tự động**, không phụ thuộc vào trí nhớ của ai.

---

## 1. Ba lớp kiểm tra

| Lớp | Chạy ở đâu | Chạy khi nào | Kiểm tra gì |
|---|---|---|---|
| **pre-commit** | Máy của bạn | Mỗi lần `git commit` | Lộ mật khẩu/API key, file bị cấm, lint & format Python |
| **CI** (GitHub Actions) | GitHub | Mỗi lần push lên một Pull Request | Mọi thứ của pre-commit + gate test cấu trúc repo + chạy schema trên Postgres thật + unit test của bạn |
| **Review** (`/review-week`) | Máy mentor (Claude Code) | Khi mentor review PR | CI + chạy bộ test trên chính bài nộp + đối chiếu từng tiêu chí DoD của task |

---

## 2. Nhánh, commit và Pull Request

- **Không push thẳng lên `main`.** Nhánh `main` được bảo vệ: mọi thay đổi phải đi qua Pull Request (PR)
  và chỉ mentor được duyệt (approve) và merge (xem `.github/CODEOWNERS`).
- **Tên nhánh:** `sprint-XX/task-X.Y-mo-ta-ngan`, ví dụ `sprint-02/task-0.3-docker-compose`.
- **Commit message:** theo dạng [Conventional Commits](https://www.conventionalcommits.org/):
  `<loại>(<phạm vi>): <mô tả ngắn>`, ví dụ `feat(infra): thêm healthcheck cho minio`,
  `docs(tracker): cập nhật tiến độ tuần 2`. Các loại hay dùng: `feat`, `fix`, `docs`, `test`, `chore`.
- **Mỗi PR gói gọn 1 task** (hoặc các task nhỏ cùng một sprint). Điền đầy đủ mẫu mô tả PR tự hiện ra
  khi tạo PR, đặc biệt mục **Bằng chứng theo Definition of Done**.

---

## 3. Cài đặt một lần trên máy bạn

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install          # từ giờ mỗi lần git commit sẽ tự chạy kiểm tra
```

Nếu một hook báo `Failed` và tự sửa file (ví dụ `ruff format`), chỉ cần `git add` lại rồi commit lần nữa.

---

## 4. Kiểm tra tự động (CI)

CI có 4 check. Cả 4 phải **xanh** thì PR mới được merge.

| Check | Kiểm tra gì | Chạy thử trên máy |
|---|---|---|
| `hygiene` | File bị cấm, ruff lint/format, `docker-compose.yml` hợp lệ, tài liệu task có đủ mục, mọi task có trong roadmap và tracker, trạng thái tracker hợp lệ, link tương đối không hỏng, `.env.example` đủ biến, dữ liệu mẫu còn nguyên các bẫy | `pytest tests/gates/test_repo_hygiene.py` |
| `schema` | Chạy `infra/sql/init.sql` (và `db/schema.sql` của bạn từ Task 0.4) 2 lần trên Postgres + pgvector, rồi thử ghi dữ liệu sai (chunk sai tenant, chunk trùng, 2 phiên bản cùng hiệu lực...) và khẳng định database từ chối | Xem bên dưới |
| `unit` | Unit test của chính bạn (từ Task 1.0): cài dự án theo `pyproject.toml` rồi chạy mọi test trong `tests/` trừ `tests/gates/`. Chưa có `pyproject.toml` thì bỏ qua; đã có mà không có test nào thì đỏ | `pytest tests --ignore=tests/gates` |
| `secrets` | Quét mật khẩu / API key / token trong toàn bộ lịch sử Git (gitleaks) | `pre-commit run gitleaks --all-files` |

Chạy test schema trên máy (cần cụm Docker Compose của Task 0.3 đang chạy):

```bash
DATABASE_URL=postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@localhost:5432/<POSTGRES_DB> \
  pytest tests/gates/test_schema_constraints.py
```

Không đặt `DATABASE_URL` thì các test schema được **bỏ qua** (skip) trên máy bạn. Trên CI thì không:
thiếu database là CI đỏ.

---

## 5. File bị cấm

Script `scripts/check_forbidden_files.py` (chạy trong cả pre-commit và CI) chặn:

1. **File môi trường chứa mật khẩu thật:** `.env`, `.env.local`, ... Chỉ commit `.env.example` (giá trị mẫu).
2. **Tài liệu văn phòng, file nén, file chạy** (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.zip`, `.exe`, ...) nằm
   ngoài thư mục `docs/`. Tài liệu không liên quan đến dự án thì không commit vào repo này.
3. **File lớn hơn 1 MB** ở bất kỳ đâu. Dữ liệu lớn để trong MinIO, không để trong Git.

---

## 6. Gate test (`tests/gates/`)

Gate test là "hàng rào" do mentor đặt ra để giữ repo luôn đúng. Quy tắc:

- **Không sửa, xóa, hay `skip` gate test để CI xanh.** Nếu bạn tin một gate test sai, ghi rõ lý do trong
  mô tả PR. Mentor sẽ quyết định và tự sửa test nếu cần.
- Khi test đỏ, đọc kỹ thông báo lỗi: thông báo nói rõ file nào sai và cần sửa gì.
- Code của bạn đặt trong `src/docflow/`, test của bạn đặt trong `tests/unit/` (Task 1.0), không đặt trong `tests/gates/`.

---

## 7. Task bị khóa (🔒)

Task của các sprint sau được viết trước nhưng lưu ở dạng mã hóa trong `tasks/_locked/`, theo lịch ở
`tasks/release_schedule.toml`. Mỗi sprint mở vào thứ Hai, 1 tuần trước khi sprint đó bắt đầu (roadmap ghi rõ ngày).
Không sửa, xóa hay đổi tên các file trong `tasks/_locked/` và file lịch: CI (`hygiene`) sẽ báo đỏ.

## 8. Quy trình review mỗi sprint (2 tuần)

1. Làm task trên nhánh riêng → mở PR → điền mẫu mô tả PR.
2. Đợi CI xanh. CI đỏ thì tự sửa trước, mentor chưa review PR đỏ.
3. Đổi trạng thái task trong `roadmap/weekly_tracker.md` thành `Sẵn sàng Review` và dán link PR.
4. Cuối sprint, mentor chạy `/review-week <số PR>`. Ngoài CI, bước này chạy bộ test trên chính phần bài bạn nộp
   và đối chiếu từng tiêu chí Definition of Done của task. Kết quả là một trong 3 mức:
   - **ĐẠT:** mentor merge PR, trạng thái task thành `Hoàn thành`.
   - **ĐẠT KÈM GHI CHÚ:** được merge; các ghi chú nên làm ở sprint sau.
   - **CẦN SỬA:** sửa theo danh sách góp ý, push thêm commit lên cùng nhánh, CI và review chạy lại.
5. Trong buổi review, bạn demo và trả lời các câu hỏi tư duy; mentor ghi nhận vào cột
   **Đánh Giá & Góp Ý Của Reviewer** của tracker.
