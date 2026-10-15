#!/usr/bin/env python3
"""Chặn những file không được phép nằm trong repo.

Dùng ở 2 nơi:
- pre-commit: kiểm tra các file đang được commit (pre-commit truyền danh sách file vào).
- CI / pytest: `python scripts/check_forbidden_files.py --all` kiểm tra toàn bộ file Git đang theo dõi.

Quy tắc (xem CONTRIBUTING.md, mục "File bị cấm"):
1. File môi trường chứa mật khẩu thật (`.env`, `.env.local`, ...). Chỉ cho phép `.env.example`.
2. Tài liệu văn phòng / file nén / file chạy (`.pdf`, `.docx`, `.zip`, ...) nằm ngoài thư mục `docs/`.
3. File lớn hơn 1 MB ở bất kỳ đâu.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath

MAX_BYTES = 1024 * 1024
BINARY_DOC_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".exe",
    ".msi",
}
ALLOWED_DOC_DIR = "docs"


def violations(path_str: str) -> list[str]:
    path = PurePosixPath(path_str.replace("\\", "/"))
    name = path.name
    problems: list[str] = []

    if (name == ".env" or name.startswith(".env.")) and name != ".env.example":
        problems.append("file môi trường chứa mật khẩu thật, chỉ được commit `.env.example`")

    if path.suffix.lower() in BINARY_DOC_EXTENSIONS and path.parts[0] != ALLOWED_DOC_DIR:
        problems.append(
            f"đuôi `{path.suffix}` chỉ được đặt trong `{ALLOWED_DOC_DIR}/` "
            "(tài liệu không liên quan dự án thì không commit)"
        )

    file_on_disk = Path(path_str)
    if file_on_disk.is_file() and file_on_disk.stat().st_size > MAX_BYTES:
        size_mb = file_on_disk.stat().st_size / MAX_BYTES
        problems.append(f"file nặng {size_mb:.1f} MB, vượt giới hạn 1 MB")

    return problems


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def main(argv: list[str]) -> int:
    files = tracked_files() if argv == ["--all"] else argv
    failed = False
    for f in files:
        for problem in violations(f):
            print(f"BỊ CHẶN: {f}: {problem}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
