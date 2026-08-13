"""PostgreSQL schema, transaction factory, and tenant-safe repository adapter."""

from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.engine import Connection, Engine, RowMapping

from careerpilot_core import (
    AuthorizationContext,
    Education,
    EvidenceItem,
    EvidenceState,
    Experience,
    ProfessionalProfile,
    Skill,
)
from careerpilot_core.ports import StaleProfileVersionError

if TYPE_CHECKING:
    from types import TracebackType

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)

profiles = Table(
    "professional_profiles",
    metadata,
    Column("profile_id", String(100), primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("display_name", Text, nullable=False),
    Column("professional_summary", Text, nullable=False),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("deleted_at", DateTime(timezone=True)),
    Column("purge_after", DateTime(timezone=True)),
    UniqueConstraint("tenant_id", "profile_id"),
    CheckConstraint("version > 0", name="positive_version"),
)

skills = Table(
    "profile_skills",
    metadata,
    Column("skill_id", Integer, primary_key=True, autoincrement=True),
    Column("profile_id", String(100), nullable=False),
    Column("tenant_id", String(100), nullable=False),
    Column("name", String(120), nullable=False),
    Column("verified", Boolean, nullable=False, server_default="false"),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "profile_id", "name"),
)

experiences = Table(
    "profile_experiences",
    metadata,
    Column("experience_id", Integer, primary_key=True, autoincrement=True),
    Column("profile_id", String(100), nullable=False),
    Column("tenant_id", String(100), nullable=False),
    Column("title", String(160), nullable=False),
    Column("organization", String(160), nullable=False),
    Column("start_date", String(10), nullable=False),
    Column("end_date", String(10)),
    Column("description", Text, nullable=False),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
)

education = Table(
    "profile_education",
    metadata,
    Column("education_id", Integer, primary_key=True, autoincrement=True),
    Column("profile_id", String(100), nullable=False),
    Column("tenant_id", String(100), nullable=False),
    Column("institution", String(200), nullable=False),
    Column("qualification", String(200), nullable=False),
    Column("start_date", String(10)),
    Column("end_date", String(10)),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
)

