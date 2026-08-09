# Agent Role Classification

Classification is provisional until each implementation phase evaluates fixtures.
“Agent” means model reasoning adds justified value; it is not a headcount target.

| Role | Primary classification | Rationale / boundary |
|---|---|---|
| Manager/Supervisor | Hybrid graph coordinator | Deterministic routes first; model delegation only when evaluated |
| Intake and Intent | Hybrid node | Schema/rules for known intents; bounded model classification for ambiguity |
| Professional Profile | Application service + optional extraction node | User owns facts; model may propose fields but cannot mutate without approval |
| Job Analysis | LLM specialist agent | Structured interpretation of untrusted job text, followed by validation |
| Company Research | Remote ADK specialist | Bounded permitted-source research with provenance |
| Retrieval | Deterministic tool/service | Search/rerank pipeline; no autonomous identity needed |
| Candidate-to-Job Match | Hybrid service/node | Deterministic scoring plus evaluated evidence-grounded interpretation |
| Skill Gap | Hybrid service/node | Taxonomy/rules plus bounded semantic comparison |
| Resume Tailoring | LLM specialist agent | Generates structured draft under claim-evidence enforcement |
| Cover Letter | LLM specialist agent | Generates structured draft under claim-evidence enforcement |
| Interview Coach | Bounded specialist agent | Interactive simulation; later ADK/OpenAI comparison candidate |
| Evidence Verification | Policy engine + deterministic node | Verifies claim links and blocks unsupported assertions |
| Privacy and PII | Policy engine/tool | Detection, minimization, redaction, consent, and authorization checks |
| Prompt-Injection and Security | Policy engine + classifiers | Deterministic controls first; model classifier may add defense, never sole control |
| Bias and Compliance | Policy engine + evaluated reviewer | Flags risks and limitations; no autonomous legal conclusion |
| Approval Coordinator | Deterministic state machine/workflow | Human decisions, versions, expiry, restart, and audit must be predictable |
| Application Tracking | Application service + Temporal workflow | Durable statuses, timers, cancellation, and follow-up |
| Quality Evaluation | Evaluation service/harness | Versioned datasets, deterministic metrics, and bounded judges |
| Explanation | Hybrid formatter/agent | Deterministic provenance plus concise generated summary; no hidden reasoning |

## Required implementation dossier

Before any role becomes an LLM agent, its phase must document purpose,
non-responsibilities, inputs, structured outputs, tools, permissions, state,
memory, handoffs, guardrails, approvals, timeouts, retries, failure behavior,
model policy, cost/latency budget, telemetry, and evaluation dataset.
