"""Prove comparison engines cannot leak into CareerPilot production dependencies."""

from __future__ import annotations

import ast
import json
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LAB_DEPENDENCIES = {"dbos", "restate-sdk", "testcontainers"}
LAB_IMPORT_PREFIXES = (
    "dbos",
    "careerpilot_dbos_lab",
    "restate",
    "careerpilot_restate_lab",
)
PRODUCTION_SOURCE_ROOTS = (
    ROOT / "apps/api/src",
    ROOT / "packages/core/src",
    ROOT / "services",
)


def dependency_names(project: dict[str, object]) -> set[str]:
    """Return normalized declared dependency names from one pyproject document."""
    names: set[str] = set()
    project_table = project.get("project", {})
    if isinstance(project_table, dict):
        dependencies = project_table.get("dependencies", [])
        if isinstance(dependencies, list):
            names.update(
                str(item).split("[")[0].split("=")[0].lower() for item in dependencies
            )
    return names


def imported_modules(path: Path) -> set[str]:
    """Return absolute imports without executing a production module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


@pytest.mark.architecture
def test_comparison_projects_are_outside_root_workspace_and_lock() -> None:
    """Keep lab SDKs out of root installation and transitive resolution."""
    root_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    workspace = root_project["tool"]["uv"]["workspace"]["members"]
    assert "labs/dbos" not in workspace
    assert "labs/restate" not in workspace
    assert dependency_names(root_project).isdisjoint(LAB_DEPENDENCIES)

    root_lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked_names = {package["name"] for package in root_lock["package"]}
    assert locked_names.isdisjoint(LAB_DEPENDENCIES)


@pytest.mark.architecture
def test_production_sources_do_not_import_comparison_labs_or_sdks() -> None:
    """Prevent accidental runtime routing through either comparison engine."""
    violations = [
        f"{path.relative_to(ROOT)} imports {module}"
        for source_root in PRODUCTION_SOURCE_ROOTS
        for path in sorted(source_root.rglob("*.py"))
        for module in imported_modules(path)
        if module.startswith(LAB_IMPORT_PREFIXES)
    ]
    assert not violations, "Comparison lab imports found:\n" + "\n".join(violations)


@pytest.mark.architecture
def test_lab_projects_pin_frameworks_and_share_safe_scenario() -> None:
    """Pin comparison inputs and dependencies without personal or document data."""
    dbos_project = tomllib.loads(
        (ROOT / "labs/dbos/pyproject.toml").read_text(encoding="utf-8")
    )
    restate_project = tomllib.loads(
        (ROOT / "labs/restate/pyproject.toml").read_text(encoding="utf-8")
    )
    assert dependency_names(dbos_project) == {"dbos"}
    assert dependency_names(restate_project) == {"restate-sdk"}
    assert (ROOT / "labs/dbos/uv.lock").is_file()
    assert (ROOT / "labs/restate/uv.lock").is_file()

    scenario = json.loads(
        (ROOT / "labs/fixtures/durable-effect-scenario.json").read_text(
            encoding="utf-8"
        )
    )
    assert scenario["schema_version"] == 1
    assert scenario["recovery"] == {
        "failure": "synthetic_transient_failure_after_commit",
        "expected_attempts": 2,
        "expected_unique_effects": 1,
    }
    assert set(scenario) == {
        "schema_version",
        "tenant_id",
        "application_id",
        "operation",
        "idempotency_key",
        "expected_artifact_ref",
        "recovery",
    }
