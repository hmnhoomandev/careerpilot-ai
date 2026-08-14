"""Data-minimized contracts persisted in Temporal workflow history."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

SAFE_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
MAX_FOLLOW_UP_DELAY_SECONDS = 2_592_000
MAX_ACTIVITY_INPUT_REFS = 8


def _require_token(value: str, field_name: str) -> None:
    if SAFE_TOKEN.fullmatch(value) is None:
        raise ValueError(f"{field_name}_must_be_an_opaque_reference")


class WorkflowStage(StrEnum):
    CREATED = "created"
    ANALYZING = "analyzing"
    RESEARCHING = "researching"
    DRAFTING = "drafting"
    AWAITING_APPROVAL = "awaiting_approval"
    TRACKING = "tracking"
    WAITING_FOLLOW_UP = "waiting_follow_up"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class ApplicationWorkflowInput:
    """Opaque references and policy values needed for one durable process."""

    tenant_id: str
    actor_id: str
    application_id: str
    profile_ref: str
    job_ref: str
    draft_ref: str
    draft_version: int
    correlation_id: str
    follow_up_delay_seconds: int = 604_800

    def __post_init__(self) -> None:
        for field_name in (
            "tenant_id",
            "actor_id",
            "application_id",
            "correlation_id",
        ):
            _require_token(str(getattr(self, field_name)), field_name)
        for field_name, prefix in (
            ("profile_ref", "profile:"),
            ("job_ref", "job:"),
            ("draft_ref", "draft:"),
        ):
            value = str(getattr(self, field_name))
            _require_token(value, field_name)
            if not value.startswith(prefix):
                raise ValueError(f"{field_name}_prefix_invalid")
        if self.draft_version < 1:
            raise ValueError("draft_version_must_be_positive")
        if not 1 <= self.follow_up_delay_seconds <= MAX_FOLLOW_UP_DELAY_SECONDS:
            raise ValueError("follow_up_delay_out_of_range")


@dataclass(frozen=True)
class ActivityCommand:
    """Idempotent command passed from deterministic workflow to an activity."""

    tenant_id: str
    actor_id: str
    application_id: str
    correlation_id: str
    step: str
    idempotency_key: str
    input_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "tenant_id",
            "actor_id",
            "application_id",
            "correlation_id",
            "step",
            "idempotency_key",
        ):
            _require_token(str(getattr(self, field_name)), field_name)
        if len(self.input_refs) > MAX_ACTIVITY_INPUT_REFS:
            raise ValueError("too_many_input_refs")
        for reference in self.input_refs:
            _require_token(reference, "input_ref")


@dataclass(frozen=True)
class ActivityResult:
    """Reference-only activity result safe to record in workflow history."""

    step: str
    artifact_ref: str
    replayed: bool


@dataclass(frozen=True)
class ApprovalSignal:
    """Human decision bound to the exact draft proposal."""

    decision: str
    draft_ref: str
    draft_version: int
    decided_by_actor_id: str

    def __post_init__(self) -> None:
        if self.decision not in {"approved", "rejected"}:
            raise ValueError("approval_decision_invalid")
        _require_token(self.draft_ref, "draft_ref")
        _require_token(self.decided_by_actor_id, "decided_by_actor_id")
        if not self.draft_ref.startswith("draft:") or self.draft_version < 1:
            raise ValueError("approval_draft_reference_invalid")


@dataclass(frozen=True)
class WorkflowStatus:
    """Read-only query view; it contains no resume, job, or draft content."""

    stage: str
    completed_steps: tuple[str, ...]
    compensated_steps: tuple[str, ...]
    approval_decision: str | None
    decision_summary: str


@dataclass(frozen=True)
class WorkflowResult:
    """Terminal metadata returned to the application layer."""

    application_id: str
    stage: str
    completed_steps: tuple[str, ...]
    compensated_steps: tuple[str, ...]
    follow_up_ref: str | None
    decision_summary: str
