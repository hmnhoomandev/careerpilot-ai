"""Add immutable career drafts and exact-version human approvals."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "career_draft_versions",
        sa.Column("draft_id", sa.String(100), primary_key=True),
        sa.Column("version", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("profile_id", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("sections_json", sa.Text(), nullable=False),
        sa.Column("claims_json", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("pii_flags_json", sa.Text(), nullable=False),
        sa.Column("policy_flags_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_id"],
            ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "draft_id", "version"),
        sa.CheckConstraint(
            "version > 0", name="ck_career_draft_versions_positive_version"
        ),
    )
    op.create_table(
        "draft_approvals",
        sa.Column("approval_id", sa.String(100), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("owner_actor_id", sa.String(100), nullable=False),
        sa.Column("draft_id", sa.String(100), nullable=False),
        sa.Column("draft_version", sa.Integer(), nullable=False),
        sa.Column("draft_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["draft_id", "draft_version"],
            ["career_draft_versions.draft_id", "career_draft_versions.version"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", "approval_id"),
        sa.CheckConstraint("revision > 0", name="ck_draft_approvals_positive_revision"),
    )


def downgrade() -> None:
    op.drop_table("draft_approvals")
    op.drop_table("career_draft_versions")
