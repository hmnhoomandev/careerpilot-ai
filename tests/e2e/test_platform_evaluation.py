"""Versioned zero-cost aggregate evaluation gate for Phase 15."""

import json
from pathlib import Path

from careerpilot_core import EvaluationGate


def test_offline_platform_metrics_meet_all_versioned_thresholds() -> None:
    fixture = json.loads(
        (
            Path(__file__).parents[1] / "fixtures" / "platform-evaluation-v1.json"
        ).read_text()
    )
    report = EvaluationGate.evaluate(
        suite_id=fixture["suite_id"],
        fixture_version=fixture["fixture_version"],
        values=fixture["values"],
        thresholds=fixture["thresholds"],
    )
    assert report.passed, [
        metric.name for metric in report.metrics if not metric.passed
    ]
    assert {metric.name for metric in report.metrics} == {
        "cost_estimate_coverage",
        "grounding",
        "handoff_correctness",
        "latency_target",
        "retrieval_quality",
        "routing_correctness",
        "safety",
        "tool_correctness",
        "workflow_completion",
    }
