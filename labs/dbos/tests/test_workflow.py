"""Executable DBOS evidence for happy-path and post-commit recovery semantics."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from dbos import DBOS, SetWorkflowID

from careerpilot_dbos_lab.workflow import (
    EffectLedger,
    PreparationCommand,
    configure_ledger,
    prepare_application,
)


@pytest.fixture(scope="session", autouse=True)
def dbos_runtime(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    database_path: Path = tmp_path_factory.mktemp("dbos") / "system.sqlite"
    database_url = f"sqlite:///{database_path}"
    DBOS(
        config={
            "name": "careerpilot-dbos-comparison",
            "system_database_url": database_url,
        }
    )
    DBOS.reset_system_database()
    DBOS.launch()
    try:
        yield
    finally:
        DBOS.destroy()


def command() -> PreparationCommand:
    return {
        "tenant_id": "tenant_synthetic_alpha",
        "application_id": "application_synthetic_001",
        "operation": "record_preparation",
        "idempotency_key": "application_synthetic_001:record_preparation:v1",
    }


def test_happy_path_commits_one_effect() -> None:
    ledger = EffectLedger()
    configure_ledger(ledger)

    with SetWorkflowID("dbos-happy-application-synthetic-001"):
        result = prepare_application(command())

    assert result["status"] == "completed"
    assert result["replayed_effect"] is False
    assert ledger.attempt_count(command()["idempotency_key"]) == 1
    assert ledger.unique_effect_count() == 1


def test_retry_after_post_commit_failure_does_not_duplicate_effect() -> None:
    ledger = EffectLedger(fail_after_commit_once=True)
    configure_ledger(ledger)

    with SetWorkflowID("dbos-recovery-application-synthetic-001"):
        result = prepare_application(command())

    assert result == {
        "application_id": "application_synthetic_001",
        "artifact_ref": "artifact:application_synthetic_001:record_preparation",
        "replayed_effect": True,
        "status": "completed",
    }
    assert ledger.attempt_count(command()["idempotency_key"]) == 2
    assert ledger.unique_effect_count() == 1
