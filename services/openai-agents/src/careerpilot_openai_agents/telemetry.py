"""Redacted local trace evidence without prompts or hidden reasoning."""

from dataclasses import dataclass

from careerpilot_openai_agents.models import OrchestrationMode


@dataclass(frozen=True, slots=True)
class TraceEvent:
    tenant_id: str
    actor_id: str
    session_id: str
    provider: str
    mode: OrchestrationMode
    outcome: str


class TraceSink:
    def __init__(self) -> None:
        self._events: list[TraceEvent] = []

    def record(self, event: TraceEvent) -> None:
        self._events.append(event)

    def events(self) -> tuple[TraceEvent, ...]:
        return tuple(self._events)
