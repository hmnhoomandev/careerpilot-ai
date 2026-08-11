"""Framework-independent document ingestion and retrieval contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from careerpilot_core.access import AuthorizationContext


class InjectionRisk(StrEnum):
    """Versioned security label applied to untrusted document content."""

    NONE_DETECTED = "none_detected"
    SUSPECTED = "suspected"


class DocumentStatus(StrEnum):
    """Processing state for a stored source document."""

    INDEXED = "indexed"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class ParsedSection:
    """Normalized parser output with source page provenance."""

    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Fail-closed local scanner decision."""

    clean: bool
    reason: str


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    """Tenant-owned source document and its index provenance."""

    document_id: str
    evidence_id: str
    profile_id: str
    tenant_id: str
    owner_actor_id: str
    title: str
    filename: str
    media_type: str
    size_bytes: int
    sha256: str
    storage_key: str
    status: DocumentStatus
    injection_risk: InjectionRisk
    parser_version: str
    chunker_version: str
    embedding_version: str
    index_version: str


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    """One citable untrusted passage and its deterministic embedding."""

    chunk_id: str
    document_id: str
    tenant_id: str
    owner_actor_id: str
    chunk_index: int
    page_number: int
    start_offset: int
    end_offset: int
    content: str
    embedding: tuple[float, ...]
    injection_risk: InjectionRisk
    index_version: str


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    """Repository-ranked candidate before deterministic fusion/reranking."""

    chunk: DocumentChunk
    document_title: str
    filename: str
    lexical_rank: int | None
    vector_rank: int | None


@dataclass(frozen=True, slots=True)
class Citation:
    """Stable provenance needed to inspect one retrieved passage."""

    document_id: str
    chunk_id: str
    document_title: str
    filename: str
    page_number: int
    start_offset: int
    end_offset: int


@dataclass(frozen=True, slots=True)
class RetrievedPassage:
    """A reranked untrusted passage paired with an inspectable citation."""

    content: str
    score: float
    injection_risk: InjectionRisk
    citation: Citation


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """Bounded cited context; it is not a generated answer."""

    query: str
    passages: tuple[RetrievedPassage, ...]
    context: str
    disclaimer: str


class DocumentStorage(Protocol):
    """Store raw bytes behind a production object-storage boundary."""

    def put(self, tenant_id: str, document_id: str, content: bytes) -> str:
        """Persist bytes and return an opaque server-generated storage key."""

    def read(self, storage_key: str) -> bytes:
        """Read bytes for authorized re-indexing."""

    def delete(self, storage_key: str) -> None:
        """Remove bytes or raise so metadata deletion does not proceed silently."""


class DocumentScanner(Protocol):
    """Inspect bounded bytes before parsing or trusted-state transitions."""

    def scan(self, filename: str, media_type: str, content: bytes) -> ScanResult:
        """Return a fail-closed decision without executing document content."""


class DocumentParser(Protocol):
    """Convert bounded clean bytes into provenance-preserving text sections."""

    def parse(self, media_type: str, content: bytes) -> tuple[ParsedSection, ...]:
        """Return normalized source sections or raise a safe parsing error."""


class EmbeddingProvider(Protocol):
    """Map text to a fixed-size vector under an explicit version."""

    @property
    def version(self) -> str:
        """Return the embedding/index compatibility version."""

    def embed(self, text: str) -> tuple[float, ...]:
        """Create one embedding without implicit provider fallback."""


class DocumentRepository(Protocol):
    """Persist and retrieve tenant-authorized documents and derived chunks."""

    def save_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        """Atomically save source metadata and its current derived index."""

    def get(
        self, document_id: str, context: AuthorizationContext
    ) -> DocumentRecord | None:
        """Return an active authorized document or non-enumerating absence."""

    def replace_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        """Atomically replace all derived chunks for a new index version."""

    def hybrid_candidates(
        self,
        context: AuthorizationContext,
        query: str,
        query_embedding: tuple[float, ...],
        index_version: str,
        candidate_limit: int,
    ) -> tuple[RetrievalCandidate, ...]:
        """Return lexical/vector ranks after tenant/document authorization filters."""

    def delete_document(
        self, document: DocumentRecord, context: AuthorizationContext
    ) -> None:
        """Soft-delete source metadata and remove every chunk/vector derivative."""
