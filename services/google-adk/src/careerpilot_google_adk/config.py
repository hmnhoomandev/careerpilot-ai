"""Fail-closed environment composition for the specialist service."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from careerpilot_google_adk.provider import (
    AdkGeminiResearchProvider,
    FakeResearchProvider,
)
from careerpilot_google_adk.service import ResearchService


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CAREERPILOT_ADK_", env_file=None, extra="ignore"
    )
    enabled: bool = True
    provider: Literal["fake", "gemini"] = "fake"
    model: str = Field(default="gemini-3.6-flash", min_length=1)
    timeout_seconds: float = Field(default=20, gt=0, le=120)
    trace_export: bool = False
    prompt_response_logging: bool = False
    bigquery_analytics: bool = False
    capture_message_content: Literal["NO_CONTENT"] = "NO_CONTENT"


def validate_telemetry(settings: Settings) -> None:
    """Require separate infrastructure/privacy approval for every ADK export tier."""
    if (
        settings.trace_export
        or settings.prompt_response_logging
        or settings.bigquery_analytics
    ):
        raise PermissionError("adk_telemetry_export_not_approved")


def build_service(settings: Settings | None = None) -> ResearchService:
    selected = settings or Settings()
    validate_telemetry(selected)
    provider = (
        FakeResearchProvider()
        if selected.provider == "fake"
        else AdkGeminiResearchProvider(model=selected.model)
    )
    return ResearchService(
        provider,
        enabled=selected.enabled,
        live_provider=selected.provider == "gemini",
        timeout_seconds=selected.timeout_seconds,
    )
