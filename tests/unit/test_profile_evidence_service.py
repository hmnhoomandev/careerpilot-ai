"""Unit evidence for optimistic profiles and fail-closed evidence metadata."""

from __future__ import annotations

import pytest

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    CareerJourneyService,
    EvidenceState,
    EvidenceValidationError,
    ProfileConflictError,
    ProfileValidationError,
    Role,
)


def context(tenant: str = "tenant-ada") -> AuthorizationContext:
    return AuthorizationContext(
        actor_id="actor-ada",
        tenant_id=tenant,
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="correlation-phase4",
    )


def service() -> CareerJourneyService:
    identifiers = iter(("profile-1", "evidence-1", "evidence-2"))
    return CareerJourneyService(
        InMemoryProfileRepository(),
        AccessPolicy(),
        InMemoryAuditLog(),
        id_factory=lambda: next(identifiers),
    )


def test_profile_update_increments_version_and_rejects_stale_write() -> None:
    journey = service()
    profile = journey.create_profile(
        context(), "Ada Example", "Synthetic summary for tests."
    )
    updated = journey.update_profile(
        context(),
        profile.profile_id,
        display_name="Ada Updated",
        professional_summary="Updated synthetic professional summary.",
        skill_names=("Python", "PostgreSQL"),
        expected_version=1,
    )
    assert updated.version == 2
    assert [skill.name for skill in updated.skills] == ["Python", "PostgreSQL"]
    with pytest.raises(ProfileConflictError):
        journey.update_profile(
            context(),
            profile.profile_id,
            display_name="Stale Update",
            professional_summary="This stale update must never overwrite data.",
            skill_names=(),
            expected_version=1,
        )


def test_evidence_filename_is_normalized_and_stays_quarantined() -> None:
    journey = service()
    profile = journey.create_profile(
        context(), "Ada Example", "Synthetic summary for tests."
    )
    evidence = journey.add_evidence(
        context(),
        profile.profile_id,
        title="Synthetic certificate",
        filename="../../private/certificate.pdf",
        media_type="application/pdf",
        size_bytes=2048,
    )
    assert evidence.filename == "certificate.pdf"
    assert evidence.state is EvidenceState.QUARANTINED


def test_duplicate_skills_are_rejected_before_persistence() -> None:
    journey = service()
    profile = journey.create_profile(
        context(), "Ada Example", "Synthetic summary for tests."
    )
    with pytest.raises(ProfileValidationError) as captured:
        journey.update_profile(
            context(),
            profile.profile_id,
            display_name=profile.display_name,
            professional_summary=profile.professional_summary,
            skill_names=("Python", "python"),
            expected_version=1,
        )
    assert captured.value.field == "skills"


@pytest.mark.parametrize(
    ("filename", "media_type", "size_bytes", "field"),
    [
        ("resume.exe", "application/x-msdownload", 100, "media_type"),
        ("resume.png", "application/pdf", 100, "filename"),
        ("resume.pdf", "application/pdf", 10 * 1024 * 1024 + 1, "size_bytes"),
        ("..", "application/pdf", 100, "filename"),
    ],
)
def test_evidence_policy_rejects_unsafe_metadata(
    filename: str, media_type: str, size_bytes: int, field: str
) -> None:
    journey = service()
    profile = journey.create_profile(
        context(), "Ada Example", "Synthetic summary for tests."
    )
    with pytest.raises(EvidenceValidationError) as captured:
        journey.add_evidence(
            context(),
            profile.profile_id,
            title="Unsafe fixture",
            filename=filename,
            media_type=media_type,
            size_bytes=size_bytes,
        )
    assert captured.value.field == field
