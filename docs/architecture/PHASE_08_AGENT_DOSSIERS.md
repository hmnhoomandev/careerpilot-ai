# Phase 8 Role Dossiers

| Role | Purpose / state | Non-responsibilities | Guardrails |
|---|---|---|---|
| Resume Tailoring | Evidence-only resume sections and claims | Invent facts, dates, metrics | Cited passages only; fake/deterministic |
| Cover Letter | Evidence-only letter sections and claims | Promise unsupported capability | Same claim graph and citations |
| Privacy/PII | Own visible PII flags | Decide lawful basis or legal compliance | Deterministic patterns; legal review remains |
| Bias/Compliance | Own policy flags/block | Make legal conclusions or rank people | Protected-trait language blocks; human review |
| Approval Coordinator | Own exact-version approval state | Execute sharing, email, submission, spending | Deterministic transitions, optimistic revision, audit |

All roles use authorized tenant context, synthetic default tests, CHF 0 cost, no
provider fallback, no external side effect, metadata-only telemetry, and no long-term
memory outside durable draft/approval records. Approval Coordinator is a deterministic
workflow role, not an LLM agent.
