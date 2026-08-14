"""Real Agents SDK definitions; execution remains explicitly provider-selected."""

from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunConfig,
    ToolGuardrailFunctionOutput,
    function_tool,
    handoff,
    input_guardrail,
    output_guardrail,
    set_tracing_disabled,
    tool_input_guardrail,
    tool_output_guardrail,
)
from agents.tool_guardrails import (
    AllowBehavior,
    ToolInputGuardrailData,
    ToolOutputGuardrailData,
)

from careerpilot_openai_agents.guardrails import guard_input, guard_output, guard_tool
from careerpilot_openai_agents.models import InterviewResult

set_tracing_disabled(True)


@input_guardrail(name="careerpilot_interview_input", run_in_parallel=False)
def sdk_input_guardrail(
    _context: Any, _agent: Any, value: Any
) -> GuardrailFunctionOutput:
    if isinstance(value, str):
        guard_input(value)
    return GuardrailFunctionOutput(
        output_info="input_allowed", tripwire_triggered=False
    )


@output_guardrail(name="careerpilot_interview_output")
def sdk_output_guardrail(
    _context: Any, _agent: Any, value: Any
) -> GuardrailFunctionOutput:
    if isinstance(value, InterviewResult):
        guard_output(value.feedback)
    return GuardrailFunctionOutput(
        output_info="output_allowed", tripwire_triggered=False
    )


@tool_input_guardrail(name="careerpilot_feedback_tool_input")
def sdk_tool_input_guardrail(
    _data: ToolInputGuardrailData,
) -> ToolGuardrailFunctionOutput:
    guard_tool("prepare_feedback_for_review")
    return ToolGuardrailFunctionOutput(
        output_info="tool_allowed", behavior=AllowBehavior(type="allow")
    )


@tool_output_guardrail(name="careerpilot_feedback_tool_output")
def sdk_tool_output_guardrail(
    data: ToolOutputGuardrailData,
) -> ToolGuardrailFunctionOutput:
    if isinstance(data.output, str):
        guard_output((data.output,))
    return ToolGuardrailFunctionOutput(
        output_info="output_allowed", behavior=AllowBehavior(type="allow")
    )


@function_tool(
    needs_approval=True,
    tool_input_guardrails=[sdk_tool_input_guardrail],
    tool_output_guardrails=[sdk_tool_output_guardrail],
)
def prepare_feedback_for_review(summary: str) -> str:
    """Prepare synthetic feedback for human review without publishing it."""
    return f"Pending human-reviewed feedback: {summary}"


def build_agents(*, model: str) -> tuple[Agent, Agent, Agent]:
    interviewer = Agent(
        name="Interview Specialist",
        model=model,
        instructions="Ask one role-relevant synthetic interview question.",
    )
    feedback = Agent(
        name="Feedback Specialist",
        model=model,
        instructions="Return concise evidence-based feedback; do not infer traits.",
        tools=[prepare_feedback_for_review],
    )
    manager = Agent(
        name="Interview Manager",
        model=model,
        instructions="Coordinate the interview and retain final response ownership.",
        handoffs=[handoff(interviewer)],
        tools=[
            feedback.as_tool(
                tool_name="request_feedback",
                tool_description=(
                    "Ask the feedback specialist for structured interview feedback."
                ),
                max_turns=3,
            )
        ],
        output_type=InterviewResult,
        input_guardrails=[sdk_input_guardrail],
        output_guardrails=[sdk_output_guardrail],
    )
    return manager, interviewer, feedback


def safe_run_config() -> RunConfig:
    return RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)
