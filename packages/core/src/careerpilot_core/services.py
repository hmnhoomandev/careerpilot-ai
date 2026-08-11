"""Deterministic application service for the Phase 2 journey."""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

from careerpilot_core.access import (
    AccessDeniedError,
    AccessPolicy,
    AuthorizationContext,
    Permission,
    ResourceAttributes,
)
from careerpilot_core.audit import AuditEventDraft, AuditOutcome, AuditSink
from careerpilot_core.models import JobAnalysis, ProfessionalProfile

if TYPE_CHECKING:
    from collections.abc import Callable

    from careerpilot_core.ports import ProfileRepository

WORD_PATTERN = re.compile(r"[a-z][a-z0-9+#.-]{2,}")
STOP_WORDS = frozenset(
    {"and", "are", "for", "from", "have", "the", "this", "with", "you", "your"}
)


class ProfileNotFoundError(LookupError):
    """Raised when analysis references a profile absent from the repository."""


class CareerJourneyService:
    """Coordinate profile creation and deterministic placeholder analysis."""

    def __init__(
        self,
        repository: ProfileRepository,
        access_policy: AccessPolicy,
        audit_sink: AuditSink,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._access_policy = access_policy
        self._audit_sink = audit_sink
        self._id_factory = id_factory or (lambda: str(uuid.uuid4()))

    def create_profile(
        self,
        context: AuthorizationContext,
        display_name: str,
        professional_summary: str,
    ) -> ProfessionalProfile:
        """Create and persist a minimal professional profile."""
        self._require_and_audit(context, Permission.PROFILE_CREATE)
        profile = ProfessionalProfile(
            profile_id=self._id_factory(),
            tenant_id=context.tenant_id,
            owner_actor_id=context.actor_id,
            display_name=display_name.strip(),
            professional_summary=professional_summary.strip(),
        )
        self._repository.save(profile, context)
        self._audit(
            context,
            action="profile.create",
            outcome="allowed",
            reason="created",
            resource_type="profile",
            resource_id=profile.profile_id,
        )
        return profile

    def analyze_job(
        self,
        context: AuthorizationContext,
        profile_id: str,
        job_description: str,
    ) -> JobAnalysis:
        """Compare normalized terms without inference, ranking, or a model call."""
        profile = self._repository.get(profile_id, context)
        if profile is None:
            self._audit(
                context,
                action="analysis.run",
                outcome="denied",
                reason="profile_unavailable",
                resource_type="profile",
                resource_id=profile_id,
            )
            raise ProfileNotFoundError(profile_id)
        resource = ResourceAttributes(
            tenant_id=profile.tenant_id,
            owner_actor_id=profile.owner_actor_id,
        )
        self._require_and_audit(
            context,
            Permission.ANALYSIS_RUN,
            resource,
            resource_type="profile",
            resource_id=profile.profile_id,
        )

        profile_terms = self._meaningful_terms(profile.professional_summary)
        job_terms = self._meaningful_terms(job_description)
        shared_terms = tuple(sorted(profile_terms & job_terms)[:8])
        if shared_terms:
            shared_text = ", ".join(shared_terms)
            summary = f"The supplied texts share these exact terms: {shared_text}."
        else:
            summary = "No exact meaningful terms were shared by the supplied texts."

        analysis = JobAnalysis(
            analysis_id=self._id_factory(),
            profile_id=profile.profile_id,
            tenant_id=profile.tenant_id,
            headline=f"Placeholder analysis for {profile.display_name}",
            summary=summary,
            shared_terms=shared_terms,
            disclaimer=(
                "Deterministic text comparison only. This is not an AI assessment "
                "and does not infer skills, suitability, or hiring outcomes."
            ),
        )
        self._audit(
            context,
            action="analysis.run",
            outcome="allowed",
            reason="completed",
            resource_type="profile",
            resource_id=profile.profile_id,
        )
        return analysis

    def _require_and_audit(
        self,
        context: AuthorizationContext,
        permission: Permission,
        resource: ResourceAttributes | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        try:
            self._access_policy.require(context, permission, resource)
        except AccessDeniedError as error:
            self._audit(
                context,
                action=permission,
                outcome="denied",
                reason=error.reason,
                resource_type=resource_type,
                resource_id=resource_id,
            )
            raise

    def _audit(
        self,
        context: AuthorizationContext,
        *,
        action: str,
        outcome: AuditOutcome,
        reason: str,
        resource_type: str | None = None,
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
                resource_type=resource_type,
                resource_id=resource_id,
            )
        )

    @staticmethod
    def _meaningful_terms(text: str) -> set[str]:
        return {
            term
            for term in WORD_PATTERN.findall(text.casefold())
            if term not in STOP_WORDS
        }
