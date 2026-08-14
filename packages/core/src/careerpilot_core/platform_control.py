"""Privacy-safe telemetry, deterministic model routing, budgets, and evaluations."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

SAFE_METADATA = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
MAX_ATTRIBUTES = 12
TELEMETRY_SCHEMA_VERSION = "careerpilot.telemetry.v1"


class OperationKind(StrEnum):
    HTTP = "http"
    WORKFLOW = "workflow"
    GRAPH = "graph"
    AGENT = "agent"
    TOOL = "tool"
    APPROVAL = "approval"
    RETRIEVAL = "retrieval"
    PROMPT = "prompt"
    MODEL = "model"


class PrivacyClass(StrEnum):
    METADATA_ONLY = "metadata_only"
    MINIMIZED_PERSONAL = "minimized_personal"
    SENSITIVE = "sensitive"


class RouteFailure(StrEnum):
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    PRIVACY_POLICY_BLOCKED = "privacy_policy_blocked"
    QUALITY_BELOW_MINIMUM = "quality_below_minimum"
    LATENCY_ABOVE_MAXIMUM = "latency_above_maximum"
    BUDGET_APPROVAL_REQUIRED = "budget_approval_required"
    BUDGET_EXCEEDED = "budget_exceeded"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


class RoutingBlockedError(RuntimeError):
    """Expose one stable reason instead of silently selecting another provider."""

    def __init__(self, reason: RouteFailure) -> None:
        super().__init__(reason)
        self.reason = reason


def _safe(value: str, field: str) -> None:
    if SAFE_METADATA.fullmatch(value) is None:
        raise ValueError(f"{field}_must_be_opaque_metadata")


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    """Versioned content-free event shared by local and future exporter adapters."""

    event_id: str
    occurred_at: str
    tenant_id: str
    actor_id: str
    correlation_id: str
    operation_id: str
    kind: OperationKind
    operation: str
    outcome: str
    duration_ms: float
    provider: str = "none"
    model: str = "none"
    prompt_version: str = "none"
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_chf: float = 0
    attributes: tuple[tuple[str, str], ...] = ()
    schema_version: str = TELEMETRY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for field in (
            "event_id",
            "tenant_id",
            "actor_id",
            "correlation_id",
            "operation_id",
            "operation",
            "outcome",
            "provider",
            "model",
            "prompt_version",
        ):
            _safe(getattr(self, field), field)
        timestamp = datetime.fromisoformat(self.occurred_at)
        if timestamp.tzinfo is None:
            raise ValueError("telemetry_timestamp_requires_timezone")
        if self.schema_version != TELEMETRY_SCHEMA_VERSION:
            raise ValueError("telemetry_schema_unsupported")
        if self.duration_ms < 0 or self.input_tokens < 0 or self.output_tokens < 0:
            raise ValueError("telemetry_measurement_invalid")
        if self.estimated_cost_chf < 0 or not math.isfinite(self.estimated_cost_chf):
            raise ValueError("telemetry_cost_invalid")
        if len(self.attributes) > MAX_ATTRIBUTES or len(dict(self.attributes)) != len(
            self.attributes
        ):
            raise ValueError("telemetry_attributes_invalid")
        for key, value in self.attributes:
            _safe(key, "attribute_key")
            _safe(value, "attribute_value")


class TelemetrySink(Protocol):
    def record(self, event: TelemetryEvent) -> None: ...


@dataclass(frozen=True, slots=True)
class MetricSummary:
    tenant_id: str
    event_count: int
    success_count: int
    error_count: int
    p50_duration_ms: float
    p95_duration_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_chf: float
    provider_failures: int


class LocalTelemetryCollector:
    """Bounded process-local sink and tenant-scoped metrics dashboard source."""

    def __init__(self, *, max_events: int = 5_000) -> None:
        if max_events < 1:
            raise ValueError("max_events_must_be_positive")
        self._max_events = max_events
        self._events: list[TelemetryEvent] = []

    def record(self, event: TelemetryEvent) -> None:
        self._events.append(event)
        if len(self._events) > self._max_events:
            del self._events[: len(self._events) - self._max_events]

    def events_for(self, tenant_id: str) -> tuple[TelemetryEvent, ...]:
        return tuple(event for event in self._events if event.tenant_id == tenant_id)

    def summary(self, tenant_id: str) -> MetricSummary:
        events = self.events_for(tenant_id)
        durations = sorted(event.duration_ms for event in events)
        return MetricSummary(
            tenant_id=tenant_id,
            event_count=len(events),
            success_count=sum(event.outcome == "success" for event in events),
            error_count=sum(event.outcome == "error" for event in events),
            p50_duration_ms=_percentile(durations, 0.50),
            p95_duration_ms=_percentile(durations, 0.95),
            input_tokens=sum(event.input_tokens for event in events),
            output_tokens=sum(event.output_tokens for event in events),
            estimated_cost_chf=round(
                sum(event.estimated_cost_chf for event in events), 6
            ),
            provider_failures=sum(
                event.outcome == "provider_failure" for event in events
            ),
        )


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0
    index = max(0, math.ceil(len(values) * quantile) - 1)
    return round(values[index], 3)


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    prompt_id: str
    version: str
    capability: str
    template_digest: str
    active: bool = True


class PromptRegistry:
    """Resolve an explicit prompt version without recording its template text."""

    def __init__(self, definitions: tuple[PromptDefinition, ...]) -> None:
        self._definitions = {
            (item.prompt_id, item.version): item for item in definitions
        }
        if len(self._definitions) != len(definitions):
            raise ValueError("duplicate_prompt_version")

    def get(self, prompt_id: str, version: str) -> PromptDefinition:
        definition = self._definitions.get((prompt_id, version))
        if definition is None or not definition.active:
            raise LookupError("prompt_version_unavailable")
        return definition


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    route_id: str
    provider: str
    model: str
    capabilities: frozenset[str]
    allowed_privacy: frozenset[PrivacyClass]
    quality_score: float
    p95_latency_ms: int
    cost_per_1k_tokens_chf: float
    available: bool
    external: bool


@dataclass(frozen=True, slots=True)
class RouteRequest:
    route_id: str
    capability: str
    privacy: PrivacyClass
    minimum_quality: float
    maximum_latency_ms: int
    estimated_tokens: int
    cost_approved: bool = False


@dataclass(frozen=True, slots=True)
class RouteDecision:
    route_id: str
    provider: str
    model: str
    estimated_cost_chf: float
    reason: str = "explicit_route_allowed"


class ModelRegistry:
    """Select only the requested versioned route; never search for a fallback."""

    def __init__(self, definitions: tuple[ModelDefinition, ...]) -> None:
        self._definitions = {item.route_id: item for item in definitions}
        if len(self._definitions) != len(definitions):
            raise ValueError("duplicate_model_route")

    def decide(
        self, request: RouteRequest, *, remaining_budget_chf: float
    ) -> RouteDecision:
        selected = self._definitions.get(request.route_id)
        if selected is None or request.capability not in selected.capabilities:
            raise RoutingBlockedError(RouteFailure.CAPABILITY_UNAVAILABLE)
        if not selected.available:
            raise RoutingBlockedError(RouteFailure.PROVIDER_UNAVAILABLE)
        if request.privacy not in selected.allowed_privacy:
            raise RoutingBlockedError(RouteFailure.PRIVACY_POLICY_BLOCKED)
        if selected.quality_score < request.minimum_quality:
            raise RoutingBlockedError(RouteFailure.QUALITY_BELOW_MINIMUM)
        if selected.p95_latency_ms > request.maximum_latency_ms:
            raise RoutingBlockedError(RouteFailure.LATENCY_ABOVE_MAXIMUM)
        estimate = round(
            selected.cost_per_1k_tokens_chf * request.estimated_tokens / 1_000, 6
        )
        if estimate > 0 and not request.cost_approved:
            raise RoutingBlockedError(RouteFailure.BUDGET_APPROVAL_REQUIRED)
        if estimate > remaining_budget_chf:
            raise RoutingBlockedError(RouteFailure.BUDGET_EXCEEDED)
        return RouteDecision(
            selected.route_id, selected.provider, selected.model, estimate
        )


@dataclass(frozen=True, slots=True)
class BudgetReservation:
    reservation_id: str
    tenant_id: str
    workflow_id: str
    amount_chf: float


class BudgetLedger:
    """Reserve spend before execution; production needs a durable replacement."""

    def __init__(self, limits: dict[str, float]) -> None:
        self._limits = dict(limits)
        self._reservations: dict[str, BudgetReservation] = {}

    def remaining(self, tenant_id: str) -> float:
        used = sum(
            item.amount_chf
            for item in self._reservations.values()
            if item.tenant_id == tenant_id
        )
        return round(self._limits.get(tenant_id, 0) - used, 6)

    def reserve(self, reservation: BudgetReservation) -> None:
        if reservation.amount_chf < 0:
            raise ValueError("reservation_amount_invalid")
        existing = self._reservations.get(reservation.reservation_id)
        if existing is not None:
            if existing != reservation:
                raise ValueError("reservation_id_conflict")
            return
        if reservation.amount_chf > self.remaining(reservation.tenant_id):
            raise RoutingBlockedError(RouteFailure.BUDGET_EXCEEDED)
        self._reservations[reservation.reservation_id] = reservation


class QuotaLedger:
    """Bound local workflow starts per tenant without hiding quota exhaustion."""

    def __init__(self, limits: dict[tuple[str, str], int]) -> None:
        self._limits = dict(limits)
        self._usage: dict[tuple[str, str], int] = {}

    def consume(self, tenant_id: str, capability: str) -> int:
        key = (tenant_id, capability)
        used = self._usage.get(key, 0)
        if used >= self._limits.get(key, 0):
            raise PermissionError("workflow_quota_exceeded")
        self._usage[key] = used + 1
        return self._usage[key]


class CachePolicy:
    """Create scoped keys only for authorized, non-sensitive deterministic inputs."""

    @staticmethod
    def key(  # noqa: PLR0913 - every isolation/version dimension is explicit
        *,
        tenant_id: str,
        capability: str,
        prompt_version: str,
        model_route: str,
        input_digest: str,
        privacy: PrivacyClass,
        authorized: bool,
    ) -> str | None:
        if not authorized or privacy is PrivacyClass.SENSITIVE:
            return None
        for value in (
            tenant_id,
            capability,
            prompt_version,
            model_route,
            input_digest,
        ):
            _safe(value, "cache_key_part")
        return f"{tenant_id}:{capability}:{prompt_version}:{model_route}:{input_digest}"


@dataclass(frozen=True, slots=True)
class EvaluationMetric:
    name: str
    value: float
    threshold: float

    @property
    def passed(self) -> bool:
        return self.value >= self.threshold


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    suite_id: str
    fixture_version: str
    metrics: tuple[EvaluationMetric, ...]

    @property
    def passed(self) -> bool:
        return all(metric.passed for metric in self.metrics)


class EvaluationGate:
    """Build an offline report and expose every missed versioned threshold."""

    @staticmethod
    def evaluate(
        *,
        suite_id: str,
        fixture_version: str,
        values: dict[str, float],
        thresholds: dict[str, float],
    ) -> EvaluationReport:
        if set(values) != set(thresholds):
            raise ValueError("evaluation_metric_set_mismatch")
        metrics = tuple(
            EvaluationMetric(name, values[name], threshold)
            for name, threshold in sorted(thresholds.items())
        )
        return EvaluationReport(suite_id, fixture_version, metrics)
