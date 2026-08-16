# Comparison Labs

Bounded educational experiments live here and must never become production
dependencies.

Phase 19 compares the existing Temporal implementation with two independent
projects:

- `dbos/` checkpoints a workflow and retryable step in a local SQLite system
  database.
- `restate/` runs a durable step through the local Restate test harness.

Both implement the synthetic contract in `fixtures/durable-effect-scenario.json`.
They use opaque identifiers only, perform no external model or cloud calls, and
must retain their own lockfiles. Run their checks from the repository root with:

```shell
uv run --project labs/dbos ruff check labs/dbos
uv run --project labs/dbos mypy labs/dbos/src labs/dbos/tests
uv run --project labs/dbos pytest labs/dbos/tests
uv run --project labs/restate ruff check labs/restate
uv run --project labs/restate mypy labs/restate/src labs/restate/tests
uv run --project labs/restate pytest labs/restate/tests
```

The Restate tests require a running Docker engine so the official harness can
start its local server container. No lab may be added to the root uv workspace.
