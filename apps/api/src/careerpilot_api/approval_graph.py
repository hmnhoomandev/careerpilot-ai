"""LangGraph human interrupt boundary for exact-version draft review."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver


class ApprovalGraphState(TypedDict):
    approval_id: str
    draft_id: str
    draft_version: int
    draft_hash: str
    status: str
    decision: NotRequired[dict[str, object]]


def build_approval_graph(
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> Any:
    """Compile a pause/resume graph; persistence adapter is injectable."""

    def review(state: ApprovalGraphState) -> dict[str, object]:
        decision = interrupt(
            {
                "type": "careerpilot.approval.v1",
                "approval_id": state["approval_id"],
                "draft_id": state["draft_id"],
                "draft_version": state["draft_version"],
                "draft_hash": state["draft_hash"],
                "allowed_decisions": [
                    "approve",
                    "edit_and_approve",
                    "reject",
                    "request_more_information",
                    "cancel",
                ],
            }
        )
        return {"decision": decision, "status": "decision_received"}

    builder = StateGraph(ApprovalGraphState)
    builder.add_node("human_review", review)
    builder.add_edge(START, "human_review")
    builder.add_edge("human_review", END)
    return builder.compile(
        checkpointer=checkpointer or InMemorySaver(), name="careerpilot-approval-v1"
    )
