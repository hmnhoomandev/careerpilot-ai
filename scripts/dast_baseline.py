"""Run a zero-network DAST baseline against the in-process FastAPI surface."""

from __future__ import annotations

from fastapi.testclient import TestClient

from careerpilot_api import create_app

REQUIRED_HEADERS = {
    "cache-control": "no-store",
    "content-security-policy": "default-src 'none'",
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
}
AUTHENTICATION_REQUIRED = 401
SAFE_PATH_FAILURES = frozenset({400, 404})


def main() -> int:
    """Probe public/protected/error responses without binding a network socket."""
    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        responses = (
            client.get("/health/live"),
            client.get("/api/v1/me"),
            client.get("/%2e%2e/%2e%2e/private"),
        )
    errors = []
    for response in responses:
        for header, expected in REQUIRED_HEADERS.items():
            if expected not in response.headers.get(header, ""):
                errors.append(f"{response.status_code}: missing {header}")
        if "server" in response.headers:
            errors.append(f"{response.status_code}: server fingerprint exposed")
    if (
        responses[1].status_code != AUTHENTICATION_REQUIRED
        or responses[2].status_code not in SAFE_PATH_FAILURES
    ):
        errors.append("safe authentication/path behavior failed")
    if errors:
        for error in errors:
            print(error)  # noqa: T201
        return 1
    print("Local DAST baseline passed: 3 probes, required headers present.")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
