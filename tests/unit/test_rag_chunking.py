"""Unit evidence for deterministic chunk metadata and overlap."""

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.document_processing import (
    BoundedDocumentParser,
    DeterministicHashEmbedder,
    InMemoryDocumentStorage,
    LocalDocumentScanner,
)
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_api.retrieval_repository import InMemoryDocumentRepository
from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    CareerJourneyService,
    RagService,
    Role,
)


def test_chunk_offsets_overlap_and_versions_are_deterministic() -> None:
    context = AuthorizationContext(
        actor_id="actor-test",
        tenant_id="tenant-test",
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="chunk-test",
    )
    profiles = InMemoryProfileRepository()
    audit = InMemoryAuditLog()
    profile = CareerJourneyService(profiles, AccessPolicy(), audit).create_profile(
        context,
        "Synthetic Candidate",
        "A sufficiently long synthetic profile summary for chunk testing.",
    )
    documents = InMemoryDocumentRepository()
    identifiers = (f"id-{index}" for index in range(100))
    service = RagService(
        profiles,
        documents,
        InMemoryDocumentStorage(),
        LocalDocumentScanner(),
        BoundedDocumentParser(),
        DeterministicHashEmbedder(),
        AccessPolicy(),
        audit,
        id_factory=lambda: next(identifiers),
    )
    document = service.ingest(
        context,
        profile.profile_id,
        title="Long synthetic evidence",
        filename="long.txt",
        media_type="text/plain",
        content=(("python evidence " * 100) + "final fact").encode(),
    )
    chunks = sorted(documents._chunks.values(), key=lambda item: item.chunk_index)  # noqa: SLF001
    assert len(chunks) >= 3
    assert chunks[0].page_number == 1
    assert chunks[1].start_offset < chunks[0].end_offset
    assert all(chunk.document_id == document.document_id for chunk in chunks)
    assert all(chunk.index_version == "rag-index-v1" for chunk in chunks)
