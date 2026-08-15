"""Policy tests for deployable artifacts that must fail closed."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.generate_sbom import build_sbom

ROOT = Path(__file__).parents[2]


def test_compose_services_are_bounded_and_fake_first() -> None:
    compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    assert {
        "postgres",
        "api",
        "web",
        "google-adk",
        "openai-agents",
        "temporal",
        "temporal-ui",
        "temporal-worker",
    } <= set(compose["services"])
    for name in ("api", "web", "google-adk", "openai-agents", "temporal-worker"):
        service = compose["services"][name]
        assert service["read_only"] is True
        assert "ALL" in service["cap_drop"]
        assert "no-new-privileges:true" in service["security_opt"]
    assert (
        compose["services"]["google-adk"]["environment"]["CAREERPILOT_ADK_PROVIDER"]
        == "fake"
    )
    assert (
        compose["services"]["openai-agents"]["environment"][
            "CAREERPILOT_OPENAI_AGENTS_PROVIDER"
        ]
        == "fake"
    )


def test_cloud_configuration_is_zurich_and_digest_pinned() -> None:
    variables = (ROOT / "infrastructure/terraform/variables.tf").read_text(
        encoding="utf-8"
    )
    main = (ROOT / "infrastructure/terraform/main.tf").read_text(encoding="utf-8")
    assert 'default     = "europe-west6"' in variables
    assert "@sha256:" in variables
    assert "allowed_persistence_regions = [var.region]" in main
    assert 'ingress             = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"' in main
    assert 'role      = "roles/secretmanager.secretAccessor"' in main
    assert "google_service_account_key" not in main


def test_sbom_is_deterministic_and_has_both_ecosystems() -> None:
    first = build_sbom(ROOT)
    second = build_sbom(ROOT)
    assert first == second
    assert first["bomFormat"] == "CycloneDX"
    purls = [component["purl"] for component in first["components"]]
    assert any(value.startswith("pkg:pypi/") for value in purls)
    assert any(value.startswith("pkg:npm/") for value in purls)
    assert len(purls) == len(set(purls))
    json.dumps(first)
