"""Temporary process-local repository adapter for Phase 2."""

from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from careerpilot_core import AuthorizationContext, ProfessionalProfile


class InMemoryProfileRepository:
    """Store profiles until process restart; this is intentionally non-durable."""

    def __init__(self) -> None:
        self._profiles: dict[str, ProfessionalProfile] = {}
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
