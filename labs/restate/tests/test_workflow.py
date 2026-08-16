"""Restate harness evidence for happy-path and post-commit recovery semantics."""

from __future__ import annotations

import pytest
from restate import create_test_harness

from careerpilot_restate_lab.workflow import (
    EffectLedger,
    PreparationCommand,
    app,
    configure_ledger,
    run,
)

RESTATE_TEST_IMAGE = "docker.io/restatedev/restate:1.7.0"


def command() -> PreparationCommand:
    return {
        "tenant_id": "tenant_synthetic_alpha",
        "application_id": "application_synthetic_001",
        "operation": "record_preparation",
        "idempotency_key": "application_synthetic_001:record_preparation:v1",
    }


@pytest.mark.asyncio
async def test_happy_path_commits_one_effect() -> None:
    ledger = EffectLedger()
    configure_ledger(ledger)

    async with create_test_harness(app, restate_image=RESTATE_TEST_IMAGE) as env:
        result = await env.client.workflow_call(
            run, "restate-happy-application-synthetic-001", command()
        )

    assert result["status"] == "completed"
    assert result["replayed_effect"] is False
    assert ledger.attempt_count(command()["idempotency_key"]) == 1
    assert ledger.unique_effect_count() == 1


@pytest.mark.asyncio
async def test_retry_after_post_commit_failure_does_not_duplicate_effect() -> None:
    ledger = EffectLedger(fail_after_commit_once=True)
    configure_ledger(ledger)

    async with create_test_harness(app, restate_image=RESTATE_TEST_IMAGE) as env:
        result = await env.client.workflow_call(
            run, "restate-recovery-application-synthetic-001", command()
        )

    assert result == {
        "application_id": "application_synthetic_001",
        "artifact_ref": "artifact:application_synthetic_001:record_preparation",
        "replayed_effect": True,
        "status": "completed",
    }
    assert ledger.attempt_count(command()["idempotency_key"]) == 2
    assert ledger.unique_effect_count() == 1
