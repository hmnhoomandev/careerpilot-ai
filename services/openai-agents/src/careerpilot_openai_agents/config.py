"""Fake-first environment composition and live budget gate."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from careerpilot_openai_agents.errors import BudgetDeniedError
from careerpilot_openai_agents.provider import (
    FakeInterviewProvider,
    OpenAIAgentsProvider,
)
from careerpilot_openai_agents.service import InterviewService


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CAREERPILOT_OPENAI_AGENTS_", env_file=None, extra="ignore"
    )
    enabled: bool = True
    provider: Literal["fake", "openai"] = "fake"
    model: str = "gpt-5.6-luna"
    trace_export: bool = False
    live_cost_approved: bool = False
    max_cost_chf: float = Field(default=0, ge=0, le=10)


def validate_live_budget(settings: Settings) -> None:
    if settings.provider == "openai" and not (
        settings.live_cost_approved and settings.max_cost_chf > 0
    ):
        raise BudgetDeniedError


def validate_trace_export(settings: Settings) -> None:
    """Keep provider trace export disabled until privacy and cost approval exists."""
    if settings.trace_export:
        raise PermissionError("openai_trace_export_not_approved")


def build_service(settings: Settings | None = None) -> InterviewService:
    selected = settings or Settings()
    validate_live_budget(selected)
    validate_trace_export(selected)
    provider = (
        FakeInterviewProvider()
        if selected.provider == "fake"
        else OpenAIAgentsProvider(model=selected.model)
    )
    return InterviewService(
        provider,
        enabled=selected.enabled,
        live_provider=selected.provider == "openai",
    )
