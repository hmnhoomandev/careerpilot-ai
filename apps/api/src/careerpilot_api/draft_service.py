"""Evidence-only draft generation and deterministic approval coordination."""

from __future__ import annotations

import re
import uuid
from dataclasses import replace
from typing import TYPE_CHECKING

from careerpilot_core import (
    AccessPolicy,
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStatus,
    AuditEventDraft,
    AuthorizationContext,
    CareerDraft,
    ClaimStatus,
    DraftClaim,
    DraftKind,
    Permission,
    ResourceAttributes,
)

if TYPE_CHECKING:
    from careerpilot_core import (
        AuditSink,
        CareerJourneyService,
        DraftRepository,
        RagService,
    )

PII_PATTERNS = {
    "email": re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b"),
    "phone": re.compile(r"\+?\d[\d\s().-]{7,}\d"),
}
BIAS_TERMS = re.compile(
    r"\b(young|native[- ]born|able[- ]bodied|male|female)\b", re.IGNORECASE
)


class DraftNotFoundError(LookupError):
    """Hide absent and foreign draft/approval identifiers."""


class DraftPolicyError(ValueError):
    """A generated or edited draft violates truth/privacy/bias policy."""


class DraftService:
    """Generate cited drafts and coordinate exact-version human decisions."""

    def __init__(
        self,
        journey: CareerJourneyService,
        rag: RagService,
        repository: DraftRepository,
        policy: AccessPolicy,
        audit: AuditSink,
    ) -> None:
        self._journey = journey
        self._rag = rag
        self._repository = repository
        self._policy = policy
        self._audit = audit

    def generate(
        self,
        context: AuthorizationContext,
        profile_id: str,
        kind: DraftKind,
        job_description: str,
    ) -> tuple[CareerDraft, ApprovalRecord]:
        profile = self._journey.get_profile(context, profile_id)
        self._require(context, profile.owner_actor_id)
        evidence = self._rag.search(context, job_description[:500], 5)
        claims = tuple(
            DraftClaim(
                claim_id=str(uuid.uuid4()),
                text=passage.content.strip(),
                status=ClaimStatus.SUPPORTED,
                citations=(passage.citation,),
            )
            for passage in evidence.passages
        )
        sections = self._sections(kind, profile.display_name, claims)
        pii_flags = tuple(
            name
            for name, pattern in PII_PATTERNS.items()
            if pattern.search(" ".join(sections))
        )
        policy_flags = (
            ("potential_bias_language",)
            if BIAS_TERMS.search(" ".join(sections))
            else ()
        )
        if policy_flags:
            raise DraftPolicyError("bias_policy_blocked")
        draft_id = str(uuid.uuid4())
        content_hash = CareerDraft.hash_content(self._title(kind), sections, claims)
        draft = CareerDraft(
            draft_id,
            context.tenant_id,
            context.actor_id,
            profile_id,
            kind,
            1,
            self._title(kind),
            sections,
            claims,
            content_hash,
            pii_flags,
            policy_flags,
        )
        approval = ApprovalRecord(
            str(uuid.uuid4()),
            context.tenant_id,
            context.actor_id,
            draft_id,
            1,
            content_hash,
            ApprovalStatus.PENDING,
            1,
        )
        self._repository.save_draft(draft)
        self._repository.save_approval(approval)
        self._record(context, "draft.generate", "generated_pending_review", draft_id)
        return draft, approval

    def edit(
        self,
        context: AuthorizationContext,
        draft_id: str,
        expected_version: int,
        sections: tuple[str, ...],
    ) -> tuple[CareerDraft, ApprovalRecord]:
        current = self._draft(context, draft_id)
        if current.version != expected_version:
            raise DraftPolicyError("stale_draft_version")
        joined = " ".join(sections)
        supported_text = " ".join(claim.text for claim in current.claims).casefold()
        if any(
            sentence.strip().casefold() not in supported_text for sentence in sections
        ):
            raise DraftPolicyError("unsupported_edit_blocked")
        updated = replace(
            current,
            version=current.version + 1,
            sections=sections,
            content_hash=CareerDraft.hash_content(
                current.title, sections, current.claims
            ),
            pii_flags=tuple(
                name for name, pattern in PII_PATTERNS.items() if pattern.search(joined)
            ),
        )
        self._repository.save_draft(updated)
        approval = ApprovalRecord(
            str(uuid.uuid4()),
            context.tenant_id,
            context.actor_id,
            updated.draft_id,
            updated.version,
            updated.content_hash,
            ApprovalStatus.PENDING,
            1,
        )
        self._repository.save_approval(approval)
        self._record(context, "draft.edit", "new_version_pending_review", draft_id)
        return updated, approval

    def decide(
        self,
        context: AuthorizationContext,
        approval_id: str,
        decision: ApprovalDecision,
        expected_revision: int,
        expected_draft_version: int,
        expected_draft_hash: str,
        feedback: str | None,
    ) -> ApprovalRecord:
        approval = self._repository.get_approval(
            context.tenant_id, context.actor_id, approval_id
        )
        if approval is None:
            raise DraftNotFoundError(approval_id)
        updated = approval.decide(
            decision,
            expected_revision=expected_revision,
            expected_draft_version=expected_draft_version,
            expected_draft_hash=expected_draft_hash,
            feedback=feedback,
        )
        self._repository.save_approval(updated, expected_revision=expected_revision)
        self._record(
            context,
            "approval.decide",
            f"decision_{updated.status.value}",
            approval_id,
        )
        return updated

    def _draft(self, context: AuthorizationContext, draft_id: str) -> CareerDraft:
        draft = self._repository.get_draft(
            context.tenant_id, context.actor_id, draft_id
        )
        if draft is None:
            raise DraftNotFoundError(draft_id)
        self._require(context, draft.owner_actor_id)
        return draft

    def _require(self, context: AuthorizationContext, owner_actor_id: str) -> None:
        self._policy.require(
            context,
            Permission.ANALYSIS_RUN,
            ResourceAttributes(context.tenant_id, owner_actor_id),
        )

    def _record(
        self,
        context: AuthorizationContext,
        action: str,
        reason: str,
        resource_id: str,
    ) -> None:
        self._audit.append(
            AuditEventDraft(
                tenant_id=context.tenant_id,
                actor_id=context.actor_id,
                action=action,
                outcome="allowed",
                reason=reason,
                correlation_id=context.correlation_id,
                resource_type="career_draft",
                resource_id=resource_id,
            )
        )

    @staticmethod
    def _sections(
        kind: DraftKind, display_name: str, claims: tuple[DraftClaim, ...]
    ) -> tuple[str, ...]:
        if not claims:
            return (f"{display_name}: no supported career claims were found.",)
        prefix = (
            "Evidence-backed resume"
            if kind is DraftKind.RESUME
            else "Evidence-backed application letter"
        )
        return tuple(f"{prefix}: {claim.text}" for claim in claims)

    @staticmethod
    def _title(kind: DraftKind) -> str:
        return (
            "Truthful Resume Draft"
            if kind is DraftKind.RESUME
            else "Truthful Cover Letter Draft"
        )
