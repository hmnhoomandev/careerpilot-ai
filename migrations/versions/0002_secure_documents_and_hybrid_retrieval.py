"""Add pgvector documents, derived chunks, and hybrid-search indexes.

Revision ID: 0002
Revises: 0001
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enable vector support and add source/derivative retrieval tables."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_unique_constraint(
        "uq_evidence_items_tenant_id", "evidence_items", ["tenant_id", "evidence_id"]
    )
    op.create_table(
        "documents",
        sa.Column("document_id", sa.String(100), primary_key=True),
        sa.Column("evidence_id", sa.String(100), nullable=False),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("injection_risk", sa.String(30), nullable=False),
        sa.Column("parser_version", sa.String(80), nullable=False),
        sa.Column("chunker_version", sa.String(80), nullable=False),
        sa.Column("embedding_version", sa.String(80), nullable=False),
        sa.Column("index_version", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "evidence_id"],
            ["evidence_items.tenant_id", "evidence_items.evidence_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "document_id"),
        sa.CheckConstraint(
            "size_bytes > 0 AND size_bytes <= 10485760",
            name="ck_documents_allowed_size",
        ),
    )
    op.create_table(
        "document_chunks",
        sa.Column("chunk_id", sa.String(100), primary_key=True),
        sa.Column("document_id", sa.String(100), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", VECTOR(64), nullable=False),
        sa.Column("injection_risk", sa.String(30), nullable=False),
        sa.Column("index_version", sa.String(80), nullable=False),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('english', content)", persisted=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.document_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "document_id", "chunk_index"),
        sa.CheckConstraint("page_number > 0", name="ck_document_chunks_positive_page"),
        sa.CheckConstraint(
            "start_offset >= 0 AND end_offset > start_offset",
            name="ck_document_chunks_offsets",
        ),
    )
    op.create_index(
        "ix_document_chunks_search_vector",
        "document_chunks",
        ["search_vector"],
        postgresql_using="gin",
    )
    op.create_index(
        "ix_document_chunks_embedding_hnsw",
        "document_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    """Remove Phase 5 tables while retaining the shared vector extension."""
    op.drop_index("ix_document_chunks_embedding_hnsw", table_name="document_chunks")
    op.drop_index("ix_document_chunks_search_vector", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_constraint("uq_evidence_items_tenant_id", "evidence_items", type_="unique")
