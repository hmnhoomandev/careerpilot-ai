"""Versioned corpus proving unsupported material draft claims remain blocked."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers

CORPUS = json.loads(
    (
        Path(__file__).parents[1] / "fixtures" / "unsupported-draft-claims-v1.json"
    ).read_text()
)


@pytest.mark.e2e
@pytest.mark.parametrize("invented", CORPUS["blocked_edits"])
def test_invented_material_claim_is_blocked(invented: str) -> None:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile_id = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Synthetic Truth Candidate",
            "professional_summary": "Minimal profile without invented claims.",
        },
    ).json()["profile_id"]
    created = client.post(
        "/api/v1/drafts",
        headers=headers,
        json={
            "profile_id": profile_id,
            "kind": "resume",
            "job_description": (
                "A synthetic role needs careful evidence review and truthful career "
                "documents without unsupported qualifications or metrics."
            ),
        },
    ).json()
    response = client.post(
        f"/api/v1/drafts/{created['draft_id']}/versions",
        headers=headers,
        json={"expected_version": 1, "sections": [invented]},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "draft_policy_rejected"
