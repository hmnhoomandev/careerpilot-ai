"""Serializable exact-action approval for the learning laboratory."""

import hashlib
import json
import uuid

from careerpilot_openai_agents.errors import ApprovalConflictError
from careerpilot_openai_agents.models import ApprovalState, InterviewRequest


def request_approval(request: InterviewRequest) -> ApprovalState:
    canonical = json.dumps(
        {
            "tenant_id": request.tenant_id,
            "actor_id": request.actor_id,
            "session_id": request.session_id,
            "answer": request.candidate_answer,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return ApprovalState(
        approval_id=str(uuid.uuid4()),
        tenant_id=request.tenant_id,
        actor_id=request.actor_id,
        session_id=request.session_id,
        action_hash=hashlib.sha256(canonical.encode()).hexdigest(),
    )


def decide(
    state: ApprovalState,
    *,
    approve: bool,
    expected_revision: int,
    expected_action_hash: str,
) -> ApprovalState:
    if (
        state.status != "pending"
        or state.revision != expected_revision
        or state.action_hash != expected_action_hash
    ):
        raise ApprovalConflictError("stale_or_terminal_approval")
    return state.model_copy(
        update={"status": "approved" if approve else "rejected", "revision": 2}
    )


class ApprovalCoordinator:
    """Process-local pause/resume; durable storage is a later workflow concern."""

    def __init__(self) -> None:
        self._states: dict[str, ApprovalState] = {}

    def pause(self, request: InterviewRequest) -> ApprovalState:
        state = request_approval(request)
        self._states[state.approval_id] = state
        return state

    def resume(
        self,
        approval_id: str,
        *,
        approve: bool,
        expected_revision: int,
        expected_action_hash: str,
    ) -> ApprovalState:
        state = self._states.get(approval_id)
        if state is None:
            raise ApprovalConflictError("approval_not_found")
        updated = decide(
            state,
            approve=approve,
            expected_revision=expected_revision,
            expected_action_hash=expected_action_hash,
        )
        self._states[approval_id] = updated
        return updated
