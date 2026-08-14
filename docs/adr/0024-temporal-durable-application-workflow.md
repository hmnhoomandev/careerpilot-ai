# ADR-0024: Temporal owns durable application preparation

**Status:** Accepted for Phase 12  
**Date:** 2026-08-14

## Context

CareerPilot's analysis graph, specialist services, and approval records have distinct
owners, but the complete preparation process must survive worker restarts, wait days for a
person, retry transient effects safely, schedule follow-up work, and compensate completed
steps after rejection or cancellation.

## Decision

Use the MIT-licensed Temporal Python SDK 1.30.x in a dedicated worker package. Temporal
owns orchestration history, deterministic transitions, durable timers, signals, queries,
activity policies, replay, and compensation. LangGraph continues to own bounded agent
graph execution. PostgreSQL remains authoritative for profiles, evidence, drafts,
approvals, applications, and audit records.

Workflow history contains only validated opaque IDs/references and concise states. All I/O,
authorization, model/agent calls, persistence, and external effects belong in activities.
Each activity receives a stable step idempotency key and heartbeats. Approval is a signal
bound to the exact draft reference, version, and actor; the production gateway must verify
the authoritative approval record before sending it. No approval authorizes email or job
submission in this phase.

The initial workflow sequentially coordinates analysis, supplied-source research, draft
preparation, approval, application tracking, and a follow-up timer. Rejection and
cancellation compensate completed effects in reverse order. `workflow.patched` records the
first follow-up behavior version for replay compatibility.

## Consequences

The local official time-skipping server proves restart recovery, timers, activity retry,
signals, queries, cancellation, compensation, and replay at CHF 0. The fake activity
ledger demonstrates contracts and idempotency but is not durable production storage.

Production still requires authenticated client/gateway composition, authoritative
activity adapters, TLS/workload identity, namespace/task-queue policy, PostgreSQL
projections, retention/deletion, visibility controls, backup/recovery, and deployment.
Temporal Cloud is neither required nor authorized. Final retention and legal basis need
professional legal review; no compliance certification is claimed.
