# Phase 08 Review: Truthful Drafts and Human Approval

## 1. Phase objective

Deliver evidence-grounded versioned resume and cover-letter drafts controlled by an
exact-version, restart-safe human-review gate.

## 2. Delivered features

- Resume Tailoring, Cover Letter, Privacy/PII, Bias/Compliance, Approval Coordinator.
- Claim-to-evidence model with citations and unsupported-edit blocking.
- Immutable draft versions, SHA-256 content hash, structured sections, PII/policy flags.
- Seven approval statuses and five human decisions under optimistic concurrency.
- PostgreSQL restart-safe draft/approval records and LangGraph interrupt/Command demo.
- Strict API v0.8 plus allowlisted A2UI-compatible draft/review messages.

## 3. Explicitly not delivered

No model call, PDF/export styling, external sharing/email/submission, profile mutation,
Temporal expiry timer, remote agent, cloud deployment, legal certification, or paid
service. PostgreSQL LangGraph checkpointer deployment is documented but not installed;
authoritative business records are restart-safe, while default graph checkpoints remain
in memory.

## 4. Files created/changed

Core drafting domain, SQL tables/repository/service, approval graph, API contracts/routes,
Alembic `0003`, unit/API/e2e/PostgreSQL tests and corpus, ADR-0020, dossiers, tutorial,
annotated source, exercises, security/privacy, traceability, roadmap, and project state.

## 5. Architecture decisions

ADR-0020 separates draft generation from approval authority, binds decisions to exact
content, uses PostgreSQL for business durability, LangGraph interrupt for interaction,
and leaves durable timers to Temporal.

## 6. Security/privacy review

Tenant/actor predicates guard repositories; stale/racing decisions fail atomically;
terminal states close; audit is metadata-only; source text and A2UI remain data; no
approval executes an action. Draft encryption/KMS, staff access, retention/deletion,
backup propagation, lawful basis, consent, and legal interpretation remain professional
review items. No compliance certification is claimed.

## 7. Data/schema/migration impact

Alembic `0003` creates `career_draft_versions` and `draft_approvals`, with composite
draft/version FK, tenant uniqueness, positive version/revision checks, and cascading
profile-linked deletion. Downgrade is limited to disposable local/test recovery.

## 8. Automated commands and exact results

- Ruff passed; strict MyPy passed for 76 source and test files.
- Default Pytest: 128 passed, 4 PostgreSQL-only skips.
- Real local PostgreSQL/pgvector: 131 passed, 0 skipped.
- Pip audit and production/full npm audits: 0 known vulnerabilities; two unpublished
  internal Python packages were expected skips.
- Web format/lint/type, 5 tests, and production build passed. Markdown lint/link and
  Mermaid checks passed. Semgrep scanned 82 Python targets with 0 findings;
  detect-secrets, all pre-commit hooks, and governance validation passed.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Generate resume and letter | Structured cited claims | Automated; owner pending |
| Open every claim citation | Document/chunk/page/offsets present | Automated pass |
| Invent a date/metric/employer | Safe 422 block | Automated pass on versioned corpus |
| Edit supported content | New version/hash and pending approval | Automated pass |
| Approve/reject/more-info/cancel/expire | Valid deterministic transitions | Automated pass |
| Use stale/concurrent decision | 409/conflict | Automated pass |
| Restart pending approval | PostgreSQL record resumes decision | Automated pass |

## 10. Requirements traceability

FR-008/009/011/012/020 plus SEC-003/006/007/009 are linked to source, migration,
API, state-machine, corpus, and PostgreSQL evidence in requirements traceability.

## 11. Example requests/responses

`POST /api/v1/drafts` returns version/hash, cited claims, flags, pending approval, and
two allowlisted A2UI messages. `POST /api/v1/approvals/{id}/decisions` requires the
expected revision, draft version, and hash.

## 12. Known limitations, debt, and risks

- Draft prose is a deterministic evidence transformation, not production-quality model
  writing. Supported edits are deliberately restrictive.
- LangGraph checkpoint is in-memory by default; PostgreSQL business records reconcile
  restart-safe approval, but persistent graph checkpoint wiring remains deployment work.
- Expiry transition exists, but Temporal scheduling is Phase 12.
- PII/bias regexes are baseline controls, not comprehensive classifiers/legal review.

## 13. Rollback/recovery instructions

Before Phase 9, revert the Phase 8 commit. On disposable local/test databases, downgrade
from `0003` to `0002`; this deletes drafts/approvals and must never run against production
without a reviewed recovery/export plan.

## 14. Learning summary

Claim graphs, immutable versions, hash/revision binding, deterministic approval state,
interrupt versus business persistence, and A2UI data/authority separation were taught.

## 15. Owner acceptance checklist

- [ ] Generate both draft types and inspect citations.
- [ ] Confirm an invented claim is blocked.
- [ ] Edit and approve exact current content.
- [ ] Reject/request information on another draft and inspect feedback.
- [ ] Restart with PostgreSQL and complete a pending approval.
- [ ] Confirm no external action or paid/model call occurred.

## 16. Proposed next phase

Phase 9 creates the isolated Google ADK/Gemini specialist service.

## 17. Exact approval command

`APPROVE PHASE 8 AND START PHASE 9`
