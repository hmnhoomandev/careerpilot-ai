# ADR-0022: OpenAI Agents Interview Laboratory

- **Status:** Accepted for Phase 10
- **Date:** 2026-08-14

## Context

CareerPilot needs a concrete comparison of manager delegation, agent-as-tool, and direct
handoff without allowing a second framework to own the main application graph or making
paid calls in default development.

## Decision

Create `services/openai-agents` as an isolated interview-simulation laboratory using the
OpenAI Agents SDK 0.8.x. Real SDK definitions demonstrate agents, handoff, agent-as-tool,
structured output, a function tool requiring approval, SQLite session compatibility, and
trace configuration. Deterministic fake execution owns all default tests.

Direct handoff transfers final-response ownership to the specialist. Agent-as-tool and
manager delegation retain manager ownership. Deterministic input/output/tool guardrails,
tenant-scoped sessions, exact-action approval state, and metadata-only traces surround
the model boundary. SDK trace export and sensitive trace content are disabled by default.

## Consequences

The OpenAI SDK is unavailable outside this service. Live execution requires a separate
explicit cost/data approval, positive CHF ceiling, credentials, consent, and transfer
authority; it never silently falls back. The static development service header,
in-memory session results, and approval store are not production controls. No external
communication, profile mutation, cloud deployment, or database migration is introduced.
