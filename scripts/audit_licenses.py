"""Fail closed on prohibited installed Python license metadata."""

from __future__ import annotations

import importlib.metadata

PROHIBITED_PREFIXES = ("AGPL", "GPL-2.0", "GPL-3.0")
REVIEWED_UNKNOWN = frozenset(
    {
        "aiosqlite",
        "careerpilot-api",
        "careerpilot-core",
        "careerpilot-google-adk",
        "careerpilot-openai-agents",
        "careerpilot-temporal-worker",
        "colorama",
        "google-adk",
        "markdown-it-py",
        "mdurl",
        "pathspec",
        "pip-api",
        "pip_audit",
    }
)


def main() -> int:
    """Inspect locked-environment metadata and reject unreviewed/prohibited licenses."""
    errors: list[str] = []
    scanned = 0
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name", "unknown")
        license_text = distribution.metadata.get(
            "License-Expression"
        ) or distribution.metadata.get("License")
        scanned += 1
        if license_text is None and name not in REVIEWED_UNKNOWN:
            errors.append(f"{name}: missing license metadata")
        elif license_text and license_text.strip().startswith(PROHIBITED_PREFIXES):
            errors.append(f"{name}: prohibited license {license_text}")
    if errors:
        for error in sorted(errors):
            print(error)  # noqa: T201
        return 1
    print(f"Python license policy passed: {scanned} distributions scanned.")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
