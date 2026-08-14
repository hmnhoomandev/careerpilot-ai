"""Deterministic input, output, and tool gates outside model authority."""

import re

from careerpilot_openai_agents.errors import GuardrailBlockedError

INJECTION = re.compile(r"ignore .*instructions|reveal .*prompt", re.IGNORECASE)
SENSITIVE = re.compile(r"\b(?:ssn|passport|credit card)\b", re.IGNORECASE)


def guard_input(value: str) -> None:
    if INJECTION.search(value) or SENSITIVE.search(value):
        raise GuardrailBlockedError("unsafe_interview_input")


def guard_tool(action: str) -> None:
    if action != "prepare_feedback_for_review":
        raise GuardrailBlockedError("tool_not_allowlisted")


def guard_output(values: tuple[str, ...]) -> None:
    if any(SENSITIVE.search(value) for value in values):
        raise GuardrailBlockedError("unsafe_interview_output")
