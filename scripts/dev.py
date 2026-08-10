"""Run the local Phase 2 API and web processes with one command."""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Start both local processes and stop both when either exits."""
    commands = (
        (
            "uv",
            "run",
            "uvicorn",
            "careerpilot_api.main:app",
            "--app-dir",
            "apps/api/src",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ),
        ("npm", "--prefix", "apps/web", "run", "dev"),
    )
    processes = [subprocess.Popen(command, cwd=ROOT) for command in commands]

    def stop_processes(_signal: int, _frame: object) -> None:
        for process in processes:
            if process.poll() is None:
                process.terminate()

    signal.signal(signal.SIGINT, stop_processes)
    signal.signal(signal.SIGTERM, stop_processes)

    try:
        while all(process.poll() is None for process in processes):
            for process in processes:
                try:
                    return_code = process.wait(timeout=0.25)
                except subprocess.TimeoutExpired:
                    continue
                return return_code
    finally:
        stop_processes(signal.SIGTERM, object())
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
