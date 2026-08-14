# Phase 11 tutorial: bounded A2A interoperability

A2A separates four concerns. An Agent Card says what a service claims to support. A
registry decides which cards are trusted. Authorization decides whether this caller may
delegate. A Task records lifecycle. Treating these as one concern would let discovery
accidentally become authority.

CareerPilot uses official SDK card/task values but keeps execution behind a small adapter.
This permits the same lifecycle tests for LangGraph, ADK, and OpenAI without starting a
model or network service. Versioned skill IDs make breaking capability changes visible.
Correlation metadata contains identifiers, not prompts or hidden reasoning.

Try `GET /api/v1/a2a/agents` with a local session. Submit a synthetic request to
`POST /api/v1/a2a/tasks`; use `defer_execution: true` and the cancel endpoint to observe a
cancelable submitted task. Repeat an identical task ID to observe idempotency, then alter
the payload to receive a conflict. A foreign tenant receives not-found.

The key lesson is that interoperability is not trust. A production A2A transport still
needs authenticated workloads, card provenance, per-operation policy, bounded content,
durable state, cancellation semantics, and retention rules.
