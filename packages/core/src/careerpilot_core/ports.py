"""Ports owned by the core and implemented by outward adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from careerpilot_core.access import AuthorizationContext
    from careerpilot_core.models import ProfessionalProfile


class ProfileRepository(Protocol):
    """Store and retrieve the minimal profile used by this phase."""

    def save(self, profile: ProfessionalProfile, context: AuthorizationContext) -> None:
        """Persist a profile for later analysis."""

    def get(
        self, profile_id: str, context: AuthorizationContext
    ) -> ProfessionalProfile | None:
        """Return a profile or ``None`` when it does not exist."""


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    """Minimal verified identity returned by an OIDC-compatible adapter."""

    issuer: str
    subject: str


class IdentityVerifier(Protocol):
    """Production boundary for validating an external identity assertion."""

    def verify(self, token: str) -> ExternalIdentity:
        """Validate issuer/audience/signature/time and return stable identity."""
