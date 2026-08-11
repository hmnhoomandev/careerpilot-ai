"""Repository-layer tenant enforcement tests."""

from __future__ import annotations

import pytest

from careerpilot_api.repository import InMemoryProfileRepository
from careerpilot_core import AuthorizationContext, ProfessionalProfile, Role


def context(tenant_id: str) -> AuthorizationContext:
    return AuthorizationContext(
        actor_id="actor-ada",
        tenant_id=tenant_id,
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="correlation-001",
    )


def test_repository_requires_matching_context_for_write_and_read() -> None:
    repository = InMemoryProfileRepository()
    profile = ProfessionalProfile(
        profile_id="profile-001",
        tenant_id="tenant-ada",
        owner_actor_id="actor-ada",
        display_name="Ada Example",
        professional_summary="Synthetic summary for repository isolation testing.",
    )

    with pytest.raises(PermissionError):
        repository.save(profile, context("tenant-grace"))

    repository.save(profile, context("tenant-ada"))
    assert repository.get(profile.profile_id, context("tenant-grace")) is None
    assert repository.get(profile.profile_id, context("tenant-ada")) == profile
