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


class ProfileResponse(StrictContract):
    profile_id: str
    display_name: str


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
