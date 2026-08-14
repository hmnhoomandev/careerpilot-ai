"""Local/production composition helpers for the Temporal worker boundary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from temporalio.worker import Worker

from careerpilot_temporal.workflow import ApplicationPreparationWorkflow

if TYPE_CHECKING:
    from temporalio.client import Client

    from careerpilot_temporal.activities import PreparationActivities

TASK_QUEUE = "careerpilot-application-preparation-v1"


def build_worker(client: Client, activities: PreparationActivities) -> Worker:
    """Build a worker; callers own connection credentials and worker lifecycle."""
    return Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ApplicationPreparationWorkflow],
        activities=activities.definitions(),
    )
