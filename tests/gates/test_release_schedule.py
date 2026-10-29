"""Gate test: lịch phát hành task (tasks/release_schedule.toml) luôn nhất quán với repo.

Mỗi task trong lịch phải ở đúng 1 trong 2 trạng thái:
- đã mở: có file task đọc được, roadmap có link tới nó;
- đang khóa: chỉ có bản mã hóa trong tasks/_locked/, roadmap hiện dòng 🔒 kèm ngày mở.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("task_release", ROOT / "scripts" / "task_release.py")
task_release = importlib.util.module_from_spec(_spec)
sys.modules["task_release"] = task_release  # dataclass cần module đã được đăng ký
_spec.loader.exec_module(task_release)

TASKS = task_release.load_tasks()
ROADMAP_TEXT = (ROOT / "roadmap" / "overview.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("task", TASKS, ids=lambda t: f"task_{t.id}")
def test_task_is_either_released_or_locked(task) -> None:
    assert task.plain.exists() != task.is_locked, (
        f"Task {task.id}: phải có đúng 1 trong 2 file: {task.path} (đã mở) hoặc "
        f"{task.locked.relative_to(ROOT)} (đang khóa). Dùng scripts/task_release.py để khóa/mở, đừng sửa tay."
    )


@pytest.mark.parametrize("task", TASKS, ids=lambda t: f"task_{t.id}")
def test_roadmap_line_matches_state(task) -> None:
    expected, unexpected = (
        (task.locked_line, task.released_line) if task.is_locked else (task.released_line, task.locked_line)
    )
    assert ROADMAP_TEXT.count(expected) == 1, f"roadmap/overview.md phải có đúng 1 dòng:\n  {expected}"
    assert unexpected not in ROADMAP_TEXT, f"roadmap/overview.md còn sót dòng:\n  {unexpected}"


def test_release_dates_are_mondays() -> None:
    for task in TASKS:
        assert task.release.weekday() == 0, (
            f"Task {task.id}: ngày mở {task.release:%d/%m/%Y} không phải thứ Hai (workflow chỉ chạy thứ Hai)"
        )


def test_public_key_present_when_anything_is_locked() -> None:
    if any(t.is_locked for t in TASKS):
        recipients = (ROOT / "tasks" / "_locked" / "recipients.txt").read_text(encoding="utf-8")
        assert any(line.startswith("age1") for line in recipients.splitlines()), (
            "tasks/_locked/recipients.txt phải chứa khóa công khai age1..."
        )


def test_no_secret_key_committed() -> None:
    for path in (ROOT / "tasks").rglob("*"):
        if path.is_file() and path.suffix in {".txt", ".key", ".toml", ".md"}:
            assert "AGE-SECRET-KEY-" not in path.read_text(encoding="utf-8", errors="ignore"), (
                f"{path.relative_to(ROOT)} chứa khóa BÍ MẬT. Khóa bí mật chỉ được đặt trong GitHub secret."
            )


@pytest.mark.parametrize("command", ["lock", "release"])
def test_mismatched_roadmap_title_changes_nothing(tmp_path: Path, command: str) -> None:
    """Title trong lịch lệch với roadmap: script phải dừng trước khi mã hóa, giải mã hay xóa file nào."""
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "task_release.py", tmp_path / "scripts")
    (tmp_path / "roadmap").mkdir()
    (tmp_path / "roadmap" / "overview.md").write_text("- [Task 9.9: Tên trong roadmap](../tasks/week_99/t.md)\n")
    (tmp_path / "tasks" / "_locked" / "week_99").mkdir(parents=True)
    (tmp_path / "tasks" / "_locked" / "recipients.txt").write_text("age1khoacongkhaigia\n")
    (tmp_path / "tasks" / "release_schedule.toml").write_text(
        "[[sprint]]\nnumber = 99\nrelease = 2027-01-04\n"
        'tasks = [{ id = "9.9", path = "tasks/week_99/t.md", title = "Tên trong lịch" }]\n'
    )
    if command == "lock":
        (tmp_path / "tasks" / "week_99").mkdir()
        draft = tmp_path / "tasks" / "week_99" / "t.md"
        draft.write_text("# Task 9.9: bản nháp\n")
    else:
        draft = tmp_path / "tasks" / "_locked" / "week_99" / "t.md.age"
        draft.write_text("-----BEGIN AGE ENCRYPTED FILE-----\n")
    before = draft.read_text()

    result = subprocess.run(
        [sys.executable, str(tmp_path / "scripts" / "task_release.py"), command, "--sprint", "99"],
        capture_output=True,
        text=True,
        env={**os.environ, "TASK_UNLOCK_KEY": "AGE-SECRET-KEY-GIA"},
    )

    assert result.returncode != 0
    assert "Chưa làm gì" in result.stderr, result.stderr
    assert draft.exists() and draft.read_text() == before, "file đề bài bị động vào dù roadmap không khớp"
