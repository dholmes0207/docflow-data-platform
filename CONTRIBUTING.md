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

## 2. Issue, nhánh, commit và Pull Request

Mọi bài làm đi qua cùng một vòng. [Task 0.0](tasks/week_01/task_00_git_github_workflow.md) cho bạn luyện trọn vòng này
ở Sprint 1.

1. **Issue:** mở issue bằng mẫu **"Bắt đầu một task"**, tự assign cho mình.
2. **Nhánh:** cập nhật `main` trên máy, rồi tạo nhánh mới **từ `main`** theo quy tắc đặt tên bên dưới.
3. **Commit:** nhỏ, mỗi commit một ý, message theo Conventional Commits.
4. **Pull Request:** tiêu đề theo Conventional Commits, mô tả theo mẫu, có dòng `Closes #<số issue>`.
5. **CI xanh** → đổi tracker thành `Sẵn sàng Review` → mentor review (mục 8).
6. **Mentor squash merge** → issue tự đóng → bạn đồng bộ `main`, xóa nhánh cũ, quay lại bước 1 cho task tiếp theo.

`main` được bảo vệ: không ai push thẳng lên được, PR cần CI xanh và mentor (`.github/CODEOWNERS`) duyệt mới merge được.

### Tên nhánh

Dạng `sprint-XX/<loại>-<mô-tả>`:

| `<loại>` | Dùng khi | Ví dụ |
|---|---|---|
| `task-X.Y` | Làm một task trong `tasks/` | `sprint-02/task-0.3-docker-compose` |
| `fix` | Sửa lỗi trong phần bài đã merge trước đó | `sprint-04/fix-minio-timeout` |
| `docs` | Chỉ sửa ghi chép, tracker, tài liệu của bạn | `sprint-03/docs-learning-log` |

- `XX` là số sprint **đang chạy**, luôn 2 chữ số (`sprint-01`, `sprint-10`).
- `<mô-tả>` 2–5 từ, chữ thường **không dấu**, chữ số, nối bằng một dấu gạch ngang. Không dấu cách, không `_`, không viết hoa.
- Một nhánh cho một issue. Nhánh sống ngắn: merge xong là xóa, task sau tạo nhánh mới.
- Các tiền tố `claude/`, `mentor/`, `release/tasks-` dành cho mentor và bot, bạn không dùng.
- Thử tên trước khi push: `python3 scripts/check_git_conventions.py --branch "$(git branch --show-current)"`.

### Issue

Có 3 mẫu, không mở issue trống:

| Mẫu | Khi nào |
|---|---|
| **Bắt đầu một task** (nhãn `task`) | Mỗi task một issue, mở khi bắt đầu làm. Chép DoD thành checklist, tick dần. Ghi chú tiến độ hoặc thay đổi kế hoạch bằng comment trong issue. |
| **Hỏi mentor / Bị tắc** (nhãn `question`) | Tắc quá 2 buổi, hoặc cần hỏi hướng làm. Ghi rõ đã thử gì và dán nguyên văn lỗi. Mở xong nhắn link cho mentor. |
| **Báo lỗi đề bài / gate test** (nhãn `bug`) | Đề bài mâu thuẫn, link hỏng, hoặc bạn tin một gate test kiểm tra sai (mục 6). |

Repo công khai: **không** dán mật khẩu, token hay nội dung file `.env` vào issue, PR hoặc bình luận.

### Commit message

