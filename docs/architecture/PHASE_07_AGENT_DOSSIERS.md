# Phase 7 Agent Role Dossiers

All roles use server-derived tenant authority, metadata-only telemetry, synthetic test
data, and a CHF 0 default budget. They have no memory outside graph state/checkpoints,
no external side effects, no approval authority, and no handoff to remote agents.

| Role | Purpose and owned state | Tools / model | Failure and guardrails |
|---|---|---|---|
| Manager + Intake | Validate intent and own `route`/`intent` | Rules first; provider only for ambiguity | 1 s, one attempt; unknown route ends |
| Job Analysis | Own structured `requirements` | Structured provider, fake default | 2 s, two attempts on connection failure; source is untrusted |
| Retrieval | Own cited `passages` | `evidence.retrieve` | 2 s; authorization remains in tool/service |
| Match | Own deterministic `match` | `candidate.match` | 2 s; no hiring decision or generated fact |
| Skill Gap | Own supported/missing/uncertain `gaps` | Deterministic comparison | 2 s; absence is never converted to qualification |
| Evidence | Own `verified` claim/citation records | `evidence.verify` | 2 s; unsupported remains explicit |
| Explanation | Own concise `explanation` and completion state | Deterministic formatter | 1 s; no hidden reasoning |

The Manager delegates node work while retaining the user-facing run. This is not a
direct handoff: no specialist becomes the conversational owner. Tool calls are not
agents, and MCP/A2A are not used by this in-process graph.
