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
from careerpilot_core.models import (
    Education,
    EvidenceItem,
    EvidenceState,
    Experience,
    JobAnalysis,
    ProfessionalProfile,
    Skill,
)
from careerpilot_core.ports import (
    ExternalIdentity,
    IdentityVerifier,
    MalwareScanner,
    ProfileRepository,
)
from careerpilot_core.services import (
    CareerJourneyService,
    EvidenceValidationError,
    ProfileConflictError,
    ProfileNotFoundError,
    ProfileValidationError,
)

__all__ = [
    "AccessDeniedError",
    "AccessPolicy",
    "Actor",
    "AuditEvent",
    "AuditEventDraft",
    "AuditSink",
    "AuthorizationContext",
    "CareerJourneyService",
    "Education",
    "EvidenceItem",
    "EvidenceState",
    "EvidenceValidationError",
    "Experience",
    "ExternalIdentity",
    "IdentityVerifier",
    "JobAnalysis",
    "MalwareScanner",
    "Membership",
    "Permission",
    "PolicyDecision",
    "ProfessionalProfile",
    "ProfileConflictError",
    "ProfileNotFoundError",
    "ProfileRepository",
    "ProfileValidationError",
    "ResourceAttributes",
    "Role",
    "Skill",
    "Tenant",
    "TenantKind",
]
