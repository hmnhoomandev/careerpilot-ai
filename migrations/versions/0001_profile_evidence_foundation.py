"""Create tenant-scoped profile and evidence metadata tables.

Revision ID: 0001
Revises: None
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the Phase 4 schema in dependency order."""
    op.create_table(
        "professional_profiles",
        sa.Column("profile_id", sa.String(100), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("professional_summary", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("purge_after", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "profile_id"),
        sa.CheckConstraint(
            "version > 0", name="ck_professional_profiles_positive_version"
        ),
    )
    op.create_table(
        "profile_skills",
        sa.Column("skill_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "profile_id", "name"),
    )
    op.create_table(
        "profile_experiences",
        sa.Column("experience_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("organization", sa.String(160), nullable=False),
        sa.Column("start_date", sa.String(10), nullable=False),
        sa.Column("end_date", sa.String(10)),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "profile_education",
        sa.Column("education_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("institution", sa.String(200), nullable=False),
        sa.Column("qualification", sa.String(200), nullable=False),
        sa.Column("start_date", sa.String(10)),
        sa.Column("end_date", sa.String(10)),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "evidence_items",
        sa.Column("evidence_id", sa.String(100), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(30), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("purge_after", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "size_bytes > 0 AND size_bytes <= 10485760",
            name="ck_evidence_items_allowed_size",
        ),
        sa.CheckConstraint("version > 0", name="ck_evidence_items_positive_version"),
    )


def downgrade() -> None:
    """Remove the Phase 4 schema for disposable local/test recovery only."""
    op.drop_table("evidence_items")
    op.drop_table("profile_education")
    op.drop_table("profile_experiences")
    op.drop_table("profile_skills")
    op.drop_table("professional_profiles")
