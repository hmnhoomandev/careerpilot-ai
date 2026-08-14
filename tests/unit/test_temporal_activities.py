"""Unit tests for heartbeat and idempotency at the Temporal activity boundary."""

from __future__ import annotations

import pytest
from careerpilot_temporal import (
    ActivityCommand,
    FakeActivityLedger,
    PreparationActivities,
)
from temporalio.testing import ActivityEnvironment


def _command(step: str = "analysis") -> ActivityCommand:
    return ActivityCommand(
        tenant_id="tenant-ada",
        actor_id="ada",
        application_id="application-1",
        correlation_id="corr-temporal-1",
        step=step,
        idempotency_key=f"application-1:{step}:v1",
        input_refs=("synthetic-ref",),
    )


@pytest.mark.asyncio
async def test_activity_heartbeats_and_replays_committed_effect() -> None:
    ledger = FakeActivityLedger(fail_after_commit_once={"analysis"})
    activities = PreparationActivities(ledger)
    environment = ActivityEnvironment()
    heartbeats: list[object] = []
    environment.on_heartbeat = lambda *details: heartbeats.extend(details)

    with pytest.raises(RuntimeError, match="synthetic_transient"):
        await environment.run(activities.analyze, _command())
    replayed = await environment.run(activities.analyze, _command())

    assert replayed.replayed is True
    assert replayed.artifact_ref == "artifact:application-1:analysis"
    assert ledger.attempts["application-1:analysis:v1"] == 2
    assert heartbeats == [{"step": "analysis"}, {"step": "analysis"}]


@pytest.mark.asyncio
async def test_compensation_is_idempotent() -> None:
    ledger = FakeActivityLedger()
    activities = PreparationActivities(ledger)
    environment = ActivityEnvironment()

    first = await environment.run(activities.compensate_step, _command("drafts"))
    second = await environment.run(activities.compensate_step, _command("drafts"))

    assert first.artifact_ref == second.artifact_ref
    assert first.replayed is False
    assert second.replayed is True
    assert ledger.compensated == ["drafts"]


def test_history_contract_rejects_content_instead_of_opaque_references() -> None:
    with pytest.raises(ValueError, match="opaque_reference"):
        ActivityCommand(
            tenant_id="tenant-ada",
            actor_id="ada",
            application_id="application-1",
            correlation_id="corr-1",
            step="analysis",
            idempotency_key="application-1:analysis:v1",
            input_refs=("Ada has ten years of private experience",),
        )
