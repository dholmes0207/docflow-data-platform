"""Fixture database cho gate test schema.

Biến môi trường:
- DATABASE_URL: chuỗi kết nối tới một Postgres có pgvector, ví dụ
  postgresql://postgres:postgres@localhost:5432/postgres
  Test sẽ tự tạo (và xóa) database riêng `docflow_gate`, không đụng dữ liệu khác.
- REQUIRE_DB=1: bắt buộc có database. CI bật cờ này để test schema không thể
  "xanh giả" bằng cách bị bỏ qua (skip) khi thiếu database.
- INIT_SQL_PATH (tùy chọn): chạy bộ test trên một file schema khác thay vì infra/sql/init.sql,
  ví dụ file schema học viên tự viết. Khi review, mentor dùng biến này để kiểm tra bài nộp.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

INIT_SQL = Path(os.environ.get("INIT_SQL_PATH") or Path(__file__).resolve().parents[2] / "infra" / "sql" / "init.sql")
GATE_DB = "docflow_gate"


def _skip_or_fail(reason: str) -> None:
    if os.environ.get("REQUIRE_DB") == "1":
        pytest.fail(f"REQUIRE_DB=1 nhưng {reason}")
    pytest.skip(reason)


@pytest.fixture(scope="session")
def gate_dsn() -> Iterator[str]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        _skip_or_fail("chưa đặt DATABASE_URL")
    try:
        import psycopg
        from psycopg.conninfo import make_conninfo
    except ImportError:
        _skip_or_fail("chưa cài psycopg (pip install -r requirements-dev.txt)")

    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute(f"DROP DATABASE IF EXISTS {GATE_DB}")
        admin.execute(f"CREATE DATABASE {GATE_DB}")
    dsn = make_conninfo(url, dbname=GATE_DB)

    # Chạy init.sql 2 lần: lần 2 chứng minh script chạy lại được (IF NOT EXISTS / OR REPLACE).
    with psycopg.connect(dsn, autocommit=True) as conn:
        for _ in range(2):
            conn.execute(INIT_SQL.read_text(encoding="utf-8"))

    yield dsn

    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute(f"DROP DATABASE IF EXISTS {GATE_DB}")


@pytest.fixture
def db(gate_dsn: str) -> Iterator[object]:
    """Mỗi test chạy trong 1 transaction và bị rollback ở cuối, nên các test không ảnh hưởng nhau."""
    import psycopg

    conn = psycopg.connect(gate_dsn)
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()
