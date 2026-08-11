"""Versioned HTTP contracts for the Phase 2 walking skeleton."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

ShortText = Annotated[str, Field(min_length=2, max_length=100)]
SummaryText = Annotated[str, Field(min_length=20, max_length=1000)]
JobText = Annotated[str, Field(min_length=50, max_length=5000)]


class StrictContract(BaseModel):
    """Reject unknown fields so clients notice contract drift."""

    model_config = ConfigDict(extra="forbid")


class ProfileCreateRequest(StrictContract):
    display_name: ShortText
    professional_summary: SummaryText


class ExperienceContract(StrictContract):
    title: Annotated[str, Field(min_length=2, max_length=160)]
    organization: Annotated[str, Field(min_length=2, max_length=160)]
    start_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    end_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")] | None = None
    description: Annotated[str, Field(min_length=10, max_length=2000)]


class EducationContract(StrictContract):
    institution: Annotated[str, Field(min_length=2, max_length=200)]
    qualification: Annotated[str, Field(min_length=2, max_length=200)]
    start_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")] | None = None
    end_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")] | None = None


class ProfileResponse(StrictContract):
    profile_id: str
    display_name: str
    professional_summary: str
    version: int
    skills: list[str]
    experiences: list[ExperienceContract]
    education: list[EducationContract]


class ProfileUpdateRequest(StrictContract):
    """Editable profile fields plus the client's last observed version."""

    display_name: ShortText
    professional_summary: SummaryText
    skills: Annotated[list[ShortText], Field(max_length=30)] = []
    experiences: Annotated[list[ExperienceContract], Field(max_length=50)] = []
    education: Annotated[list[EducationContract], Field(max_length=50)] = []
    expected_version: Annotated[int, Field(ge=1)]


class EvidenceCreateRequest(StrictContract):
    """Metadata-only intake; document bytes are not accepted in Phase 4."""

    profile_id: str
    title: Annotated[str, Field(min_length=2, max_length=200)]
    filename: Annotated[str, Field(min_length=1, max_length=255)]
    media_type: Annotated[str, Field(min_length=3, max_length=100)]
    size_bytes: Annotated[int, Field(ge=1, le=10 * 1024 * 1024)]


class EvidenceResponse(StrictContract):
    evidence_id: str
    profile_id: str
    title: str
    filename: str
    media_type: str
    size_bytes: int
    state: str
    version: int


class AnalysisCreateRequest(StrictContract):
    profile_id: str
    job_description: JobText


class AnalysisResponse(StrictContract):
    analysis_id: str
    profile_id: str
    headline: str
    summary: str
    shared_terms: list[str]
    disclaimer: str
    correlation_id: str


class HealthResponse(StrictContract):
    status: Literal["ok", "ready"]


class ErrorDetail(StrictContract):
    code: str
    message: str
    correlation_id: str
    fields: dict[str, list[str]] | None = None


class ErrorResponse(StrictContract):
    error: ErrorDetail


class LocalLoginRequest(StrictContract):
    local_user_id: Annotated[str, Field(min_length=2, max_length=30)]


class TenantSummary(StrictContract):
    tenant_id: str
    display_name: str
    role: str


class SessionResponse(StrictContract):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"  # noqa: S105 - protocol scheme
    actor_id: str
    display_name: str
    tenants: list[TenantSummary]


class LocalUserResponse(StrictContract):
    local_user_id: str
    display_name: str


class CurrentContextResponse(StrictContract):
    actor_id: str
    display_name: str
    tenant_id: str
    tenant_name: str
    role: str


class MembershipRoleRequest(StrictContract):
    role: Literal["owner", "member"]


class MembershipResponse(StrictContract):
    actor_id: str
    tenant_id: str
    role: str


class AuditEventResponse(StrictContract):
    event_id: str
    occurred_at: str
    actor_id: str
    action: str
    outcome: str
    reason: str
    correlation_id: str
    resource_type: str | None
    resource_id: str | None
    previous_hash: str
    event_hash: str
