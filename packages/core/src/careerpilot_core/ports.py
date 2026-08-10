"""Ports owned by the core and implemented by outward adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from careerpilot_core.models import ProfessionalProfile


class ProfileRepository(Protocol):
    """Store and retrieve the minimal profile used by this phase."""

    def save(self, profile: ProfessionalProfile) -> None:
        """Persist a profile for later analysis."""

    def get(self, profile_id: str) -> ProfessionalProfile | None:
        """Return a profile or ``None`` when it does not exist."""
