"""Side-effect boundary and deterministic fake activities for local verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from temporalio import activity

from careerpilot_temporal.contracts import ActivityCommand, ActivityResult


class ActivityLedger(Protocol):
    """Persistence port that makes activity effects and compensation idempotent."""

    def apply(self, command: ActivityCommand) -> ActivityResult: ...

    def compensate(self, command: ActivityCommand) -> ActivityResult: ...


@dataclass(slots=True)
class FakeActivityLedger:
    """Process-local synthetic ledger used only by default tests and learning runs."""

    fail_after_commit_once: set[str] = field(default_factory=set)
    results: dict[str, ActivityResult] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    compensated: list[str] = field(default_factory=list)

    def apply(self, command: ActivityCommand) -> ActivityResult:
        attempts = self.attempts.get(command.idempotency_key, 0) + 1
        self.attempts[command.idempotency_key] = attempts
        existing = self.results.get(command.idempotency_key)
        if existing is not None:
            return ActivityResult(existing.step, existing.artifact_ref, replayed=True)
        result = ActivityResult(
            step=command.step,
            artifact_ref=f"artifact:{command.application_id}:{command.step}",
            replayed=False,
        )
        self.results[command.idempotency_key] = result
        if command.step in self.fail_after_commit_once and attempts == 1:
            raise RuntimeError("synthetic_transient_failure_after_commit")
        return result

    def compensate(self, command: ActivityCommand) -> ActivityResult:
        replayed = command.step in self.compensated
        if not replayed:
            self.compensated.append(command.step)
        return ActivityResult(
            step=command.step,
            artifact_ref=f"compensation:{command.application_id}:{command.step}",
            replayed=replayed,
        )


class PreparationActivities:
    """Temporal activities that delegate all effects to an idempotent ledger port."""

    def __init__(self, ledger: ActivityLedger) -> None:
        self._ledger = ledger

    def _run(self, command: ActivityCommand) -> ActivityResult:
        activity.heartbeat({"step": command.step})
        return self._ledger.apply(command)

    @activity.defn
    async def analyze(self, command: ActivityCommand) -> ActivityResult:
        return self._run(command)

    @activity.defn
    async def research(self, command: ActivityCommand) -> ActivityResult:
        return self._run(command)

    @activity.defn
    async def prepare_drafts(self, command: ActivityCommand) -> ActivityResult:
        return self._run(command)

    @activity.defn
    async def track_application(self, command: ActivityCommand) -> ActivityResult:
        return self._run(command)

    @activity.defn
    async def record_follow_up(self, command: ActivityCommand) -> ActivityResult:
        return self._run(command)

    @activity.defn
    async def compensate_step(self, command: ActivityCommand) -> ActivityResult:
        activity.heartbeat({"step": command.step, "operation": "compensate"})
        return self._ledger.compensate(command)

    def definitions(self) -> list[Any]:
        """Return bound activities registered by the worker."""
        return [
            self.analyze,
            self.research,
            self.prepare_drafts,
            self.track_application,
            self.record_follow_up,
            self.compensate_step,
        ]
