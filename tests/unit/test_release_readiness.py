"""Scope-aware release gate and percentile tests."""

import pytest

from careerpilot_core import (
    EvidenceScope,
    ReadinessMeasurement,
    ReadinessTarget,
    ThresholdDirection,
    evaluate_readiness,
    nearest_rank_percentile,
)


def test_local_evidence_passes_local_gate_but_not_production_gate() -> None:
    report = evaluate_readiness(
        release_version="0.20.0-rc.1",
        targets=(
            ReadinessTarget(
                "local_completion", 1, ThresholdDirection.AT_LEAST, EvidenceScope.LOCAL
            ),
            ReadinessTarget(
                "availability",
                0.995,
                ThresholdDirection.AT_LEAST,
                EvidenceScope.PRODUCTION,
            ),
        ),
        measurements=(
            ReadinessMeasurement("local_completion", 1, EvidenceScope.LOCAL, 100),
            ReadinessMeasurement("availability", 1, EvidenceScope.LOCAL, 100),
        ),
    )

    assert report.local_gates_passed is True
    assert report.production_gates_passed is False
    assert report.decision == "no_go_production"
    assert report.gates[1].reason == "production_evidence_required"


def test_missing_and_failed_measurements_fail_closed() -> None:
    report = evaluate_readiness(
        release_version="0.20.0-rc.1",
        targets=(
            ReadinessTarget(
                "error_rate", 0.005, ThresholdDirection.AT_MOST, EvidenceScope.LOCAL
            ),
            ReadinessTarget(
                "restore", 1, ThresholdDirection.AT_LEAST, EvidenceScope.LOCAL
            ),
        ),
        measurements=(
            ReadinessMeasurement("error_rate", 0.01, EvidenceScope.LOCAL, 100),
        ),
    )

    assert report.local_gates_passed is False
    assert [gate.reason for gate in report.gates] == [
        "threshold_not_met",
        "measurement_missing",
    ]


def test_nearest_rank_percentile_is_deterministic_and_validated() -> None:
    assert nearest_rank_percentile((5, 1, 2, 3, 4), 0.95) == 5
    with pytest.raises(ValueError, match="percentile_input_invalid"):
        nearest_rank_percentile((), 0.95)
