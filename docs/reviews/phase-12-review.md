# Phase 12 Review: Temporal Durable Application Workflow

## 1. Phase objective

Deliver a crash-resilient, long-running, human-controlled Temporal workflow for synthetic
job-application preparation while preserving LangGraph, PostgreSQL, and activity ownership.

## 2. Delivered features

- Dedicated Temporal 1.30 worker package and versioned task queue.
- Analysis, research, draft, approval wait, tracking, and durable follow-up orchestration.
- Frozen opaque-reference contracts, status query, exact approval/cancel signals.
- Activity timeout/retry/heartbeat, stable idempotency, worker recovery, patch marker,
  reverse compensation, Temporal cancellation, time skipping, and history replay.
- Deterministic fake ledger that proves retry after a committed effect without duplication.

## 3. Explicitly not delivered

No Temporal Cloud/production server, authenticated production gateway, real database/model/
agent activity adapter, customer data, email, job submission, external notification,
Pub/Sub, Dapr, production deployment, paid resource, or Phase 13 behavior was delivered.

## 4. Files created/changed

The new `services/temporal-worker/` package, root workspace/lock/test marker, Temporal unit
and integration tests, Phase 12 plan, ADR-0024, state architecture, annotated source,
tutorial, exercises/answers, decision/learning/traceability/state/roadmap, dependency,
threat/privacy/risk documentation, and this review changed.

## 5. Architecture decisions

Temporal owns durable orchestration history, timers, retry, signals, queries, recovery and
compensation. PostgreSQL remains authoritative for business records; LangGraph owns a
bounded agent graph. Workflow code has no I/O or model authority. Activities own effects
through an idempotent port. A patch marker versions the follow-up command path.

## 6. Security/privacy review

Contracts allow only bounded opaque identifiers and typed profile/job/draft references in
history; personal prose, prompts, secrets and hidden reasoning are rejected. Approval binds
draft reference/version/actor and only advances preparation/tracking. Production must
authenticate/authorize starts and signals and verify PostgreSQL approval before signalling.
Namespace IAM, TLS, workload identity, retention/deletion, visibility, encryption,
regional placement, transfers and lawful basis require security/privacy and professional
legal review. No compliance certification is claimed.

## 7. Data/schema/migration impact

No PostgreSQL schema or migration changed. `temporalio` 1.30.0 (MIT), `nexus-rpc` 1.4.0,
and protobuf typing metadata entered the lock. Local workflow history lives only in the
ephemeral official test server; the fake activity ledger is process-local.

## 8. Automated commands and exact results

- Focused Temporal Ruff/MyPy/Pytest passed; 8 focused tests passed.
- Lock check and full Ruff passed; strict MyPy passed 116 source/test/script files.
- Full Pytest: 164 passed, 6 skipped, 4 upstream ADK deprecation warnings. Four skips need
  local PostgreSQL and two live-model tests lack explicit cost approval.
- Frontend Prettier, ESLint, TypeScript, five Vitest tests and Next.js build passed.
- Markdown lint passed 127 files; ten Mermaid diagrams rendered; governance validated 24
  required files, 74 requirement IDs and 135 Markdown files; pre-commit passed.
- Pip-audit and production/full npm audits found zero known vulnerabilities. Five local
  unpublished Python packages were expected pip-audit skips.
- Semgrep scanned 122 Python targets with three rules and zero findings; its macOS signal
  handler warning did not prevent exit 0. Detect-secrets passed.
- External link validation returned `Status: 0` for pre-existing external links because
  the checker could not reach them. Link success is not claimed.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Start/query workflow | Stops at exact approval with three prepared refs | Automated pass; owner pending |
| Stop and replace worker | New worker reconstructs and resumes from history | Automated pass; owner pending |
| Approve and advance one week | Tracking and follow-up complete via time skipping | Automated pass; owner pending |
| Fail after activity commit | Retry reuses effect; attempts equal two | Automated pass; owner pending |
| Reject or cancel | Reverse compensation then correct terminal result | Automated pass; owner pending |
| Replay completed history | No nondeterminism error | Automated pass; owner pending |

## 10. Requirements traceability

FR-012/013/020 and NFR-013 map to durable approval, application tracking, follow-up,
cancellation and compensation. NFR-002/003/009/010/011/016/020 map to versioned contracts,
free local tests, correlation references, activity policies, docs and disclosed warnings.

## 11. Example requests/responses

The client starts `ApplicationPreparationWorkflow.run` with opaque tenant, actor,
application, profile/job/draft and correlation references. The `status` query returns stage,
completed/compensated step names, approval decision and concise summary. The terminal
result adds the follow-up artifact reference but never career content.

## 12. Known limitations, debt, and risks

- Fake activities do not call the existing services or durable PostgreSQL records.
- A production gateway must authenticate, authorize and validate approval records.
- Compensation is semantic and cannot guarantee every future external effect is reversible.
- Local test-server recovery is not a production backup/multi-region exercise.
- Search attributes, codecs/encryption, history growth/continue-as-new, schedules, worker
  version deployment, production telemetry and SLO/load behavior remain open.
- External link validation must be rerun with reliable network access.

## 13. Rollback/recovery instructions

Before Phase 13, revert the eventual Phase 12 commit, remove the Temporal workspace member,
and restore `uv.lock`. No database/cloud rollback exists. The ephemeral test server and
fake ledger contain only synthetic disposable state.

## 14. Learning summary

Temporal makes orchestration durable by replaying deterministic history. Activities remain
at-least-once and require idempotency. Worker restart, workflow cancellation, retry, replay,
resume, compensation and fallback are distinct operations with different guarantees.

## 15. Owner acceptance checklist

- Inspect the workflow state ownership table and ADR-0024.
- Run/query, stop/restart, approve, time-skip and replay the synthetic workflow.
- Trigger retry-after-commit, rejection, signal cancellation and Temporal cancellation.
- Accept the local-only activity/gateway/deployment limitations.

## 16. Proposed next phase

Phase 13 will add versioned asynchronous events and notification foundations only after the
exact phase gate. It is not started.

## 17. Exact approval command

`APPROVE PHASE 12 AND START PHASE 13`
