"""Official-SDK A2A cards and a bounded local task/registry adapter."""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Protocol

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    APIKeySecurityScheme,
    In,
    SecurityScheme,
    Task,
    TaskState,
    TaskStatus,
)

from careerpilot_core import AuthorizationContext, Permission

PROTOCOL_VERSION = "0.3.0"
CARD_VERSION = "1.0.0"
JSON_MODE = "application/json"


class A2ARegistryError(RuntimeError):
    code = "a2a_registry_error"


class A2ANotFoundError(A2ARegistryError):
    code = "a2a_not_found"


class A2AAccessDeniedError(A2ARegistryError):
    code = "a2a_access_denied"


class A2ACompatibilityError(A2ARegistryError):
    code = "a2a_incompatible"


class A2AConflictError(A2ARegistryError):
    code = "a2a_task_conflict"


class A2ATimeoutError(A2ARegistryError):
    code = "a2a_timeout"


class A2AUnavailableError(A2ARegistryError):
    code = "a2a_unavailable"


class RemoteAgentAdapter(Protocol):
    async def execute(
        self, skill_id: str, payload: dict[str, str]
    ) -> dict[str, str]: ...

    async def cancel(self, task_id: str) -> None: ...


class FakeRemoteAgentAdapter:
    """Deterministic remote-agent stand-in; no network or model call occurs."""

    def __init__(
        self, runtime: str, *, available: bool = True, delay: float = 0
    ) -> None:
        self.runtime = runtime
        self.available = available
        self.delay = delay
        self.cancelled: set[str] = set()

    async def execute(self, skill_id: str, payload: dict[str, str]) -> dict[str, str]:
        if not self.available:
            raise ConnectionError("remote_unavailable")
        if self.delay:
            await asyncio.sleep(self.delay)
        return {
            "runtime": self.runtime,
            "skill_id": skill_id,
            "summary": f"Processed synthetic {skill_id} request.",
            "input_reference": payload.get("fixture_id", "synthetic-fixture"),
        }

    async def cancel(self, task_id: str) -> None:
        self.cancelled.add(task_id)


@dataclass(frozen=True, slots=True)
class RegisteredAgent:
    card: AgentCard
    adapter: RemoteAgentAdapter
    permission: Permission = Permission.ANALYSIS_RUN


def _card(
    *, agent_id: str, name: str, description: str, skill_id: str, skill_name: str
) -> AgentCard:
    return AgentCard(
        name=name,
        description=description,
        url=f"http://127.0.0.1:8000/a2a/{agent_id}",
        version=CARD_VERSION,
        protocol_version=PROTOCOL_VERSION,
        preferred_transport="JSONRPC",
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False,
            state_transition_history=True,
        ),
        default_input_modes=[JSON_MODE],
        default_output_modes=[JSON_MODE],
        security_schemes={
            "careerpilotService": SecurityScheme(
                root=APIKeySecurityScheme(
                    name="X-CareerPilot-Service",
                    in_=In.header,
                    description=(
                        "Local development identity; workload identity replaces it."
                    ),
                )
            )
        },
        security=[{"careerpilotService": []}],
        skills=[
            AgentSkill(
                id=skill_id,
                name=skill_name,
                description=description,
                tags=["careerpilot", "synthetic", agent_id],
                examples=[f"Run {skill_name} for synthetic fixture fixture-1."],
                input_modes=[JSON_MODE],
                output_modes=[JSON_MODE],
            )
        ],
    )


def default_cards() -> tuple[AgentCard, ...]:
    return (
        _card(
            agent_id="langgraph-core",
            name="CareerPilot LangGraph Core",
            description="Evidence-grounded candidate-to-job analysis.",
            skill_id="job-analysis.v1",
            skill_name="Job analysis",
        ),
        _card(
            agent_id="google-adk-research",
            name="CareerPilot Google ADK Research",
            description="Research over explicitly supplied company/job sources.",
            skill_id="company-research.v1",
            skill_name="Company research",
        ),
        _card(
            agent_id="openai-interview",
            name="CareerPilot OpenAI Interview",
            description="Synthetic interview simulation and feedback.",
            skill_id="interview-simulation.v1",
            skill_name="Interview simulation",
        ),
    )


