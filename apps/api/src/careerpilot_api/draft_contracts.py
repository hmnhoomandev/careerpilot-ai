"""Strict draft, approval, citation, and A2UI-compatible HTTP contracts."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DraftContract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DraftCreateRequest(DraftContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]
    kind: Literal["resume", "cover_letter"]
    job_description: Annotated[str, Field(min_length=50, max_length=5000)]


class CitationContract(DraftContract):
    document_id: str
    chunk_id: str
    filename: str
    page_number: int
    start_offset: int
    end_offset: int


class ClaimContract(DraftContract):
    claim_id: str
    text: str
    status: str
    citations: list[CitationContract]


class A2UIMessage(DraftContract):
    schema_version: Literal["careerpilot.a2ui.v1"] = Field(
        default="careerpilot.a2ui.v1", alias="schema"
    )
    component: Literal["editable_career_draft", "approval_review"]
    actions: list[
        Literal["edit", "approve", "reject", "request_more_information", "cancel"]
    ]
    data: dict[str, object]


class DraftResponse(DraftContract):
    draft_id: str
    version: int
    kind: str
    title: str
    sections: list[str]
    claims: list[ClaimContract]
    content_hash: str
    pii_flags: list[str]
    policy_flags: list[str]
    approval_id: str
    approval_status: str
    approval_revision: int
    correlation_id: str
    messages: list[A2UIMessage]


class DraftEditRequest(DraftContract):
    expected_version: Annotated[int, Field(ge=1)]
    sections: Annotated[list[str], Field(min_length=1, max_length=20)]


class ApprovalDecisionRequest(DraftContract):
    decision: Literal[
        "approve", "edit_and_approve", "reject", "request_more_information", "cancel"
    ]
    expected_revision: Annotated[int, Field(ge=1)]
    expected_draft_version: Annotated[int, Field(ge=1)]
    expected_draft_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    feedback: Annotated[str, Field(min_length=3, max_length=1000)] | None = None


class ApprovalResponse(DraftContract):
    approval_id: str
    draft_id: str
    draft_version: int
    draft_hash: str
    status: str
    revision: int
    feedback: str | None
    correlation_id: str
