"""API evidence for all nine typed tools and transport policy controls."""

from fastapi.testclient import TestClient
from httpx2 import Response

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers


def _setup() -> tuple[TestClient, dict[str, str], str]:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Synthetic Tool Candidate",
            "professional_summary": (
                "Python engineer building accessible PostgreSQL services."
            ),
        },
    )
    assert profile.status_code == 201
    profile_id = str(profile.json()["profile_id"])
    uploaded = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"profile_id": profile_id, "title": "Synthetic evidence"},
        files={
            "file": (
                "evidence.txt",
                b"Built an accessible Python service with PostgreSQL.",
                "text/plain",
            )
        },
    )
    assert uploaded.status_code == 201
    return client, headers, profile_id


def _invoke(
    client: TestClient,
    headers: dict[str, str],
    name: str,
    arguments: dict[str, object],
    idempotency_key: str | None = None,
) -> Response:
    return client.post(
        f"/api/v1/tools/{name}/invoke",
        headers=headers,
        json={"arguments": arguments, "idempotency_key": idempotency_key},
    )


def test_discovery_and_all_nine_capabilities() -> None:
    client, headers, profile_id = _setup()
    discovery = client.get("/api/v1/tools", headers=headers)
    assert discovery.status_code == 200
    tools = {item["name"]: item for item in discovery.json()}
    assert set(tools) == {
        "approval.request",
        "audit.lookup",
        "candidate.match",
        "cost.estimate",
        "evidence.retrieve",
        "evidence.verify",
        "job.ingest",
        "profile.lookup",
        "skill.taxonomy",
    }
    assert tools["approval.request"]["idempotency_required"] is True
    assert tools["profile.lookup"]["input_schema"]["additionalProperties"] is False
    assert {name for name, item in tools.items() if item["mcp_exposed"]} == {
        "cost.estimate",
        "evidence.retrieve",
        "profile.lookup",
        "skill.taxonomy",
    }

    job_text = (
        "We need a Python engineer to build accessible PostgreSQL services for "
        "synthetic users."
    )
    cases: dict[str, dict[str, object]] = {
        "profile.lookup": {"profile_id": profile_id},
        "evidence.retrieve": {"query": "accessible Python PostgreSQL"},
        "job.ingest": {"profile_id": profile_id, "job_description": job_text},
        "skill.taxonomy": {"query": "Python"},
        "candidate.match": {"profile_id": profile_id, "job_description": job_text},
        "evidence.verify": {"claim": "Built an accessible Python service"},
        "approval.request": {
            "action": "external_share",
            "resource_id": profile_id,
            "reason": "User review is required before sharing.",
        },
        "audit.lookup": {"limit": 10},
        "cost.estimate": {"workflow": "retrieval", "units": 4},
    }
    for name, arguments in cases.items():
        key = f"idempotency-{name}" if tools[name]["idempotency_required"] else None
        response = _invoke(client, headers, name, arguments, key)
        assert response.status_code == 200, (name, response.text)
        assert response.json()["tool_name"] == name
    assert (
        _invoke(client, headers, "cost.estimate", cases["cost.estimate"]).json()[
            "output"
        ]["estimated_chf"]
        == 0
    )


def test_invalid_unauthorized_idempotency_and_rate_limit() -> None:
    client, headers, profile_id = _setup()
    invalid = _invoke(
        client,
        headers,
        "profile.lookup",
        {"profile_id": profile_id, "unexpected": True},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_input"

    sam_headers = login_headers(client, "sam", "tenant-ada")
    denied = _invoke(client, sam_headers, "audit.lookup", {"limit": 5})
    assert denied.status_code == 403

    grace_headers = login_headers(client, "grace", "tenant-grace")
    foreign = _invoke(
        client, grace_headers, "profile.lookup", {"profile_id": profile_id}
    )
    assert foreign.status_code == 404

    unknown = _invoke(client, headers, "unknown.tool", {})
    assert unknown.status_code == 404

    arguments: dict[str, object] = {
        "action": "external_share",
        "resource_id": profile_id,
        "reason": "Explicit review is required before external sharing.",
    }
    missing_key = _invoke(client, headers, "approval.request", arguments)
    assert missing_key.status_code == 422
    first = _invoke(client, headers, "approval.request", arguments, "approval-key-001")
    replay = _invoke(client, headers, "approval.request", arguments, "approval-key-001")
    assert first.status_code == replay.status_code == 200
    assert replay.json()["idempotent_replay"] is True
    assert replay.json()["output"] == first.json()["output"]
    conflict = _invoke(
        client,
        headers,
        "approval.request",
        {**arguments, "resource_id": "different-resource"},
        "approval-key-001",
    )
    assert conflict.status_code == 409
    assert (
        _invoke(
            client,
            headers,
            "approval.request",
            arguments,
            "approval-key-002",
        ).status_code
        == 200
    )
    limited = _invoke(
        client, headers, "approval.request", arguments, "approval-key-003"
    )
    assert limited.status_code == 429


def test_tool_audit_records_decisions_and_correlation_without_arguments() -> None:
    client, headers, profile_id = _setup()
    correlation_id = "00000000-0000-4000-8000-000000000006"
    headers = {**headers, "X-Correlation-ID": correlation_id}
    response = _invoke(
        client,
        headers,
        "profile.lookup",
        {"profile_id": profile_id},
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == correlation_id

    audit = client.get("/api/v1/audit-events", headers=headers)
    assert audit.status_code == 200
    tool_events = [
        event for event in audit.json() if event["action"] == "tool.profile.lookup"
    ]
    assert tool_events
    assert tool_events[-1]["outcome"] == "allowed"
    assert tool_events[-1]["reason"] == "completed"
    assert tool_events[-1]["correlation_id"] == correlation_id
    serialized = str(tool_events[-1])
    assert profile_id not in serialized
