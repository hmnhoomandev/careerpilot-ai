"""Strict HTTP contracts for the Phase 7 graph workflow."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class GraphContract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalysisGraphRequest(GraphContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]
    job_description: Annotated[str, Field(min_length=50, max_length=5000)]


class AnalysisGraphResponse(GraphContract):
    run_id: str
    profile_id: str
    status: str
    provider: str
    correlation_id: str
    requirements: dict[str, object] | None = None
    passages: list[dict[str, object]]
    match: dict[str, object] | None = None
    gaps: dict[str, list[str]] | None = None
    verified: list[dict[str, object]]
    explanation: str | None = None
    events: list[dict[str, str]]
    error: dict[str, str] | None = None
