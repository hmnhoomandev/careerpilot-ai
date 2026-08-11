"""In-memory and PostgreSQL adapters for authorized hybrid document retrieval."""

from __future__ import annotations

import math
import re
from dataclasses import replace
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, cast, delete, func, insert, select, update

from careerpilot_api.database import (
    Transaction,
    document_chunks,
    documents,
    evidence_items,
)
from careerpilot_core import (
    AuthorizationContext,
    DocumentChunk,
    DocumentRecord,
    DocumentStatus,
    EvidenceState,
    InjectionRisk,
    RetrievalCandidate,
)

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection, Engine, RowMapping

MIN_VECTOR_SIMILARITY = 0.15
MAX_VECTOR_DISTANCE = 1 - MIN_VECTOR_SIMILARITY


class InMemoryDocumentRepository:
    """Process-local deterministic adapter for offline API/unit tests."""

    def __init__(self) -> None:
        self._documents: dict[str, DocumentRecord] = {}
        self._chunks: dict[str, DocumentChunk] = {}

    def save_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        self._require_owner(document, context)
        self._documents[document.document_id] = document
        self._chunks.update({chunk.chunk_id: chunk for chunk in chunks})

    def get(
        self, document_id: str, context: AuthorizationContext
    ) -> DocumentRecord | None:
        document = self._documents.get(document_id)
        if (
            document is None
            or document.tenant_id != context.tenant_id
            or document.owner_actor_id != context.actor_id
            or document.status is DocumentStatus.DELETED
        ):
            return None
        return document

    def replace_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        self._require_owner(document, context)
        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if chunk.document_id != document.document_id
        }
        self._documents[document.document_id] = document
        self._chunks.update({chunk.chunk_id: chunk for chunk in chunks})

    def hybrid_candidates(
        self,
        context: AuthorizationContext,
        query: str,
        query_embedding: tuple[float, ...],
        index_version: str,
        candidate_limit: int,
    ) -> tuple[RetrievalCandidate, ...]:
        query_terms = set(re.findall(r"[a-z][a-z0-9+#.-]{1,}", query.casefold()))
        eligible = [
            chunk
            for chunk in self._chunks.values()
            if chunk.tenant_id == context.tenant_id
            and chunk.owner_actor_id == context.actor_id
            and chunk.index_version == index_version
            and self._documents[chunk.document_id].status is DocumentStatus.INDEXED
        ]
        lexical = sorted(
            eligible,
            key=lambda chunk: (
                -len(query_terms & self._terms(chunk.content)),
                chunk.chunk_id,
            ),
        )[:candidate_limit]
        vector = sorted(
            eligible,
            key=lambda chunk: (
                -self._cosine(query_embedding, chunk.embedding),
                chunk.chunk_id,
            ),
        )[:candidate_limit]
        ranks: dict[str, list[int | None]] = {}
        for rank, chunk in enumerate(lexical, start=1):
            if query_terms & self._terms(chunk.content):
                ranks.setdefault(chunk.chunk_id, [None, None])[0] = rank
        for rank, chunk in enumerate(vector, start=1):
            if self._cosine(query_embedding, chunk.embedding) >= MIN_VECTOR_SIMILARITY:
                ranks.setdefault(chunk.chunk_id, [None, None])[1] = rank
        return tuple(
            RetrievalCandidate(
                chunk=self._chunks[chunk_id],
                document_title=self._documents[chunk.document_id].title,
                filename=self._documents[chunk.document_id].filename,
                lexical_rank=rank_pair[0],
                vector_rank=rank_pair[1],
            )
            for chunk_id, rank_pair in ranks.items()
            for chunk in (self._chunks[chunk_id],)
        )

    def delete_document(
        self, document: DocumentRecord, context: AuthorizationContext
    ) -> None:
        self._require_owner(document, context)
        self._documents[document.document_id] = replace(
            document, status=DocumentStatus.DELETED
        )
        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if chunk.document_id != document.document_id
        }

    @staticmethod
    def _require_owner(document: DocumentRecord, context: AuthorizationContext) -> None:
        if (
            document.tenant_id != context.tenant_id
            or document.owner_actor_id != context.actor_id
        ):
            raise PermissionError("tenant_or_owner_mismatch")

    @staticmethod
    def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
        denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(
            sum(value * value for value in right)
        )
        return (
            sum(first * second for first, second in zip(left, right, strict=True))
            / denominator
            if denominator
            else 0.0
        )

    @staticmethod
    def _terms(value: str) -> set[str]:
        return set(re.findall(r"[a-z][a-z0-9+#.-]{1,}", value.casefold()))


