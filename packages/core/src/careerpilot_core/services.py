"""Deterministic application service for the Phase 2 journey."""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

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
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._id_factory = id_factory or (lambda: str(uuid.uuid4()))

    def create_profile(
        self, display_name: str, professional_summary: str
    ) -> ProfessionalProfile:
        """Create and persist a minimal professional profile."""
        profile = ProfessionalProfile(
            profile_id=self._id_factory(),
            display_name=display_name.strip(),
            professional_summary=professional_summary.strip(),
        )
        self._repository.save(profile)
        return profile

    def analyze_job(self, profile_id: str, job_description: str) -> JobAnalysis:
        """Compare normalized terms without inference, ranking, or a model call."""
        profile = self._repository.get(profile_id)
        if profile is None:
            raise ProfileNotFoundError(profile_id)

        profile_terms = self._meaningful_terms(profile.professional_summary)
        job_terms = self._meaningful_terms(job_description)
        shared_terms = tuple(sorted(profile_terms & job_terms)[:8])
        if shared_terms:
            shared_text = ", ".join(shared_terms)
            summary = f"The supplied texts share these exact terms: {shared_text}."
        else:
            summary = "No exact meaningful terms were shared by the supplied texts."

        return JobAnalysis(
            analysis_id=self._id_factory(),
            profile_id=profile.profile_id,
            headline=f"Placeholder analysis for {profile.display_name}",
            summary=summary,
            shared_terms=shared_terms,
            disclaimer=(
                "Deterministic text comparison only. This is not an AI assessment "
                "and does not infer skills, suitability, or hiring outcomes."
            ),
        )

    @staticmethod
    def _meaningful_terms(text: str) -> set[str]:
        return {
            term
            for term in WORD_PATTERN.findall(text.casefold())
            if term not in STOP_WORDS
        }
