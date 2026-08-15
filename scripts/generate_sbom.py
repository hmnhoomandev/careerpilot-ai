"""Generate deterministic CycloneDX component inventories from lock files."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any


def _component(name: str, version: str, ecosystem: str) -> dict[str, object]:
    return {
        "type": "library",
        "name": name,
        "version": version,
        "purl": f"pkg:{ecosystem}/{name}@{version}",
    }


def build_sbom(root: Path) -> dict[str, Any]:
    """Return one normalized SBOM for Python and production Node dependencies."""
    python_lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    components = {
        (item["name"], item["version"], "pypi")
        for item in python_lock["package"]
        if "version" in item
    }
    node_lock = json.loads(
        (root / "apps/web/package-lock.json").read_text(encoding="utf-8")
    )
    for path, item in node_lock["packages"].items():
        if not path or item.get("dev", False) or "version" not in item:
            continue
        name = path.rsplit("node_modules/", maxsplit=1)[-1]
        components.add((name, item["version"], "npm"))
    ordered = [_component(*item) for item in sorted(components)]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": "careerpilot"}},
        "components": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_sbom(Path.cwd()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
