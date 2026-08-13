"""Deterministic approval transitions and LangGraph interrupt evidence."""

import pytest
from langgraph.types import Command

from careerpilot_api.approval_graph import build_approval_graph
from careerpilot_api.draft_service import BIAS_TERMS, PII_PATTERNS
from careerpilot_core import (
    ApprovalConflictError,
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStatus,
    ApprovalTransitionError,
    CareerDraft,
    Citation,
    ClaimStatus,
    DraftClaim,
)


def _approval() -> ApprovalRecord:
    return ApprovalRecord(
        "approval-1",
        "tenant-ada",
        "actor-ada",
        "draft-1",
        2,
        "a" * 64,
        ApprovalStatus.PENDING,
        1,
    )


@pytest.mark.parametrize(
    ("decision", "status", "feedback"),
    [
        (ApprovalDecision.APPROVE, ApprovalStatus.APPROVED, None),
        (ApprovalDecision.EDIT_AND_APPROVE, ApprovalStatus.EDITED_AND_APPROVED, None),
        (ApprovalDecision.REJECT, ApprovalStatus.REJECTED, "Revise this."),
        (
            ApprovalDecision.REQUEST_MORE_INFORMATION,
            ApprovalStatus.MORE_INFORMATION,
            "Add evidence.",
        ),
        (ApprovalDecision.CANCEL, ApprovalStatus.CANCELLED, None),
    ],
)
def test_all_human_decisions_reach_expected_terminal_state(
    decision: ApprovalDecision, status: ApprovalStatus, feedback: str | None
) -> None:
    updated = _approval().decide(
        decision,
        expected_revision=1,
        expected_draft_version=2,
        expected_draft_hash="a" * 64,
        feedback=feedback,
    )
    assert updated.status is status
    assert updated.revision == 2


def test_stale_and_invalid_transitions_fail_closed() -> None:
    with pytest.raises(ApprovalConflictError):
        _approval().decide(
            ApprovalDecision.APPROVE,
            expected_revision=2,
            expected_draft_version=2,
            expected_draft_hash="a" * 64,
        )

    first_version = ApprovalRecord(
        "approval-1",
        "tenant-ada",
        "actor-ada",
        "draft-1",
        1,
        "a" * 64,
        ApprovalStatus.PENDING,
        1,
    )
    with pytest.raises(ApprovalTransitionError, match="edited_version_required"):
        first_version.decide(
            ApprovalDecision.EDIT_AND_APPROVE,
            expected_revision=1,
            expected_draft_version=1,
            expected_draft_hash="a" * 64,
        )


def test_draft_hash_binds_citation_provenance() -> None:
    citation = Citation("doc-1", "chunk-1", "CV", "cv.txt", 1, 0, 20)
    claim = DraftClaim("claim-1", "Built APIs.", ClaimStatus.SUPPORTED, (citation,))
    original = CareerDraft.hash_content("Resume", ("Built APIs.",), (claim,))
    changed_citation = Citation("doc-1", "chunk-2", "CV", "cv.txt", 1, 0, 20)
    changed = CareerDraft.hash_content(
        "Resume",
        ("Built APIs.",),
        (
            DraftClaim(
                "claim-1", "Built APIs.", ClaimStatus.SUPPORTED, (changed_citation,)
            ),
        ),
    )
    assert original != changed
    expired = _approval().expire(expected_revision=1)
    assert expired.status is ApprovalStatus.EXPIRED
    assert expired.revision == 2
    with pytest.raises(ApprovalTransitionError, match="feedback_required"):
        _approval().decide(
            ApprovalDecision.REJECT,
            expected_revision=1,
            expected_draft_version=2,
            expected_draft_hash="a" * 64,
        )


def test_langgraph_interrupt_payload_binds_exact_draft_and_resumes() -> None:
    graph = build_approval_graph()
    config = {"configurable": {"thread_id": "tenant-ada:actor-ada:approval-1"}}
    paused = graph.invoke(
        {
            "approval_id": "approval-1",
            "draft_id": "draft-1",
            "draft_version": 2,
            "draft_hash": "a" * 64,
            "status": "pending",
        },
        config=config,
    )
    payload = paused["__interrupt__"][0].value
    assert payload["draft_version"] == 2
    assert payload["draft_hash"] == "a" * 64
    resumed = graph.invoke(Command(resume={"decision": "approve"}), config=config)
    assert resumed["status"] == "decision_received"


def test_privacy_and_bias_policy_patterns_are_deterministic() -> None:
    text = "Contact synthetic@example.invalid or +41 44 555 01 02."
    assert {name for name, pattern in PII_PATTERNS.items() if pattern.search(text)} == {
        "email",
        "phone",
    }
    assert BIAS_TERMS.search("Seeking a young native-born candidate")
