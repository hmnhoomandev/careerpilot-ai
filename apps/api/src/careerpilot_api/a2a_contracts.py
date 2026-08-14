"""Strict application API contracts around official A2A values."""

from pydantic import BaseModel, ConfigDict, Field


class A2ADelegateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str = Field(min_length=1, max_length=80)
    skill_id: str = Field(min_length=1, max_length=100)
    task_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,100}$")
    payload: dict[str, str] = Field(max_length=12)
    timeout_seconds: float = Field(default=5, gt=0, le=30)
    defer_execution: bool = False
