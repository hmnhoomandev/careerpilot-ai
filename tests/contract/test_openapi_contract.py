"""Contract checks for versioned paths and stable error schemas."""

from __future__ import annotations

import pytest

from careerpilot_api import create_app


@pytest.mark.contract
def test_openapi_contains_phase2_paths_and_error_contract() -> None:
    schema = create_app().openapi()

    assert schema["info"]["version"] == "0.2.0"
    assert set(schema["paths"]) == {
        "/api/v1/analyses",
        "/api/v1/profiles",
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
