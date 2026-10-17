"""Gate test: bộ kiểm tra quy ước Git (scripts/check_git_conventions.py) chấp nhận và từ chối đúng trường hợp.

Quy ước: CONTRIBUTING.md, mục 2. Test này giữ cho bộ kiểm tra trong CI không bị nới lỏng hay siết nhầm.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_git_conventions.py"
_spec = importlib.util.spec_from_file_location("check_git_conventions", SCRIPT)
conv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(conv)

GOOD_COMMIT = "docs(git): thêm ghi chép về squash merge"


@pytest.mark.parametrize(
    "branch",
    [
        "sprint-01/task-0.0-git-workflow",
        "sprint-02/task-0.3-docker-compose",
        "sprint-10/task-4.1-airflow",
        "sprint-04/fix-minio-timeout",
        "sprint-03/docs-learning-log",
        "claude/github-repo-status-review-1jxt96",
        "release/tasks-20261123-010000",
    ],
)
def test_branch_accepted(branch: str) -> None:
    assert conv.branch_error(branch) is None


@pytest.mark.parametrize(
    "branch",
    [
        "main",
        "task-0.3",
        "sprint-1/task-0.3-docker",
        "sprint-02/task-0.3",
        "sprint-02/task-0.3-Docker-Compose",
        "sprint-02/task-0.3_docker_compose",
        "sprint-02/task-0.3-docker--compose",
        "sprint-02/feature-docker",
        "Sprint-02/task-0.3-docker",
        "thanh/sprint-02/task-0.3-docker",
    ],
)
def test_branch_rejected(branch: str) -> None:
    assert conv.branch_error(branch) is not None


@pytest.mark.parametrize(
    "subject",
    [
        GOOD_COMMIT,
        "feat(infra): thêm healthcheck cho minio",
        "fix: sửa cổng 5433",
        "test(chunking)!: đổi kích thước chunk mặc định",
        "chore(task-0.0): cập nhật tracker",
        "Merge branch 'main' into sprint-01/task-0.0-git-workflow",
        'Revert "feat(infra): thêm healthcheck cho minio"',
    ],
)
def test_commit_accepted(subject: str) -> None:
    assert conv.commit_subject_error(subject) is None


@pytest.mark.parametrize(
    "subject",
    [
        "update",
        "Update README.md",
        "fix bug",
        "feat:thiếu dấu cách",
        "feat: ",
        "Feat(infra): viết hoa loại",
        "feat(Infra): viết hoa phạm vi",
        "feature(infra): loại không hợp lệ",
        "docs: " + "a" * 100,
    ],
)
def test_commit_rejected(subject: str) -> None:
    assert conv.commit_subject_error(subject) is not None


@pytest.mark.parametrize("body", ["Closes #12", "closes #3\n", "- Fixes #7 và vài thứ", "Resolved #1"])
def test_issue_link_accepted(body: str) -> None:
    assert conv.issue_link_error(body) is None


@pytest.mark.parametrize(
    "body",
    ["", "Closes #", "Liên quan #12", "<!-- Closes #12 -->", "Closes #<!-- số issue -->", "Closes#12"],
)
def test_issue_link_rejected(body: str) -> None:
    assert conv.issue_link_error(body) is not None


def test_learner_pr_needs_everything() -> None:
    assert conv.pr_errors("sprint-01/task-0.0-git-workflow", GOOD_COMMIT, "Closes #2", [GOOD_COMMIT]) == []
    errors = conv.pr_errors("sprint-01/task-0.0-git-workflow", "Task 0.0", "", ["update", GOOD_COMMIT])
    assert len(errors) == 3, errors  # thiếu Closes, tiêu đề sai, 1 commit sai


def test_mentor_and_bot_branches() -> None:
    assert conv.pr_errors("claude/x", GOOD_COMMIT, "", [GOOD_COMMIT]) == []
    assert len(conv.pr_errors("claude/x", "Sửa linh tinh", "", ["wip"])) == 2
    assert conv.pr_errors("release/tasks-20261123-010000", "Phát hành task mới theo lịch", "", ["x"]) == []


@pytest.mark.parametrize(("message", "code"), [(f"# chú thích\n\n{GOOD_COMMIT}\n\nThân bài", 0), ("update\n", 1)])
def test_commit_msg_hook(tmp_path: Path, message: str, code: int) -> None:
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), str(message_file)], capture_output=True, text=True)
    assert result.returncode == code, result.stderr
