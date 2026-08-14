"""Authenticated Phase 11 A2A API tests."""

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from tests.api.helpers import login_headers


def test_discovery_delegation_status_and_cancellation() -> None:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")

    discovered = client.get("/api/v1/a2a/agents", headers=headers)
    assert discovered.status_code == 200
    assert len(discovered.json()) == 3

    delegated = client.post(
        "/api/v1/a2a/tasks",
        headers=headers,
        json={
            "agent_id": "google-adk-research",
            "skill_id": "company-research.v1",
            "task_id": "task-api-complete",
            "payload": {"fixture_id": "company-1"},
        },
    )
    assert delegated.status_code == 200
    assert delegated.json()["status"]["state"] == "completed"
    fetched = client.get("/api/v1/a2a/tasks/task-api-complete", headers=headers)
    assert fetched.json()["metadata"]["result"]["runtime"] == "google-adk"

    submitted = client.post(
        "/api/v1/a2a/tasks",
        headers=headers,
        json={
            "agent_id": "openai-interview",
            "skill_id": "interview-simulation.v1",
            "task_id": "task-api-cancel",
            "payload": {},
            "defer_execution": True,
        },
    )
    assert submitted.json()["status"]["state"] == "submitted"
    cancelled = client.post("/api/v1/a2a/tasks/task-api-cancel/cancel", headers=headers)
    assert cancelled.json()["status"]["state"] == "canceled"


def test_a2a_requires_auth_and_foreign_tasks_are_not_enumerable() -> None:
    client = TestClient(create_app())
    assert client.get("/api/v1/a2a/agents").status_code == 401
    ada = login_headers(client, "ada", "tenant-ada")
    grace = login_headers(client, "grace", "tenant-grace")
    created = client.post(
        "/api/v1/a2a/tasks",
        headers=ada,
        json={
            "agent_id": "langgraph-core",
            "skill_id": "job-analysis.v1",
            "task_id": "task-tenant-private",
            "payload": {},
            "defer_execution": True,
        },
    )
    assert created.status_code == 200
    foreign = client.get("/api/v1/a2a/tasks/task-tenant-private", headers=grace)
    assert foreign.status_code == 404
    assert foreign.json()["error"]["code"] == "a2a_not_found"
