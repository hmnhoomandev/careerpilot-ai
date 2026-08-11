"""Thread-safe in-memory adapter for default offline tests and local fallback."""

from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import TYPE_CHECKING

from careerpilot_core.ports import StaleProfileVersionError

if TYPE_CHECKING:
    from careerpilot_core import AuthorizationContext, EvidenceItem, ProfessionalProfile


class InMemoryProfileRepository:
    """Store profiles until process restart; this is intentionally non-durable."""

    def __init__(self) -> None:
        self._profiles: dict[str, ProfessionalProfile] = {}
        self._evidence: dict[str, EvidenceItem] = {}
        self._lock = RLock()

    def save(self, profile: ProfessionalProfile, context: AuthorizationContext) -> None:
        if profile.tenant_id != context.tenant_id:
            raise PermissionError("tenant_mismatch")
        with self._lock:
            self._profiles[profile.profile_id] = profile

    def get(
        self, profile_id: str, context: AuthorizationContext
    ) -> ProfessionalProfile | None:
        with self._lock:
            profile = self._profiles.get(profile_id)
            if profile is None or profile.tenant_id != context.tenant_id:
                return None
            return profile

    def update(
        self,
        profile: ProfessionalProfile,
        expected_version: int,
        context: AuthorizationContext,
    ) -> ProfessionalProfile:
        """Apply a tenant-scoped compare-and-swap update."""
        if profile.tenant_id != context.tenant_id:
            raise PermissionError("tenant_mismatch")
        with self._lock:
            stored = self._profiles.get(profile.profile_id)
            if (
                stored is None
                or stored.tenant_id != context.tenant_id
                or stored.version != expected_version
            ):
                raise StaleProfileVersionError
            updated = replace(profile, version=expected_version + 1)
            self._profiles[profile.profile_id] = updated
            return updated

    def add_evidence(
        self, evidence: EvidenceItem, context: AuthorizationContext
    ) -> EvidenceItem:
        """Atomically require the owning profile before storing metadata."""
        if evidence.tenant_id != context.tenant_id:
            raise PermissionError("tenant_mismatch")
        with self._lock:
            profile = self._profiles.get(evidence.profile_id)
            if profile is None or profile.tenant_id != context.tenant_id:
                raise KeyError(evidence.profile_id)
            self._evidence[evidence.evidence_id] = evidence
            return evidence

    def list_evidence(
        self, profile_id: str, context: AuthorizationContext
    ) -> tuple[EvidenceItem, ...]:
        """List only active evidence from the authenticated tenant."""
        with self._lock:
            return tuple(
                item
                for item in self._evidence.values()
                if item.profile_id == profile_id
                and item.tenant_id == context.tenant_id
                and item.deleted_at is None
            )