class A2ARegistry:
    """Trusted local registry with tenant-scoped official A2A Task values."""

    def __init__(self, registrations: tuple[RegisteredAgent, ...]) -> None:
        self._agents = {
            item.card.url.rsplit("/", 1)[-1]: item for item in registrations
        }
        self._tasks: dict[tuple[str, str, str], Task] = {}
        self._fingerprints: dict[tuple[str, str, str], str] = {}

    def cards(self) -> tuple[AgentCard, ...]:
        cards = tuple(item.card for item in self._agents.values())
        for card in cards:
            self._validate_card(card)
        return cards

    def discover(self, agent_id: str) -> AgentCard:
        item = self._agents.get(agent_id)
        if item is None:
            raise A2ANotFoundError
        self._validate_card(item.card)
        return item.card

    @staticmethod
    def _validate_card(card: AgentCard) -> None:
        if card.protocol_version != PROTOCOL_VERSION or card.version != CARD_VERSION:
            raise A2ACompatibilityError
        if card.preferred_transport != "JSONRPC":
            raise A2ACompatibilityError

    def _registration(
        self, context: AuthorizationContext, agent_id: str, skill_id: str
    ) -> RegisteredAgent:
        item = self._agents.get(agent_id)
        if item is None:
            raise A2ANotFoundError
        self._validate_card(item.card)
        if item.permission is not Permission.ANALYSIS_RUN:
            raise A2AAccessDeniedError
        if context.role.value not in {"owner", "member", "coach"}:
            raise A2AAccessDeniedError
        if skill_id not in {skill.id for skill in item.card.skills}:
            raise A2AAccessDeniedError
        return item

    @staticmethod
    def _key(context: AuthorizationContext, task_id: str) -> tuple[str, str, str]:
        return context.tenant_id, context.actor_id, task_id

    def submit(
        self,
        context: AuthorizationContext,
        *,
        agent_id: str,
        skill_id: str,
        task_id: str,
        payload: dict[str, str],
    ) -> Task:
        self._registration(context, agent_id, skill_id)
        key = self._key(context, task_id)
        canonical = json.dumps(
            {"agent_id": agent_id, "skill_id": skill_id, "payload": payload},
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        if key in self._tasks:
            if self._fingerprints[key] != fingerprint:
                raise A2AConflictError
            return self._tasks[key]
        task = Task(
            id=task_id,
            context_id=str(uuid.uuid4()),
            status=TaskStatus(state=TaskState.submitted),
            metadata={
                "agent_id": agent_id,
                "skill_id": skill_id,
                "correlation_id": context.correlation_id,
            },
        )
        self._tasks[key] = task
        self._fingerprints[key] = fingerprint
        return task

    def get(self, context: AuthorizationContext, task_id: str) -> Task:
        task = self._tasks.get(self._key(context, task_id))
        if task is None:
            raise A2ANotFoundError
        return task

    async def execute(
        self,
        context: AuthorizationContext,
        *,
        task_id: str,
        payload: dict[str, str],
        timeout_seconds: float,
    ) -> Task:
        key = self._key(context, task_id)
        task = self.get(context, task_id)
        if task.status.state is not TaskState.submitted:
            return task
        metadata = dict(task.metadata or {})
        agent_id = str(metadata["agent_id"])
        skill_id = str(metadata["skill_id"])
        item = self._registration(context, agent_id, skill_id)
        self._tasks[key] = task.model_copy(
            update={"status": TaskStatus(state=TaskState.working)}
        )
        try:
            output = await asyncio.wait_for(
                item.adapter.execute(skill_id, payload), timeout=timeout_seconds
            )
        except TimeoutError as error:
            self._tasks[key] = task.model_copy(
                update={"status": TaskStatus(state=TaskState.failed)}
            )
            raise A2ATimeoutError from error
        except Exception as error:
            self._tasks[key] = task.model_copy(
                update={"status": TaskStatus(state=TaskState.failed)}
            )
            raise A2AUnavailableError from error
        completed_metadata = {**metadata, "result": output}
        completed = task.model_copy(
            update={
                "status": TaskStatus(state=TaskState.completed),
                "metadata": completed_metadata,
            }
        )
        self._tasks[key] = completed
        return completed

    async def cancel(self, context: AuthorizationContext, task_id: str) -> Task:
        key = self._key(context, task_id)
        task = self.get(context, task_id)
        if task.status.state in {
            TaskState.completed,
            TaskState.failed,
            TaskState.canceled,
            TaskState.rejected,
        }:
            raise A2AConflictError
        metadata = dict(task.metadata or {})
        item = self._agents[str(metadata["agent_id"])]
        await item.adapter.cancel(task_id)
        cancelled = task.model_copy(
            update={"status": TaskStatus(state=TaskState.canceled)}
        )
        self._tasks[key] = cancelled
        return cancelled


def build_default_registry() -> A2ARegistry:
    cards = default_cards()
    runtimes = ("langgraph", "google-adk", "openai-agents")
    return A2ARegistry(
        tuple(
            RegisteredAgent(card, FakeRemoteAgentAdapter(runtime))
            for card, runtime in zip(cards, runtimes, strict=True)
        )
    )
