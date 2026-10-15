"""Gate test: schema trong infra/sql/init.sql phải tự chặn dữ liệu sai.

Mỗi test mô phỏng một lỗi mà code pipeline có thể gây ra (ghi nhầm tenant, chạy lại sinh trùng,
2 phiên bản cùng hiệu lực...) và khẳng định database từ chối nó.
Cần Postgres + pgvector, xem hướng dẫn chạy trong CONTRIBUTING.md.
"""

from __future__ import annotations

import pytest

psycopg = pytest.importorskip("psycopg")
errors = psycopg.errors

RETAIL = "tenant_retail"
TECH = "tenant_tech"


def insert_document(db, tenant: str, path: str, file_hash: str, version: int = 1) -> int:
    row = db.execute(
        "INSERT INTO documents (tenant_id, file_name, file_path, file_hash, version) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (tenant, path.rsplit("/", 1)[-1], path, file_hash * 64, version),
    ).fetchone()
    return row[0]


def insert_chunk(db, document_id: int, tenant: str, chunk_index: int) -> None:
    db.execute(
        "INSERT INTO document_chunks (document_id, tenant_id, chunk_index, content) VALUES (%s, %s, %s, %s)",
        (document_id, tenant, chunk_index, f"đoạn {chunk_index}"),
    )


def test_chunk_of_same_tenant_is_accepted(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    insert_chunk(db, doc_id, RETAIL, 0)


def test_chunk_with_other_tenant_is_rejected(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    with pytest.raises(errors.ForeignKeyViolation), db.transaction():
        insert_chunk(db, doc_id, TECH, 0)


def test_rerun_cannot_duplicate_chunks(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    insert_chunk(db, doc_id, RETAIL, 0)
    with pytest.raises(errors.UniqueViolation), db.transaction():
        insert_chunk(db, doc_id, RETAIL, 0)


def test_two_active_versions_are_rejected(db) -> None:
    insert_document(db, RETAIL, "tenant_retail/a.md", "a", version=1)
    with pytest.raises(errors.UniqueViolation), db.transaction():
        insert_document(db, RETAIL, "tenant_retail/a.md", "b", version=2)


def test_scd2_flow_deactivate_then_insert_is_accepted(db) -> None:
    old_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a", version=1)
    db.execute("UPDATE documents SET is_active = FALSE WHERE id = %s", (old_id,))
    insert_document(db, RETAIL, "tenant_retail/a.md", "b", version=2)
    active = db.execute("SELECT version FROM documents WHERE file_path = 'tenant_retail/a.md' AND is_active").fetchall()
    assert active == [(2,)]


def test_same_file_path_in_two_tenants_does_not_collide(db) -> None:
    insert_document(db, RETAIL, "noi_quy.txt", "a")
    insert_document(db, TECH, "noi_quy.txt", "b")


def test_updated_at_is_refreshed_on_update(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    db.execute("UPDATE documents SET updated_at = '2000-01-01' WHERE id = %s", (doc_id,))
    db.execute("UPDATE documents SET file_name = 'b.md' WHERE id = %s", (doc_id,))
    (updated_at,) = db.execute("SELECT updated_at FROM documents WHERE id = %s", (doc_id,)).fetchone()
    assert updated_at.year > 2000, "trigger phải tự cập nhật updated_at mỗi khi UPDATE"


def test_moving_document_to_other_tenant_is_rejected_while_it_has_chunks(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    insert_chunk(db, doc_id, RETAIL, 0)
    with pytest.raises(errors.ForeignKeyViolation), db.transaction():
        db.execute("UPDATE documents SET tenant_id = %s WHERE id = %s", (TECH, doc_id))


def test_deleting_document_cascades_to_chunks(db) -> None:
    doc_id = insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    insert_chunk(db, doc_id, RETAIL, 0)
    insert_chunk(db, doc_id, RETAIL, 1)
    db.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    (remaining,) = db.execute("SELECT count(*) FROM document_chunks WHERE document_id = %s", (doc_id,)).fetchone()
    assert remaining == 0


@pytest.mark.parametrize(
    ("sql", "params"),
    [
        (
            "INSERT INTO documents (tenant_id, file_name, file_path, file_hash, version) "
            "VALUES ('t', 'a', 'a', 'x', 0)",
            None,
        ),
        (
            "INSERT INTO document_chunks (document_id, tenant_id, chunk_index, content) "
            "SELECT id, tenant_id, -1, 'x' FROM documents LIMIT 1",
            None,
        ),
    ],
    ids=["version_zero", "negative_chunk_index"],
)
def test_invalid_numbers_are_rejected(db, sql: str, params) -> None:
    insert_document(db, RETAIL, "tenant_retail/a.md", "a")
    with pytest.raises(errors.CheckViolation), db.transaction():
        db.execute(sql, params)


def test_embedding_column_matches_model_dimension(db) -> None:
    (column_type,) = db.execute(
        "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
        "WHERE attrelid = 'document_chunks'::regclass AND attname = 'embedding'"
    ).fetchone()
    assert column_type == "vector(384)", "all-MiniLM-L6-v2 sinh vector 384 chiều"


def test_hnsw_cosine_index_exists(db) -> None:
    (indexdef,) = db.execute(
        "SELECT indexdef FROM pg_indexes WHERE tablename = 'document_chunks' AND indexdef ILIKE '%hnsw%'"
    ).fetchone()
    assert "vector_cosine_ops" in indexdef