evidence_items = Table(
    "evidence_items",
    metadata,
    Column("evidence_id", String(100), primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("profile_id", String(100), nullable=False),
    Column("title", String(200), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("media_type", String(100), nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("state", String(30), nullable=False),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("deleted_at", DateTime(timezone=True)),
    Column("purge_after", DateTime(timezone=True)),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "evidence_id"),
    CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="allowed_size"),
    CheckConstraint("version > 0", name="positive_version"),
)

documents = Table(
    "documents",
    metadata,
    Column("document_id", String(100), primary_key=True),
    Column("evidence_id", String(100), nullable=False),
    Column("profile_id", String(100), nullable=False),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("title", String(200), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("media_type", String(100), nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("sha256", String(64), nullable=False),
    Column("storage_key", String(255), nullable=False),
    Column("status", String(30), nullable=False),
    Column("injection_risk", String(30), nullable=False),
    Column("parser_version", String(80), nullable=False),
    Column("chunker_version", String(80), nullable=False),
    Column("embedding_version", String(80), nullable=False),
    Column("index_version", String(80), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("deleted_at", DateTime(timezone=True)),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
    ForeignKeyConstraint(
        ["tenant_id", "evidence_id"],
        ["evidence_items.tenant_id", "evidence_items.evidence_id"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "document_id"),
    CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="allowed_size"),
)

document_chunks = Table(
    "document_chunks",
    metadata,
    Column("chunk_id", String(100), primary_key=True),
    Column("document_id", String(100), nullable=False),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("chunk_index", Integer, nullable=False),
    Column("page_number", Integer, nullable=False),
    Column("start_offset", Integer, nullable=False),
    Column("end_offset", Integer, nullable=False),
    Column("content", Text, nullable=False),
    Column("embedding", VECTOR(64), nullable=False),
    Column("injection_risk", String(30), nullable=False),
    Column("index_version", String(80), nullable=False),
    Column(
        "search_vector",
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
        nullable=False,
    ),
    ForeignKeyConstraint(
        ["tenant_id", "document_id"],
        ["documents.tenant_id", "documents.document_id"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "document_id", "chunk_index"),
    CheckConstraint("page_number > 0", name="positive_page"),
    CheckConstraint("start_offset >= 0 AND end_offset > start_offset", name="offsets"),
)

draft_versions = Table(
    "career_draft_versions",
    metadata,
    Column("draft_id", String(100), primary_key=True),
    Column("version", Integer, primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("profile_id", String(100), nullable=False),
    Column("kind", String(30), nullable=False),
    Column("title", Text, nullable=False),
    Column("sections_json", Text, nullable=False),
    Column("claims_json", Text, nullable=False),
    Column("content_hash", String(64), nullable=False),
    Column("pii_flags_json", Text, nullable=False),
    Column("policy_flags_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["tenant_id", "profile_id"],
        ["professional_profiles.tenant_id", "professional_profiles.profile_id"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "draft_id", "version"),
    CheckConstraint("version > 0", name="positive_version"),
)

approvals = Table(
    "draft_approvals",
    metadata,
    Column("approval_id", String(100), primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("owner_actor_id", String(100), nullable=False),
    Column("draft_id", String(100), nullable=False),
    Column("draft_version", Integer, nullable=False),
    Column("draft_hash", String(64), nullable=False),
    Column("status", String(40), nullable=False),
    Column("revision", Integer, nullable=False),
    Column("feedback", Text),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["draft_id", "draft_version"],
        ["career_draft_versions.draft_id", "career_draft_versions.version"],
        ondelete="CASCADE",
    ),
    UniqueConstraint("tenant_id", "approval_id"),
    CheckConstraint("revision > 0", name="positive_revision"),
)

Index(
    "ix_document_chunks_search_vector",
    document_chunks.c.search_vector,
    postgresql_using="gin",
)
Index(
    "ix_document_chunks_embedding_hnsw",
    document_chunks.c.embedding,
    postgresql_using="hnsw",
    postgresql_ops={"embedding": "vector_cosine_ops"},
)


class Transaction(AbstractContextManager[Connection]):
    """Expose one database connection whose context commits or rolls back."""

    def __init__(self, engine: Engine) -> None:
        self._context = engine.begin()

    def __enter__(self) -> Connection:
        return self._context.__enter__()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return self._context.__exit__(exc_type, exc_value, traceback)


class UnsupportedDatabaseError(ValueError):
    """Raised when production persistence is pointed at a non-PostgreSQL engine."""


class PostgresProfileRepository:
    """Persist profile aggregates with tenant predicates on every operation."""

    def __init__(self, engine: Engine) -> None:
        if engine.dialect.name != "postgresql":
            raise UnsupportedDatabaseError
        self._engine = engine

    def save(self, profile: ProfessionalProfile, context: AuthorizationContext) -> None:
        """Insert the aggregate in one transaction."""
        self._require_tenant(profile.tenant_id, context)
        now = datetime.now(UTC)
        with Transaction(self._engine) as connection:
            connection.execute(
                insert(profiles).values(
                    profile_id=profile.profile_id,
                    tenant_id=profile.tenant_id,
                    owner_actor_id=profile.owner_actor_id,
                    display_name=profile.display_name,
                    professional_summary=profile.professional_summary,
                    version=profile.version,
                    created_at=now,
                    updated_at=now,
                    deleted_at=profile.deleted_at,
                    purge_after=profile.purge_after,
                )
            )
            self._replace_children(connection, profile)

    def get(
        self, profile_id: str, context: AuthorizationContext
    ) -> ProfessionalProfile | None:
        """Load one active aggregate using tenant and ID together."""
        with self._engine.connect() as connection:
            row = (
                connection.execute(
                    select(profiles).where(
                        profiles.c.profile_id == profile_id,
                        profiles.c.tenant_id == context.tenant_id,
                        profiles.c.deleted_at.is_(None),
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                return None
            return self._hydrate(connection, row)

    def update(
        self,
        profile: ProfessionalProfile,
        expected_version: int,
        context: AuthorizationContext,
    ) -> ProfessionalProfile:
        """Compare-and-swap the aggregate and children in one transaction."""
        self._require_tenant(profile.tenant_id, context)
        with Transaction(self._engine) as connection:
            result = connection.execute(
                update(profiles)
                .where(
                    profiles.c.profile_id == profile.profile_id,
                    profiles.c.tenant_id == context.tenant_id,
                    profiles.c.version == expected_version,
                    profiles.c.deleted_at.is_(None),
                )
                .values(
                    display_name=profile.display_name,
                    professional_summary=profile.professional_summary,
                    version=expected_version + 1,
                    updated_at=datetime.now(UTC),
                )
            )
            if result.rowcount != 1:
                raise StaleProfileVersionError
            saved = ProfessionalProfile(
                profile_id=profile.profile_id,
                tenant_id=profile.tenant_id,
                owner_actor_id=profile.owner_actor_id,
                display_name=profile.display_name,
                professional_summary=profile.professional_summary,
                version=expected_version + 1,
                skills=profile.skills,
                experiences=profile.experiences,
                education=profile.education,
            )
            self._replace_children(connection, saved)
            return saved

    def add_evidence(
        self, evidence: EvidenceItem, context: AuthorizationContext
    ) -> EvidenceItem:
        """Insert quarantined metadata only when the tenant owns the profile."""
        self._require_tenant(evidence.tenant_id, context)
        now = datetime.now(UTC)
        with Transaction(self._engine) as connection:
            profile_exists = connection.scalar(
                select(profiles.c.profile_id).where(
                    profiles.c.profile_id == evidence.profile_id,
                    profiles.c.tenant_id == context.tenant_id,
                    profiles.c.deleted_at.is_(None),
                )
            )
            if profile_exists is None:
                raise KeyError(evidence.profile_id)
            connection.execute(
                insert(evidence_items).values(
                    evidence_id=evidence.evidence_id,
                    tenant_id=evidence.tenant_id,
                    owner_actor_id=evidence.owner_actor_id,
                    profile_id=evidence.profile_id,
                    title=evidence.title,
                    filename=evidence.filename,
                    media_type=evidence.media_type,
                    size_bytes=evidence.size_bytes,
                    state=evidence.state,
                    version=evidence.version,
                    created_at=now,
                    updated_at=now,
                )
            )
        return evidence

    def list_evidence(
        self, profile_id: str, context: AuthorizationContext
    ) -> tuple[EvidenceItem, ...]:
        """Return active evidence metadata without raw document content."""
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(evidence_items)
                .where(
                    evidence_items.c.profile_id == profile_id,
                    evidence_items.c.tenant_id == context.tenant_id,
                    evidence_items.c.deleted_at.is_(None),
                )
                .order_by(evidence_items.c.created_at, evidence_items.c.evidence_id)
            ).mappings()
            return tuple(
                EvidenceItem(
                    evidence_id=row["evidence_id"],
                    tenant_id=row["tenant_id"],
                    owner_actor_id=row["owner_actor_id"],
                    profile_id=row["profile_id"],
                    title=row["title"],
                    filename=row["filename"],
                    media_type=row["media_type"],
                    size_bytes=row["size_bytes"],
                    state=EvidenceState(row["state"]),
                    version=row["version"],
                    deleted_at=row["deleted_at"],
                    purge_after=row["purge_after"],
                )
                for row in rows
            )

    @staticmethod
    def _require_tenant(tenant_id: str, context: AuthorizationContext) -> None:
        if tenant_id != context.tenant_id:
            raise PermissionError("tenant_mismatch")

    @staticmethod
    def _replace_children(connection: Connection, profile: ProfessionalProfile) -> None:
        for table in (skills, experiences, education):
            connection.execute(
                delete(table).where(
                    table.c.profile_id == profile.profile_id,
                    table.c.tenant_id == profile.tenant_id,
                )
            )
        if profile.skills:
            connection.execute(
                insert(skills),
                [
                    {
                        "profile_id": profile.profile_id,
                        "tenant_id": profile.tenant_id,
                        "name": item.name,
                        "verified": item.verified,
                    }
                    for item in profile.skills
                ],
            )
        if profile.experiences:
            connection.execute(
                insert(experiences),
                [
                    {
                        "profile_id": profile.profile_id,
                        "tenant_id": profile.tenant_id,
                        "title": item.title,
                        "organization": item.organization,
                        "start_date": item.start_date,
                        "end_date": item.end_date,
                        "description": item.description,
                    }
                    for item in profile.experiences
                ],
            )
        if profile.education:
            connection.execute(
                insert(education),
                [
                    {
                        "profile_id": profile.profile_id,
                        "tenant_id": profile.tenant_id,
                        "institution": item.institution,
                        "qualification": item.qualification,
                        "start_date": item.start_date,
                        "end_date": item.end_date,
                    }
                    for item in profile.education
                ],
            )

    @staticmethod
    def _hydrate(connection: Connection, row: RowMapping) -> ProfessionalProfile:
        mapping = row
        tenant_id = mapping["tenant_id"]
        profile_id = mapping["profile_id"]
        skill_rows = connection.execute(
            select(skills)
            .where(skills.c.tenant_id == tenant_id, skills.c.profile_id == profile_id)
            .order_by(skills.c.skill_id)
        ).mappings()
        experience_rows = connection.execute(
            select(experiences)
            .where(
                experiences.c.tenant_id == tenant_id,
                experiences.c.profile_id == profile_id,
            )
            .order_by(experiences.c.experience_id)
        ).mappings()
        education_rows = connection.execute(
            select(education)
            .where(
                education.c.tenant_id == tenant_id,
                education.c.profile_id == profile_id,
            )
            .order_by(education.c.education_id)
        ).mappings()
        return ProfessionalProfile(
            profile_id=profile_id,
            tenant_id=tenant_id,
            owner_actor_id=mapping["owner_actor_id"],
            display_name=mapping["display_name"],
            professional_summary=mapping["professional_summary"],
            version=mapping["version"],
            skills=tuple(
                Skill(name=item["name"], verified=item["verified"])
                for item in skill_rows
            ),
            experiences=tuple(
                Experience(
                    title=item["title"],
                    organization=item["organization"],
                    start_date=item["start_date"],
                    end_date=item["end_date"],
                    description=item["description"],
                )
                for item in experience_rows
            ),
            education=tuple(
                Education(
                    institution=item["institution"],
                    qualification=item["qualification"],
                    start_date=item["start_date"],
                    end_date=item["end_date"],
                )
                for item in education_rows
            ),
            deleted_at=mapping["deleted_at"],
            purge_after=mapping["purge_after"],
        )


def create_postgres_engine(database_url: str) -> Engine:
    """Create a pre-ping PostgreSQL engine without logging statement values."""
    return create_engine(database_url, pool_pre_ping=True, hide_parameters=True)
