"""Versioned hallucination, uncertainty, and injection evaluation for Phase 7."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers

FIXTURE = json.loads(
    (
        Path(__file__).parents[1] / "fixtures" / "agent-grounding-evaluation-v1.json"
    ).read_text()
)


@pytest.mark.e2e
@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_unsupported_requirements_stay_uncertain_without_evidence(
    case: dict[str, str],
) -> None:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Synthetic Grounding Candidate",
            "professional_summary": "A deliberately minimal synthetic profile.",
        },
    )
    assert profile.status_code == 201
    response = client.post(
        "/api/v1/agent-runs",
        headers=headers,
        json={
            "profile_id": profile.json()["profile_id"],
            "job_description": case["job_description"],
        },
    )
    assert response.status_code == 201
    result = response.json()
    expected = case["expected_skill"]
    assert expected in result["requirements"]["required_skills"]
    assert expected in result["gaps"]["uncertain"]
    verification = next(
        item for item in result["verified"] if item["claim"] == expected
    )
    assert verification["status"] == "unsupported"
    assert verification["citations"] == []
    assert "certified" not in result["explanation"].casefold()
