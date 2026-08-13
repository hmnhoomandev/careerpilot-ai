# ADR-0019: Bounded LangGraph Analysis and Provider Port

- **Status:** Accepted for Phase 7
- **Date:** 2026-08-13

## Context

CareerPilot needs a visible stateful analysis path without giving a model authority over
authorization, tools, truth, or long-running business state. Graph retry and checkpoint
behavior must also remain distinct from Temporal workflow durability.

## Decision

Use LangGraph `>=1.2.9,<1.3` (MIT, Python 3.10+) for a typed in-process graph with an
in-memory local/test checkpointer. Nodes own disjoint state outputs and follow an
explicit path. Known intake routes are deterministic; only ambiguous intake may call
the provider port. Side-effect-free structured extraction may retry once on
`ConnectionError`. Tools retain their Phase 6 authorization and audit enforcement.

Use a provider-neutral core protocol, deterministic fake by default, and a Google Gen
AI `>=2.13,<2.14` adapter (Apache-2.0, Python 3.10+) for the future live Gemini path.
Adapter construction requires explicit external-transfer authorization; no provider
fallback exists. The SDK is preferred over handwritten HTTP for maintained schemas,
authentication integration, and async structured output.

## Consequences

- Checkpoints are process-local educational state, not production durability.
- Temporal still owns durable waits, schedules, compensation, and business recovery.
- Retrieved/job text remains untrusted data; deterministic verification and citations
  determine support. The graph exposes concise decisions, never hidden reasoning.
- Live Gemini calls require a later explicit opt-in, consent/data-policy check, secret,
  cost authorization, and marked evaluation. Phase 7 made none.
