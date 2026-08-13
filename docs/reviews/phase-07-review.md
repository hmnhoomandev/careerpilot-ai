# Phase 07 Review: LangGraph Core Analysis Flow

## 1. Phase objective

Deliver a stateful, observable, fake-first LangGraph workflow that turns an authorized
profile, cited evidence, and user-supplied job text into structured requirements,
candidate match, skill gaps, evidence decisions, and a concise explanation.

## 2. Delivered features

- Typed graph state, disjoint role ownership, deterministic-first routing, ordered
  progress events, terminal failure path, cancellation, bounded retry, and checkpoints.
- Manager/Intake, Job Analysis, Retrieval, Match, Gap, Evidence, and Explanation roles.
- Strict authenticated start/status/cancel API v0.7 with tenant/actor-scoped run IDs.
- Default deterministic fake provider and explicit no-fallback Gemini adapter.
- Cited evidence, supported/missing/uncertain gaps, and no unsupported candidate facts.

## 3. Explicitly not delivered

No live Gemini call, human interrupt/approval, document generation, durable checkpoint
database, Temporal workflow, UI progress screen, remote agent, ADK, A2A, deployment,
company research, scraping, email, submission, or application tracking was delivered.

## 4. Files created/changed

Core agent contracts, API graph/service/contracts/provider adapters, API composition,
dependency locks, graph/API/evaluation tests and fixtures, ADR-0019, role dossiers,
annotated source, tutorial, exercises, security/privacy/governance documentation.

## 5. Architecture decisions

ADR-0019 assigns bounded graph execution to LangGraph while Temporal retains durable
business workflow ownership. Models cannot authorize, establish truth, choose providers,
or call arbitrary tools. The manager delegates; it does not hand off user ownership.

## 6. Security/privacy review

Run access is server-derived and scoped by tenant, actor, and run. Inputs are bounded;
job/document text stays untrusted; tool policy is reused; outputs are structured and
cited; telemetry omits prompts/hidden reasoning. Gemini construction requires explicit
external-transfer authorization. Production checkpoint encryption, retention, deletion,
consent, region, and provider terms remain open and require legal/security review.

## 7. Data/schema/migration impact

No database migration. Graph/checkpoint/run state is process-local and disappears on
restart. Production PostgreSQL/pgvector schemas remain unchanged.

## 8. Automated commands and exact results

- Ruff format/lint passed; strict MyPy passed for 68 source files.
- Default Pytest: 113 passed, 3 PostgreSQL skips.
- Local PostgreSQL/pgvector Pytest: 116 passed, 0 skipped.
- Web Prettier, ESLint, TypeScript, 5 Vitest tests, and production build passed.
- Markdown lint/link checks and 8 Mermaid renders passed.
- Semgrep scanned 73 Python targets with 0 findings; detect-secrets/pre-commit passed.
- Pip audit and production/full npm audit found 0 known vulnerabilities; two internal
  unpublished Python packages were expected pip-audit skips.
- Governance validator passed: 24 required files, 74 IDs, 101 Markdown files.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Submit synthetic job via `POST /api/v1/agent-runs` | Ordered completed nodes | Automated; owner walkthrough pending |
| Inspect result | Requirements, citations, match, gaps, provider, correlation | Automated; owner walkthrough pending |
| Use absent skill evidence | Missing/uncertain, never candidate fact | Automated; owner walkthrough pending |
| Read run as another tenant | Safe 404 | Automated pass |
| Replay checkpoint/cancel | Stable replay / no later nodes | Automated pass |
| Compare fake/live routing | Fake available; live disabled without approval | Fake pass; live intentionally not run |

## 10. Requirements traceability

FR-004, FR-006, FR-007, FR-010; SEC-003/004/006/011; and
NFR-003/010/012/013 are mapped in requirements traceability to graph/API/evaluation
evidence. Production/durable aspects remain explicitly partial.

## 11. Example response

The response exposes `provider=fake-deterministic-v1`, ordered node events, untrusted
requirements, cited passages, deterministic match, three-way gaps, verification
status/citations, concise explanation, status, and correlation ID.

## 12. Known limitations, debt, and risks

- Runs/checkpoints/audit remain process-local and cannot resume after restart.
- The API currently completes synchronously; UI streaming/polling progress is Phase 14.
- Cancellation is cooperative for pre-cancelled/incomplete runs; synchronous requests
  cannot be cancelled concurrently through the local run store.
- Fake extraction and exact-term matching are educational baselines.
- Gemini adapter is compiled but not configured, called, or live-evaluated.

## 13. Rollback/recovery instructions

Revert the Phase 7 commit before Phase 8. No migration or external resource requires
rollback. A process restart clears all local graph runs/checkpoints.

## 14. Learning summary

This phase distinguishes graph state from application/workflow/session/memory/audit
state, delegation from handoff, retry from replay/resume, and agents from tools/A2A.

## 15. Owner acceptance checklist

- [ ] Start a synthetic analysis and inspect ordered progress.
- [ ] Open the cited evidence behind supported results.
- [ ] Confirm unsupported skills remain missing or uncertain.
- [ ] Inspect provider and correlation metadata.
- [ ] Confirm no live model, provider fallback, external action, or paid call occurred.

## 16. Proposed next phase

Phase 8 adds truthful resume/cover-letter drafts and durable human approval states.

## 17. Exact approval command

`APPROVE PHASE 7 AND START PHASE 8`
