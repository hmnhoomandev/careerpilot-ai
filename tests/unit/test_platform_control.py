"""Decision-table tests for telemetry, routing, budgets, and evaluation gates."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from careerpilot_api.observability import (
    ContentCaptureMode,
    DisabledTelemetryExporter,
    ExporterConfiguration,
    telemetry_json,
)
from careerpilot_core import (
    BudgetLedger,
    BudgetReservation,
    CachePolicy,
    EvaluationGate,
    LocalTelemetryCollector,
    ModelDefinition,
    ModelRegistry,
    OperationKind,
    PrivacyClass,
    PromptDefinition,
    PromptRegistry,
    QuotaLedger,
    RouteFailure,
    RouteRequest,
    RoutingBlockedError,
    TelemetryEvent,
)


def event(event_id: str = "event-1", **changes: object) -> TelemetryEvent:
    fields: dict[str, object] = {
        "event_id": event_id,
        "occurred_at": datetime(2026, 8, 14, tzinfo=UTC).isoformat(),
        "tenant_id": "tenant-ada",
        "actor_id": "actor-ada",
        "correlation_id": "correlation-1",
        "operation_id": "workflow-1",
        "kind": OperationKind.MODEL,
        "operation": "analysis.extract",
        "outcome": "success",
        "duration_ms": 20,
        "provider": "fake",
        "model": "deterministic-v1",
        "prompt_version": "analysis-v1",
    }
    fields.update(changes)
    return TelemetryEvent(**fields)  # type: ignore[arg-type]


def registry(*, available: bool = True) -> ModelRegistry:
    return ModelRegistry(
        (
            ModelDefinition(
                route_id="analysis-fake-v1",
                provider="fake",
                model="deterministic-v1",
                capabilities=frozenset({"job_analysis"}),
                allowed_privacy=frozenset(PrivacyClass),
                quality_score=0.95,
                p95_latency_ms=100,
                cost_per_1k_tokens_chf=0,
                available=available,
                external=False,
            ),
            ModelDefinition(
                route_id="analysis-paid-v1",
                provider="gemini",
                model="configured-model",
                capabilities=frozenset({"job_analysis"}),
                allowed_privacy=frozenset({PrivacyClass.METADATA_ONLY}),
                quality_score=0.97,
                p95_latency_ms=900,
                cost_per_1k_tokens_chf=0.02,
                available=True,
                external=True,
            ),
        )
    )


def request(route_id: str = "analysis-fake-v1", **changes: object) -> RouteRequest:
    fields: dict[str, object] = {
        "route_id": route_id,
        "capability": "job_analysis",
        "privacy": PrivacyClass.MINIMIZED_PERSONAL,
        "minimum_quality": 0.9,
        "maximum_latency_ms": 1_000,
        "estimated_tokens": 1_000,
    }
    fields.update(changes)
    return RouteRequest(**fields)  # type: ignore[arg-type]


def test_telemetry_is_bounded_content_free_and_tenant_scoped() -> None:
    collector = LocalTelemetryCollector(max_events=2)
    collector.record(event("event-1", duration_ms=10))
    collector.record(event("event-2", duration_ms=20, outcome="error"))
    collector.record(event("event-3", duration_ms=30, estimated_cost_chf=0.01))
    summary = collector.summary("tenant-ada")
    assert summary.event_count == 2
    assert summary.p95_duration_ms == 30
    assert summary.estimated_cost_chf == 0.01
    assert collector.events_for("tenant-grace") == ()
    with pytest.raises(ValueError, match="opaque"):
        event(attributes=(("prompt", "private career content with spaces"),))


def test_exporters_are_disabled_and_no_content_is_serialized() -> None:
    configuration = ExporterConfiguration("cloud-trace")
    assert configuration.content_capture is ContentCaptureMode.NO_CONTENT
    payload = telemetry_json(event())
    assert "private career content" not in payload
    assert '"prompt_version":"analysis-v1"' in payload
    with pytest.raises(RuntimeError, match="disabled"):
        DisabledTelemetryExporter(configuration).export(event())
    with pytest.raises(ValueError, match="approval"):
        ExporterConfiguration("langsmith", enabled=True)


@pytest.mark.parametrize(
    ("route_request", "remaining", "reason"),
    [
        (request("missing"), 0, RouteFailure.CAPABILITY_UNAVAILABLE),
        (request(minimum_quality=0.99), 0, RouteFailure.QUALITY_BELOW_MINIMUM),
        (request(maximum_latency_ms=50), 0, RouteFailure.LATENCY_ABOVE_MAXIMUM),
        (request("analysis-paid-v1"), 1, RouteFailure.PRIVACY_POLICY_BLOCKED),
        (
            request(
                "analysis-paid-v1",
                privacy=PrivacyClass.METADATA_ONLY,
                cost_approved=False,
            ),
            1,
            RouteFailure.BUDGET_APPROVAL_REQUIRED,
        ),
        (
            request(
                "analysis-paid-v1",
                privacy=PrivacyClass.METADATA_ONLY,
                cost_approved=True,
            ),
            0,
            RouteFailure.BUDGET_EXCEEDED,
        ),
    ],
)
def test_routing_fails_with_one_explicit_reason_and_no_fallback(
    route_request: RouteRequest, remaining: float, reason: RouteFailure
) -> None:
    with pytest.raises(RoutingBlockedError) as caught:
        registry().decide(route_request, remaining_budget_chf=remaining)
    assert caught.value.reason is reason


def test_zero_cost_route_and_idempotent_budget_reservation() -> None:
    decision = registry().decide(request(), remaining_budget_chf=0)
    assert (decision.provider, decision.estimated_cost_chf) == ("fake", 0)
    ledger = BudgetLedger({"tenant-ada": 0.01})
    reservation = BudgetReservation("reserve-1", "tenant-ada", "workflow-1", 0.01)
    ledger.reserve(reservation)
    ledger.reserve(reservation)
    assert ledger.remaining("tenant-ada") == 0
    with pytest.raises(RoutingBlockedError):
        ledger.reserve(BudgetReservation("reserve-2", "tenant-ada", "workflow-2", 0.01))


def test_evaluation_gate_exposes_threshold_failures() -> None:
    passed = EvaluationGate.evaluate(
        suite_id="offline-platform-v1",
        fixture_version="1",
        values={"grounding": 1.0, "routing": 1.0},
        thresholds={"grounding": 1.0, "routing": 0.95},
    )
    assert passed.passed
    failed = EvaluationGate.evaluate(
        suite_id="offline-platform-v1",
        fixture_version="1",
        values={"grounding": 0.8},
        thresholds={"grounding": 0.95},
    )
    assert not failed.passed


def test_prompt_quota_and_cache_policies_are_explicit_and_scoped() -> None:
    prompts = PromptRegistry(
        (PromptDefinition("job-analysis", "v1", "job_analysis", "digest-1"),)
    )
    assert prompts.get("job-analysis", "v1").template_digest == "digest-1"
    with pytest.raises(LookupError):
        prompts.get("job-analysis", "latest")

    quotas = QuotaLedger({("tenant-ada", "job_analysis"): 1})
    assert quotas.consume("tenant-ada", "job_analysis") == 1
    with pytest.raises(PermissionError, match="quota"):
        quotas.consume("tenant-ada", "job_analysis")

    assert (
        CachePolicy.key(
            tenant_id="tenant-ada",
            capability="job-analysis",
            prompt_version="v1",
            model_route="fake-v1",
            input_digest="sha256:abc",
            privacy=PrivacyClass.SENSITIVE,
            authorized=True,
        )
        is None
    )
    cache_key = CachePolicy.key(
        tenant_id="tenant-ada",
        capability="job-analysis",
        prompt_version="v1",
        model_route="fake-v1",
        input_digest="sha256:abc",
        privacy=PrivacyClass.MINIMIZED_PERSONAL,
        authorized=True,
    )
    assert cache_key is not None
    assert cache_key.startswith("tenant-ada:")
