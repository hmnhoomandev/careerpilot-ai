"""Local-only authentication and server-derived tenant context adapter."""

from __future__ import annotations

import secrets
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from careerpilot_core import (
    Actor,
    AuditEventDraft,
    AuthorizationContext,
    Membership,
    Role,
    Tenant,
    TenantKind,
)

if TYPE_CHECKING:
    from careerpilot_api.audit import InMemoryAuditLog
    from careerpilot_core.audit import AuditOutcome


class AuthenticationError(PermissionError):
    """Raised for an absent, expired, or unknown local session."""


class TenantMembershipError(PermissionError):
    """Raised when a session requests a tenant without active membership."""


class LocalAuthenticationDisabledError(RuntimeError):
    """Raised if the development adapter is enabled outside local mode."""


class LastOwnerError(ValueError):
    """Raised when a role change would leave a tenant without an owner."""


@dataclass(frozen=True, slots=True)
class LocalUser:
    login_id: str
    actor: Actor


@dataclass(frozen=True, slots=True)
class LocalSession:
    token: str
    actor_id: str


class InMemoryIdentityAccess:
    """Synthetic identity/membership store for local development only."""

    def __init__(self, audit_log: InMemoryAuditLog, environment: str = "local") -> None:
        if environment != "local":
            raise LocalAuthenticationDisabledError(environment)
        self._audit_log = audit_log
        self._actors = {
            "actor-ada": Actor("actor-ada", "local:ada", "Ada Example"),
            "actor-grace": Actor("actor-grace", "local:grace", "Grace Example"),
            "actor-sam": Actor("actor-sam", "local:sam", "Sam Example"),
        }
        self._users = {
            "ada": LocalUser("ada", self._actors["actor-ada"]),
            "grace": LocalUser("grace", self._actors["actor-grace"]),
            "sam": LocalUser("sam", self._actors["actor-sam"]),
        }
        self._tenants = {
            "tenant-ada": Tenant(
                "tenant-ada", "Ada's personal workspace", TenantKind.PERSONAL
            ),
            "tenant-grace": Tenant(
                "tenant-grace", "Grace's personal workspace", TenantKind.PERSONAL
            ),
        }
        self._memberships = {
            ("actor-ada", "tenant-ada"): Membership(
                "actor-ada", "tenant-ada", Role.OWNER
            ),
            ("actor-sam", "tenant-ada"): Membership(
                "actor-sam", "tenant-ada", Role.MEMBER
            ),
            ("actor-grace", "tenant-grace"): Membership(
                "actor-grace", "tenant-grace", Role.OWNER
            ),
        }
        self._sessions: dict[str, LocalSession] = {}

    def local_users(self) -> tuple[LocalUser, ...]:
        return tuple(self._users.values())

    def login(self, login_id: str, correlation_id: str) -> LocalSession:
        user = self._users.get(login_id)
        if user is None:
            self._audit_authentication(
                "security", "anonymous", "denied", "unknown_local_user", correlation_id
            )
            raise AuthenticationError
        session = LocalSession(secrets.token_urlsafe(32), user.actor.actor_id)
        self._sessions[session.token] = session
        membership = self.memberships_for_actor(user.actor.actor_id)[0]
        self._audit_authentication(
            membership.tenant_id,
            user.actor.actor_id,
            "allowed",
            "local_session_issued",
            correlation_id,
        )
        return session

    def context_for(
        self,
        token: str,
        tenant_id: str,
        correlation_id: str,
        purpose: str = "personal_career_support",
    ) -> AuthorizationContext:
        session = self._sessions.get(token)
        if session is None:
            self._audit_authentication(
                "security", "anonymous", "denied", "invalid_session", correlation_id
            )
            raise AuthenticationError
        membership = self._memberships.get((session.actor_id, tenant_id))
        tenant = self._tenants.get(tenant_id)
        if (
            membership is None
            or not membership.active
            or tenant is None
            or not tenant.active
        ):
            fallback = self.memberships_for_actor(session.actor_id)[0].tenant_id
            self._audit_authentication(
                fallback,
                session.actor_id,
                "denied",
                "tenant_membership_missing",
                correlation_id,
            )
            raise TenantMembershipError
        self._audit_authentication(
            tenant_id,
            session.actor_id,
            "allowed",
            "request_context_derived",
            correlation_id,
        )
        return AuthorizationContext(
            actor_id=session.actor_id,
            tenant_id=tenant_id,
            role=membership.role,
            purpose=purpose,
            correlation_id=correlation_id,
        )

    def actor(self, actor_id: str) -> Actor | None:
        return self._actors.get(actor_id)

    def tenant(self, tenant_id: str) -> Tenant | None:
        return self._tenants.get(tenant_id)

    def memberships_for_actor(self, actor_id: str) -> tuple[Membership, ...]:
        return tuple(
            membership
            for membership in self._memberships.values()
            if membership.actor_id == actor_id and membership.active
        )

    def set_role(self, actor_id: str, tenant_id: str, role: Role) -> Membership:
        key = (actor_id, tenant_id)
        membership = self._memberships.get(key)
        if membership is None:
            raise TenantMembershipError
        if membership.role is Role.OWNER and role is not Role.OWNER:
            owners = sum(
                candidate.active
                and candidate.tenant_id == tenant_id
                and candidate.role is Role.OWNER
                for candidate in self._memberships.values()
            )
            if owners <= 1:
                raise LastOwnerError
        updated = replace(membership, role=role)
        self._memberships[key] = updated
        return updated

    def _audit_authentication(
        self,
        tenant_id: str,
        actor_id: str,
        outcome: AuditOutcome,
        reason: str,
        correlation_id: str,
    ) -> None:
        self._audit_log.append(
            AuditEventDraft(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action="authentication",
                outcome=outcome,
                reason=reason,
                correlation_id=correlation_id,
            )
        )
