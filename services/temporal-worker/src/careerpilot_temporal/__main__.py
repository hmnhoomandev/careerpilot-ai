"""Run the synthetic local worker against an explicitly configured Temporal server."""

from __future__ import annotations

import asyncio
import os

from temporalio.client import Client

from careerpilot_temporal.activities import FakeActivityLedger, PreparationActivities
from careerpilot_temporal.worker import build_worker


async def _run() -> None:
    target = os.environ.get("CAREERPILOT_TEMPORAL_TARGET", "temporal:7233")
    client = await Client.connect(target)
    worker = build_worker(client, PreparationActivities(FakeActivityLedger()))
    await worker.run()


def main() -> None:
    """Start the worker; connection failures fail closed and restart via Compose."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
