"""Local authentication safety-gate tests."""

from __future__ import annotations

import pytest

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.security import (
    InMemoryIdentityAccess,
    LocalAuthenticationDisabledError,
    TenantMembershipError,
)


def test_local_authentication_refuses_non_local_environment() -> None:
    with pytest.raises(LocalAuthenticationDisabledError):
        InMemoryIdentityAccess(InMemoryAuditLog(), environment="production")


def test_tenant_context_comes_from_active_membership() -> None:
    identity = InMemoryIdentityAccess(InMemoryAuditLog())
    session = identity.login("ada", "correlation-001")

    context = identity.context_for(session.token, "tenant-ada", "correlation-002")
    assert context.actor_id == "actor-ada"
    assert context.role.value == "owner"

    with pytest.raises(TenantMembershipError):
        identity.context_for(session.token, "tenant-grace", "correlation-003")
