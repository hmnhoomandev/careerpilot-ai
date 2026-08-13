"""API evidence for cited drafts, version binding, policy, and approvals."""

from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers


def _setup() -> tuple[TestClient, dict[str, str], str]:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    profile = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Synthetic Draft Candidate",
            "professional_summary": "Synthetic evidence-controlled profile.",
        },
    )
    profile_id = profile.json()["profile_id"]
    upload = client.post(
        "/api/v1/documents",
        headers=headers,
        data={"profile_id": profile_id, "title": "Verified synthetic achievement"},
        files={
            "file": (
                "achievement.txt",
                b"Built accessible Python services using PostgreSQL.",
                "text/plain",
            )
        },
    )
    assert upload.status_code == 201
    return client, headers, profile_id


def test_resume_and_letter_are_cited_and_exact_version_approval_is_terminal() -> None:
    client, headers, profile_id = _setup()
    for kind in ("resume", "cover_letter"):
        created = client.post(
            "/api/v1/drafts",
            headers=headers,
            json={
                "profile_id": profile_id,
                "kind": kind,
                "job_description": (
                    "We need an accessible Python engineer using PostgreSQL for "
                    "reliable synthetic services and careful human review."
                ),
            },
        )
        assert created.status_code == 201, created.text
        body = created.json()
        assert body["claims"]
        assert all(claim["status"] == "supported" for claim in body["claims"])
        assert all(claim["citations"] for claim in body["claims"])
        assert {message["schema"] for message in body["messages"]} == {
            "careerpilot.a2ui.v1"
        }

    decision = client.post(
        f"/api/v1/approvals/{body['approval_id']}/decisions",
        headers=headers,
        json={
            "decision": "approve",
            "expected_revision": body["approval_revision"],
            "expected_draft_version": body["version"],
            "expected_draft_hash": body["content_hash"],
        },
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "approved"
    repeated = client.post(
        f"/api/v1/approvals/{body['approval_id']}/decisions",
        headers=headers,
        json={
            "decision": "approve",
            "expected_revision": body["approval_revision"],
            "expected_draft_version": body["version"],
            "expected_draft_hash": body["content_hash"],
        },
    )
    assert repeated.status_code == 422


def test_stale_approval_unsupported_edit_and_foreign_decision_fail_closed() -> None:
    client, headers, profile_id = _setup()
    created = client.post(
        "/api/v1/drafts",
        headers=headers,
        json={
            "profile_id": profile_id,
            "kind": "resume",
            "job_description": (
                "We need a Python PostgreSQL engineer for accessible synthetic "
                "services with documented and reviewable evidence."
            ),
        },
    ).json()
    invented = client.post(
        f"/api/v1/drafts/{created['draft_id']}/versions",
        headers=headers,
        json={
            "expected_version": 1,
            "sections": ["Led 40 engineers from 2012 to 2020."],
        },
    )
    assert invented.status_code == 422
    stale = client.post(
        f"/api/v1/approvals/{created['approval_id']}/decisions",
        headers=headers,
        json={
            "decision": "approve",
            "expected_revision": 1,
            "expected_draft_version": 2,
            "expected_draft_hash": created["content_hash"],
        },
    )
    assert stale.status_code == 409
    grace = login_headers(client, "grace", "tenant-grace")
    foreign = client.post(
        f"/api/v1/approvals/{created['approval_id']}/decisions",
        headers=grace,
        json={
            "decision": "cancel",
            "expected_revision": 1,
            "expected_draft_version": 1,
            "expected_draft_hash": created["content_hash"],
        },
    )
    assert foreign.status_code == 404
