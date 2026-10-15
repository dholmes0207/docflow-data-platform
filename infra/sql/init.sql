-- Script khởi tạo Schema ban đầu cho DocFlow Platform
-- Lưu ý: Postgres chỉ chạy các script trong /docker-entrypoint-initdb.d khi volume dữ liệu còn TRỐNG.
-- Sau khi sửa file này, cần `docker compose down -v` (xóa volume) rồi `up` lại thì thay đổi mới có hiệu lực.

CREATE EXTENSION IF NOT EXISTS vector;

-- Hàm dùng chung: tự động cập nhật cột updated_at mỗi khi bản ghi bị UPDATE
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. Bảng quản lý Tài liệu gốc (Documents)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    version INT NOT NULL DEFAULT 1 CHECK (version >= 1),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_tenant_file_version UNIQUE (tenant_id, file_path, version),
    -- Cho phép bảng chunks tham chiếu cặp (id, tenant_id) để khóa chặt tenant
    CONSTRAINT unique_document_tenant UNIQUE (id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id);
-- Pipeline kiểm tra trùng lặp theo hash TRONG PHẠM VI một tenant
CREATE INDEX IF NOT EXISTS idx_documents_tenant_hash ON documents(tenant_id, file_hash);

-- Mỗi file của một tenant chỉ được có tối đa 1 phiên bản đang hiệu lực.
-- Khi tạo version mới: UPDATE bản cũ is_active = FALSE trước, rồi mới INSERT bản mới (trong cùng 1 transaction).
CREATE UNIQUE INDEX IF NOT EXISTS uq_documents_one_active_version
ON documents(tenant_id, file_path)
WHERE is_active;

CREATE OR REPLACE TRIGGER trg_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- 2. Bảng quản lý Các đoạn cắt (Document Chunks)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    chunk_index INT NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Khóa ngoại ghép: chunk chỉ có thể trỏ tới document của CÙNG tenant
    CONSTRAINT fk_document
        FOREIGN KEY (document_id, tenant_id)
        REFERENCES documents(id, tenant_id)
        ON DELETE CASCADE,
    -- Chạy lại pipeline không sinh chunk trùng (Idempotency)
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_tenant ON document_chunks(tenant_id);
-- Tra cứu theo document_id đã được phục vụ bởi index của ràng buộc unique_document_chunk

-- Index tìm kiếm tương đồng vector với HNSW
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON document_chunks
USING hnsw (embedding vector_cosine_ops);
