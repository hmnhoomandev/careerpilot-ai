"""Enforce repository dependency direction without importing application code."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORE_SOURCE = ROOT / "packages/core/src"
FORBIDDEN_CORE_PREFIXES = (
    "careerpilot_api",
    "fastapi",
    "google",
    "langgraph",
    "openai",
    "sqlalchemy",
    "temporalio",
)


def imported_modules(path: Path) -> set[str]:
    """Return absolute import names declared by one Python source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


@pytest.mark.architecture
def test_core_does_not_import_outward_dependencies() -> None:
    """Keep domain-safe core code independent of adapters and provider SDKs."""
    violations = [
        f"{path.relative_to(ROOT)} imports {module}"
        for path in sorted(CORE_SOURCE.rglob("*.py"))
        for module in imported_modules(path)
        if module.startswith(FORBIDDEN_CORE_PREFIXES)
    ]

    assert not violations, "Forbidden outward imports:\n" + "\n".join(violations)
