"""Framework-independent CareerPilot AI core package."""

from careerpilot_core.access import (
    AccessDeniedError,
    AccessPolicy,
    Actor,
    AuthorizationContext,
    Membership,
    Permission,
    PolicyDecision,
    ResourceAttributes,
    Role,
    Tenant,
    TenantKind,
)
from careerpilot_core.audit import AuditEvent, AuditEventDraft, AuditSink
from careerpilot_core.models import JobAnalysis, ProfessionalProfile
from careerpilot_core.ports import ExternalIdentity, IdentityVerifier, ProfileRepository
from careerpilot_core.services import CareerJourneyService, ProfileNotFoundError

__all__ = [
    "AccessDeniedError",
    "AccessPolicy",
    "Actor",
    "AuditEvent",
    "AuditEventDraft",
    "AuditSink",
    "AuthorizationContext",
    "CareerJourneyService",
    "ExternalIdentity",
    "IdentityVerifier",
    "JobAnalysis",
    "Membership",
    "Permission",
    "PolicyDecision",
    "ProfessionalProfile",
    "ProfileNotFoundError",
    "ProfileRepository",
    "ResourceAttributes",
    "Role",
    "Tenant",
    "TenantKind",
]
