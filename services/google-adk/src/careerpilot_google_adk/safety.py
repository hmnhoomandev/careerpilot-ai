"""Deterministic pre/post-model safety policy."""

import re

from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest

from careerpilot_google_adk.errors import MalformedProviderOutputError
from careerpilot_google_adk.models import ResearchRequest, ResearchResult

INJECTION = re.compile(
    r"ignore (?:all |the )?(?:previous|system)|system prompt|developer message",
    re.IGNORECASE,
)


def inspect_request(request: ResearchRequest) -> None:
    """Reject instruction-like source data instead of forwarding it to a model."""
    if any(INJECTION.search(source.content) for source in request.sources):
        raise MalformedProviderOutputError("untrusted_source_instruction_detected")


def validate_citations(request: ResearchRequest, result: ResearchResult) -> None:
    """Fail closed when a finding cites anything outside the request allowlist."""
    allowed = {source.source_id for source in request.sources}
    if any(not set(finding.source_ids) <= allowed for finding in result.findings):
        raise MalformedProviderOutputError("unknown_source_citation")


def before_model_safety_callback(_context: Context, request: LlmRequest) -> None:
    """ADK callback that rejects instruction-like content at the model boundary."""
    text = " ".join(
        part.text or ""
        for content in request.contents
        for part in (content.parts or [])
    )
    if INJECTION.search(text):
        raise MalformedProviderOutputError("model_boundary_instruction_detected")
