"""Strict HTTP contracts for local data-subject lifecycle controls."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 - Pydantic resolves this at runtime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StrictPrivacyContract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataInventoryResponse(StrictPrivacyContract):
    schema_version: str
    tenant_id: str
    actor_id: str
    items: list[dict[str, str | int]]
    legal_review_required: bool = True


class ConsentRequest(StrictPrivacyContract):
    purpose: Annotated[str, Field(min_length=2, max_length=80)]
    granted: bool


class ConsentResponse(StrictPrivacyContract):
    purpose: str
    granted: bool
    recorded_at: datetime


class DataRightRequest(StrictPrivacyContract):
    right: Annotated[str, Field(pattern="^(access|correction|export|deletion)$")]
    step_up_verified: bool
    approval_reference: Annotated[str, Field(min_length=10, max_length=100)]


class DataExportRequest(StrictPrivacyContract):
    profile_id: Annotated[str, Field(min_length=1, max_length=100)]
    step_up_verified: bool
    approval_reference: Annotated[str, Field(min_length=10, max_length=100)]


class DataExportResponse(StrictPrivacyContract):
    schema_version: str
    request_id: str
    tenant_id: str
    actor_id: str
    profile: dict[str, object]
    evidence: list[dict[str, object]]
    excluded_categories: list[str]
    legal_review_required: bool = True


class DataRightResponse(StrictPrivacyContract):
    request_id: str
    right: str
    status: str
    requested_at: datetime
    purge_after: datetime | None
    recovery_window_days: int


class CancelDeletionRequest(StrictPrivacyContract):
    confirmed: bool
