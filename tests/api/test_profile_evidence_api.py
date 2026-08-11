"""Authenticated API tests for Phase 4 profile and evidence behavior."""

from fastapi.testclient import TestClient

from careerpilot_api.main import create_app
from tests.api.helpers import login_headers


def test_profile_edit_evidence_and_stale_conflict() -> None:
    client = TestClient(create_app())
    headers = login_headers(client, "ada", "tenant-ada")
    created = client.post(
        "/api/v1/profiles",
        headers=headers,
        json={
            "display_name": "Ada Example",
            "professional_summary": "A fully synthetic professional summary.",
        },
    ).json()
    updated = client.patch(
        f"/api/v1/profiles/{created['profile_id']}",
        headers=headers,
        json={
            "display_name": "Ada Updated",
            "professional_summary": "A fully synthetic updated professional summary.",
            "skills": ["Python", "PostgreSQL"],
            "experiences": [
                {
                    "title": "Synthetic Engineer",
                    "organization": "Example Organization",
                    "start_date": "2024-01-01",
                    "end_date": None,
                    "description": "Built synthetic systems for a test fixture.",
                }
            ],
            "education": [
                {
                    "institution": "Example University",
                    "qualification": "Synthetic Degree",
                    "start_date": "2020-01-01",
                    "end_date": "2023-12-31",
                }
            ],
            "expected_version": 1,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert updated.json()["experiences"][0]["title"] == "Synthetic Engineer"
    assert updated.json()["education"][0]["institution"] == "Example University"
    stale = client.patch(
        f"/api/v1/profiles/{created['profile_id']}",
        headers=headers,
        json={
            "display_name": "Stale Update",
            "professional_summary": "A stale synthetic professional summary update.",
            "skills": [],
            "experiences": [],
            "education": [],
            "expected_version": 1,
        },
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "profile_version_conflict"
    evidence = client.post(
        "/api/v1/evidence",
        headers=headers,
        json={
            "profile_id": created["profile_id"],
            "title": "Synthetic certificate",
            "filename": "../certificate.pdf",
            "media_type": "application/pdf",
            "size_bytes": 1024,
        },
    )
    assert evidence.status_code == 201
    assert evidence.json()["state"] == "quarantined"
    assert evidence.json()["filename"] == "certificate.pdf"


def test_unsupported_evidence_and_foreign_profile_are_safe() -> None:
    client = TestClient(create_app())
    ada_headers = login_headers(client, "ada", "tenant-ada")
    grace_headers = login_headers(client, "grace", "tenant-grace")
    profile_id = client.post(
        "/api/v1/profiles",
        headers=ada_headers,
        json={
            "display_name": "Ada Example",
            "professional_summary": "A fully synthetic professional summary.",
        },
    ).json()["profile_id"]
    unsupported = client.post(
        "/api/v1/evidence",
        headers=ada_headers,
        json={
            "profile_id": profile_id,
            "title": "Executable",
            "filename": "payload.exe",
            "media_type": "application/x-msdownload",
            "size_bytes": 100,
        },
    )
    assert unsupported.status_code == 422
    assert unsupported.json()["error"]["code"] == "evidence_not_accepted"
    foreign = client.get(f"/api/v1/profiles/{profile_id}", headers=grace_headers)
    assert foreign.status_code == 404
