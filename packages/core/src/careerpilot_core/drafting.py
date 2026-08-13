"""Truthful draft and exact-version human approval domain model."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from careerpilot_core.retrieval import Citation


class DraftKind(StrEnum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"


class ClaimStatus(StrEnum):
    SUPPORTED = "supported"
    SUGGESTION = "suggestion_requires_confirmation"
    BLOCKED = "blocked"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EDITED_AND_APPROVED = "edited_and_approved"
    REJECTED = "rejected"
    MORE_INFORMATION = "more_information"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    EDIT_AND_APPROVE = "edit_and_approve"
    REJECT = "reject"
    REQUEST_MORE_INFORMATION = "request_more_information"
    CANCEL = "cancel"


@dataclass(frozen=True, slots=True)
class DraftClaim:
    claim_id: str
    text: str
    status: ClaimStatus
    citations: tuple[Citation, ...] = ()


@dataclass(frozen=True, slots=True)
class CareerDraft:
    draft_id: str
    tenant_id: str
    owner_actor_id: str
    profile_id: str
    kind: DraftKind
    version: int
    title: str
    sections: tuple[str, ...]
    claims: tuple[DraftClaim, ...]
    content_hash: str
    pii_flags: tuple[str, ...] = ()
    policy_flags: tuple[str, ...] = ()

    @staticmethod
    def hash_content(
        title: str, sections: tuple[str, ...], claims: tuple[DraftClaim, ...]
    ) -> str:
        value = json.dumps(
            {
                "title": title,
                "sections": sections,
                "claims": [
                    {
                        "text": claim.text,
                        "status": claim.status.value,
                        "citations": [
                            {
                                "document_id": citation.document_id,
                                "chunk_id": citation.chunk_id,
                                "document_title": citation.document_title,
                                "filename": citation.filename,
                                "page_number": citation.page_number,
                                "start_offset": citation.start_offset,
                                "end_offset": citation.end_offset,
                            }
                            for citation in claim.citations
                        ],
                    }
                    for claim in claims
                ],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    approval_id: str
    tenant_id: str
    owner_actor_id: str
    draft_id: str
    draft_version: int
    draft_hash: str
    status: ApprovalStatus
    revision: int
    feedback: str | None = None

    def decide(
        self,
        decision: ApprovalDecision,
        *,
        expected_revision: int,
        expected_draft_version: int,
        expected_draft_hash: str,
        feedback: str | None = None,
    ) -> ApprovalRecord:
        """Apply one valid transition while binding the reviewed bytes and revision."""
        if self.status is not ApprovalStatus.PENDING:
            raise ApprovalTransitionError("approval_not_pending")
        if expected_revision != self.revision:
            raise ApprovalConflictError("stale_approval_revision")
        if (
            expected_draft_version != self.draft_version
            or expected_draft_hash != self.draft_hash
        ):
            raise ApprovalConflictError("stale_draft_version")
        if decision is ApprovalDecision.EDIT_AND_APPROVE and self.draft_version <= 1:
            raise ApprovalTransitionError("edited_version_required")
        target = {
            ApprovalDecision.APPROVE: ApprovalStatus.APPROVED,
            ApprovalDecision.EDIT_AND_APPROVE: ApprovalStatus.EDITED_AND_APPROVED,
            ApprovalDecision.REJECT: ApprovalStatus.REJECTED,
            ApprovalDecision.REQUEST_MORE_INFORMATION: ApprovalStatus.MORE_INFORMATION,
            ApprovalDecision.CANCEL: ApprovalStatus.CANCELLED,
        }[decision]
        if (
            target in {ApprovalStatus.REJECTED, ApprovalStatus.MORE_INFORMATION}
            and not feedback
        ):
            raise ApprovalTransitionError("feedback_required")
        return replace(
            self, status=target, revision=self.revision + 1, feedback=feedback
        )

    def expire(self, *, expected_revision: int) -> ApprovalRecord:
        """Expire a pending record; scheduling belongs to Temporal later."""
        if self.status is not ApprovalStatus.PENDING:
            raise ApprovalTransitionError("approval_not_pending")
        if expected_revision != self.revision:
            raise ApprovalConflictError("stale_approval_revision")
        return replace(self, status=ApprovalStatus.EXPIRED, revision=self.revision + 1)


class ApprovalConflictError(RuntimeError):
    """A concurrent or stale human decision cannot bind to current state."""


class ApprovalTransitionError(ValueError):
    """The requested approval transition violates the deterministic state machine."""


class DraftRepository(Protocol):
    def save_draft(self, draft: CareerDraft) -> None: ...
    def get_draft(
        self, tenant_id: str, actor_id: str, draft_id: str, version: int | None = None
    ) -> CareerDraft | None: ...
    def save_approval(
        self, approval: ApprovalRecord, expected_revision: int | None = None
    ) -> None: ...
    def get_approval(
        self, tenant_id: str, actor_id: str, approval_id: str
    ) -> ApprovalRecord | None: ...
