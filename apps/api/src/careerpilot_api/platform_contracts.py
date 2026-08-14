"""Strict local dashboard contracts for Phase 15 platform controls."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PlatformContract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlatformMetricsResponse(PlatformContract):
    schema_version: str
    event_count: int
    success_count: int
    error_count: int
    provider_failures: int
    p50_duration_ms: float
    p95_duration_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_chf: float
    budget_limit_chf: float
    budget_remaining_chf: float
    export_status: str
    content_capture: str
