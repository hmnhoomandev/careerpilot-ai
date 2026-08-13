"""API evidence for the tenant-safe Phase 7 LangGraph journey."""

from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers


def _setup() -> tuple[TestClient, dict[str, str], str]:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Synthetic Graph Candidate",
            "professional_summary": "Python PostgreSQL accessibility engineer.",
        },
    )
    assert profile.status_code == 201
    profile_id = profile.json()["profile_id"]
    upload = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"profile_id": profile_id, "title": "Synthetic graph evidence"},
        files={
            "file": (
                "graph-evidence.txt",
                b"Built accessible Python services backed by PostgreSQL.",
                "text/plain",
            )
        },
    )
    assert upload.status_code == 201
    return client, headers, profile_id


def test_graph_returns_ordered_progress_grounding_and_uncertainty() -> None:
    client, headers, profile_id = _setup()
    response = client.post(
        "/api/v1/agent-runs",
        headers={**headers, "X-Correlation-ID": "00000000-0000-4000-8000-000000000007"},
        json={
            "profile_id": profile_id,
            "job_description": (
                "We need a Python and PostgreSQL engineer to build accessible "
                "services and maintain React systems with strong Security practices."
            ),
        },
    )
    assert response.status_code == 201, response.text
    result = response.json()
    assert result["status"] == "completed"
    assert result["provider"] == "fake-deterministic-v1"
    assert [event["node"] for event in result["events"]] == [
        "intake",
        "job_analysis",
        "retrieval",
        "match",
        "gap",
        "evidence",
        "explanation",
    ]
    assert result["requirements"]["untrusted_source"] is True
    assert result["passages"][0]["citation"]["chunk_id"]
    assert "React" in result["gaps"]["missing"]
    assert "candidate facts" in result["explanation"]

    fetched = client.get(f"/api/v1/agent-runs/{result['run_id']}", headers=headers)
    assert fetched.status_code == 200
    grace = login_headers(client, "grace", "tenant-grace")
    assert (
        client.get(f"/api/v1/agent-runs/{result['run_id']}", headers=grace).status_code
        == 404
    )


def test_graph_input_is_strict_and_short_ambiguous_input_rejects() -> None:
    client, headers, profile_id = _setup()
    invalid = client.post(
        "/api/v1/agent-runs",
        headers=headers,
        json={"profile_id": profile_id, "job_description": "short", "extra": True},
    )
    assert invalid.status_code == 422
