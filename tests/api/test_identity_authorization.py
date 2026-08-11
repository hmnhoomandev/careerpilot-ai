"""Authentication, tenant isolation, IDOR, role, and audit API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from tests.api.helpers import login_headers

PROFILE_BODY = {
    "display_name": "Ada Example",
    "professional_summary": "Synthetic professional summary for authorization tests.",
}
JOB_BODY = "A synthetic job description that is sufficiently long for validation."


def test_protected_endpoint_denies_missing_authentication_before_body_validation() -> (
    None
):
    with TestClient(create_app()) as client:
        response = client.post("/api/v1/profiles", json={})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_unknown_local_user_has_safe_authentication_error() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/dev/sessions", json={"local_user_id": "unknown"}
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_required"


def test_forged_tenant_header_is_denied() -> None:
    with TestClient(create_app()) as client:
        headers = login_headers(client, "ada", tenant_id="tenant-grace")
        response = client.get("/api/v1/me", headers=headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "access_denied"


def test_cross_tenant_profile_identifier_is_non_enumerating() -> None:
    app = create_app()
    with TestClient(app) as client:
        ada_headers = login_headers(client, "ada")
        profile = client.post(
            "/api/v1/profiles", headers=ada_headers, json=PROFILE_BODY
        ).json()
        grace_headers = login_headers(client, "grace")
        response = client.post(
            "/api/v1/analyses",
            headers=grace_headers,
            json={"profile_id": profile["profile_id"], "job_description": JOB_BODY},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"
    denials = [
        event
        for event in app.state.audit_log.list_for_tenant("tenant-grace")
        if event.outcome == "denied"
    ]
    assert denials[-1].reason == "profile_unavailable"


def test_same_tenant_member_cannot_access_another_actors_profile() -> None:
    with TestClient(create_app()) as client:
        sam_headers = login_headers(client, "sam")
        profile = client.post(
            "/api/v1/profiles",
            headers=sam_headers,
            json={
                "display_name": "Sam Example",
                "professional_summary": "Synthetic professional summary owned by Sam.",
            },
        ).json()
        ada_headers = login_headers(client, "ada")
        response = client.post(
            "/api/v1/analyses",
            headers=ada_headers,
            json={"profile_id": profile["profile_id"], "job_description": JOB_BODY},
        )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "access_denied"


def test_role_change_controls_audit_view_and_records_success_and_denial() -> None:
    app = create_app()
    with TestClient(app) as client:
        sam_headers = login_headers(client, "sam")
        denied = client.get("/api/v1/audit-events", headers=sam_headers)
        assert denied.status_code == 403

        ada_headers = login_headers(client, "ada")
        changed = client.patch(
            "/api/v1/memberships/actor-sam",
            headers=ada_headers,
            json={"role": "owner"},
        )
        assert changed.status_code == 200

        promoted_headers = login_headers(client, "sam")
        allowed = client.get("/api/v1/audit-events", headers=promoted_headers)

    assert allowed.status_code == 200
    outcomes = {(event["action"], event["outcome"]) for event in allowed.json()}
    assert ("audit.view", "denied") in outcomes
    assert ("membership.role_changed", "allowed") in outcomes
    assert ("audit.view", "allowed") in outcomes
    assert app.state.audit_log.verify_chain()


def test_last_owner_cannot_demote_themselves() -> None:
    app = create_app()
    with TestClient(app) as client:
        ada_headers = login_headers(client, "ada")
        response = client.patch(
            "/api/v1/memberships/actor-ada",
            headers=ada_headers,
            json={"role": "member"},
        )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "role_change_conflict"
    assert app.state.audit_log.list_for_tenant("tenant-ada")[-1].reason == (
        "last_owner_required"
    )
