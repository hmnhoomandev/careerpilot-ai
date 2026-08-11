"""Authentication helpers for local-only API tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def login_headers(
    client: TestClient,
    local_user_id: str = "ada",
    tenant_id: str | None = None,
) -> dict[str, str]:
    response = client.post(
        "/api/v1/dev/sessions", json={"local_user_id": local_user_id}
    )
    assert response.status_code == 200
    session = response.json()
    selected_tenant = tenant_id or session["tenants"][0]["tenant_id"]
    return {
        "Authorization": f"Bearer {session['access_token']}",
        "X-CareerPilot-Tenant-ID": selected_tenant,
    }
