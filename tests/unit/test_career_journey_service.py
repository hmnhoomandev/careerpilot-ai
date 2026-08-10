"""Unit tests for deterministic Phase 2 application behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from careerpilot_core import (
    CareerJourneyService,
    ProfessionalProfile,
    ProfileNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class FakeProfileRepository:
    """Small test adapter that makes service behavior observable."""

    def __init__(self) -> None:
        self.profiles: dict[str, ProfessionalProfile] = {}

    def save(self, profile: ProfessionalProfile) -> None:
        self.profiles[profile.profile_id] = profile

    def get(self, profile_id: str) -> ProfessionalProfile | None:
        return self.profiles.get(profile_id)


def sequential_ids() -> Iterator[str]:
    yield "profile-001"
    yield "analysis-001"


def test_journey_creates_profile_and_compares_exact_terms() -> None:
    identifiers = sequential_ids()
    repository = FakeProfileRepository()
    service = CareerJourneyService(repository, id_factory=lambda: next(identifiers))

    profile = service.create_profile(
        "Ada Example", "Python engineer building accessible data platforms."
    )
    analysis = service.analyze_job(
        profile.profile_id,
        "We need a Python engineer to build reliable and accessible services.",
    )

    assert profile.profile_id == "profile-001"
    assert analysis.analysis_id == "analysis-001"
    assert analysis.shared_terms == ("accessible", "engineer", "python")
    assert "not an AI assessment" in analysis.disclaimer


def test_journey_rejects_unknown_profile() -> None:
    service = CareerJourneyService(FakeProfileRepository())

    with pytest.raises(ProfileNotFoundError):
        service.analyze_job("missing", "A sufficiently long synthetic job description.")
