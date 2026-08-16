# DBOS durable-effect lab

This standalone project checkpoints a synchronous workflow and its retryable
effect step in DBOS. Tests use a temporary SQLite system database and a synthetic
idempotent ledger; they make no cloud or model calls.

DBOS is comparison-only. Its MIT-licensed SDK is pinned in this lab's lockfile,
and neither it nor SQLite is a CareerPilot production architecture decision.
Temporal remains the production durable-workflow owner.
