#!/usr/bin/env python3
"""Kiểm tra quy ước Git của repo: tên nhánh, commit message, tiêu đề và mô tả Pull Request.

Ba cách chạy (quy ước đầy đủ: CONTRIBUTING.md, mục 2):
- Hook commit-msg của pre-commit, tự chạy mỗi lần `git commit`: `check_git_conventions.py <file commit message>`
- Thử tên nhánh trên máy: `check_git_conventions.py --branch "$(git branch --show-current)"`
- CI (job `hygiene`, chỉ trên Pull Request): `check_git_conventions.py --pr`, đọc các biến môi trường
  PR_BRANCH, PR_TITLE, PR_BODY, BASE_SHA, HEAD_SHA.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Nhánh của bot: không kiểm tra gì.
BOT_PREFIXES = ("release/tasks-", "dependabot/")
# Nhánh của mentor: không bắt buộc tên dạng sprint-XX/... và Closes #, vẫn kiểm tra commit + tiêu đề PR.
MENTOR_PREFIXES = ("claude/", "mentor/")

BRANCH_RE = re.compile(r"^sprint-\d{2}/(task-\d+\.\d+|fix|docs)-[a-z0-9]+(-[a-z0-9]+)*$")
COMMIT_TYPES = ("feat", "fix", "docs", "test", "refactor", "chore", "ci", "style", "perf", "build")
COMMIT_RE = re.compile(rf"^({'|'.join(COMMIT_TYPES)})(\([a-z0-9._/-]+\))?!?: \S.*$")
MAX_SUBJECT = 100
ISSUE_LINK_RE = re.compile(r"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#\d+\b", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Commit do Git tự sinh khi merge / revert: không bắt theo quy ước.
AUTO_SUBJECT_PREFIXES = ("Merge ", "Revert ")


def branch_error(branch: str) -> str | None:
    if branch.startswith(BOT_PREFIXES + MENTOR_PREFIXES) or BRANCH_RE.match(branch):
        return None
    return (
        f"Tên nhánh '{branch}' sai quy ước. Dạng đúng: sprint-XX/<loại>-<mô-tả>, trong đó XX là 2 chữ số, "
        "<loại> là task-X.Y, fix hoặc docs, mô tả viết thường không dấu, nối bằng gạch ngang. "
        "Ví dụ: sprint-01/task-0.0-git-workflow"
    )


def commit_subject_error(subject: str) -> str | None:
    if subject.startswith(AUTO_SUBJECT_PREFIXES):
        return None
    if not COMMIT_RE.match(subject):
        return (
            f"'{subject}' không theo Conventional Commits. Dạng đúng: <loại>(<phạm vi>): <mô tả>, "
            f"<loại> là một trong {', '.join(COMMIT_TYPES)}; phạm vi viết thường, có thể bỏ. "
            "Ví dụ: docs(git): thêm ghi chép về squash merge"
        )
    if len(subject) > MAX_SUBJECT:
        return f"'{subject[:40]}...' dài {len(subject)} ký tự, tối đa {MAX_SUBJECT} (nên giữ dưới 72)."
    return None


def issue_link_error(body: str) -> str | None:
    if ISSUE_LINK_RE.search(HTML_COMMENT_RE.sub("", body)):
        return None
    return (
        "Mô tả PR chưa liên kết issue. Thêm một dòng 'Closes #<số issue>' (ngoài phần chú thích <!-- -->) "
        "để issue tự đóng khi PR được merge."
    )


def pr_errors(branch: str, title: str, body: str, subjects: list[str]) -> list[str]:
    if branch.startswith(BOT_PREFIXES):
        return []
    errors = []
    if (err := branch_error(branch)) is not None:
        errors.append(err)
    if not branch.startswith(MENTOR_PREFIXES) and (err := issue_link_error(body)) is not None:
        errors.append(err)
    if (err := commit_subject_error(title)) is not None:
        errors.append(f"Tiêu đề PR (sẽ thành commit trên main khi squash merge): {err}")
    for subject in subjects:
        if (err := commit_subject_error(subject)) is not None:
            errors.append(f"Commit: {err}")
    return errors


def _commit_subjects(base: str, head: str) -> list[str]:
    result = subprocess.run(["git", "log", "--format=%s", f"{base}..{head}"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Không đọc được commit {base[:7]}..{head[:7]} (cần fetch-depth: 0):\n{result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def _subject_from_message_file(path: str) -> str:
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            return line.strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("message_file", nargs="?", help="file commit message (pre-commit truyền vào ở bước commit-msg)")
    parser.add_argument("--branch", help="chỉ kiểm tra một tên nhánh")
    parser.add_argument("--pr", action="store_true", help="kiểm tra Pull Request từ biến môi trường (dùng trong CI)")
    args = parser.parse_args()

    if args.pr:
        env = os.environ
        errors = pr_errors(
            env["PR_BRANCH"],
            env.get("PR_TITLE", ""),
            env.get("PR_BODY", ""),
            _commit_subjects(env["BASE_SHA"], env["HEAD_SHA"]),
        )
        hint = "Cách sửa từng lỗi: CONTRIBUTING.md mục 2 và Task 0.0 (Mức 2)."
    elif args.branch is not None:
        errors = [err] if (err := branch_error(args.branch)) else []
        hint = "Đổi tên nhánh: git branch -m <tên mới> (xem CONTRIBUTING.md mục 2)."
    elif args.message_file:
        errors = [err] if (err := commit_subject_error(_subject_from_message_file(args.message_file))) else []
        hint = "Commit chưa được tạo. Sửa dòng đầu của message rồi commit lại (CONTRIBUTING.md mục 2)."
    else:
        parser.error("cần một trong: <file commit message>, --branch <tên>, --pr")

    if errors:
        print("Sai quy ước Git:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(hint, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
