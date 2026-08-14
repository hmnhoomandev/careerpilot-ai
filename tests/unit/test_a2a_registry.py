"""Phase 11 A2A registry and lifecycle tests."""

from __future__ import annotations

import pytest
from a2a.types import TaskState

from careerpilot_api.a2a_registry import (
    A2AAccessDeniedError,
    A2ACompatibilityError,
    A2AConflictError,
    A2ANotFoundError,
    A2ARegistry,
    A2ATimeoutError,
    A2AUnavailableError,
    FakeRemoteAgentAdapter,
    RegisteredAgent,
    build_default_registry,
    default_cards,
)
from careerpilot_core import AuthorizationContext, Role


def _context(
    *, actor: str = "ada", tenant: str = "tenant-ada", role: Role = Role.OWNER
) -> AuthorizationContext:
    return AuthorizationContext(
        actor_id=actor,
        tenant_id=tenant,
        role=role,
        purpose="personal_career_support",
        correlation_id="corr-phase-11",
    )


def test_cards_are_official_versioned_and_security_declared() -> None:
    cards = default_cards()

    assert {card.url.rsplit("/", 1)[-1] for card in cards} == {
        "langgraph-core",
        "google-adk-research",
        "openai-interview",
    }
    assert {card.skills[0].id for card in cards} == {
        "job-analysis.v1",
        "company-research.v1",
        "interview-simulation.v1",
    }
    assert all(card.protocol_version == "0.3.0" for card in cards)
    assert all(card.security and card.security_schemes for card in cards)
    assert all(not card.capabilities.streaming for card in cards)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("agent_id", "skill_id", "runtime"),
    [
        ("langgraph-core", "job-analysis.v1", "langgraph"),
        ("google-adk-research", "company-research.v1", "google-adk"),
        ("openai-interview", "interview-simulation.v1", "openai-agents"),
    ],
)
async def test_each_runtime_completes_a_correlated_synthetic_task(
    agent_id: str, skill_id: str, runtime: str
) -> None:
    registry = build_default_registry()
    context = _context()
    task = registry.submit(
        context,
        agent_id=agent_id,
        skill_id=skill_id,
        task_id=f"task-{runtime}",
        payload={"fixture_id": "fixture-1"},
    )
    assert task.status.state is TaskState.submitted

    completed = await registry.execute(
        context,
        task_id=task.id,
        payload={"fixture_id": "fixture-1"},
        timeout_seconds=1,
    )

    assert completed.status.state is TaskState.completed
    assert completed.metadata is not None
    assert completed.metadata["correlation_id"] == "corr-phase-11"
    assert completed.metadata["result"]["runtime"] == runtime


def test_duplicate_is_idempotent_but_changed_payload_conflicts() -> None:
    registry = build_default_registry()
    context = _context()
    arguments = {
        "agent_id": "langgraph-core",
        "skill_id": "job-analysis.v1",
        "task_id": "task-duplicate",
    }
    first = registry.submit(context, payload={"fixture_id": "one"}, **arguments)
    repeated = registry.submit(context, payload={"fixture_id": "one"}, **arguments)
    assert repeated.context_id == first.context_id

    with pytest.raises(A2AConflictError):
        registry.submit(context, payload={"fixture_id": "two"}, **arguments)


@pytest.mark.asyncio
async def test_cancel_and_terminal_state_rules_are_explicit() -> None:
    registry = build_default_registry()
    context = _context()
    registry.submit(
        context,
        agent_id="openai-interview",
        skill_id="interview-simulation.v1",
        task_id="task-cancel",
        payload={},
    )
    cancelled = await registry.cancel(context, "task-cancel")
    assert cancelled.status.state is TaskState.canceled
    with pytest.raises(A2AConflictError):
        await registry.cancel(context, "task-cancel")


@pytest.mark.asyncio
async def test_timeout_and_unavailable_agent_fail_without_fallback() -> None:
    card = default_cards()[0]
    context = _context()
    slow = A2ARegistry(
        (RegisteredAgent(card, FakeRemoteAgentAdapter("slow", delay=0.05)),)
    )
    slow.submit(
        context,
        agent_id="langgraph-core",
        skill_id="job-analysis.v1",
        task_id="task-timeout",
        payload={},
    )
    with pytest.raises(A2ATimeoutError):
        await slow.execute(
            context, task_id="task-timeout", payload={}, timeout_seconds=0.001
        )
    assert slow.get(context, "task-timeout").status.state is TaskState.failed

    down = A2ARegistry(
        (RegisteredAgent(card, FakeRemoteAgentAdapter("down", available=False)),)
    )
    down.submit(
        context,
        agent_id="langgraph-core",
        skill_id="job-analysis.v1",
        task_id="task-down",
        payload={},
    )
    with pytest.raises(A2AUnavailableError):
        await down.execute(context, task_id="task-down", payload={}, timeout_seconds=1)


def test_compatibility_capability_and_tenant_boundaries_fail_closed() -> None:
    context = _context()
    card = default_cards()[0]
    incompatible = card.model_copy(update={"protocol_version": "9.9"})
    registry = A2ARegistry(
        (RegisteredAgent(incompatible, FakeRemoteAgentAdapter("invalid")),)
    )
    with pytest.raises(A2ACompatibilityError):
        registry.discover("langgraph-core")

    registry = build_default_registry()
    with pytest.raises(A2AAccessDeniedError):
        registry.submit(
            _context(role=Role.ORGANIZATION_ADMIN),
            agent_id="langgraph-core",
            skill_id="job-analysis.v1",
            task_id="task-denied",
            payload={},
        )
    with pytest.raises(A2AAccessDeniedError):
        registry.submit(
            context,
            agent_id="langgraph-core",
            skill_id="unknown.v1",
            task_id="task-skill",
            payload={},
        )

    registry.submit(
        context,
        agent_id="langgraph-core",
        skill_id="job-analysis.v1",
        task_id="task-private",
        payload={},
    )
    with pytest.raises(A2ANotFoundError):
        registry.get(_context(actor="grace", tenant="tenant-grace"), "task-private")
