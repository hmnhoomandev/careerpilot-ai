"""Create a deterministic local SLSA provenance predicate for verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable is required")
    revision = subprocess.run(
        [git, "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    materials = ["uv.lock", "apps/web/package-lock.json"]
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "careerpilot-source", "digest": {"gitCommit": revision}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://careerpilot.example/build/local-verification/v1",
                "externalParameters": {"network": "not-required"},
                "resolvedDependencies": [
                    {"uri": path, "digest": {"sha256": _sha256(Path(path))}}
                    for path in materials
                ],
            },
            "runDetails": {"builder": {"id": "careerpilot-local-verifier"}},
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(statement, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
