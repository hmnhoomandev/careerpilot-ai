"""Validate critical repository configuration without external services."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str) -> object:
    """Load one trusted repository YAML document for structural tests."""
    return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))


def test_compose_uses_pinned_local_only_postgres() -> None:
    """Keep the development database explicit, local, and password-gated."""
    document = load_yaml("compose.yaml")

    assert isinstance(document, dict)
    postgres = document["services"]["postgres"]
    assert postgres["image"].startswith("pgvector/pgvector:0.8.5-pg17-bookworm@sha256:")
    assert len(postgres["image"].rsplit(":", maxsplit=1)[-1]) == 64
    assert postgres["ports"] == ["127.0.0.1:${CAREERPILOT_POSTGRES_PORT:-5432}:5432"]
    assert ":?" in postgres["environment"]["POSTGRES_PASSWORD"]


def test_ci_workflow_is_valid_yaml_with_read_only_permissions() -> None:
    """Catch YAML syntax drift and accidental broad default permissions."""
    document = load_yaml(".github/workflows/ci.yml")

    assert isinstance(document, dict)
    assert document["permissions"] == {"contents": "read"}
    assert set(document["jobs"]) == {"backend", "documentation", "frontend"}
