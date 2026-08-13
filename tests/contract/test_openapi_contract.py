"""Contract checks for versioned paths and stable error schemas."""

from __future__ import annotations

import pytest

from careerpilot_api import create_app


@pytest.mark.contract
def test_openapi_contains_phase6_paths_and_error_contract() -> None:
    schema = create_app().openapi()

    assert schema["info"]["version"] == "0.8.0"
    assert set(schema["paths"]) == {
        "/api/v1/analyses",
        "/api/v1/audit-events",
        "/api/v1/dev/sessions",
        "/api/v1/dev/users",
        "/api/v1/me",
        "/api/v1/memberships/{actor_id}",
        "/api/v1/profiles",
        "/api/v1/profiles/{profile_id}",
        "/api/v1/evidence",
        "/api/v1/documents",
        "/api/v1/documents/{document_id}/deletion",
        "/api/v1/documents/{document_id}/reindex",
        "/api/v1/retrieval/search",
        "/api/v1/tools",
        "/api/v1/tools/{tool_name}/invoke",
        "/api/v1/agent-runs",
        "/api/v1/agent-runs/{run_id}",
        "/api/v1/agent-runs/{run_id}/cancel",
        "/api/v1/drafts",
        "/api/v1/drafts/{draft_id}/versions",
        "/api/v1/approvals/{approval_id}/decisions",
        "/api/v1/profiles/{profile_id}/evidence",
        "/health/live",
        "/health/ready",
    }
    error_schema = schema["components"]["schemas"]["ErrorDetail"]
    assert set(error_schema["required"]) == {
        "code",
        "correlation_id",
        "message",
    }
    assert "500" in schema["paths"]["/api/v1/profiles"]["post"]["responses"]
