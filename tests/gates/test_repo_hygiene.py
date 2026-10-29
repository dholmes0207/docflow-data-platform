"""Gate test: cấu trúc repo, tài liệu task và dữ liệu mẫu phải luôn nhất quán.

Các test này không cần database, chạy được ở mọi máy: `pytest tests/gates`.
Nếu một test đỏ, đọc thông báo lỗi: nó nói rõ file nào sai và cần sửa gì.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TASK_FILES = sorted((ROOT / "tasks").glob("week_*/task_*.md"))
OVERVIEW = ROOT / "roadmap" / "overview.md"
TRACKER = ROOT / "roadmap" / "weekly_tracker.md"
VALID_STATUSES = {"Chưa bắt đầu", "Đang thực hiện", "Sẵn sàng Review", "Hoàn thành"}

_spec = importlib.util.spec_from_file_location("check_forbidden_files", ROOT / "scripts" / "check_forbidden_files.py")
forbidden = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(forbidden)


def _task_id(task_file: Path) -> str:
    first_line = task_file.read_text(encoding="utf-8").splitlines()[0]
    match = re.match(r"# Task (\d+\.\d+):", first_line)
    assert match, f"{task_file.relative_to(ROOT)}: dòng đầu phải có dạng '# Task X.Y: <tên task>'"
    return match.group(1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tracker_rows() -> list[list[str]]:
    rows = []
    for line in TRACKER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[1].startswith("Task "):
            rows.append(cells)
    return rows


def test_no_forbidden_files_tracked() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_forbidden_files.py"), "--all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Có file bị cấm trong repo:\n{result.stderr}"


@pytest.mark.parametrize(
    ("path", "blocked"),
    [
        (".env", True),
        ("infra/.env", True),
        ("infra/.env.local", True),
        ("infra/.env.production", True),
        ("infra/.env.example", False),
        ("bao_cao.pdf", True),
        ("src/docflow/data.zip", True),
        ("sample_data/tenant_tech/hop_dong.docx", True),
        ("docs/erd.pdf", False),
        ("docs/slides/demo.PPTX", False),
        ("src/docflow/config.py", False),
    ],
)
def test_forbidden_file_rules(path: str, blocked: bool) -> None:
    assert bool(forbidden.violations(path)) == blocked, f"{path}: mong đợi {'bị chặn' if blocked else 'được phép'}"


def test_forbidden_file_size_limit(tmp_path: Path) -> None:
    big = tmp_path / "corpus.txt"
    big.write_bytes(b"x" * (forbidden.MAX_BYTES + 1))
    small = tmp_path / "ok.txt"
    small.write_bytes(b"x" * forbidden.MAX_BYTES)
    assert forbidden.violations(str(big)), "file lớn hơn 1 MB phải bị chặn"
    assert not forbidden.violations(str(small)), "file đúng 1 MB vẫn được phép"


@pytest.mark.parametrize("task_file", TASK_FILES, ids=lambda p: p.name)
def test_task_file_has_required_sections(task_file: Path) -> None:
    text = task_file.read_text(encoding="utf-8")
    for heading in ("Definition of Done", "MỨC 1", "MỨC 2"):
        assert heading in text, f"{task_file.name}: thiếu mục '{heading}'"
    assert text.count("<details>") == text.count("</details>"), (
        f"{task_file.name}: số thẻ <details> và </details> không khớp, phần gợi ý Mức 2 sẽ hiển thị sai"
    )


@pytest.mark.parametrize("task_file", TASK_FILES, ids=lambda p: p.name)
def test_task_is_linked_from_roadmap_and_tracked(task_file: Path) -> None:
    task_id = _task_id(task_file)
    relative_link = f"../tasks/{task_file.parent.name}/{task_file.name}"
    assert relative_link in OVERVIEW.read_text(encoding="utf-8"), (
        f"roadmap/overview.md chưa có link tới {relative_link}"
    )
    tracked_ids = [row[1] for row in _tracker_rows()]
    assert f"Task {task_id}" in tracked_ids, f"roadmap/weekly_tracker.md chưa có dòng cho Task {task_id}"


def test_tracker_rows_are_unique_and_statuses_valid() -> None:
    rows = _tracker_rows()
    assert rows, "Không đọc được dòng nào trong bảng tiến độ của weekly_tracker.md"
    task_ids = [row[1] for row in rows]
    duplicates = {t for t in task_ids if task_ids.count(t) > 1}
    assert not duplicates, f"weekly_tracker.md có task bị lặp: {sorted(duplicates)}"
    for row in rows:
        status = row[3].strip("`")
        assert status in VALID_STATUSES, (
            f"weekly_tracker.md, {row[1]}: trạng thái '{status}' không hợp lệ. "
            f"Chỉ dùng một trong: {sorted(VALID_STATUSES)}"
        )


def _repo_markdown_files() -> list[Path]:
    """File .md của repo: đã commit hoặc mới tạo, bỏ qua mọi thứ .gitignore loại (.venv, cache...)."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--deduplicate", "*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line for line in out.stdout.splitlines() if (ROOT / line).is_file()]


def test_relative_markdown_links_resolve() -> None:
    broken = []
    for md in _repo_markdown_files():
        for target in re.findall(r"\]\(([^)#\s]+)", md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (md.parent / target).exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")
    assert not broken, "Link tương đối bị hỏng:\n" + "\n".join(broken)


def test_env_example_covers_every_compose_variable() -> None:
    compose = (ROOT / "infra" / "docker-compose.yml").read_text(encoding="utf-8")
    used = set(re.findall(r"(?<!\$)\$\{(\w+)", compose))
    example = (ROOT / "infra" / ".env.example").read_text(encoding="utf-8")
    defined = set(re.findall(r"^(\w+)=", example, flags=re.MULTILINE))
    missing = used - defined
    assert not missing, f"infra/.env.example thiếu biến mà docker-compose.yml dùng: {sorted(missing)}"


def test_sample_data_edge_cases_intact() -> None:
    sample = ROOT / "sample_data"
    empty = sample / "tenant_retail" / "empty_document.txt"
    assert empty.exists() and empty.stat().st_size == 0, (
        "sample_data/tenant_retail/empty_document.txt phải tồn tại và rỗng 0 byte (bẫy file rỗng của Task 0.5)"
    )
    for tenant in ("tenant_retail", "tenant_tech"):
        docs = [f for f in (sample / tenant).iterdir() if f.is_file() and f.stat().st_size > 0]
        assert len(docs) >= 2, f"sample_data/{tenant} cần ít nhất 2 tài liệu có nội dung"

    updates = sorted((sample / "updates").rglob("*.*"))
    assert updates, "sample_data/updates/ cần ít nhất 1 tài liệu phiên bản mới (bẫy Versioning của Task 0.5)"
    for new_version in updates:
        original = sample / new_version.relative_to(sample / "updates")
        assert original.exists(), (
            f"{new_version.relative_to(ROOT)} không có bản gốc tương ứng ở {original.relative_to(ROOT)}"
        )
        assert _sha256(original) != _sha256(new_version), (
            f"{new_version.relative_to(ROOT)} có nội dung trùng bản gốc, không kiểm thử được Versioning"
        )
