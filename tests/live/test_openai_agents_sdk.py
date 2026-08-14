"""Opt-in bounded OpenAI Agents SDK run; skipped in the CHF 0 workflow."""

import os

import pytest
from agents import Runner
from careerpilot_openai_agents.config import Settings, validate_live_budget
from careerpilot_openai_agents.sdk_agents import build_agents, safe_run_config


@pytest.mark.live_model
@pytest.mark.asyncio
async def test_openai_agents_live_run_requires_explicit_budget() -> None:
    if os.getenv("CAREERPILOT_OPENAI_AGENTS_LIVE_COST_APPROVED") != "true":
        pytest.skip("explicit OpenAI live cost approval is not set")
    settings = Settings(
        provider="openai",
        live_cost_approved=True,
        max_cost_chf=float(os.environ["CAREERPILOT_OPENAI_AGENTS_MAX_COST_CHF"]),
    )
    validate_live_budget(settings)
    manager, _, _ = build_agents(model=settings.model)
    result = await Runner.run(
        manager,
        "Run one synthetic Platform Engineer interview turn.",
        max_turns=2,
        run_config=safe_run_config(),
    )
    assert result.final_output is not None
