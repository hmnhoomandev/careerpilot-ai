"""Authenticated, tenant-scoped API tests for the local platform dashboard."""

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from tests.api.helpers import login_headers


def test_owner_sees_content_free_local_metrics_and_zero_budget() -> None:
    app = create_app()
    client = TestClient(app)
    headers = login_headers(client, "ada", "tenant-ada")
    client.get("/api/v1/me", headers=headers)

    response = client.get("/api/v1/platform/metrics", headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert result["schema_version"] == "careerpilot.metrics.v1"
    assert result["event_count"] >= 1
    assert result["budget_limit_chf"] == 0
    assert result["budget_remaining_chf"] == 0
    assert result["export_status"] == "disabled_local_only"
    assert result["content_capture"] == "NO_CONTENT"
    assert "career content" not in response.text.casefold()


def test_member_cannot_read_platform_metrics() -> None:
    client = TestClient(create_app())
    headers = login_headers(client, "sam", "tenant-ada")
    response = client.get("/api/v1/platform/metrics", headers=headers)
    assert response.status_code == 403


def test_untrusted_path_is_hashed_before_telemetry() -> None:
    app = create_app()
    client = TestClient(app, raise_server_exceptions=False)
    headers = login_headers(client, "ada", "tenant-ada")
    assert (
        client.get("/api/v1/unknown/%3Cprivate%3E", headers=headers).status_code == 404
    )
    events = app.state.telemetry.events_for("tenant-ada")
    assert events[-1].kind == "http"
    assert "private" not in events[-1].operation
