"""Unit tests for authorized deterministic application behavior."""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import TYPE_CHECKING

import pytest

from careerpilot_core import (
    AccessPolicy,
    AuditEvent,
    AuditEventDraft,
    AuthorizationContext,
    CareerJourneyService,
    EvidenceItem,
    ProfessionalProfile,
    ProfileNotFoundError,
    Role,
)
from careerpilot_core.ports import StaleProfileVersionError

if TYPE_CHECKING:
    from collections.abc import Iterator


class FakeProfileRepository:
    def __init__(self) -> None:
        self.profiles: dict[str, ProfessionalProfile] = {}

    def save(self, profile: ProfessionalProfile, context: AuthorizationContext) -> None:
        assert profile.tenant_id == context.tenant_id
        self.profiles[profile.profile_id] = profile

    def get(
        self, profile_id: str, context: AuthorizationContext
    ) -> ProfessionalProfile | None:
        profile = self.profiles.get(profile_id)
        return profile if profile and profile.tenant_id == context.tenant_id else None

    def update(
        self,
        profile: ProfessionalProfile,
        expected_version: int,
        context: AuthorizationContext,
    ) -> ProfessionalProfile:
        stored = self.get(profile.profile_id, context)
        if stored is None or stored.version != expected_version:
            raise StaleProfileVersionError
        updated = replace(profile, version=expected_version + 1)
        self.profiles[profile.profile_id] = updated
        return updated

    def add_evidence(
        self, evidence: EvidenceItem, context: AuthorizationContext
    ) -> EvidenceItem:
        assert evidence.tenant_id == context.tenant_id
        return evidence

    def list_evidence(
        self, profile_id: str, context: AuthorizationContext
    ) -> tuple[EvidenceItem, ...]:
        del profile_id, context
        return ()


class FakeAuditSink:
    def __init__(self) -> None:
        self.drafts: list[AuditEventDraft] = []

    def append(self, draft: AuditEventDraft) -> AuditEvent:
        self.drafts.append(draft)
        raise NotImplementedError

    def list_for_tenant(self, tenant_id: str) -> tuple[AuditEvent, ...]:
        del tenant_id
        return ()


class RecordingAuditSink(FakeAuditSink):
    def append(self, draft: AuditEventDraft) -> AuditEvent:
        self.drafts.append(draft)
        return AuditEvent(
            event_id="event",
            occurred_at="2026-08-10T00:00:00+00:00",
            previous_hash="0" * 64,
            event_hash="1" * 64,
            **asdict(draft),
        )


def sequential_ids() -> Iterator[str]:
    yield "profile-001"
    yield "analysis-001"


def context(tenant_id: str = "tenant-ada") -> AuthorizationContext:
    return AuthorizationContext(
        actor_id="actor-ada",
        tenant_id=tenant_id,
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="correlation-001",
    )


def test_journey_creates_tenant_profile_and_compares_exact_terms() -> None:
    identifiers = sequential_ids()
    repository = FakeProfileRepository()
    audit = RecordingAuditSink()
    service = CareerJourneyService(
        repository,
        AccessPolicy(),
        audit,
        id_factory=lambda: next(identifiers),
    )

    profile = service.create_profile(
        context(),
        "Ada Example",
        "Python engineer building accessible data platforms.",
    )
    analysis = service.analyze_job(
        context(),
        profile.profile_id,
        "We need a Python engineer to build reliable and accessible services.",
    )

    assert profile.tenant_id == "tenant-ada"
    assert analysis.shared_terms == ("accessible", "engineer", "python")
    assert [event.outcome for event in audit.drafts] == ["allowed", "allowed"]


def test_journey_hides_profile_from_foreign_tenant() -> None:
    repository = FakeProfileRepository()
    audit = RecordingAuditSink()
    service = CareerJourneyService(repository, AccessPolicy(), audit)
    profile = service.create_profile(
        context(), "Ada Example", "Synthetic professional summary for Ada."
    )

    with pytest.raises(ProfileNotFoundError):
        service.analyze_job(
            context("tenant-grace"),
            profile.profile_id,
            "A sufficiently long synthetic job description for testing.",
        )

    assert audit.drafts[-1].reason == "profile_unavailable"
