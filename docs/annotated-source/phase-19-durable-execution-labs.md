# Annotated source: Phase 19 durable-execution labs

`labs/fixtures/durable-effect-scenario.json` is the human-readable comparison
contract. Opaque synthetic identifiers and exact expected attempt/effect counts
make the assertion comparable without sharing production packages between labs.

Each lab's `workflow.py` defines the same typed command/result and a thread-safe
fake ledger. `apply` records the artifact before injecting its first failure. On
retry it returns the stored artifact with `replayed_effect=true`; this is the key
lesson that runtime durability and effect idempotency solve different problems.

The DBOS module decorates the effect as a bounded retryable step and the caller as
a workflow. Tests launch DBOS against a temporary SQLite system database and use
explicit workflow IDs. The Restate module awaits `ctx.run_typed` with two attempts
and short local intervals. Its tests call a workflow through the official harness,
which launches a pinned local server and SDK endpoint.

`test_durable_lab_isolation.py` reads manifests and imports as data. It proves the
labs are absent from the root workspace/lock and production source graph without
importing or executing application modules. This negative assertion is what keeps
an educational comparison from becoming an accidental runtime dependency.
