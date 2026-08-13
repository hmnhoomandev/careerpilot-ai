"""Opt-in live Gemini evaluation; never part of the default CHF 0 workflow."""

import os

import pytest
from careerpilot_google_adk.models import ResearchRequest, SourceExcerpt
from careerpilot_google_adk.provider import AdkGeminiResearchProvider
from careerpilot_google_adk.service import ResearchService


@pytest.mark.live_model
@pytest.mark.asyncio
async def test_gemini_returns_grounded_schema_when_explicitly_authorized() -> None:
    if os.getenv("CAREERPILOT_ADK_LIVE_EVAL_COST_APPROVED") != "true":
        pytest.skip("explicit live model cost approval is not set")
    model = os.environ["CAREERPILOT_ADK_MODEL"]
    request = ResearchRequest(
        tenant_id="synthetic-live-eval",
        actor_id="synthetic-evaluator",
        session_id="live-eval-1",
        question="What interview topic follows from this supplied job description?",
        sources=(
            SourceExcerpt(
                source_id="synthetic-job",
                title="Synthetic job",
                content="The fictional role requires accessible Python APIs.",
            ),
        ),
        external_transfer_authorized=True,
        consent_recorded=True,
    )
    result = await ResearchService(
        AdkGeminiResearchProvider(model=model), live_provider=True
    ).research(request)
    assert all(finding.source_ids == ("synthetic-job",) for finding in result.findings)
