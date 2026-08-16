"""Run bounded local release measurements and write a content-free JSON report."""

from __future__ import annotations

import argparse
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from careerpilot_core import (
    BackupRecord,
    EvidenceScope,
    ModelDefinition,
    ModelRegistry,
    PrivacyClass,
    ReadinessMeasurement,
    ReadinessTarget,
    RouteFailure,
    RouteRequest,
    RoutingBlockedError,
    ThresholdDirection,
    create_backup_snapshot,
    evaluate_readiness,
    nearest_rank_percentile,
    restore_backup_snapshot,
)

HTTP_OK = 200


def _request(client: TestClient, path: str) -> tuple[bool, float]:
    started = time.perf_counter()
    response = client.get(path)
    elapsed_ms = (time.perf_counter() - started) * 1_000
    return response.status_code == HTTP_OK, elapsed_ms


def measure_local_api(profile: dict[str, int]) -> tuple[ReadinessMeasurement, ...]:
    """Measure bounded in-process health traffic with warm-up and concurrency."""
    logging.getLogger("careerpilot.api").setLevel(logging.WARNING)
    app = create_app()
    durations: list[float] = []
    with TestClient(app) as client:
        for _ in range(profile["warmup_requests"]):
            _request(client, "/health/live")
        with ThreadPoolExecutor(max_workers=profile["concurrency"]) as pool:
            load_results = tuple(
                pool.map(
                    lambda _index: _request(client, "/health/live"),
                    range(profile["load_requests"]),
                )
            )
        soak_results = tuple(
            _request(client, "/health/ready") for _ in range(profile["soak_requests"])
        )
    durations.extend(duration for _success, duration in load_results)
    successes = sum(success for success, _duration in load_results)
    soak_successes = sum(success for success, _duration in soak_results)
    return (
        ReadinessMeasurement(
            name="local_api_success_rate",
            value=successes / len(load_results),
            scope=EvidenceScope.LOCAL,
            sample_count=len(load_results),
        ),
        ReadinessMeasurement(
            name="local_api_p95_latency_ms",
            value=nearest_rank_percentile(tuple(durations), 0.95),
            scope=EvidenceScope.LOCAL,
            sample_count=len(durations),
        ),
        ReadinessMeasurement(
            name="local_concurrent_completion_rate",
            value=successes / len(load_results),
            scope=EvidenceScope.LOCAL,
            sample_count=len(load_results),
        ),
        ReadinessMeasurement(
            name="local_soak_completion_rate",
            value=soak_successes / len(soak_results),
            scope=EvidenceScope.LOCAL,
            sample_count=len(soak_results),
        ),
    )


def measure_recovery_and_policy() -> tuple[ReadinessMeasurement, ...]:
    """Exercise tombstone-safe restore and visible no-fallback provider outage."""
    snapshot = create_backup_snapshot(
        (
            BackupRecord("tenant_synthetic_alpha", "record-active", "profile"),
            BackupRecord("tenant_synthetic_alpha", "record-deleted", "document"),
            BackupRecord("tenant_synthetic_beta", "record-foreign", "profile"),
        ),
        ("record-deleted",),
    )
    restored = restore_backup_snapshot(
        snapshot, isolated_tenant_id="tenant_synthetic_alpha"
    )
    registry = ModelRegistry(
        (
            ModelDefinition(
                route_id="synthetic-unavailable-v1",
                provider="synthetic-provider",
                model="synthetic-model",
                capabilities=frozenset({"job_analysis"}),
                allowed_privacy=frozenset({PrivacyClass.METADATA_ONLY}),
                quality_score=1,
                p95_latency_ms=1,
                cost_per_1k_tokens_chf=0,
                available=False,
                external=False,
            ),
        )
    )
    outage_visible = 0.0
    try:
        registry.decide(
            RouteRequest(
                route_id="synthetic-unavailable-v1",
                capability="job_analysis",
                privacy=PrivacyClass.METADATA_ONLY,
                minimum_quality=1,
                maximum_latency_ms=10,
                estimated_tokens=1,
            ),
            remaining_budget_chf=0,
        )
    except RoutingBlockedError as error:
        outage_visible = float(error.reason is RouteFailure.PROVIDER_UNAVAILABLE)
    return (
        ReadinessMeasurement(
            name="local_backup_restore_success",
            value=float(restored == (snapshot.records[0],)),
            scope=EvidenceScope.LOCAL,
            sample_count=3,
        ),
        ReadinessMeasurement(
            name="local_provider_outage_visible",
            value=outage_visible,
            scope=EvidenceScope.LOCAL,
            sample_count=1,
        ),
        ReadinessMeasurement(
            name="local_default_cost_chf",
            value=0,
            scope=EvidenceScope.LOCAL,
            sample_count=1,
        ),
    )


def build_report(policy: dict[str, Any]) -> dict[str, Any]:
    """Build one serializable report from a validated policy document."""
    targets = tuple(
        ReadinessTarget(
            name=item["name"],
            threshold=float(item["threshold"]),
            direction=ThresholdDirection(item["direction"]),
            required_scope=EvidenceScope(item["required_scope"]),
        )
        for item in policy["targets"]
    )
    measurements = measure_local_api(policy["local_profile"])
    measurements += measure_recovery_and_policy()
    report = evaluate_readiness(
        release_version=policy["release_version"],
        targets=targets,
        measurements=measurements,
    )
    return {
        "schema_version": report.schema_version,
        "release_version": report.release_version,
        "decision": report.decision,
        "local_gates_passed": report.local_gates_passed,
        "production_gates_passed": report.production_gates_passed,
        "gates": [asdict(gate) for gate in report.gates],
        "limitations": [
            "in_process_local_measurement",
            "synthetic_data_only",
            "no_production_or_staging_traffic",
            "unsigned_unpublished_candidate",
        ],
    }


def main() -> int:
    """Load policy, run bounded measurements and write deterministic-shape JSON."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("tests/fixtures/release-readiness-v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/release-readiness.json"),
    )
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    report = build_report(policy)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(  # noqa: T201
        f"Local release gates passed={report['local_gates_passed']}; "
        f"production decision={report['decision']}; report={args.output}"
    )
    return 0 if report["local_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
