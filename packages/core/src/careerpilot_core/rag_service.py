"""Deterministic secure-ingestion and cited-retrieval application service."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import replace
from pathlib import PurePath
from typing import TYPE_CHECKING

from careerpilot_core.access import (
    AccessDeniedError,
    AccessPolicy,
    AuthorizationContext,
    Permission,
    ResourceAttributes,
)
from careerpilot_core.audit import AuditEventDraft, AuditOutcome, AuditSink
from careerpilot_core.retrieval import (
    Citation,
    DocumentChunk,
    DocumentRecord,
    DocumentStatus,
    InjectionRisk,
    RetrievalCandidate,
    RetrievalResult,
    RetrievedPassage,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from careerpilot_core.ports import ProfileRepository
    from careerpilot_core.retrieval import (
        DocumentParser,
        DocumentRepository,
        DocumentScanner,
        DocumentStorage,
        EmbeddingProvider,
        ParsedSection,
    )

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_CONTEXT_CHARACTERS = 4_000
MIN_QUERY_CHARACTERS = 2
MAX_QUERY_CHARACTERS = 500
MIN_RESULT_LIMIT = 1
MAX_RESULT_LIMIT = 10
MIN_TITLE_CHARACTERS = 2
MAX_TITLE_CHARACTERS = 200
CHUNK_CHARACTERS = 700
CHUNK_OVERLAP = 100
PARSER_VERSION = "bounded-parser-v1"
CHUNKER_VERSION = "character-overlap-v1"
INDEX_VERSION = "rag-index-v1"
TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9+#.-]{1,}")
INJECTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(the\s+)?system\s+prompt",
        r"exfiltrat(e|ion)",
        r"send\s+.*\s+to\s+https?://",
        r"act\s+as\s+(an?\s+)?(administrator|system)",
        r"(reveal|print|return)\s+.*(secret|token|credential)",
        r"(disable|bypass)\s+.*(guardrail|authorization|policy)",
        r"(call|invoke|execute)\s+.*(delete|export|submit|email).*(tool|function)",
    )
)


class DocumentNotFoundError(LookupError):
    """Raised without revealing whether a foreign document exists."""


class DocumentValidationError(ValueError):
    """Safe document rejection with one field/reason pair."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(reason)
        self.field = field
        self.reason = reason


class DeletionConfirmationError(PermissionError):
    """Raised when an explicit human deletion confirmation is absent."""