class PostgresDocumentRepository:
    """Use tenant/owner predicates inside lexical and vector retrieval queries."""

    def __init__(self, engine: Engine) -> None:
        if engine.dialect.name != "postgresql":
            raise ValueError("postgresql_required")
        self._engine = engine

    def save_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        self._require_owner(document, context)
        now = datetime.now(UTC)
        with Transaction(self._engine) as connection:
            connection.execute(
                insert(evidence_items).values(
                    evidence_id=document.evidence_id,
                    tenant_id=document.tenant_id,
                    owner_actor_id=document.owner_actor_id,
                    profile_id=document.profile_id,
                    title=document.title,
                    filename=document.filename,
                    media_type=document.media_type,
                    size_bytes=document.size_bytes,
                    state=EvidenceState.CLEAN,
                    version=1,
                    created_at=now,
                    updated_at=now,
                )
            )
            connection.execute(
                insert(documents).values(**self._document_values(document, now))
            )
            self._insert_chunks(connection, chunks)

    def get(
        self, document_id: str, context: AuthorizationContext
    ) -> DocumentRecord | None:
        with self._engine.connect() as connection:
            row = (
                connection.execute(
                    select(documents).where(
                        documents.c.document_id == document_id,
                        documents.c.tenant_id == context.tenant_id,
                        documents.c.owner_actor_id == context.actor_id,
                        documents.c.deleted_at.is_(None),
                    )
                )
                .mappings()
                .one_or_none()
            )
        return self._document_from_row(row) if row else None

    def replace_index(
        self,
        document: DocumentRecord,
        chunks: tuple[DocumentChunk, ...],
        context: AuthorizationContext,
    ) -> None:
        self._require_owner(document, context)
        with Transaction(self._engine) as connection:
            result = connection.execute(
                update(documents)
                .where(
                    documents.c.document_id == document.document_id,
                    documents.c.tenant_id == context.tenant_id,
                    documents.c.owner_actor_id == context.actor_id,
                    documents.c.deleted_at.is_(None),
                )
                .values(
                    injection_risk=document.injection_risk,
                    parser_version=document.parser_version,
                    chunker_version=document.chunker_version,
                    embedding_version=document.embedding_version,
                    index_version=document.index_version,
                    updated_at=datetime.now(UTC),
                )
            )
            if result.rowcount != 1:
                raise KeyError(document.document_id)
            connection.execute(
                delete(document_chunks).where(
                    document_chunks.c.document_id == document.document_id,
                    document_chunks.c.tenant_id == context.tenant_id,
                    document_chunks.c.owner_actor_id == context.actor_id,
                )
            )
            self._insert_chunks(connection, chunks)

    def hybrid_candidates(
        self,
        context: AuthorizationContext,
        query: str,
        query_embedding: tuple[float, ...],
        index_version: str,
        candidate_limit: int,
    ) -> tuple[RetrievalCandidate, ...]:
        base_conditions = (
            document_chunks.c.tenant_id == context.tenant_id,
            document_chunks.c.owner_actor_id == context.actor_id,
            document_chunks.c.index_version == index_version,
            documents.c.tenant_id == context.tenant_id,
            documents.c.owner_actor_id == context.actor_id,
            documents.c.status == DocumentStatus.INDEXED,
            documents.c.deleted_at.is_(None),
        )
        query_value = func.websearch_to_tsquery("english", query)
        lexical_score = func.ts_rank_cd(document_chunks.c.search_vector, query_value)
        distance = cast(
            document_chunks.c.embedding.op("<=>")(list(query_embedding)), Float
        )
        columns = (
            document_chunks,
            documents.c.title.label("document_title"),
            documents.c.filename.label("filename"),
        )
        with self._engine.connect() as connection:
            lexical_rows = connection.execute(
                select(*columns, lexical_score.label("score"))
                .join(
                    documents,
                    (documents.c.document_id == document_chunks.c.document_id)
                    & (documents.c.tenant_id == document_chunks.c.tenant_id),
                )
                .where(
                    *base_conditions,
                    document_chunks.c.search_vector.op("@@")(query_value),
                )
                .order_by(lexical_score.desc(), document_chunks.c.chunk_id)
                .limit(candidate_limit)
            ).mappings()
            vector_rows = connection.execute(
                select(*columns, distance.label("distance"))
                .join(
                    documents,
                    (documents.c.document_id == document_chunks.c.document_id)
                    & (documents.c.tenant_id == document_chunks.c.tenant_id),
                )
                .where(*base_conditions, distance <= MAX_VECTOR_DISTANCE)
                .order_by(distance, document_chunks.c.chunk_id)
                .limit(candidate_limit)
            ).mappings()
            merged: dict[str, RetrievalCandidate] = {}
            for rank, row in enumerate(lexical_rows, start=1):
                candidate = self._candidate_from_row(row, lexical_rank=rank)
                merged[candidate.chunk.chunk_id] = candidate
            for rank, row in enumerate(vector_rows, start=1):
                candidate = self._candidate_from_row(row, vector_rank=rank)
                existing = merged.get(candidate.chunk.chunk_id)
                merged[candidate.chunk.chunk_id] = (
                    replace(existing, vector_rank=rank) if existing else candidate
                )
        return tuple(merged.values())

    def delete_document(
        self, document: DocumentRecord, context: AuthorizationContext
    ) -> None:
        self._require_owner(document, context)
        now = datetime.now(UTC)
        with Transaction(self._engine) as connection:
            result = connection.execute(
                update(documents)
                .where(
                    documents.c.document_id == document.document_id,
                    documents.c.tenant_id == context.tenant_id,
                    documents.c.owner_actor_id == context.actor_id,
                    documents.c.deleted_at.is_(None),
                )
                .values(status=DocumentStatus.DELETED, deleted_at=now, updated_at=now)
            )
            if result.rowcount != 1:
                raise KeyError(document.document_id)
            connection.execute(
                delete(document_chunks).where(
                    document_chunks.c.document_id == document.document_id,
                    document_chunks.c.tenant_id == context.tenant_id,
                    document_chunks.c.owner_actor_id == context.actor_id,
                )
            )
            connection.execute(
                update(evidence_items)
                .where(
                    evidence_items.c.evidence_id == document.evidence_id,
                    evidence_items.c.tenant_id == context.tenant_id,
                    evidence_items.c.owner_actor_id == context.actor_id,
                    evidence_items.c.deleted_at.is_(None),
                )
                .values(state=EvidenceState.DELETED, deleted_at=now, updated_at=now)
            )

    @staticmethod
    def _require_owner(document: DocumentRecord, context: AuthorizationContext) -> None:
        if (
            document.tenant_id != context.tenant_id
            or document.owner_actor_id != context.actor_id
        ):
            raise PermissionError("tenant_or_owner_mismatch")

    @staticmethod
    def _document_values(document: DocumentRecord, now: datetime) -> dict[str, object]:
        return {
            "document_id": document.document_id,
            "evidence_id": document.evidence_id,
            "profile_id": document.profile_id,
            "tenant_id": document.tenant_id,
            "owner_actor_id": document.owner_actor_id,
            "title": document.title,
            "filename": document.filename,
            "media_type": document.media_type,
            "size_bytes": document.size_bytes,
            "sha256": document.sha256,
            "storage_key": document.storage_key,
            "status": document.status,
            "injection_risk": document.injection_risk,
            "parser_version": document.parser_version,
            "chunker_version": document.chunker_version,
            "embedding_version": document.embedding_version,
            "index_version": document.index_version,
            "created_at": now,
            "updated_at": now,
        }

    @staticmethod
    def _insert_chunks(
        connection: Connection, chunks: tuple[DocumentChunk, ...]
    ) -> None:
        if not chunks:
            return
        connection.execute(
            insert(document_chunks),
            [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "tenant_id": chunk.tenant_id,
                    "owner_actor_id": chunk.owner_actor_id,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "start_offset": chunk.start_offset,
                    "end_offset": chunk.end_offset,
                    "content": chunk.content,
                    "embedding": list(chunk.embedding),
                    "injection_risk": chunk.injection_risk,
                    "index_version": chunk.index_version,
                }
                for chunk in chunks
            ],
        )

    @staticmethod
    def _document_from_row(row: RowMapping) -> DocumentRecord:
        return DocumentRecord(
            document_id=row["document_id"],
            evidence_id=row["evidence_id"],
            profile_id=row["profile_id"],
            tenant_id=row["tenant_id"],
            owner_actor_id=row["owner_actor_id"],
            title=row["title"],
            filename=row["filename"],
            media_type=row["media_type"],
            size_bytes=row["size_bytes"],
            sha256=row["sha256"],
            storage_key=row["storage_key"],
            status=DocumentStatus(row["status"]),
            injection_risk=InjectionRisk(row["injection_risk"]),
            parser_version=row["parser_version"],
            chunker_version=row["chunker_version"],
            embedding_version=row["embedding_version"],
            index_version=row["index_version"],
        )

    @classmethod
    def _candidate_from_row(
        cls,
        row: RowMapping,
        *,
        lexical_rank: int | None = None,
        vector_rank: int | None = None,
    ) -> RetrievalCandidate:
        return RetrievalCandidate(
            chunk=DocumentChunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                tenant_id=row["tenant_id"],
                owner_actor_id=row["owner_actor_id"],
                chunk_index=row["chunk_index"],
                page_number=row["page_number"],
                start_offset=row["start_offset"],
                end_offset=row["end_offset"],
                content=row["content"],
                embedding=tuple(row["embedding"]),
                injection_risk=InjectionRisk(row["injection_risk"]),
                index_version=row["index_version"],
            ),
            document_title=row["document_title"],
            filename=row["filename"],
            lexical_rank=lexical_rank,
            vector_rank=vector_rank,
        )
