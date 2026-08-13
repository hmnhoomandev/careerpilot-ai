# ADR-0020: Truthful Drafts and Exact-Version Human Approval

- **Status:** Accepted for Phase 8
- **Date:** 2026-08-13

## Decision

Career drafts are immutable versions. Every material claim is `supported` with one or
more source/chunk citations, `suggestion_requires_confirmation`, or `blocked` and absent
from factual prose. Deterministic privacy and bias checks run after generation.

Approval is a deterministic state machine bound to draft ID, version, SHA-256 content
hash, tenant, actor, and optimistic revision. Pending is the default; terminal or stale
records cannot authorize another decision. Approval never performs external sharing.

PostgreSQL owns durable draft/approval records through Alembic `0003`. LangGraph
`interrupt` supplies the pause/resume interaction contract with an injectable
checkpointer. In-memory checkpointing is the default fake; production deployment must
configure the official PostgreSQL checkpointer in a dedicated migration step before
claiming cross-process graph-checkpoint durability. PostgreSQL business records already
support restart-safe review and reconciliation.

## Consequences

Temporal will later own expiry schedules and long-running recovery; Phase 8 exposes the
expired transition but starts no timer. A2UI-compatible messages are allowlisted data
contracts, not executable UI code or authorization. No model/provider call is needed.
