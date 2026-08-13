"""Local and PostgreSQL repositories for immutable drafts and approvals."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime

from sqlalchemy import Engine, and_, insert, select, update

from careerpilot_api.database import approvals, draft_versions
from careerpilot_core import (
    ApprovalConflictError,
    ApprovalRecord,
    ApprovalStatus,
    CareerDraft,
    Citation,
    ClaimStatus,
    DraftClaim,
    DraftKind,
)


class InMemoryDraftRepository:
    """Process-local fake preserving immutable versions and optimistic approvals."""

    def __init__(self) -> None:
        self._drafts: dict[tuple[str, str, int], CareerDraft] = {}
        self._approvals: dict[tuple[str, str], ApprovalRecord] = {}

    def save_draft(self, draft: CareerDraft) -> None:
        key = (draft.tenant_id, draft.draft_id, draft.version)
        if key in self._drafts:
            raise ApprovalConflictError("draft_version_exists")
        self._drafts[key] = draft

    def get_draft(
        self,
        tenant_id: str,
        actor_id: str,
        draft_id: str,
        version: int | None = None,
    ) -> CareerDraft | None:
        matches = [
            draft
            for (tenant, candidate, _), draft in self._drafts.items()
            if tenant == tenant_id
            and candidate == draft_id
            and draft.owner_actor_id == actor_id
            and (version is None or draft.version == version)
        ]
        return max(matches, key=lambda item: item.version) if matches else None

    def save_approval(
        self, approval: ApprovalRecord, expected_revision: int | None = None
    ) -> None:
        key = (approval.tenant_id, approval.approval_id)
        current = self._approvals.get(key)
        if expected_revision is not None and (
            current is None or current.revision != expected_revision
        ):
            raise ApprovalConflictError("stale_approval_revision")
        self._approvals[key] = approval

    def get_approval(
        self, tenant_id: str, actor_id: str, approval_id: str
    ) -> ApprovalRecord | None:
        approval = self._approvals.get((tenant_id, approval_id))
        return approval if approval and approval.owner_actor_id == actor_id else None


class PostgresDraftRepository:
    """Persist tenant-filtered immutable drafts and compare-and-update approvals."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save_draft(self, draft: CareerDraft) -> None:
        with self._engine.begin() as connection:
            connection.execute(insert(draft_versions).values(**_draft_values(draft)))

    def get_draft(
        self,
        tenant_id: str,
        actor_id: str,
        draft_id: str,
        version: int | None = None,
    ) -> CareerDraft | None:
        query = select(draft_versions).where(
            draft_versions.c.tenant_id == tenant_id,
            draft_versions.c.owner_actor_id == actor_id,
            draft_versions.c.draft_id == draft_id,
        )
        query = (
            query.where(draft_versions.c.version == version)
            if version is not None
            else query.order_by(draft_versions.c.version.desc()).limit(1)
        )
        with self._engine.connect() as connection:
            row = connection.execute(query).mappings().first()
        return _draft_from_row(dict(row)) if row else None

    def save_approval(
        self, approval: ApprovalRecord, expected_revision: int | None = None
    ) -> None:
        values = _approval_values(approval)
        with self._engine.begin() as connection:
            if expected_revision is None:
                connection.execute(insert(approvals).values(**values))
                return
            result = connection.execute(
                update(approvals)
                .where(
                    approvals.c.tenant_id == approval.tenant_id,
                    approvals.c.approval_id == approval.approval_id,
                    approvals.c.revision == expected_revision,
                )
                .values(**values)
            )
            if result.rowcount != 1:
                raise ApprovalConflictError("stale_approval_revision")

    def get_approval(
        self, tenant_id: str, actor_id: str, approval_id: str
    ) -> ApprovalRecord | None:
        query = select(approvals).where(
            and_(
                approvals.c.tenant_id == tenant_id,
                approvals.c.owner_actor_id == actor_id,
                approvals.c.approval_id == approval_id,
            )
        )
        with self._engine.connect() as connection:
            row = connection.execute(query).mappings().first()
        if not row:
            return None
        values = dict(row)
        values.pop("updated_at")
        values["status"] = ApprovalStatus(str(values["status"]))
        return ApprovalRecord(**values)


def _draft_values(draft: CareerDraft) -> dict[str, object]:
    return {
        "draft_id": draft.draft_id,
        "tenant_id": draft.tenant_id,
        "owner_actor_id": draft.owner_actor_id,
        "profile_id": draft.profile_id,
        "kind": draft.kind.value,
        "version": draft.version,
        "title": draft.title,
        "sections_json": json.dumps(draft.sections),
        "claims_json": json.dumps(
            [
                {
                    "claim_id": item.claim_id,
                    "text": item.text,
                    "status": item.status.value,
                    "citations": [asdict(citation) for citation in item.citations],
                }
                for item in draft.claims
            ]
        ),
        "content_hash": draft.content_hash,
        "pii_flags_json": json.dumps(draft.pii_flags),
        "policy_flags_json": json.dumps(draft.policy_flags),
        "created_at": datetime.now(UTC),
    }


def _draft_from_row(row: dict[str, object]) -> CareerDraft:
    claims = json.loads(str(row["claims_json"]))
    return CareerDraft(
        draft_id=str(row["draft_id"]),
        tenant_id=str(row["tenant_id"]),
        owner_actor_id=str(row["owner_actor_id"]),
        profile_id=str(row["profile_id"]),
        kind=DraftKind(str(row["kind"])),
        version=int(str(row["version"])),
        title=str(row["title"]),
        sections=tuple(json.loads(str(row["sections_json"]))),
        claims=tuple(
            DraftClaim(
                item["claim_id"],
                item["text"],
                ClaimStatus(item["status"]),
                tuple(Citation(**citation) for citation in item["citations"]),
            )
            for item in claims
        ),
        content_hash=str(row["content_hash"]),
        pii_flags=tuple(json.loads(str(row["pii_flags_json"]))),
        policy_flags=tuple(json.loads(str(row["policy_flags_json"]))),
    )


def _approval_values(approval: ApprovalRecord) -> dict[str, object]:
    return {
        "approval_id": approval.approval_id,
        "tenant_id": approval.tenant_id,
        "owner_actor_id": approval.owner_actor_id,
        "draft_id": approval.draft_id,
        "draft_version": approval.draft_version,
        "draft_hash": approval.draft_hash,
        "status": approval.status.value,
        "revision": approval.revision,
        "feedback": approval.feedback,
        "updated_at": datetime.now(UTC),
    }
