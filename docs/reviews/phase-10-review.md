# Phase 10 Review: OpenAI Agents SDK Interview Laboratory

## 1. Phase objective

Deliver a product-relevant, isolated OpenAI Agents SDK service that compares direct
handoff, agent-as-tool, and manager delegation with fake-first execution.

## 2. Delivered features

- SDK manager, interviewer, feedback agents, handoff, agent-as-tool, structured output,
  approval function tool, SQLite-session compatibility, and safe tracing configuration.
- Equivalent deterministic scenarios with explicit active-agent/final-owner results.
- Input/output/tool guardrails, tenant sessions, metadata traces, and provider abstraction.
- Serializable exact-action approval request/approve/reject/resume plus internal API.
- Opt-in live provider/test requiring data authority and a positive CHF budget.

## 3. Explicitly not delivered

No live model call, real candidate data, publication, email, submission, profile mutation,
voice/realtime, hosted tool, A2A, deployment, cloud tracing, durable production state,
database migration, or Phase 11 feature was delivered.

## 4. Files created/changed

`services/openai-agents/` contains package/config, SDK definitions, fake/live providers,
contracts, guards, approvals, sessions/service, API, and telemetry. Root unit/contract/live
tests and Phase 10 ADR/tutorial/annotated source/exercises/security/project records changed.

## 5. Architecture decisions

Direct handoff transfers response ownership to the specialist. Agent-as-tool and manager
delegation retain manager ownership. The SDK remains isolated from domain/main API. Fake
is default; OpenAI is explicit, budgeted, transfer-gated, bounded to six turns, and has no
fallback. SDK trace export and sensitive content are disabled.

## 6. Security/privacy review

Deterministic guards run outside model authority. Approval binds tenant, actor, session,
action hash, state, and revision and authorizes no external publication. Local traces omit
prompts, answers, tool payloads, secrets, and hidden reasoning. The development service
header, process-local sessions/approvals, provider policy, retention, workload identity,
and lawful basis require production/legal review. No compliance claim is made.

## 7. Data/schema/migration impact

No database schema/migration changed. OpenAI Agents SDK 0.8.4 and OpenAI 2.54.0 enter the
uv lock. Sessions, approvals, and traces are process-local prototype state.

## 8. Automated commands and exact results

- Focused final service/API suite: 10 passed.
- Ruff passed; strict MyPy passed for 105 source/test/script files.
- Pytest: 146 passed; four PostgreSQL and two live-model tests skipped.
- Pip-audit and production/full npm audits: zero known vulnerabilities; four internal
  workspace packages were expected pip-audit skips.
- Semgrep scanned 111 Python targets with three rules and zero findings; its macOS signal
  warning did not prevent a successful scan. Detect-secrets passed.
- Frontend format/lint/typecheck, five Vitest tests, and production build passed.
- Markdown lint (114 files), external links, eight Mermaid diagrams, pre-commit hooks,
  and governance validation passed (122 Markdown files counted by the validator).
- The live OpenAI test skipped because explicit cost approval was not set; no call ran.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Direct handoff fixture | Specialist owns final response | Automated pass; owner pending |
| Agent-as-tool fixture | Manager retains final response | Automated pass; owner pending |
| Trigger guardrail | Safe `guardrail_blocked` | Automated pass; owner pending |
| Pause/approve/reject | Exact action resumes once | Automated pass; owner pending |
| Inspect trace | Metadata, no hidden reasoning | Automated pass; owner pending |

## 10. Requirements traceability

FR-015/016 map to interview/feedback orchestration. FR-020 and SEC-011 map to the approval
gate. SEC-006/009 and NFR-003/010/012 map to provider, privacy, cost, trace, and live-skip
controls in `docs/project/REQUIREMENTS_TRACEABILITY.md`.

## 11. Example requests/responses

`POST /v1/interviews` accepts scoped IDs, role, synthetic answer, and orchestration mode.
It returns active agent, final owner, question, feedback, and a concise decision summary.
The two approval routes return pending then approved/rejected exact-action state.

## 12. Known limitations, debt, and risks

- Static internal identity and process-local state are not production controls.
- Pattern guardrails are not complete safety classifiers.
- Live quality, cost, latency, and SDK-generated HITL serialization remain unevaluated.
- A configured positive ceiling is a pre-run gate, not metered hard-stop billing control.
- Provider terms, residency, retention/deletion, and legal basis need review.

## 13. Rollback/recovery instructions

Before Phase 11, revert the Phase 10 commit, remove its uv workspace member, and restore
the lock. No database or cloud rollback exists.

## 14. Learning summary

The lab makes control transfer concrete and separates SDK orchestration from application
authority, human approval, privacy policy, cost control, and observable decision summaries.

## 15. Owner acceptance checklist

- Compare the three equivalent modes.
- Trigger each guardrail and approval outcome.
- Inspect redacted trace metadata.
- Review ADR-0022/tutorial and accept the documented live/production gaps.

## 16. Proposed next phase

Phase 11 adds bounded A2A interoperability and an agent registry. It is not started.

## 17. Exact approval command

`APPROVE PHASE 10 AND START PHASE 11`
