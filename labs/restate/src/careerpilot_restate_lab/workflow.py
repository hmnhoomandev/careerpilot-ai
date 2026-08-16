"""Restate implementation of the bounded durable-effect comparison scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from threading import Lock
from typing import TypedDict

import restate


class PreparationCommand(TypedDict):
    """Opaque, synthetic input shared conceptually by all three implementations."""

    tenant_id: str
    application_id: str
    operation: str
    idempotency_key: str


class PreparationResult(TypedDict):
    """Observable result used to compare completion and effect identity."""

    application_id: str
    artifact_ref: str
    replayed_effect: bool
    status: str


@dataclass(slots=True)
class EffectLedger:
    """Thread-safe fake effect store with a deterministic post-commit failure."""

    fail_after_commit_once: bool = False
    results: dict[str, str] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def apply(self, command: PreparationCommand) -> PreparationResult:
        """Apply once per idempotency key, even when Restate retries the run."""
        key = command["idempotency_key"]
        with self._lock:
            attempt = self.attempts.get(key, 0) + 1
            self.attempts[key] = attempt
            existing = self.results.get(key)
            if existing is not None:
                return self._result(command, existing, replayed=True)
            artifact_ref = (
                f"artifact:{command['application_id']}:{command['operation']}"
            )
            self.results[key] = artifact_ref
            if self.fail_after_commit_once and attempt == 1:
                raise RuntimeError("synthetic_transient_failure_after_commit")
            return self._result(command, artifact_ref, replayed=False)

    @staticmethod
    def _result(
        command: PreparationCommand, artifact_ref: str, *, replayed: bool
    ) -> PreparationResult:
        return {
            "application_id": command["application_id"],
            "artifact_ref": artifact_ref,
            "replayed_effect": replayed,
            "status": "completed",
        }

    def attempt_count(self, key: str) -> int:
        """Return how often the effect boundary was entered."""
        return self.attempts.get(key, 0)

    def unique_effect_count(self) -> int:
        """Return the number of committed idempotency keys."""
        return len(self.results)


_ledger = EffectLedger()


def configure_ledger(ledger: EffectLedger) -> None:
    """Install a synthetic ledger before starting the local harness."""
    global _ledger
    _ledger = ledger


workflow = restate.Workflow("CareerPilotDurableComparison")


@workflow.main()
async def run(
    ctx: restate.WorkflowContext, command: PreparationCommand
) -> PreparationResult:
    """Journal a bounded durable run with two quick local retry attempts."""
    options: restate.RunOptions[PreparationResult] = restate.RunOptions(
        max_attempts=2,
        initial_retry_interval=timedelta(milliseconds=10),
        max_retry_interval=timedelta(milliseconds=10),
    )
    return await ctx.run_typed(
        "record-preparation-effect", _ledger.apply, options, command
    )


app = restate.app([workflow])
