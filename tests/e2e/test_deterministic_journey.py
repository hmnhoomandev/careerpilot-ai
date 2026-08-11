"""End-to-end HTTP test across contracts, service, and temporary repository."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from careerpilot_api import create_app
from tests.api.helpers import login_headers


@pytest.mark.e2e
def test_profile_to_visible_analysis_contract() -> None:
    with TestClient(create_app()) as client:
        headers = login_headers(client)
        profile_response = client.post(
            "/api/v1/profiles",
            headers=headers,
            json={
                "display_name": "Ada Example",
                "professional_summary": (
                    "Python engineer building accessible and reliable data platforms."
                ),
            },
        )
        profile = profile_response.json()
        analysis_response = client.post(
            "/api/v1/analyses",
            headers=headers,
            json={
                "profile_id": profile["profile_id"],
                "job_description": (
                    "We seek a Python engineer to build accessible services for our "
                    "reliable data platform and support a collaborative team."
                ),
            },
        )
        analysis = analysis_response.json()

    assert profile_response.status_code == 201
    assert analysis_response.status_code == 201
    assert analysis["shared_terms"] == [
        "accessible",
        "data",
        "engineer",
        "python",
        "reliable",
    ]
    assert analysis["correlation_id"] == analysis_response.headers["X-Correlation-ID"]
    assert "not an AI assessment" in analysis["disclaimer"]


@pytest.mark.e2e
def test_restart_makes_temporary_profile_unavailable() -> None:
    with TestClient(create_app()) as first_process:
        first_headers = login_headers(first_process)
        profile = first_process.post(
            "/api/v1/profiles",
            headers=first_headers,
            json={
                "display_name": "Ada Example",
                "professional_summary": (
                    "Synthetic profile summary for restart testing."
                ),
            },
        ).json()

    with TestClient(create_app()) as restarted_process:
        restarted_headers = login_headers(restarted_process)
        response = restarted_process.post(
            "/api/v1/analyses",
            headers=restarted_headers,
            json={
                "profile_id": profile["profile_id"],
                "job_description": (
                    "This synthetic job description is long enough to pass validation."
                ),
            },
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"
