"""Typed LangGraph composition for the bounded job-analysis agent workflow."""

from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Annotated, Any, NotRequired, TypedDict, cast

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from careerpilot_core import AuthorizationContext, Role, RouteDecision

if TYPE_CHECKING:
    from careerpilot_api.tool_runtime import ToolExecutor
    from careerpilot_core import AnalysisModelProvider

MIN_DETERMINISTIC_DESCRIPTION_CHARACTERS = 50
MIN_DETERMINISTIC_DESCRIPTION_WORDS = 8


class AnalysisGraphState(TypedDict):
    """Serializable graph state; each node owns only its named output fields."""

    run_id: str
    profile_id: str
    job_description: str
    actor_id: str
    tenant_id: str
    role: str
    purpose: str
    correlation_id: str
    cancelled: bool
    route: NotRequired[str]
    intent: NotRequired[str]
    requirements: NotRequired[dict[str, object]]
    passages: NotRequired[list[dict[str, object]]]
    match: NotRequired[dict[str, object]]
    gaps: NotRequired[dict[str, list[str]]]
    verified: NotRequired[list[dict[str, object]]]
    explanation: NotRequired[str]
    status: NotRequired[str]
    events: NotRequired[Annotated[list[dict[str, str]], operator.add]]
    error: NotRequired[dict[str, str]]


def build_analysis_graph(
    executor: ToolExecutor | Any,
    provider: AnalysisModelProvider,
    checkpointer: InMemorySaver | None = None,
) -> Any:
    """Compile the explicit role path with checkpointing and bounded retries."""

    async def intake(state: AnalysisGraphState) -> dict[str, object]:
        if state["cancelled"]:
            return {"status": "cancelled", **_event("intake", status="cancelled")}
        description = " ".join(state["job_description"].split())
        route = (
            RouteDecision.ANALYZE
            if len(description) >= MIN_DETERMINISTIC_DESCRIPTION_CHARACTERS
            and len(description.split()) >= MIN_DETERMINISTIC_DESCRIPTION_WORDS
            else await provider.route(description)
        )
        return {"intent": "job_analysis", "route": route.value, **_event("intake")}

    async def job_analysis(state: AnalysisGraphState) -> dict[str, object]:
        requirements = await provider.extract_requirements(state["job_description"])
        return {
            "requirements": {
                "title": requirements.title,
                "required_skills": list(requirements.required_skills),
                "responsibilities": list(requirements.responsibilities),
                "untrusted_source": True,
            },
            **_event("job_analysis"),
        }

    async def retrieval(state: AnalysisGraphState) -> dict[str, object]:
        requirements = state["requirements"]
        skills = cast("list[str]", requirements["required_skills"])
        query = " ".join(skills) or state["job_description"][:500]
        result = await executor.execute(
            "evidence.retrieve", _context(state), {"query": query, "limit": 5}
        )
        return {
            "passages": cast("list[dict[str, object]]", result.output["passages"]),
            **_event("retrieval"),
        }

    async def match(state: AnalysisGraphState) -> dict[str, object]:
        result = await executor.execute(
            "candidate.match",
            _context(state),
            {
                "profile_id": state["profile_id"],
                "job_description": state["job_description"],
            },
        )
        return {"match": result.output, **_event("match")}

    async def gap(state: AnalysisGraphState) -> dict[str, object]:
        requirements = state["requirements"]
        required = cast("list[str]", requirements["required_skills"])
        match_output = state["match"]
        supported_terms = {
            str(item).casefold()
            for item in cast("list[object]", match_output["supported_terms"])
        }
        supported = [skill for skill in required if skill.casefold() in supported_terms]
        missing = [
            skill for skill in required if skill.casefold() not in supported_terms
        ]
        uncertain = missing if not state["passages"] else []
        return {
            "gaps": {
                "supported": supported,
                "missing": missing,
                "uncertain": uncertain,
            },
            **_event("gap"),
        }

    async def evidence(state: AnalysisGraphState) -> dict[str, object]:
        requirements = state["requirements"]
        verified: list[dict[str, object]] = []
        for skill in cast("list[str]", requirements["required_skills"]):
            result = await executor.execute(
                "evidence.verify",
                _context(state),
                {"claim": f"Professional evidence demonstrates {skill}"},
            )
            verified.append({"claim": skill, **result.output})
        return {"verified": verified, **_event("evidence")}

    async def explanation(state: AnalysisGraphState) -> dict[str, object]:
        verified = state.get("verified", [])
        supported = sum(item.get("status") == "supported" for item in verified)
        total = len(verified)
        message = (
            f"{supported} of {total} extracted skill requirements have cited support. "
            "Unverified items remain missing or uncertain and are not candidate facts."
        )
        return {"explanation": message, "status": "completed", **_event("explanation")}

    async def error_node(_state: AnalysisGraphState) -> dict[str, object]:
        return {
            "status": "failed",
            "error": {
                "code": "unsupported_or_insufficient_input",
                "message": "The input could not be routed to job analysis.",
            },
            **_event("error", status="failed"),
        }

    builder = StateGraph(AnalysisGraphState)
    builder.add_node("intake", intake, timeout=1.0)
    builder.add_node(
        "job_analysis",
        job_analysis,
        timeout=2.0,
        retry_policy=RetryPolicy(
            max_attempts=2, jitter=False, retry_on=ConnectionError
        ),
    )
    builder.add_node("retrieval", retrieval, timeout=2.0)
    builder.add_node("match", match, timeout=2.0)
    builder.add_node("gap", gap, timeout=2.0)
    builder.add_node("evidence", evidence, timeout=2.0)
    builder.add_node("explanation", explanation, timeout=1.0)
    builder.add_node("failure", cast("Any", error_node), timeout=1.0)
    builder.add_edge(START, "intake")
    builder.add_conditional_edges(
        "intake",
        _route_after_intake,
        {"job_analysis": "job_analysis", "error": "failure", "end": END},
    )
    builder.add_edge("job_analysis", "retrieval")
    builder.add_edge("retrieval", "match")
    builder.add_edge("match", "gap")
    builder.add_edge("gap", "evidence")
    builder.add_edge("evidence", "explanation")
    builder.add_edge("explanation", END)
    builder.add_edge("failure", END)
    return builder.compile(
        checkpointer=checkpointer or InMemorySaver(), name="careerpilot-job-analysis-v1"
    )


def _route_after_intake(state: AnalysisGraphState) -> str:
    if state["cancelled"]:
        return "end"
    if state.get("route") != RouteDecision.ANALYZE:
        return "error"
    return "job_analysis"


def _context(state: AnalysisGraphState) -> AuthorizationContext:
    return AuthorizationContext(
        actor_id=state["actor_id"],
        tenant_id=state["tenant_id"],
        role=Role(state["role"]),
        purpose=state["purpose"],
        correlation_id=state["correlation_id"],
    )


def _event(node: str, *, status: str = "completed") -> dict[str, object]:
    return {"events": [{"node": node, "status": status}]}
