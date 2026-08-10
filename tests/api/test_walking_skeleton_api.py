"""HTTP tests for safe contracts, health, and correlation behavior."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from careerpilot_core import CareerJourneyService, ProfessionalProfile


class FailingJourneyService(CareerJourneyService):
    """Test double for the safe unexpected-error boundary."""

    def __init__(self) -> None:
        pass

    def create_profile(
        self, display_name: str, professional_summary: str
    ) -> ProfessionalProfile:
        del display_name, professional_summary
        raise RuntimeError


def test_health_and_readiness_are_separate() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/health/live").json() == {"status": "ok"}
        assert client.get("/health/ready").json() == {"status": "ready"}


def test_invalid_profile_returns_safe_structured_error() -> None:
    correlation_id = str(uuid.uuid4())
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/profiles",
            headers={"X-Correlation-ID": correlation_id},
            json={"display_name": "A", "professional_summary": "too short"},
        )

    assert response.status_code == 422
    assert response.headers["X-Correlation-ID"] == correlation_id
    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": "Please correct the highlighted fields and try again.",
            "correlation_id": correlation_id,
            "fields": {
                "display_name": ["String should have at least 2 characters"],
                "professional_summary": ["String should have at least 20 characters"],
            },
        }
    }


def test_unknown_profile_returns_safe_not_found() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/analyses",
            json={
                "profile_id": "missing",
                "job_description": (
                    "A synthetic description long enough for validation to pass safely."
                ),
            },
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"
    assert "traceback" not in response.text.casefold()


def test_unexpected_error_is_safe_and_correlated() -> None:
    app = create_app(service_factory=FailingJourneyService)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/v1/profiles",
            json={
                "display_name": "Private Example",
                "professional_summary": (
                    "Private synthetic content that must not appear in the response."
                ),
            },
        )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert (
        response.json()["error"]["correlation_id"]
        == response.headers["X-Correlation-ID"]
    )
    assert "Private Example" not in response.text
