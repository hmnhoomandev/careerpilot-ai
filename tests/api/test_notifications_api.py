"""API tests for local in-app notification preferences and isolation."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from careerpilot_core import IntegrationEvent
from tests.api.helpers import login_headers


def test_notification_api_is_authenticated_preference_aware_and_isolated() -> None:
    app = create_app()
    client = TestClient(app)
    ada = login_headers(client, "ada", "tenant-ada")
    grace = login_headers(client, "grace", "tenant-grace")
    item = IntegrationEvent.create(
        event_id="event-api-1",
        event_type="approval.requested",
        tenant_id="tenant-ada",
        aggregate_id="draft-1",
        sequence=1,
        correlation_id="correlation-1",
        data=(("actor_id", "actor-ada"), ("subject_ref", "draft-1")),
        occurred_at=datetime(2026, 8, 14, tzinfo=UTC),
    )
    app.state.event_consumer.consume(item)

    response = client.get("/api/v1/notifications", headers=ada)
    assert response.status_code == 200
    notification_id = response.json()[0]["notification_id"]
    assert client.get("/api/v1/notifications", headers=grace).json() == []
    assert (
        client.post(
            f"/api/v1/notifications/{notification_id}/read", headers=grace
        ).status_code
        == 404
    )
    assert client.post(
        f"/api/v1/notifications/{notification_id}/read", headers=ada
    ).json()["read_at"]

    disabled = client.put(
        "/api/v1/notification-preferences", json={"enabled_categories": []}, headers=ada
    )
    assert disabled.status_code == 200
    assert disabled.json() == {"enabled_categories": []}
