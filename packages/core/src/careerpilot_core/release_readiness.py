"""Framework-neutral release gates that keep evidence scope explicit."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class ThresholdDirection(StrEnum):
    """Describe whether a metric must stay above or below its threshold."""

    AT_LEAST = "at_least"
    AT_MOST = "at_most"


class EvidenceScope(StrEnum):
    """Distinguish local regression evidence from production observations."""

    LOCAL = "local"
    PRODUCTION = "production"


@dataclass(frozen=True, slots=True)
class ReadinessTarget:
    """Versioned quantitative target and the scope required to satisfy it."""

    name: str
    threshold: float
    direction: ThresholdDirection
    required_scope: EvidenceScope

    def __post_init__(self) -> None:
        if not self.name or not math.isfinite(self.threshold):
            raise ValueError("readiness_target_invalid")


@dataclass(frozen=True, slots=True)
class ReadinessMeasurement:
    """One aggregate content-free measurement produced by a named check."""

    name: str
    value: float
    scope: EvidenceScope
    sample_count: int

    def __post_init__(self) -> None:
        if not self.name or not math.isfinite(self.value) or self.sample_count < 1:
            raise ValueError("readiness_measurement_invalid")


@dataclass(frozen=True, slots=True)
class ReadinessGate:
    """Evaluated result retaining the target, measurement and failure reason."""

    name: str
    threshold: float
    value: float | None
    required_scope: EvidenceScope
    observed_scope: EvidenceScope | None
    sample_count: int
    passed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ReleaseReadinessReport:
    """Machine-readable gates and an explicit production promotion decision."""

    schema_version: str
    release_version: str
    gates: tuple[ReadinessGate, ...]

    @property
    def local_gates_passed(self) -> bool:
        """Return true when every target requiring only local evidence passes."""
        return all(
            gate.passed
            for gate in self.gates
            if gate.required_scope is EvidenceScope.LOCAL
        )

    @property
    def production_gates_passed(self) -> bool:
        """Return true only when every target has sufficient passing evidence."""
        return all(gate.passed for gate in self.gates)

    @property
    def decision(self) -> str:
        """Never infer production readiness from local-only results."""
        return "go_production" if self.production_gates_passed else "no_go_production"


def evaluate_readiness(
    *,
    release_version: str,
    targets: tuple[ReadinessTarget, ...],
    measurements: tuple[ReadinessMeasurement, ...],
) -> ReleaseReadinessReport:
    """Evaluate unique measurements against unique, scope-aware targets."""
    if not release_version:
        raise ValueError("release_version_required")
    target_names = {target.name for target in targets}
    measured = {measurement.name: measurement for measurement in measurements}
    if len(target_names) != len(targets) or len(measured) != len(measurements):
        raise ValueError("readiness_metric_names_must_be_unique")

    gates: list[ReadinessGate] = []
    for target in targets:
        measurement = measured.get(target.name)
        if measurement is None:
            gates.append(_missing_gate(target))
            continue
        scope_sufficient = (
            target.required_scope is EvidenceScope.LOCAL
            or measurement.scope is EvidenceScope.PRODUCTION
        )
        threshold_met = (
            measurement.value >= target.threshold
            if target.direction is ThresholdDirection.AT_LEAST
            else measurement.value <= target.threshold
        )
        passed = scope_sufficient and threshold_met
        reason = "passed"
        if not scope_sufficient:
            reason = "production_evidence_required"
        elif not threshold_met:
            reason = "threshold_not_met"
        gates.append(
            ReadinessGate(
                name=target.name,
                threshold=target.threshold,
                value=measurement.value,
                required_scope=target.required_scope,
                observed_scope=measurement.scope,
                sample_count=measurement.sample_count,
                passed=passed,
                reason=reason,
            )
        )
    return ReleaseReadinessReport(
        schema_version="careerpilot.release-readiness.v1",
        release_version=release_version,
        gates=tuple(gates),
    )


def nearest_rank_percentile(values: tuple[float, ...], quantile: float) -> float:
    """Return the deterministic nearest-rank percentile for a non-empty sample."""
    if not values or not 0 < quantile <= 1:
        raise ValueError("percentile_input_invalid")
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * quantile) - 1)
    return round(ordered[index], 3)


def _missing_gate(target: ReadinessTarget) -> ReadinessGate:
    return ReadinessGate(
        name=target.name,
        threshold=target.threshold,
        value=None,
        required_scope=target.required_scope,
        observed_scope=None,
        sample_count=0,
        passed=False,
        reason="measurement_missing",
    )
