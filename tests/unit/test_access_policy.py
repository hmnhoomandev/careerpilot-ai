"""Permission-matrix and contextual ABAC tests."""

from __future__ import annotations

import pytest

from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    Permission,
    ResourceAttributes,
    Role,
)
from careerpilot_core.access import ROLE_PERMISSIONS


def context(role: Role, actor_id: str = "actor-ada") -> AuthorizationContext:
    return AuthorizationContext(
        actor_id=actor_id,
        tenant_id="tenant-ada",
        role=role,
        purpose="personal_career_support",
        correlation_id="correlation-001",
    )


@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("permission", list(Permission))
def test_rbac_permission_matrix(role: Role, permission: Permission) -> None:
    decision = AccessPolicy().decide(context(role), permission)

    if permission in AccessPolicy.RESOURCE_PERMISSIONS:
        assert not decision.allowed
        assert decision.reason in {
            "resource_context_required",
            "role_permission_missing",
        }
    else:
        assert decision.allowed is (permission in ROLE_PERMISSIONS[role])


def test_abac_allows_owner_and_denies_foreign_tenant() -> None:
    policy = AccessPolicy()
    owned = ResourceAttributes("tenant-ada", "actor-ada")
    foreign = ResourceAttributes("tenant-grace", "actor-grace")

    assert policy.decide(context(Role.OWNER), Permission.PROFILE_READ, owned).allowed
    denial = policy.decide(context(Role.OWNER), Permission.PROFILE_READ, foreign)
    assert not denial.allowed
    assert denial.reason == "tenant_mismatch"


def test_document_and_tool_permissions_fail_closed_without_resource() -> None:
    policy = AccessPolicy()

    for permission in (Permission.DOCUMENT_READ, Permission.TOOL_INVOKE):
        decision = policy.decide(context(Role.OWNER), permission)
        assert not decision.allowed
        assert decision.reason == "resource_context_required"


def test_coach_requires_explicit_delegation_and_cannot_read_restricted_resource() -> (
    None
):
    policy = AccessPolicy()
    coach = context(Role.COACH, actor_id="actor-coach")
    ordinary = ResourceAttributes(
        "tenant-ada",
        "actor-ada",
        delegated_actor_ids=frozenset({"actor-coach"}),
    )
    restricted = ResourceAttributes(
        "tenant-ada",
        "actor-ada",
        sensitivity="restricted",
        delegated_actor_ids=frozenset({"actor-coach"}),
    )

    assert policy.decide(coach, Permission.PROFILE_READ, ordinary).allowed
    assert not policy.decide(coach, Permission.PROFILE_READ, restricted).allowed
