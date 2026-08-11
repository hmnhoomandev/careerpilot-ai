"""Ports owned by the core and implemented by outward adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from careerpilot_core.access import AuthorizationContext
    from careerpilot_core.models import EvidenceItem, ProfessionalProfile


class StaleProfileVersionError(RuntimeError):
    """Adapter-neutral signal that an optimistic update lost a race."""


class ProfileRepository(Protocol):
    """Store and retrieve the minimal profile used by this phase."""

    def save(self, profile: ProfessionalProfile, context: AuthorizationContext) -> None:
        """Persist a profile for later analysis."""

    def get(
        self, profile_id: str, context: AuthorizationContext
    ) -> ProfessionalProfile | None:
        """Return a profile or ``None`` when it does not exist."""

    def update(
        self,
        profile: ProfessionalProfile,
        expected_version: int,
        context: AuthorizationContext,
    ) -> ProfessionalProfile:
        """Atomically update a profile or raise on a stale version."""

    def add_evidence(
        self, evidence: EvidenceItem, context: AuthorizationContext
    ) -> EvidenceItem:
        """Persist quarantined evidence metadata in the profile transaction."""

    def list_evidence(
        self, profile_id: str, context: AuthorizationContext
    ) -> tuple[EvidenceItem, ...]:
        """Return active tenant-scoped evidence metadata for a profile."""


class MalwareScanner(Protocol):
    """Boundary for a future scanner; absence must leave evidence quarantined."""

    def request_scan(self, evidence: EvidenceItem) -> None:
        """Request scanning without treating dispatch as a clean result."""


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    """Minimal verified identity returned by an OIDC-compatible adapter."""

    issuer: str
    subject: str


class IdentityVerifier(Protocol):
    """Production boundary for validating an external identity assertion."""

    def verify(self, token: str) -> ExternalIdentity:
        """Validate issuer/audience/signature/time and return stable identity."""
