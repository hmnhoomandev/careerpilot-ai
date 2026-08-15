"""DAST-style security-header and privacy authorization API tests."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from careerpilot_api import create_app
from tests.api.helpers import login_headers

if TYPE_CHECKING:
    import pytest


def test_all_responses_have_security_headers_and_no_store() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live")
    assert response.headers["Cache-Control"] == "no-store, max-age=0"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_owner_can_inventory_withdraw_consent_and_cancel_deletion() -> None:
    with TestClient(create_app()) as client:
        headers = login_headers(client)
        inventory = client.get("/api/v1/privacy/inventory", headers=headers)
        consent = client.post(
            "/api/v1/privacy/consents",
            headers=headers,
            json={"purpose": "external_model_processing", "granted": False},
        )
        deletion = client.post(
            "/api/v1/privacy/requests",
            headers=headers,
            json={
                "right": "deletion",
                "step_up_verified": True,
                "approval_reference": "approval-delete-ada",
            },
        )
        cancelled = client.post(
            f"/api/v1/privacy/requests/{deletion.json()['request_id']}/cancel-deletion",
            headers=headers,
            json={"confirmed": True},
        )
    assert inventory.status_code == 200
    assert inventory.json()["legal_review_required"] is True
    assert consent.json()["granted"] is False
    assert deletion.json()["status"] == "recoverable_deletion"
    assert deletion.json()["recovery_window_days"] == 30
    assert cancelled.json()["status"] == "cancelled"


def test_member_and_cross_tenant_request_are_denied_without_enumeration() -> None:
    app = create_app()
    with TestClient(app) as client:
        member = client.get(
            "/api/v1/privacy/inventory", headers=login_headers(client, "sam")
        )
        ada_headers = login_headers(client, "ada")
        deletion = client.post(
            "/api/v1/privacy/requests",
            headers=ada_headers,
            json={
                "right": "deletion",
                "step_up_verified": True,
                "approval_reference": "approval-delete-ada",
            },
        )
        grace_headers = login_headers(client, "grace")
        foreign = client.post(
            f"/api/v1/privacy/requests/{deletion.json()['request_id']}/cancel-deletion",
            headers=grace_headers,
            json={"confirmed": True},
        )
    assert member.status_code == 403
    assert foreign.status_code == 409
    assert foreign.json()["error"]["code"] == "request_unavailable"


def test_export_requires_step_up_and_approval() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/privacy/requests",
            headers=login_headers(client),
            json={
                "right": "export",
                "step_up_verified": False,
                "approval_reference": "approval-export-ada",
            },
        )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "step_up_required"


def test_portable_export_is_profile_scoped_and_minimized() -> None:
    with TestClient(create_app()) as client:
        headers = login_headers(client)
        profile = client.post(
            "/api/v1/profiles",
            headers=headers,
            json={
                "display_name": "Ada Example",
                "professional_summary": (
                    "Synthetic profile for portable export verification."
                ),
            },
        ).json()
        response = client.post(
            "/api/v1/privacy/exports",
            headers=headers,
            json={
                "profile_id": profile["profile_id"],
                "step_up_verified": True,
                "approval_reference": "approval-export-ada",
            },
        )
    assert response.status_code == 200
    assert response.json()["schema_version"] == "careerpilot.portable-export.v1"
    assert response.json()["profile"]["display_name"] == "Ada Example"
    assert "raw_document_bytes" in response.json()["excluded_categories"]
    assert response.headers["Cache-Control"] == "no-store, max-age=0"


def test_request_logging_hashes_private_path(caplog: pytest.LogCaptureFixture) -> None:
    private_marker = "sensitive-profile-reference"
    caplog.set_level(logging.INFO, logger="careerpilot.api")
    with TestClient(create_app()) as client:
        response = client.get(
            f"/api/v1/private/{private_marker}", headers=login_headers(client)
        )
    assert response.status_code == 404
    serialized = json.dumps([record.__dict__ for record in caplog.records], default=str)
    assert private_marker not in serialized
    assert "path_hash" in serialized
