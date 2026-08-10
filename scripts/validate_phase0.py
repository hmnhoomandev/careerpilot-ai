"""Validate the documentation-only Phase 0 acceptance baseline.

This standard-library script performs structural checks without installing a
dependency or contacting an external service. It is project tooling, not
production application code.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "AGENTS.md",
    "PLANS.md",
    "docs/project/PROJECT_STATE.md",
    "docs/project/ROADMAP.md",
    "docs/project/DECISION_LOG.md",
    "docs/project/REQUIREMENTS_TRACEABILITY.md",
    "docs/project/LEARNING_LOG.md",
    "docs/product/PRODUCT_VISION.md",
    "docs/product/USER_JOURNEYS.md",
    "docs/product/REQUIREMENTS.md",
    "docs/product/DOMAIN_GLOSSARY.md",
    "docs/product/DOMAIN_MODEL.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/TECHNOLOGY_DECISION_MATRIX.md",
    "docs/architecture/AGENT_ROLE_CLASSIFICATION.md",
    "docs/security/THREAT_MODEL.md",
    "docs/security/PRIVACY_IMPACT_ASSESSMENT.md",
    "docs/security/RISK_REGISTER.md",
    "docs/cost/COST_ASSUMPTIONS.md",
    "docs/tutorials/phase-00-architecture-baseline.md",
    "docs/exercises/phase-00-exercises.md",
    "docs/exercises/phase-00-answers.md",
    "docs/annotated-source/validate-phase0.md",
    "docs/reviews/phase-00-review.md",
)

REQUIREMENT_RANGES = {"FR": 24, "SEC": 22, "NFR": 20, "LEG": 8}
GENERATED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
}


def main() -> int:
    """Return zero when required files, IDs, and Mermaid fences are valid."""
    errors = [
        f"missing required file: {relative_path}"
        for relative_path in REQUIRED_FILES
        if not (ROOT / relative_path).is_file()
    ]
    markdown_files = sorted(
        path
        for path in ROOT.glob("**/*.md")
        if GENERATED_DIRECTORIES.isdisjoint(path.relative_to(ROOT).parts)
    )

    requirements_path = ROOT / "docs/product/REQUIREMENTS.md"
    requirements = requirements_path.read_text(encoding="utf-8")
    for prefix, maximum in REQUIREMENT_RANGES.items():
        for number in range(1, maximum + 1):
            requirement_id = f"{prefix}-{number:03d}"
            if requirement_id not in requirements:
                errors.append(f"missing requirement ID: {requirement_id}")

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("# "):
            errors.append(f"missing H1 at start: {path.relative_to(ROOT)}")
        if text.count("```mermaid") > text.count("```"):
            errors.append(f"unclosed Mermaid fence: {path.relative_to(ROOT)}")
        if re.search(r"(?i)(api[_-]?key|secret|password)\s*[=:]\s*['\"][^'\"]+", text):
            errors.append(f"possible secret literal: {path.relative_to(ROOT)}")
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            local_target = target.split("#", maxsplit=1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                errors.append(
                    f"broken local link in {path.relative_to(ROOT)}: {target}"
                )

    if errors:
        print("Phase 0 validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Phase 0 validation passed: "
        f"{len(REQUIRED_FILES)} required files, "
        f"{sum(REQUIREMENT_RANGES.values())} requirement IDs, "
        f"{len(markdown_files)} Markdown files."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
