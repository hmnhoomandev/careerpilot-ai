"""Durability, time-skipping, signal, retry, compensation, and replay tests."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import pytest
from careerpilot_temporal import (
    TASK_QUEUE,
    ApplicationPreparationWorkflow,
    ApplicationWorkflowInput,
    ApprovalSignal,
    FakeActivityLedger,
    PreparationActivities,
    WorkflowStage,
)
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import CancelledError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Replayer, Worker

pytestmark = [pytest.mark.asyncio, pytest.mark.temporal]


def _input(*, delay: int = 604_800) -> ApplicationWorkflowInput:
    return ApplicationWorkflowInput(
        tenant_id="tenant-ada",
        actor_id="ada",
        application_id=f"application-{uuid.uuid4()}",
        profile_ref="profile:synthetic-1",
        job_ref="job:synthetic-1",
        draft_ref="draft:synthetic-1",
        draft_version=3,
        correlation_id="corr-temporal-integration",
        follow_up_delay_seconds=delay,
    )


def _approval(input_: ApplicationWorkflowInput, decision: str) -> ApprovalSignal:
    return ApprovalSignal(
        decision=decision,
        draft_ref=input_.draft_ref,
        draft_version=input_.draft_version,
        decided_by_actor_id=input_.actor_id,
    )


async def _await_stage(handle: Any, stage: WorkflowStage) -> None:
    for _ in range(100):
        status = await handle.query(ApplicationPreparationWorkflow.status)
        if status.stage == stage:
            return
        await asyncio.sleep(0.01)
    raise AssertionError(stage)


@pytest.mark.temporal
async def test_worker_restart_exact_approval_time_skip_and_replay() -> None:
    async with await WorkflowEnvironment.start_time_skipping() as environment:
        ledger = FakeActivityLedger()
        activities = PreparationActivities(ledger)
        input_ = _input()
        async with Worker(
            environment.client,
            task_queue=TASK_QUEUE,
            workflows=[ApplicationPreparationWorkflow],
            activities=activities.definitions(),
            max_cached_workflows=0,
        ):
            handle = await environment.client.start_workflow(
                ApplicationPreparationWorkflow.run,
                input_,
                id=input_.application_id,
                task_queue=TASK_QUEUE,
            )
            await _await_stage(handle, WorkflowStage.AWAITING_APPROVAL)

        async with Worker(
            environment.client,
            task_queue=TASK_QUEUE,
            workflows=[ApplicationPreparationWorkflow],
            activities=activities.definitions(),
            max_cached_workflows=0,
        ):
            await handle.signal(
                ApplicationPreparationWorkflow.decide_approval,
                ApprovalSignal("approved", input_.draft_ref, 2, input_.actor_id),
            )
            await _await_stage(handle, WorkflowStage.AWAITING_APPROVAL)
            status = await handle.query(ApplicationPreparationWorkflow.status)
            assert status.approval_decision is None
            assert "stale" in status.decision_summary

            await handle.signal(
                ApplicationPreparationWorkflow.decide_approval,
                _approval(input_, "approved"),
            )
            result = await handle.result()

        assert result.stage == WorkflowStage.COMPLETED
        assert result.completed_steps == (
            "analysis",
            "research",
            "drafts",
            "tracking",
            "follow_up",
        )
        assert result.follow_up_ref is not None
        history = await handle.fetch_history()
        await Replayer(workflows=[ApplicationPreparationWorkflow]).replay_workflow(
            history
        )


@pytest.mark.temporal
async def test_retry_after_commit_does_not_duplicate_effect() -> None:
    async with await WorkflowEnvironment.start_time_skipping() as environment:
        ledger = FakeActivityLedger(fail_after_commit_once={"research"})
        activities = PreparationActivities(ledger)
        input_ = _input(delay=1)
        async with Worker(
            environment.client,
            task_queue=TASK_QUEUE,
            workflows=[ApplicationPreparationWorkflow],
            activities=activities.definitions(),
            max_cached_workflows=0,
        ):
            handle = await environment.client.start_workflow(
                ApplicationPreparationWorkflow.run,
                input_,
                id=input_.application_id,
                task_queue=TASK_QUEUE,
            )
            await _await_stage(handle, WorkflowStage.AWAITING_APPROVAL)
            await handle.signal(
                ApplicationPreparationWorkflow.decide_approval,
                _approval(input_, "approved"),
            )
            result = await handle.result()

        assert result.stage == WorkflowStage.COMPLETED
        assert ledger.attempts[f"{input_.application_id}:research:v1"] == 2
        assert len(ledger.results) == 5


@pytest.mark.temporal
@pytest.mark.parametrize("decision", ["rejected", "cancelled"])
async def test_rejection_and_signal_cancellation_compensate_in_reverse(
    decision: str,
) -> None:
    async with await WorkflowEnvironment.start_time_skipping() as environment:
        ledger = FakeActivityLedger()
        activities = PreparationActivities(ledger)
        input_ = _input(delay=1)
        async with Worker(
            environment.client,
            task_queue=TASK_QUEUE,
            workflows=[ApplicationPreparationWorkflow],
            activities=activities.definitions(),
            max_cached_workflows=0,
        ):
            handle = await environment.client.start_workflow(
                ApplicationPreparationWorkflow.run,
                input_,
                id=input_.application_id,
                task_queue=TASK_QUEUE,
            )
            await _await_stage(handle, WorkflowStage.AWAITING_APPROVAL)
            if decision == "rejected":
                await handle.signal(
                    ApplicationPreparationWorkflow.decide_approval,
                    _approval(input_, "rejected"),
                )
            else:
                await handle.signal(ApplicationPreparationWorkflow.request_cancellation)
            result = await handle.result()

        expected = (
            WorkflowStage.REJECTED
            if decision == "rejected"
            else WorkflowStage.CANCELLED
        )
        assert result.stage == expected
        assert result.compensated_steps == ("drafts", "research", "analysis")
        assert ledger.compensated == ["drafts", "research", "analysis"]


@pytest.mark.temporal
async def test_temporal_cancellation_compensates_before_terminal_cancel() -> None:
    async with await WorkflowEnvironment.start_time_skipping() as environment:
        ledger = FakeActivityLedger()
        activities = PreparationActivities(ledger)
        input_ = _input(delay=1)
        async with Worker(
            environment.client,
            task_queue=TASK_QUEUE,
            workflows=[ApplicationPreparationWorkflow],
            activities=activities.definitions(),
            max_cached_workflows=0,
        ):
            handle = await environment.client.start_workflow(
                ApplicationPreparationWorkflow.run,
                input_,
                id=input_.application_id,
                task_queue=TASK_QUEUE,
            )
            await _await_stage(handle, WorkflowStage.AWAITING_APPROVAL)
            await handle.cancel()
            with pytest.raises(WorkflowFailureError) as failure:
                await handle.result()

        assert isinstance(failure.value.cause, CancelledError)
        assert ledger.compensated == ["drafts", "research", "analysis"]
