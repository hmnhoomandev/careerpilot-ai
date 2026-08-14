"""Deterministic Temporal owner of the durable application-preparation process."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from careerpilot_temporal.activities import PreparationActivities
    from careerpilot_temporal.contracts import (
        ActivityCommand,
        ActivityResult,
        ApplicationWorkflowInput,
        ApprovalSignal,
        WorkflowResult,
        WorkflowStage,
        WorkflowStatus,
    )

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

ACTIVITY_TIMEOUT = timedelta(seconds=10)
HEARTBEAT_TIMEOUT = timedelta(seconds=2)
RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2,
    maximum_interval=timedelta(seconds=5),
    maximum_attempts=3,
)


@workflow.defn
class ApplicationPreparationWorkflow:
    """Coordinate durable steps while keeping every external effect in activities."""

    def __init__(self) -> None:
        self._input: ApplicationWorkflowInput | None = None
        self._stage = WorkflowStage.CREATED
        self._completed: list[str] = []
        self._compensated: list[str] = []
        self._approval: ApprovalSignal | None = None
        self._cancel_requested = False
        self._decision_summary = "Workflow created."

    def _command(self, step: str, *refs: str) -> ActivityCommand:
        if self._input is None:
            raise RuntimeError("workflow_input_unavailable")
        return ActivityCommand(
            tenant_id=self._input.tenant_id,
            actor_id=self._input.actor_id,
            application_id=self._input.application_id,
            correlation_id=self._input.correlation_id,
            step=step,
            idempotency_key=f"{self._input.application_id}:{step}:v1",
            input_refs=tuple(refs),
        )

    async def _activity(
        self,
        method: Callable[
            [PreparationActivities, ActivityCommand], Awaitable[ActivityResult]
        ],
        command: ActivityCommand,
    ) -> str:
        result: ActivityResult = await workflow.execute_activity_method(
            method,
            command,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )
        self._completed.append(command.step)
        return result.artifact_ref

    async def _compensate(self) -> None:
        self._stage = WorkflowStage.CANCELLING
        for step in reversed(self._completed):
            if step in self._compensated:
                continue
            await workflow.execute_activity_method(
                PreparationActivities.compensate_step,
                self._command(step),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                heartbeat_timeout=HEARTBEAT_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            self._compensated.append(step)

    def _result(self, *, follow_up_ref: str | None = None) -> WorkflowResult:
        if self._input is None:
            raise RuntimeError("workflow_input_unavailable")
        return WorkflowResult(
            application_id=self._input.application_id,
            stage=self._stage,
            completed_steps=tuple(self._completed),
            compensated_steps=tuple(self._compensated),
            follow_up_ref=follow_up_ref,
            decision_summary=self._decision_summary,
        )

    @workflow.run
    async def run(self, input_: ApplicationWorkflowInput) -> WorkflowResult:
        self._input = input_
        try:
            self._stage = WorkflowStage.ANALYZING
            analysis_ref = await self._activity(
                PreparationActivities.analyze,
                self._command("analysis", input_.profile_ref, input_.job_ref),
            )
            self._stage = WorkflowStage.RESEARCHING
            research_ref = await self._activity(
                PreparationActivities.research,
                self._command("research", input_.job_ref),
            )
            self._stage = WorkflowStage.DRAFTING
            await self._activity(
                PreparationActivities.prepare_drafts,
                self._command("drafts", analysis_ref, research_ref, input_.draft_ref),
            )
            self._stage = WorkflowStage.AWAITING_APPROVAL
            self._decision_summary = "Waiting for exact-version human approval."
            await workflow.wait_condition(
                lambda: self._approval is not None or self._cancel_requested
            )
            if self._cancel_requested:
                await self._compensate()
                self._stage = WorkflowStage.CANCELLED
                self._decision_summary = "Cancelled and compensated by request."
                return self._result()
            if self._approval is None or self._approval.decision != "approved":
                await self._compensate()
                self._stage = WorkflowStage.REJECTED
                self._decision_summary = (
                    "Rejected by human review; effects compensated."
                )
                return self._result()
            self._stage = WorkflowStage.TRACKING
            tracking_ref = await self._activity(
                PreparationActivities.track_application,
                self._command("tracking", input_.draft_ref),
            )
            self._stage = WorkflowStage.WAITING_FOLLOW_UP
            if workflow.patched("phase12-follow-up-v1"):
                await workflow.sleep(input_.follow_up_delay_seconds)
            follow_up_ref = await self._activity(
                PreparationActivities.record_follow_up,
                self._command("follow_up", tracking_ref),
            )
            self._stage = WorkflowStage.COMPLETED
            self._decision_summary = "Approved preparation and follow-up completed."
            return self._result(follow_up_ref=follow_up_ref)
        except asyncio.CancelledError:
            await asyncio.shield(self._compensate())
            self._stage = WorkflowStage.CANCELLED
            self._decision_summary = (
                "Temporal cancellation compensated completed steps."
            )
            raise

    @workflow.signal
    def decide_approval(self, signal: ApprovalSignal) -> None:
        if self._stage is not WorkflowStage.AWAITING_APPROVAL or self._input is None:
            return
        exact_draft = (
            signal.draft_ref == self._input.draft_ref
            and signal.draft_version == self._input.draft_version
            and signal.decided_by_actor_id == self._input.actor_id
        )
        if signal.decision not in {"approved", "rejected"} or not exact_draft:
            self._decision_summary = "Ignored invalid or stale approval signal."
            return
        self._approval = signal

    @workflow.signal
    def request_cancellation(self) -> None:
        self._cancel_requested = True

    @workflow.query
    def status(self) -> WorkflowStatus:
        return WorkflowStatus(
            stage=self._stage,
            completed_steps=tuple(self._completed),
            compensated_steps=tuple(self._compensated),
            approval_decision=(
                self._approval.decision if self._approval is not None else None
            ),
            decision_summary=self._decision_summary,
        )
