"""Strict contracts for equivalent interview orchestration scenarios."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class OrchestrationMode(StrEnum):
    DIRECT_HANDOFF = "direct_handoff"
    AGENT_AS_TOOL = "agent_as_tool"
    MANAGER_DELEGATION = "manager_delegation"


class InterviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    tenant_id: str = Field(min_length=1, max_length=80)
    actor_id: str = Field(min_length=1, max_length=80)
    session_id: str = Field(min_length=1, max_length=100)
    role_title: str = Field(min_length=2, max_length=120)
    candidate_answer: str = Field(min_length=2, max_length=2_000)
    mode: OrchestrationMode
    consent_recorded: bool = False
    external_transfer_authorized: bool = False


class InterviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: OrchestrationMode
    active_agent: str
    final_owner: str
    interview_question: str
    feedback: tuple[str, ...]
    decision_summary: str


class ApprovalState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    approval_id: str
    tenant_id: str
    actor_id: str
    session_id: str
    action_hash: str
    status: str = "pending"
    revision: int = 1


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    approve: bool
    expected_revision: int = Field(ge=1)
    expected_action_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
