"""Deterministic application service for the Phase 2 journey."""

from __future__ import annotations

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
from careerpilot_core.models import (
    Education,
    EvidenceItem,
    EvidenceState,
    Experience,
    JobAnalysis,
    ProfessionalProfile,
    Skill,
)
from careerpilot_core.ports import StaleProfileVersionError

if TYPE_CHECKING:
    from collections.abc import Callable

    from careerpilot_core.ports import ProfileRepository

WORD_PATTERN = re.compile(r"[a-z][a-z0-9+#.-]{2,}")
STOP_WORDS = frozenset(
    {"and", "are", "for", "from", "have", "the", "this", "with", "you", "your"}
)
MIN_EVIDENCE_TITLE_LENGTH = 2
MAX_EVIDENCE_TITLE_LENGTH = 200


class ProfileNotFoundError(LookupError):
    """Raised when analysis references a profile absent from the repository."""


class ProfileConflictError(RuntimeError):
    """Raised when a client attempts to overwrite a newer profile version."""


class ProfileValidationError(ValueError):
    """Raised when profile aggregate input violates a domain invariant."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(reason)
        self.field = field
        self.reason = reason


class EvidenceValidationError(ValueError):
    """Raised when evidence metadata violates the upload security policy."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(reason)
        self.field = field
        self.reason = reason


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

    def get_profile(
        self, context: AuthorizationContext, profile_id: str
    ) -> ProfessionalProfile:
        """Return one authorized active profile without revealing foreign IDs."""
        profile = self._repository.get(profile_id, context)
        if profile is None:
            self._audit(
                context,
                action="profile.read",
                outcome="denied",
                reason="profile_unavailable",
                resource_type="profile",
                resource_id=profile_id,
            )
            raise ProfileNotFoundError(profile_id)
        self._require_and_audit(
            context,
            Permission.PROFILE_READ,
            self._resource(profile),
            resource_type="profile",
            resource_id=profile.profile_id,
        )
        self._audit(
            context,
            action="profile.read",
            outcome="allowed",
            reason="read",
            resource_type="profile",
            resource_id=profile.profile_id,
        )
        return profile

    def update_profile(
        self,
        context: AuthorizationContext,
        profile_id: str,
        *,
        display_name: str,
        professional_summary: str,
        skill_names: tuple[str, ...],
        expected_version: int,
        experiences: tuple[Experience, ...] = (),
        education: tuple[Education, ...] = (),
    ) -> ProfessionalProfile:
        """Validate and atomically update a profile using optimistic concurrency."""
        current = self.get_profile(context, profile_id)
        self._require_and_audit(
            context,
            Permission.PROFILE_UPDATE,
            self._resource(current),
            resource_type="profile",
            resource_id=profile_id,
        )
        normalized_skills = tuple(name.strip() for name in skill_names)
        if len({name.casefold() for name in normalized_skills}) != len(
            normalized_skills
        ):
            raise ProfileValidationError("skills", "duplicate_skill")
        updated = replace(
            current,
            display_name=display_name.strip(),
            professional_summary=professional_summary.strip(),
            skills=tuple(Skill(name=name) for name in normalized_skills),
            experiences=experiences,
            education=education,
        )
        try:
            saved = self._repository.update(updated, expected_version, context)
        except StaleProfileVersionError as error:
            self._audit(
                context,
                action="profile.update",
                outcome="denied",
                reason="stale_version",
                resource_type="profile",
                resource_id=profile_id,
            )
            raise ProfileConflictError from error
        self._audit(
            context,
            action="profile.update",
            outcome="allowed",
            reason="updated",
            resource_type="profile",
            resource_id=profile_id,
        )
        return saved

    def add_evidence(
        self,
        context: AuthorizationContext,
        profile_id: str,
        *,
        title: str,
        filename: str,
        media_type: str,
        size_bytes: int,
    ) -> EvidenceItem:
        """Persist minimized metadata in quarantine; never mark unscanned data clean."""
        profile = self.get_profile(context, profile_id)
        self._require_and_audit(
            context,
            Permission.EVIDENCE_CREATE,
            self._resource(profile),
            resource_type="profile",
            resource_id=profile_id,
        )
        title_length = len(title.strip())
        if not MIN_EVIDENCE_TITLE_LENGTH <= title_length <= MAX_EVIDENCE_TITLE_LENGTH:
            raise EvidenceValidationError("title", "title_not_allowed")
        safe_filename = self._validate_evidence(filename, media_type, size_bytes)
        evidence = EvidenceItem(
            evidence_id=self._id_factory(),
            tenant_id=context.tenant_id,
            owner_actor_id=profile.owner_actor_id,
            profile_id=profile_id,
            title=title.strip(),
            filename=safe_filename,
            media_type=media_type,
            size_bytes=size_bytes,
            state=EvidenceState.QUARANTINED,
        )
        saved = self._repository.add_evidence(evidence, context)
        self._audit(
            context,
            action="evidence.create",
            outcome="allowed",
            reason="metadata_quarantined",
            resource_type="evidence",
            resource_id=saved.evidence_id,
        )
        return saved

    def list_evidence(
        self, context: AuthorizationContext, profile_id: str
    ) -> tuple[EvidenceItem, ...]:
        """List authorized evidence metadata for an active profile."""
        profile = self.get_profile(context, profile_id)
        self._require_and_audit(
            context,
            Permission.EVIDENCE_READ,
            self._resource(profile),
            resource_type="profile",
            resource_id=profile_id,
        )
        return self._repository.list_evidence(profile_id, context)

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

    @staticmethod
    def _resource(profile: ProfessionalProfile) -> ResourceAttributes:
        return ResourceAttributes(
            tenant_id=profile.tenant_id,
            owner_actor_id=profile.owner_actor_id,
            state="deleted" if profile.deleted_at else "active",
        )

    @staticmethod
    def _validate_evidence(filename: str, media_type: str, size_bytes: int) -> str:
        allowed_types = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png",
        }
        if size_bytes < 1 or size_bytes > 10 * 1024 * 1024:
            raise EvidenceValidationError("size_bytes", "size_not_allowed")
        expected_suffix = allowed_types.get(media_type)
        if expected_suffix is None:
            raise EvidenceValidationError("media_type", "media_type_not_allowed")
        normalized = PurePath(filename.replace("\\", "/")).name.strip()
        if not normalized or normalized in {".", ".."} or "\x00" in normalized:
            raise EvidenceValidationError("filename", "filename_not_allowed")
        suffix = PurePath(normalized).suffix.casefold()
        accepted_suffixes = {expected_suffix}
        if media_type == "image/jpeg":
            accepted_suffixes.add(".jpeg")
        if suffix not in accepted_suffixes:
            raise EvidenceValidationError("filename", "extension_mismatch")
        return normalized
