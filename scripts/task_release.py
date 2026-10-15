#!/usr/bin/env python3
"""Khóa và phát hành task theo lịch trong tasks/release_schedule.toml.

Task chưa tới ngày được mã hóa bằng `age` thành tasks/_locked/<đường dẫn>.age:
- Khóa:  dùng khóa CÔNG KHAI trong tasks/_locked/recipients.txt (ai cũng khóa được).
- Mở:    cần khóa BÍ MẬT, chỉ có trong secret TASK_UNLOCK_KEY của GitHub Environment `task-release`.
Mỗi lần khóa/mở, dòng tương ứng trong roadmap/overview.md được đổi giữa dạng link và dạng 🔒.

Lệnh:
    python3 scripts/task_release.py status
    python3 scripts/task_release.py lock --sprint 5           # mentor: khóa task vừa viết
    python3 scripts/task_release.py release --due             # workflow: mở các sprint đã tới ngày
    python3 scripts/task_release.py release --sprint 5        # mở sớm một sprint
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "tasks" / "release_schedule.toml"
LOCKED_DIR = ROOT / "tasks" / "_locked"
RECIPIENTS = LOCKED_DIR / "recipients.txt"
ROADMAP = ROOT / "roadmap" / "overview.md"
TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


@dataclass(frozen=True)
class Task:
    sprint: int
    release: dt.date
    id: str
    title: str
    path: str

    @property
    def plain(self) -> Path:
        return ROOT / self.path

    @property
    def locked(self) -> Path:
        return LOCKED_DIR / (Path(self.path).relative_to("tasks").as_posix() + ".age")

    @property
    def is_locked(self) -> bool:
        return self.locked.exists()

    @property
    def released_line(self) -> str:
        return f"- [Task {self.id}: {self.title}](../{self.path})"

    @property
    def locked_line(self) -> str:
        return f"- 🔒 Task {self.id}: {self.title} *(mở ngày {self.release:%d/%m/%Y})*"


def load_tasks() -> list[Task]:
    data = tomllib.loads(SCHEDULE.read_text(encoding="utf-8"))
    return [
        Task(sprint=s["number"], release=s["release"], id=t["id"], title=t["title"], path=t["path"])
        for s in data["sprint"]
        for t in s["tasks"]
    ]


def swap_roadmap_line(old: str, new: str) -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    if text.count(old) != 1:
        sys.exit(f"Không tìm thấy đúng 1 dòng trong roadmap/overview.md:\n  {old}")
    ROADMAP.write_text(text.replace(old, new), encoding="utf-8")


def run_age(args: list[str]) -> None:
    result = subprocess.run(["age", *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"age lỗi: {result.stderr.strip()}")


def lock(tasks: list[Task]) -> None:
    if not RECIPIENTS.exists():
        sys.exit(f"Thiếu {RECIPIENTS.relative_to(ROOT)} (khóa công khai age1...).")
    for task in tasks:
        if task.is_locked:
            print(f"Bỏ qua Task {task.id}: đã khóa.")
            continue
        task.locked.parent.mkdir(parents=True, exist_ok=True)
        run_age(["--encrypt", "--armor", "-R", str(RECIPIENTS), "-o", str(task.locked), str(task.plain)])
        task.plain.unlink()
        swap_roadmap_line(task.released_line, task.locked_line)
        print(f"Đã khóa Task {task.id} → {task.locked.relative_to(ROOT)}")


def release(tasks: list[Task]) -> list[Task]:
    pending = [t for t in tasks if t.is_locked]
    if not pending:
        print("Không có task nào cần mở.")
        return []
    key = os.environ.get("TASK_UNLOCK_KEY", "").strip()
    if not key:
        sys.exit("Thiếu biến môi trường TASK_UNLOCK_KEY (khóa bí mật AGE-SECRET-KEY-...).")
    with tempfile.NamedTemporaryFile("w", suffix=".key", delete=False) as f:
        f.write(key + "\n")
        identity = f.name
    try:
        os.chmod(identity, 0o600)
        for task in pending:
            task.plain.parent.mkdir(parents=True, exist_ok=True)
            run_age(["--decrypt", "-i", identity, "-o", str(task.plain), str(task.locked)])
            task.locked.unlink()
            swap_roadmap_line(task.locked_line, task.released_line)
            print(f"Đã mở Task {task.id} → {task.path}")
    finally:
        os.unlink(identity)
    return pending


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Liệt kê task và trạng thái khóa/mở")
    for name in ("lock", "release"):
        p = sub.add_parser(name)
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument("--sprint", type=int, help="Chỉ xử lý task của sprint này")
        if name == "release":
            group.add_argument("--due", action="store_true", help="Mở mọi sprint đã tới ngày phát hành")
    p_release = sub.choices["release"]
    p_release.add_argument("--summary", type=Path, help="Ghi danh sách task vừa mở ra file (dùng cho PR)")
    args = parser.parse_args()

    tasks = load_tasks()
    if args.command == "status":
        for t in tasks:
            state = "🔒 đang khóa" if t.is_locked else "đã mở"
            print(f"Sprint {t.sprint:>2} | mở ngày {t.release:%d/%m/%Y} | Task {t.id:<4} | {state}")
        return

    if args.sprint is not None:
        selected = [t for t in tasks if t.sprint == args.sprint]
        if not selected:
            sys.exit(f"Sprint {args.sprint} không có trong {SCHEDULE.relative_to(ROOT)}.")
    else:
        today = dt.datetime.now(TIMEZONE).date()
        selected = [t for t in tasks if t.release <= today]

    if args.command == "lock":
        lock(selected)
        return

    opened = release(selected)
    if args.summary and opened:
        args.summary.write_text(
            "\n".join(f"- Sprint {t.sprint}: Task {t.id}: {t.title}" for t in opened) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