Theo [Conventional Commits](https://www.conventionalcommits.org/): `<loại>(<phạm vi>): <mô tả ngắn>`, phạm vi viết
thường và có thể bỏ, mô tả bằng tiếng Việt, tối đa 100 ký tự (nên dưới 72).

| Loại | Dùng khi | Ví dụ |
|---|---|---|
| `feat` | Thêm chức năng | `feat(infra): thêm healthcheck cho minio` |
| `fix` | Sửa lỗi | `fix(ingest): bỏ qua file 0 byte thay vì dừng cả lô` |
| `docs` | Tài liệu, ghi chép, tracker | `docs(tracker): cập nhật tiến độ sprint 2` |
| `test` | Thêm hoặc sửa test của bạn | `test(chunking): kiểm tra overlap giữa 2 chunk` |
| `refactor` | Đổi cấu trúc code, không đổi hành vi | `refactor(minio): tách hàm tạo client` |
| `chore` | Việc lặt vặt: cấu hình, dependency | `chore: thêm .vscode vào .gitignore` |

Các loại `ci`, `style`, `perf`, `build` cũng hợp lệ. Commit do Git tự sinh khi merge (`Merge ...`) hoặc revert (`Revert ...`)
không bị kiểm tra. Hook `commit-msg` (mục 3) chặn message sai ngay trên máy; CI kiểm tra lại mọi commit của PR.

### Pull Request

- **Một PR cho một task** (một issue). Điền đầy đủ mẫu mô tả PR, đặc biệt mục **Bằng chứng theo Definition of Done**.
- **Tiêu đề PR** theo Conventional Commits, vì khi squash merge nó trở thành commit trên `main`.
- **Mô tả PR** có `Closes #<số issue>` để issue tự đóng khi merge. Sửa tiêu đề hoặc mô tả thì CI tự chạy lại.
- **Sửa theo review:** push thêm commit lên **cùng nhánh** (PR tự cập nhật), không mở PR mới. Trả lời từng thread góp ý,
  rồi bấm **Re-request review**.
- **Merge:** PR của bạn được mentor merge bằng **squash merge**. Sau đó Git trên máy bạn sẽ báo nhánh cũ "not fully merged";
  kiểm tra PR đã merged trên GitHub rồi mới xóa nhánh.
- Chỉ sửa lịch sử (`commit --amend`, `rebase -i`, `push --force-with-lease`) trên **nhánh của chính bạn**, không bao giờ trên `main`.

Bước "Quy ước Git" trong check `hygiene` kiểm tra tên nhánh, tiêu đề PR, mọi commit của PR và dòng `Closes #`.

---

## 3. Cài đặt một lần trên máy bạn

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install          # từ giờ mỗi lần git commit sẽ tự chạy kiểm tra
```

`pre-commit install` cài 2 hook: **pre-commit** (kiểm tra file sắp commit) và **commit-msg** (kiểm tra commit message).

Nếu một hook báo `Failed` và tự sửa file (ví dụ `ruff format`), chỉ cần `git add` lại rồi commit lần nữa.

---

## 4. Kiểm tra tự động (CI)

CI có 4 check. Cả 4 phải **xanh** thì PR mới được merge.

| Check | Kiểm tra gì | Chạy thử trên máy |
|---|---|---|
| `hygiene` | File bị cấm, ruff lint/format, `docker-compose.yml` hợp lệ, tài liệu task có đủ mục, mọi task có trong roadmap và tracker, trạng thái tracker hợp lệ, link tương đối không hỏng, `.env.example` đủ biến, dữ liệu mẫu còn nguyên các bẫy, lịch task bị khóa; **quy ước Git** của PR (tên nhánh, tiêu đề, commit, `Closes #`) | `pytest tests/gates` (không cần database); quy ước Git: hook `commit-msg` và lệnh thử tên nhánh ở mục 2 |
| `schema` | Chạy `infra/sql/init.sql` (và `db/schema.sql` của bạn từ Task 0.4) 2 lần trên Postgres + pgvector, rồi thử ghi dữ liệu sai (chunk sai tenant, chunk trùng, 2 phiên bản cùng hiệu lực...) và khẳng định database từ chối | Xem bên dưới |
| `unit` | Unit test của chính bạn (từ Task 1.0): cài dự án theo `pyproject.toml` rồi chạy mọi test trong `tests/` trừ `tests/gates/`. Job có sẵn PostgreSQL + pgvector (biến `DATABASE_URL`, quyền quản trị) cho test tích hợp từ Task 1.5. Chưa có `pyproject.toml` thì bỏ qua; đã có mà không có test nào thì đỏ | `pytest tests --ignore=tests/gates` |
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

- **Không sửa, xóa, hay `skip` gate test để CI xanh.** Nếu bạn tin một gate test sai, mở issue mẫu
  **"Báo lỗi đề bài / gate test"** hoặc ghi rõ lý do trong mô tả PR. Mentor sẽ quyết định và tự sửa test nếu cần.
- Khi test đỏ, đọc kỹ thông báo lỗi: thông báo nói rõ file nào sai và cần sửa gì.
- Code của bạn đặt trong `src/docflow/`, test của bạn đặt trong `tests/unit/` (Task 1.0), không đặt trong `tests/gates/`.

---

## 7. Task bị khóa (🔒)

Task của các sprint sau được viết trước nhưng lưu ở dạng mã hóa trong `tasks/_locked/`, theo lịch ở
`tasks/release_schedule.toml`. Mỗi sprint mở vào thứ Hai, 1 tuần trước khi sprint đó bắt đầu (roadmap ghi rõ ngày).
Không sửa, xóa hay đổi tên các file trong `tasks/_locked/` và file lịch: CI (`hygiene`) sẽ báo đỏ.

## 8. Quy trình review mỗi sprint (2 tuần)

1. Mở issue → làm task trên nhánh riêng → mở PR có `Closes #<số issue>` → điền mẫu mô tả PR (mục 2).
2. Đợi CI xanh. CI đỏ thì tự sửa trước, mentor chưa review PR đỏ.
3. Đổi trạng thái task trong `roadmap/weekly_tracker.md` thành `Sẵn sàng Review` và dán link PR.
4. Cuối sprint, mentor chạy `/review-week <số PR>`. Ngoài CI, bước này chạy bộ test trên chính phần bài bạn nộp
   và đối chiếu từng tiêu chí Definition of Done của task. Kết quả là một trong 3 mức:
   - **ĐẠT:** mentor merge PR, trạng thái task thành `Hoàn thành`.
   - **ĐẠT KÈM GHI CHÚ:** được merge; các ghi chú nên làm ở sprint sau.
   - **CẦN SỬA:** sửa theo danh sách góp ý, push thêm commit lên cùng nhánh, CI và review chạy lại.
5. Trong buổi review, bạn demo và trả lời các câu hỏi tư duy; mentor ghi nhận vào cột
   **Đánh Giá & Góp Ý Của Reviewer** của tracker.