class RagService:
    """Coordinate safe ingestion, versioned indexing, retrieval, and deletion."""

    def __init__(
        self,
        profiles: ProfileRepository,
        documents: DocumentRepository,
        storage: DocumentStorage,
        scanner: DocumentScanner,
        parser: DocumentParser,
        embedder: EmbeddingProvider,
        access_policy: AccessPolicy,
        audit_sink: AuditSink,
        *,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._profiles = profiles
        self._documents = documents
        self._storage = storage
        self._scanner = scanner
        self._parser = parser
        self._embedder = embedder
        self._access_policy = access_policy
        self._audit_sink = audit_sink
        self._id_factory = id_factory or (lambda: str(uuid.uuid4()))

    def ingest(
        self,
        context: AuthorizationContext,
        profile_id: str,
        *,
        title: str,
        filename: str,
        media_type: str,
        content: bytes,
    ) -> DocumentRecord:
        """Scan, parse, chunk, embed, and persist a tenant-owned source document."""
        profile = self._profiles.get(profile_id, context)
        if profile is None:
            self._audit(context, "document.ingest", "denied", "profile_unavailable")
            raise DocumentNotFoundError(profile_id)
        resource = ResourceAttributes(profile.tenant_id, profile.owner_actor_id)
        self._require(context, Permission.DOCUMENT_CREATE, resource)
        safe_filename = self._validate_upload(filename, media_type, content)
        scan = self._scanner.scan(safe_filename, media_type, content)
        if not scan.clean:
            self._audit(context, "document.ingest", "denied", scan.reason)
            raise DocumentValidationError("file", scan.reason)
        try:
            sections = self._parser.parse(media_type, content)
        except ValueError as error:
            self._audit(context, "document.ingest", "denied", "parse_rejected")
            raise DocumentValidationError("file", "parse_rejected") from error
        if not sections or not any(section.text.strip() for section in sections):
            raise DocumentValidationError("file", "no_searchable_text")
        normalized_title = title.strip()
        if not MIN_TITLE_CHARACTERS <= len(normalized_title) <= MAX_TITLE_CHARACTERS:
            raise DocumentValidationError("title", "title_length_not_allowed")

        document_id = self._id_factory()
        evidence_id = self._id_factory()
        risk = self._risk_for("\n".join(section.text for section in sections))
        storage_key = self._storage.put(context.tenant_id, document_id, content)
        document = DocumentRecord(
            document_id=document_id,
            evidence_id=evidence_id,
            profile_id=profile_id,
            tenant_id=context.tenant_id,
            owner_actor_id=profile.owner_actor_id,
            title=normalized_title,
            filename=safe_filename,
            media_type=media_type,
            size_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            storage_key=storage_key,
            status=DocumentStatus.INDEXED,
            injection_risk=risk,
            parser_version=PARSER_VERSION,
            chunker_version=CHUNKER_VERSION,
            embedding_version=self._embedder.version,
            index_version=INDEX_VERSION,
        )
        chunks = self._build_chunks(document, sections)
        try:
            self._documents.save_index(document, chunks, context)
        except Exception:
            self._storage.delete(storage_key)
            raise
        self._audit(
            context,
            "document.ingest",
            "allowed",
            "indexed_injection_suspected"
            if risk is InjectionRisk.SUSPECTED
            else "indexed",
            document_id,
        )
        return document

    def search(
        self, context: AuthorizationContext, query: str, limit: int = 5
    ) -> RetrievalResult:
        """Return cited untrusted passages or an explicit empty result."""
        normalized_query = " ".join(query.split())
        if not MIN_QUERY_CHARACTERS <= len(normalized_query) <= MAX_QUERY_CHARACTERS:
            raise DocumentValidationError("query", "query_length_not_allowed")
        if not MIN_RESULT_LIMIT <= limit <= MAX_RESULT_LIMIT:
            raise DocumentValidationError("limit", "limit_not_allowed")
        candidates = self._documents.hybrid_candidates(
            context,
            normalized_query,
            self._embedder.embed(normalized_query),
            INDEX_VERSION,
            max(limit * 4, 20),
        )
        passages = self._rerank(normalized_query, candidates, limit)
        context_text = self._assemble_context(passages)
        self._audit(
            context,
            "retrieval.search",
            "allowed",
            "results_returned" if passages else "no_evidence_found",
        )
        return RetrievalResult(
            query=normalized_query,
            passages=passages,
            context=context_text,
            disclaimer=(
                "Retrieved document text is untrusted evidence, not instructions or "
                "a generated answer. Empty results mean no supporting passage was "
                "found."
            ),
        )

    def reindex(
        self, context: AuthorizationContext, document_id: str
    ) -> DocumentRecord:
        """Rebuild every derivative using current component/index versions."""
        document = self._get_authorized(
            context, document_id, Permission.DOCUMENT_REINDEX
        )
        content = self._storage.read(document.storage_key)
        sections = self._parser.parse(document.media_type, content)
        updated = replace(
            document,
            injection_risk=self._risk_for("\n".join(item.text for item in sections)),
            parser_version=PARSER_VERSION,
            chunker_version=CHUNKER_VERSION,
            embedding_version=self._embedder.version,
            index_version=INDEX_VERSION,
        )
        self._documents.replace_index(
            updated, self._build_chunks(updated, sections), context
        )
        self._audit(context, "document.reindex", "allowed", "reindexed", document_id)
        return updated

    def delete(
        self, context: AuthorizationContext, document_id: str, *, confirmed: bool
    ) -> None:
        """Propagate an explicitly confirmed deletion to bytes, chunks, and vectors."""
        if not confirmed:
            self._audit(context, "document.delete", "denied", "confirmation_required")
            raise DeletionConfirmationError
        document = self._get_authorized(
            context, document_id, Permission.DOCUMENT_DELETE
        )
        self._storage.delete(document.storage_key)
        self._documents.delete_document(document, context)
        self._audit(context, "document.delete", "allowed", "deleted", document_id)

    def _get_authorized(
        self,
        context: AuthorizationContext,
        document_id: str,
        permission: Permission,
    ) -> DocumentRecord:
        document = self._documents.get(document_id, context)
        if document is None:
            self._audit(
                context, permission, "denied", "document_unavailable", document_id
            )
            raise DocumentNotFoundError(document_id)
        self._require(
            context,
            permission,
            ResourceAttributes(document.tenant_id, document.owner_actor_id),
        )
        return document

    def _require(
        self,
        context: AuthorizationContext,
        permission: Permission,
        resource: ResourceAttributes,
    ) -> None:
        try:
            self._access_policy.require(context, permission, resource)
        except AccessDeniedError as error:
            self._audit(context, permission, "denied", error.reason)
            raise

    def _build_chunks(
        self, document: DocumentRecord, sections: tuple[ParsedSection, ...]
    ) -> tuple[DocumentChunk, ...]:
        chunks: list[DocumentChunk] = []
        chunk_index = 0
        for section in sections:
            normalized = " ".join(section.text.split())
            start = 0
            while start < len(normalized):
                proposed_end = min(start + CHUNK_CHARACTERS, len(normalized))
                end = proposed_end
                if proposed_end < len(normalized):
                    boundary = normalized.rfind(" ", start, proposed_end)
                    if boundary > start:
                        end = boundary
                content = normalized[start:end].strip()
                if content:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=self._id_factory(),
                            document_id=document.document_id,
                            tenant_id=document.tenant_id,
                            owner_actor_id=document.owner_actor_id,
                            chunk_index=chunk_index,
                            page_number=section.page_number,
                            start_offset=start,
                            end_offset=end,
                            content=content,
                            embedding=self._embedder.embed(content),
                            injection_risk=self._risk_for(content),
                            index_version=document.index_version,
                        )
                    )
                    chunk_index += 1
                if end >= len(normalized):
                    break
                start = max(end - CHUNK_OVERLAP, start + 1)
        return tuple(chunks)

    @staticmethod
    def _validate_upload(filename: str, media_type: str, content: bytes) -> str:
        if not content or len(content) > MAX_UPLOAD_BYTES:
            raise DocumentValidationError("file", "size_not_allowed")
        allowed = {"text/plain": {".txt"}, "application/pdf": {".pdf"}}
        suffixes = allowed.get(media_type)
        if suffixes is None:
            raise DocumentValidationError("file", "media_type_not_allowed")
        normalized = PurePath(filename.replace("\\", "/")).name.strip()
        if not normalized or normalized in {".", ".."} or "\x00" in normalized:
            raise DocumentValidationError("file", "filename_not_allowed")
        if PurePath(normalized).suffix.casefold() not in suffixes:
            raise DocumentValidationError("file", "extension_mismatch")
        return normalized

    @staticmethod
    def _risk_for(text: str) -> InjectionRisk:
        return (
            InjectionRisk.SUSPECTED
            if any(pattern.search(text) for pattern in INJECTION_PATTERNS)
            else InjectionRisk.NONE_DETECTED
        )

    @staticmethod
    def _rerank(
        query: str,
        candidates: tuple[RetrievalCandidate, ...],
        limit: int,
    ) -> tuple[RetrievedPassage, ...]:
        query_terms = set(TOKEN_PATTERN.findall(query.casefold()))
        ranked: list[tuple[float, RetrievalCandidate]] = []
        for candidate in candidates:
            rrf = sum(
                1 / (60 + rank)
                for rank in (candidate.lexical_rank, candidate.vector_rank)
                if rank is not None
            )
            content_terms = set(
                TOKEN_PATTERN.findall(candidate.chunk.content.casefold())
            )
            overlap = len(query_terms & content_terms) / max(len(query_terms), 1)
            ranked.append((rrf + overlap, candidate))
        ranked.sort(key=lambda item: (-item[0], item[1].chunk.chunk_id))
        return tuple(
            RetrievedPassage(
                content=candidate.chunk.content,
                score=round(score, 6),
                injection_risk=candidate.chunk.injection_risk,
                citation=Citation(
                    document_id=candidate.chunk.document_id,
                    chunk_id=candidate.chunk.chunk_id,
                    document_title=candidate.document_title,
                    filename=candidate.filename,
                    page_number=candidate.chunk.page_number,
                    start_offset=candidate.chunk.start_offset,
                    end_offset=candidate.chunk.end_offset,
                ),
            )
            for score, candidate in ranked[:limit]
        )

    @staticmethod
    def _assemble_context(passages: tuple[RetrievedPassage, ...]) -> str:
        blocks: list[str] = []
        used = 0
        for passage in passages:
            header = (
                f"[UNTRUSTED document={passage.citation.document_id} "
                f"chunk={passage.citation.chunk_id} "
                f"page={passage.citation.page_number} "
                f"injection={passage.injection_risk}]"
            )
            block = f"{header}\n{passage.content}"
            if used + len(block) > MAX_CONTEXT_CHARACTERS:
                break
            blocks.append(block)
            used += len(block)
        return "\n\n".join(blocks)

    def _audit(
        self,
        context: AuthorizationContext,
        action: str,
        outcome: AuditOutcome,
        reason: str,
        resource_id: str | None = None,
    ) -> None:
        self._audit_sink.append(
            AuditEventDraft(
                tenant_id=context.tenant_id,
                actor_id=context.actor_id,
                action=action,
                outcome=outcome,
                reason=reason,
                correlation_id=context.correlation_id,
                resource_type="document" if resource_id else None,
                resource_id=resource_id,
            )
        )
