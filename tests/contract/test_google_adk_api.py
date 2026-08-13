"""HTTP contract for the independently testable ADK specialist."""

from careerpilot_google_adk.api import create_app
from careerpilot_google_adk.provider import FakeResearchProvider
from careerpilot_google_adk.service import ResearchService
from fastapi.testclient import TestClient

PAYLOAD = {
    "tenant_id": "tenant-ada",
    "actor_id": "actor-ada",
    "session_id": "session-1",
    "question": "What matters for this role?",
    "sources": [
        {
            "source_id": "job-ad",
            "title": "Synthetic job ad",
            "content": "The role requires Python and accessibility experience.",
        }
    ],
}


def test_service_identity_and_structured_response_contract() -> None:
    client = TestClient(create_app(ResearchService(FakeResearchProvider())))
    assert client.post("/v1/research", json=PAYLOAD).status_code == 422
    denied = client.post(
        "/v1/research",
        json=PAYLOAD,
        headers={"X-CareerPilot-Service": "unknown"},
    )
    assert denied.status_code == 403
    response = client.post(
        "/v1/research",
        json=PAYLOAD,
        headers={"X-CareerPilot-Service": "careerpilot-main-api"},
    )
    assert response.status_code == 200
    assert response.json()["findings"][0]["source_ids"] == ["job-ad"]


def test_openapi_is_narrow_and_versioned() -> None:
    schema = create_app().openapi()
    assert schema["info"]["version"] == "0.9.0"
    assert set(schema["paths"]) == {"/v1/research"}
