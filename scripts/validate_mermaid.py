"""Render every Mermaid fence to validate diagram syntax.

The script extracts diagrams into a temporary directory and invokes the pinned
Mermaid CLI from `tools/documentation`. Generated SVG files never enter the
repository.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MMDC = ROOT / "tools/documentation/node_modules/.bin/mmdc"
MERMAID_FENCE = re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL)
MACOS_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def diagram_sources() -> list[tuple[Path, int, str]]:
    """Return source path, one-based diagram number, and Mermaid text."""
    diagrams: list[tuple[Path, int, str]] = []
    for path in sorted(ROOT.glob("**/*.md")):
        if any(part in {".git", ".venv", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        diagrams.extend(
            (path, number, match.group("body"))
            for number, match in enumerate(MERMAID_FENCE.finditer(text), start=1)
        )
    return diagrams


def main() -> int:
    """Render diagrams and return nonzero if the CLI is missing or syntax fails."""
    if not MMDC.is_file():
        print("Mermaid CLI is missing; run npm ci in tools/documentation.")
        return 1

    diagrams = diagram_sources()
    with tempfile.TemporaryDirectory(prefix="careerpilot-mermaid-") as directory:
        temporary_root = Path(directory)
        configured_chrome = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
        chrome = configured_chrome or shutil.which("google-chrome")
        if not chrome and MACOS_CHROME.is_file():
            chrome = str(MACOS_CHROME)
        if not chrome:
            print("Chrome is missing; set PUPPETEER_EXECUTABLE_PATH.")
            return 1
        puppeteer_config = temporary_root / "puppeteer.json"
        puppeteer_config.write_text(
            json.dumps({"executablePath": chrome, "headless": True}), encoding="utf-8"
        )
        for index, (source, number, body) in enumerate(diagrams, start=1):
            input_path = temporary_root / f"diagram-{index}.mmd"
            output_path = temporary_root / f"diagram-{index}.svg"
            input_path.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [
                    str(MMDC),
                    "--puppeteerConfigFile",
                    str(puppeteer_config),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                location = f"{source.relative_to(ROOT)} #{number}"
                print(f"Mermaid validation failed: {location}")
                print(result.stderr.strip())
                return result.returncode

    print(f"Mermaid validation passed: {len(diagrams)} diagrams rendered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
