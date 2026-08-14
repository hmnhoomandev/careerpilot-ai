# ADR-0027: Local-first observability, routing, and cost control

- Status: Accepted
- Date: 2026-08-14

## Context

CareerPilot has component-specific logs, traces and offline evaluations, but needs one safe
schema, measurable local dashboard, explicit provider routing and pre-execution cost control.
The CHF 0 development budget and personal-data policy prohibit live exporters and model calls.

## Decision

Adopt `careerpilot.telemetry.v1`, a bounded metadata-only event compatible with OpenTelemetry
concepts. Aggregate it in a tenant-scoped process-local collector. Export adapters accept only
validated events and remain disabled until deployment/privacy/cost approval.

Keep ADK trace capture at `NO_CONTENT`. Independently disable ADK prompt-response upload and
BigQuery Agent Analytics: the upload tier can contain full prompts/responses even when span
content is disabled. Keep OpenAI SDK trace export disabled. Define Cloud Logging/Trace,
BigQuery and LangSmith as future adapter destinations, not active dependencies.

Use versioned prompt/model registries and deterministic routing by an explicit route ID.
Capability, privacy, quality, latency, availability, approval and remaining budget all fail
closed with one reason. Never search another provider after failure. Reserve estimated cost
before work; CHF 0 allows only zero-cost routes. Cache only authorized, non-sensitive inputs
under tenant/capability/prompt/model/digest keys.

Use versioned deterministic offline metrics as the default evaluation gate. Managed or
LLM-as-judge ADK evaluation is opt-in because it can make model/cloud calls and has region,
residency and cost implications.

## Consequences

Local metrics prove contracts and policy, not production SLO achievement. PostgreSQL/durable
budget reconciliation, distributed quotas, exporters, sampling, alerting, retention and real
traffic baselines remain future production work. The core stays vendor-neutral and no new
runtime dependency or cloud resource is introduced.
