"""Fake-first equivalent-scenario provider port."""

from typing import Protocol

from agents import Runner

from careerpilot_openai_agents.models import (
    InterviewRequest,
    InterviewResult,
    OrchestrationMode,
)
from careerpilot_openai_agents.sdk_agents import build_agents, safe_run_config


class InterviewProvider(Protocol):
    name: str

    async def run(self, request: InterviewRequest) -> InterviewResult: ...


class FakeInterviewProvider:
    name = "fake-openai-agents-v1"

    async def run(self, request: InterviewRequest) -> InterviewResult:
        handoff = request.mode is OrchestrationMode.DIRECT_HANDOFF
        return InterviewResult(
            mode=request.mode,
            active_agent="Interview Specialist" if handoff else "Feedback Specialist",
            final_owner="Interview Specialist" if handoff else "Interview Manager",
            interview_question=(
                f"How would you approach a {request.role_title} challenge?"
            ),
            feedback=(
                "Use one concrete example.",
                "Explain your measurable contribution.",
            ),
            decision_summary=(
                "Control transferred to the specialist."
                if handoff
                else "The manager invoked a specialist and retained control."
            ),
        )


class OpenAIAgentsProvider:
    """Explicit live SDK provider; construction performs no network request."""

    name = "openai-agents-sdk"

    def __init__(self, *, model: str) -> None:
        self._model = model

    async def run(self, request: InterviewRequest) -> InterviewResult:
        manager, _, _ = build_agents(model=self._model)
        prompt = (
            f"Role: {request.role_title}\n"
            f"Synthetic candidate answer: {request.candidate_answer}\n"
            f"Requested orchestration mode: {request.mode.value}."
        )
        result = await Runner.run(
            manager,
            prompt,
            max_turns=6,
            run_config=safe_run_config(),
        )
        return result.final_output_as(InterviewResult)
