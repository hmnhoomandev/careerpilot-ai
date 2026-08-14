# Phase 12 tutorial: durable workflows without magical thinking

A normal async function remembers progress only while its process lives. A Temporal
workflow emits commands into an event history. If its worker disappears, another worker
replays that history and reaches the same state before continuing. This is why workflow
code must be deterministic and why network/database/model work belongs in activities.

Temporal guarantees durable orchestration, not exactly-once side effects. An activity can
write a record and crash before reporting success. Temporal then retries it. CareerPilot
therefore gives every step a stable idempotency key; the fake test deliberately fails after
commit and proves the second attempt reuses the original result.

Signals change workflow state without returning a business result. The approval signal is
accepted only while waiting and only for the expected draft reference/version/actor.
Queries read current stage without mutation. A durable timer schedules follow-up without a
sleeping application process, and time-skipping tests advance that week in seconds.

Stopping a worker is not cancellation: history stays and a new worker recovers it.
Cancellation is a requested terminal outcome. Compensation then performs explicit reverse
actions for completed steps. It cannot erase an email or make the outside world atomic;
each compensation must be designed, authorized, idempotent, and auditable.

Run the focused lesson with:

```text
uv run pytest -m temporal -q
```

The first run may download Temporal's free local test-server binary. It creates no cloud
account or paid resource. Production connection, credentials and deployment are deferred.
