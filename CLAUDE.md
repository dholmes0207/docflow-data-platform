# CLAUDE.md

Repo đào tạo Data Engineering "DocFlow": nền tảng dữ liệu cho trợ lý AI đa doanh nghiệp (multi-tenant RAG).
Mentor là chủ repo (`@dholmes0207`); học viên là AZIST (`@thanhtrido12`), có quyền Write, làm bài theo `tasks/` trên
Windows + WSL2 Ubuntu 24.04 (Python 3.12), nộp qua Pull Request cuối mỗi sprint (2 tuần, lịch 02/11/2026 – 30/05/2027).

## Quy tắc bắt buộc

- Viết tài liệu, commit message phần mô tả, bình luận PR bằng **tiếng Việt**; xưng "bạn" với học viên.
- **Không** thêm dòng `Co-Authored-By: Claude...`, `Claude-Session: ...` vào commit message, và **không** thêm
  chữ ký "Generated with Claude Code" vào mô tả PR hay bình luận. Commit dùng danh tính git của người dùng.
- Không push thẳng `main`: làm trên nhánh, mở PR. Commit theo Conventional Commits.
- **Không sửa, xóa hay `skip` test trong `tests/gates/` để CI xanh.** Chỉ sửa gate test khi mentor yêu cầu rõ.
- Tài liệu task giữ cấu trúc: Definition of Done → Mức 1 (định hướng tự học) → Mức 2 (gợi ý trong `<details>`).
  Gợi ý luồng tư duy và từ khóa tra cứu, **không** đưa lời giải chép được.

## Lệnh

```bash
pip install -r requirements-dev.txt     # pytest, psycopg, ruff (ghim bản), pre-commit
ruff check . && ruff format --check .
pytest tests/gates                      # test schema bị skip nếu thiếu DATABASE_URL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres REQUIRE_DB=1 pytest tests/gates
pre-commit run --all-files
```

## Bản đồ

- `tasks/week_XX/`: đề bài từng task; thư mục `week_XX` tương ứng **Sprint XX** (sprint 2 tuần, lịch trong `roadmap/overview.md`). Thêm task mới thì phải thêm cả link trong `roadmap/overview.md` và
  dòng trong `roadmap/weekly_tracker.md` (gate test kiểm tra điều này).
- `infra/`: hạ tầng mẫu (Docker Compose đọc mật khẩu từ `infra/.env`, schema `infra/sql/init.sql`).
- `sample_data/`: dữ liệu mẫu có chủ đích chứa bẫy (file rỗng, tài liệu 2 phiên bản trong `updates/`).
- `tests/gates/`: gate test do mentor đặt ra; CI (`.github/workflows/ci.yml`) chạy 4 check
  `hygiene`, `schema`, `unit` (test của học viên trong `tests/unit/`, code trong `src/docflow/`), `secrets`.
- Quy tắc làm việc đầy đủ: `CONTRIBUTING.md`. Review PR học viên: skill `/review-week`
  (`.claude/skills/review-week/SKILL.md`).
