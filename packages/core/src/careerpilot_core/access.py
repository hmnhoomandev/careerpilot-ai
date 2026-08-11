"""Provider-neutral identity, tenancy, and authorization domain model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TenantKind(StrEnum):
    PERSONAL = "personal"
    ORGANIZATION = "organization"


class Role(StrEnum):
    OWNER = "owner"
    MEMBER = "member"
    COACH = "coach"
    ORGANIZATION_ADMIN = "organization_admin"


class Permission(StrEnum):
    PROFILE_CREATE = "profile.create"
    PROFILE_READ = "profile.read"
    PROFILE_UPDATE = "profile.update"
    ANALYSIS_RUN = "analysis.run"
    AUDIT_VIEW = "audit.view"
    MEMBERSHIP_MANAGE = "membership.manage"
    DOCUMENT_READ = "document.read"
    TOOL_INVOKE = "tool.invoke"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(Permission),
    Role.MEMBER: frozenset(
        {
            Permission.PROFILE_CREATE,
            Permission.PROFILE_READ,
            Permission.PROFILE_UPDATE,
            Permission.ANALYSIS_RUN,
            Permission.DOCUMENT_READ,
            Permission.TOOL_INVOKE,
        }
    ),
    Role.COACH: frozenset(
        {
            Permission.PROFILE_READ,
            Permission.ANALYSIS_RUN,
            Permission.DOCUMENT_READ,
        }
    ),
    Role.ORGANIZATION_ADMIN: frozenset(
        {Permission.AUDIT_VIEW, Permission.MEMBERSHIP_MANAGE}
    ),
}


@dataclass(frozen=True, slots=True)
class Actor:
    actor_id: str
    external_subject: str
    display_name: str


@dataclass(frozen=True, slots=True)
class Tenant:
    tenant_id: str
    display_name: str
    kind: TenantKind
    active: bool = True


@dataclass(frozen=True, slots=True)
class Membership:
    actor_id: str
    tenant_id: str
    role: Role
    active: bool = True


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Server-derived authority for one authenticated request."""

    actor_id: str
    tenant_id: str
    role: Role
    purpose: str
    correlation_id: str


@dataclass(frozen=True, slots=True)
class ResourceAttributes:
    tenant_id: str
    owner_actor_id: str | None
    sensitivity: str = "personal"
    state: str = "active"
    delegated_actor_ids: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    reason: str


class AccessDeniedError(PermissionError):
    """Raised when the centralized policy denies an operation."""

    def __init__(self, permission: Permission, reason: str) -> None:
        super().__init__(f"{permission}: {reason}")
        self.permission = permission
        self.reason = reason


class AccessPolicy:
    """Apply RBAC first and contextual ABAC second; missing rules deny."""

    ALLOWED_PURPOSES = frozenset(
        {"personal_career_support", "security_review", "tenant_administration"}
    )
    RESOURCE_PERMISSIONS = frozenset(
        {
            Permission.PROFILE_READ,
            Permission.PROFILE_UPDATE,
            Permission.ANALYSIS_RUN,
            Permission.DOCUMENT_READ,
            Permission.TOOL_INVOKE,
        }
    )

    def decide(
        self,
        context: AuthorizationContext,
        permission: Permission,
        resource: ResourceAttributes | None = None,
    ) -> PolicyDecision:
        if permission not in ROLE_PERMISSIONS.get(context.role, frozenset()):
            return PolicyDecision(allowed=False, reason="role_permission_missing")
        if context.purpose not in self.ALLOWED_PURPOSES:
            return PolicyDecision(allowed=False, reason="purpose_not_allowed")
        if permission in self.RESOURCE_PERMISSIONS:
            denial_reason = self._resource_denial_reason(context, resource)
            if denial_reason:
                return PolicyDecision(allowed=False, reason=denial_reason)
        return PolicyDecision(allowed=True, reason="allowed")

    @staticmethod
    def _resource_denial_reason(
        context: AuthorizationContext, resource: ResourceAttributes | None
    ) -> str | None:
        if resource is None:
            return "resource_context_required"
        if resource.tenant_id != context.tenant_id:
            return "tenant_mismatch"
        if resource.state != "active":
            return "resource_inactive"
        owns_resource = resource.owner_actor_id == context.actor_id
        delegated = context.actor_id in resource.delegated_actor_ids
        if not owns_resource and not delegated:
            return "ownership_or_delegation_required"
        if resource.sensitivity == "restricted" and not owns_resource:
            return "restricted_resource_requires_owner"
        return None

    def require(
        self,
        context: AuthorizationContext,
        permission: Permission,
        resource: ResourceAttributes | None = None,
    ) -> None:
        decision = self.decide(context, permission, resource)
        if not decision.allowed:
            raise AccessDeniedError(permission, decision.reason)
