"""Strict service contracts shared by fake and live ADK execution."""

from pydantic import BaseModel, ConfigDict, Field


class SourceExcerpt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=8_000)


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    statement: str = Field(min_length=1, max_length=1_000)
    source_ids: tuple[str, ...] = Field(min_length=1, max_length=8)


class ResearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    summary: str = Field(min_length=1, max_length=2_000)
    findings: tuple[Finding, ...] = Field(max_length=20)
    questions_to_verify: tuple[str, ...] = Field(max_length=12)


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    tenant_id: str = Field(min_length=1, max_length=80)
    actor_id: str = Field(min_length=1, max_length=80)
    session_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=3, max_length=1_000)
    sources: tuple[SourceExcerpt, ...] = Field(min_length=1, max_length=12)
    external_transfer_authorized: bool = False
    consent_recorded: bool = False
