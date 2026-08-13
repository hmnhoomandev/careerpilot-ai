"""Strict Pydantic contracts for the versioned CareerPilot tool layer."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolContract(BaseModel):
    """Reject unknown fields and provide JSON Schema for every tool boundary."""

    model_config = ConfigDict(extra="forbid")


class ProfileLookupInput(ToolContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]


class ProfileLookupOutput(ToolContract):
    profile_id: str
    display_name: str
    professional_summary: str
    skills: list[str]
    version: int


class EvidenceRetrievalInput(ToolContract):
    query: Annotated[str, Field(min_length=2, max_length=500)]
    limit: Annotated[int, Field(ge=1, le=5)] = 5


class ToolCitation(ToolContract):
    document_id: str
    chunk_id: str
    filename: str
    page_number: int
    start_offset: int
    end_offset: int


class ToolPassage(ToolContract):
    content: str
    injection_risk: str
    citation: ToolCitation


class EvidenceRetrievalOutput(ToolContract):
    passages: list[ToolPassage]
    untrusted: Literal[True] = True


class JobIngestionInput(ToolContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]
    job_description: Annotated[str, Field(min_length=50, max_length=5000)]


class JobIngestionOutput(ToolContract):
    analysis_id: str
    profile_id: str
    headline: str
    shared_terms: list[str]
    disclaimer: str


class SkillTaxonomyInput(ToolContract):
    query: Annotated[str, Field(min_length=2, max_length=100)]
    limit: Annotated[int, Field(ge=1, le=10)] = 5


class SkillTaxonomyOutput(ToolContract):
    canonical_skills: list[str]
    taxonomy_version: Literal["synthetic-taxonomy-v1"] = "synthetic-taxonomy-v1"


class CandidateMatchInput(ToolContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]
    job_description: Annotated[str, Field(min_length=50, max_length=5000)]


class CandidateMatchOutput(ToolContract):
    supported_terms: list[str]
    score_percent: Annotated[int, Field(ge=0, le=100)]
    explanation: str
    generated_claims: Literal[False] = False


class EvidenceVerificationInput(ToolContract):
    claim: Annotated[str, Field(min_length=5, max_length=500)]


class EvidenceVerificationOutput(ToolContract):
    status: Literal["supported", "unsupported"]
    citations: list[ToolCitation]
    suggestion_requires_confirmation: bool


class ApprovalRequestInput(ToolContract):
    action: Literal[
        "external_share",
        "profile_mutation",
        "document_deletion",
        "sensitive_transfer",
        "spending",
    ]
    resource_id: Annotated[str, Field(min_length=1, max_length=100)]
    reason: Annotated[str, Field(min_length=10, max_length=500)]


class ApprovalRequestOutput(ToolContract):
    approval_id: str
    status: Literal["pending"] = "pending"
    action_executed: Literal[False] = False


class AuditLookupInput(ToolContract):
    limit: Annotated[int, Field(ge=1, le=100)] = 20


class ToolAuditEvent(ToolContract):
    event_id: str
    occurred_at: str
    action: str
    outcome: str
    reason: str
    correlation_id: str


class AuditLookupOutput(ToolContract):
    events: list[ToolAuditEvent]


class CostEstimateInput(ToolContract):
    workflow: Literal[
        "profile_lookup",
        "retrieval",
        "job_ingestion",
        "candidate_match",
        "evidence_verification",
    ]
    units: Annotated[int, Field(ge=1, le=1000)] = 1


class CostEstimateOutput(ToolContract):
    estimated_chf: Literal[0] = 0
    provider: Literal["local_deterministic"] = "local_deterministic"
    paid_call_authorized: Literal[False] = False
    note: str


class ToolInvokeRequest(ToolContract):
    arguments: dict[str, object]
    idempotency_key: Annotated[str, Field(min_length=8, max_length=100)] | None = None


class ToolInvokeResponse(ToolContract):
    tool_name: str
    tool_version: str
    correlation_id: str
    idempotent_replay: bool
    output: dict[str, object]


class ToolCapabilityResponse(ToolContract):
    name: str
    version: str
    description: str
    permission: str
    risk: str
    side_effects: bool
    approval_required: bool
    timeout_seconds: float
    max_retries: int
    idempotency_required: bool
    rate_limit: int
    rate_window_seconds: int
    audit_action: str
    mcp_exposed: bool
    error_codes: list[str]
    input_schema: dict[str, object]
    output_schema: dict[str, object]
