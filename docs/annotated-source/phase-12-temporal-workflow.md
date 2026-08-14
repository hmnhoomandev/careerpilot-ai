# Annotated source: Phase 12 Temporal workflow

`contracts.py` defines every object that may enter Temporal history. Frozen dataclasses
make intent explicit and the allowlisted token/reference validation blocks accidental
resume, job-description, research, or draft prose from durable history.

`workflow.py` is deterministic orchestration. `_command` derives stable step idempotency
keys. `_activity` applies one retry, timeout, and heartbeat policy and records a completed
step only after success. `run` advances through analysis, research, drafts, an unbounded
human wait, tracking, a durable follow-up timer, and completion. Signals mutate only
workflow state; `status` is a read-only query. Exact draft/actor mismatch is ignored and
visible. Rejection or cancellation calls `_compensate` in reverse order. The patch marker
creates a history-safe change point rather than branching on deployed code version.

`activities.py` is the side-effect boundary. `PreparationActivities` heartbeats before
calling an `ActivityLedger` port. The fake can commit then fail once; the retry returns the
already-recorded result, proving why activity idempotency is separate from Temporal's
at-least-once execution. Compensation is also idempotent. A production ledger must use
transactional PostgreSQL records and reauthorize each command.

`worker.py` registers workflow and bound activities on one versioned task queue. The
caller owns credentials, connection and lifecycle so the package cannot silently connect
to Temporal Cloud. Tests use the official local time-skipping environment, stop/recreate a
worker, query and signal the workflow, advance a week instantly, inject retry, cancel,
inspect compensation, and replay history.
