"""Metadata-only process-local telemetry used by the prototype."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResearchMetric:
    tenant_id: str
    actor_id: str
    session_id: str
    provider: str
    outcome: str
    source_count: int


class MetricSink:
    def __init__(self) -> None:
        self._items: list[ResearchMetric] = []

    def record(self, metric: ResearchMetric) -> None:
        self._items.append(metric)

    def items(self) -> tuple[ResearchMetric, ...]:
        return tuple(self._items)
