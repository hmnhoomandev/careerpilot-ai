"""Narrow HTTP contract for the OpenAI Agents laboratory."""

from careerpilot_openai_agents.api import create_app
from fastapi.testclient import TestClient

PAYLOAD = {
    "tenant_id": "tenant-ada",
    "actor_id": "actor-ada",
    "session_id": "session-1",
    "role_title": "Platform Engineer",
    "candidate_answer": "I used synthetic test evidence to improve an API.",
    "mode": "direct_handoff",
}


def test_internal_identity_and_result_contract() -> None:
    client = TestClient(create_app())
    assert client.post("/v1/interviews", json=PAYLOAD).status_code == 422
    denied = client.post(
        "/v1/interviews",
        json=PAYLOAD,
        headers={"X-CareerPilot-Service": "unknown"},
    )
    assert denied.status_code == 403
    response = client.post(
        "/v1/interviews",
        json=PAYLOAD,
        headers={"X-CareerPilot-Service": "careerpilot-main-api"},
    )
    assert response.status_code == 200
    assert response.json()["final_owner"] == "Interview Specialist"


def test_openapi_surface_is_versioned_and_narrow() -> None:
    schema = create_app().openapi()
    assert schema["info"]["version"] == "0.10.0"
    assert set(schema["paths"]) == {
        "/v1/interviews",
        "/v1/feedback-approvals",
        "/v1/feedback-approvals/{approval_id}/decision",
    }


def test_approval_pauses_and_resumes_exact_action() -> None:
    client = TestClient(create_app())
    headers = {"X-CareerPilot-Service": "careerpilot-main-api"}
    paused = client.post("/v1/feedback-approvals", json=PAYLOAD, headers=headers)
    assert paused.status_code == 200
    state = paused.json()
    assert state["status"] == "pending"
    resumed = client.post(
        f"/v1/feedback-approvals/{state['approval_id']}/decision",
        json={
            "approve": True,
            "expected_revision": 1,
            "expected_action_hash": state["action_hash"],
        },
        headers=headers,
    )
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "approved"
    stale = client.post(
        f"/v1/feedback-approvals/{state['approval_id']}/decision",
        json={
            "approve": True,
            "expected_revision": 1,
            "expected_action_hash": state["action_hash"],
        },
        headers=headers,
    )
    assert stale.status_code == 422
