# ADR-0031: Keep DBOS and Restate as isolated comparison labs

- **Status:** Accepted for Phase 19 laboratory scope
- **Date:** 2026-08-16

## Context

Temporal owns CareerPilot's long-running durable business workflows. DBOS and
Restate offer different durable-execution abstractions that are useful to study,
but adding multiple engines to production would multiply state stores, recovery
procedures, telemetry, deployment, security, licensing and operational ownership.

## Decision

Retain Temporal as the only production durable-workflow engine. Implement DBOS
and Restate solely as standalone projects under `labs/`, outside the root uv
workspace and production import graph. Compare the same synthetic idempotent
effect, including a failure after commit, through official framework runtimes.

DBOS tests use its supported local SQLite system database. Restate tests use the
official SDK harness and a pinned local Restate server container. Neither runtime
may receive customer data, expose a CareerPilot route, or become a deployment
artifact. A future adoption requires a replacement ADR, measured need, security
and license review, migration/recovery design, operational and regional-hosting
evidence, cost approval and an explicit implementation phase.

## Consequences

The labs provide practical evidence without creating a split-brain production
architecture. Their separate manifests and locks intentionally duplicate a small
amount of configuration. Root tests enforce that their packages and imports stay
outside production.

The Python SDKs are MIT licensed. The Restate server is distributed under BSL 1.1
with an additional-use grant and future change license; professional license
review is required before relying on that grant. This ADR makes no legal approval
or certification claim.
