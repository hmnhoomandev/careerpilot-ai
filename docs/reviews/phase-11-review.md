# Phase 11 Review: A2A Interoperability and Agent Registry

## 1. Phase objective

Connect the existing LangGraph, Google ADK, and OpenAI Agents boundaries through
discoverable, versioned, policy-controlled capabilities and a local A2A task lifecycle.

## 2. Delivered features

- Official `a2a-sdk` Agent Cards and Tasks for three versioned capabilities.
- Trusted registry, compatibility checks, bounded remote adapter, and fake runtimes.
- Authenticated discovery/delegation/status/cancel application endpoints.
- Tenant/actor scoping, resource authorization, correlation, idempotency, timeout, outage,
  cancellation, safe errors, and explicit no-fallback behavior.

## 3. Explicitly not delivered

No public/production A2A JSON-RPC server or client, live remote runtime, dynamic registry,
OAuth/mTLS/workload identity, signed card, durable task storage, streaming, push, model
call, customer data, cloud deployment, Temporal/Pub/Sub, or Phase 12 work was delivered.

## 4. Files created/changed

The API dependency/lock, A2A contracts/registry/routes, unit/API/OpenAPI tests, ADR-0023,
architecture and annotated-source notes, tutorial/exercises, security records, phase plan,
traceability, roadmap, learning log, project state, and this review changed.

## 5. Architecture decisions

Cards advertise but never authorize. A static trusted registry validates protocol, card,
transport, and skill versions. Existing runtimes remain isolated behind a protocol-shaped
adapter. Phase 11 deliberately stops at a local application boundary; official network
server/client construction belongs with workload identity and deployment controls.

## 6. Security/privacy review

Every route requires a server-derived session and owned tenant resource. Task keys bind
tenant, actor, and ID; foreign lookup is non-enumerating. Inputs are strict and bounded,
correlation excludes payloads, and errors do not leak causes. Tests use synthetic data.
Remote credentials, card provenance, retention, lawful basis, residency/transfers, and
final deletion rules require security/privacy and professional legal review. No compliance
claim is made.

## 7. Data/schema/migration impact

No database schema or migration changed. `a2a-sdk` 0.3.26 and its locked transitive
packages were added. Tasks are process-local and disappear on restart.

## 8. Automated commands and exact results

- Focused Ruff/MyPy/Pytest: all passed; 10 focused tests passed.
- Full Ruff passed; strict MyPy passed 109 files.
- Full Pytest: 156 passed, 6 skipped, 4 upstream ADK deprecation warnings. Four skips need
  local PostgreSQL; two live-provider tests lack explicit cost approval.
- Frontend Prettier, ESLint, TypeScript, five Vitest tests, and Next.js build passed.
- Markdown lint passed 120 files; governance validated 24 required files, 74 requirement
  IDs, and 128 Markdown files; pre-commit and detect-secrets passed.
- Semgrep scanned 115 Python targets with three rules and zero findings; its macOS signal
  handler warning did not prevent successful completion.
- External-link validation returned network `Status: 0`; npm audit had DNS failure;
  pip-audit approval/network review timed out. No vulnerability result is claimed.
- Mermaid rendering failed because the local Puppeteer browser connection closed. The
  prior eight-diagram result is not claimed for this phase.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Discover registry | Three versioned secured cards | Automated pass; owner pending |
| Delegate each runtime | Correlated completed synthetic task | Automated pass; owner pending |
| Cancel submitted task | Explicit canceled terminal state | Automated pass; owner pending |
| Foreign/unauthorized access | 404/403 without enumeration | Automated pass; owner pending |
| Disable runtime | Explicit unavailable; no fallback | Automated pass; owner pending |

## 10. Requirements traceability

FR-004/013/015 and NFR-009 map to the three versioned capabilities and lifecycle.
SEC-001/003/006 and NFR-010/012 map to authorization, tenancy, correlation, bounded
failure, and no-fallback controls in the traceability matrix.

## 11. Example requests/responses

`GET /api/v1/a2a/agents` returns official card documents. `POST /api/v1/a2a/tasks`
accepts agent, versioned skill, safe task ID, bounded string payload, timeout, and optional
deferred execution. The response is an official Task document with correlation metadata.

## 12. Known limitations, debt, and risks

- Card URLs are future deployment descriptors and are not active JSON-RPC routes.
- In-process storage is neither durable nor horizontally consistent.
- Cancellation is cooperative and locally demonstrated before execution, not proven over
  a distributed running request.
- Production authentication, provenance/revocation, retention/deletion, rate limiting,
  SSRF controls, telemetry, load behavior, and audits remain open.
- Advisory and Mermaid checks must be rerun when network/browser tooling is available.

## 13. Rollback/recovery instructions

Before Phase 12, revert the eventual Phase 11 commit and restore the dependency lock. No
database or cloud rollback exists; restarting the API clears local tasks.

## 14. Learning summary

A2A interoperability needs four separate controls: advertised capability, registry trust,
caller/resource authorization, and explicit task lifecycle. Protocol metadata alone is
never an authorization decision.

## 15. Owner acceptance checklist

- Inspect the three cards and versioned skills.
- Exercise complete, cancel, conflict, timeout, outage, and tenant-denial cases.
- Review ADR-0023 and accept the local-only network/durability boundary.
- Rerun the three inconclusive environment-dependent checks when available.

## 16. Proposed next phase

Phase 12 is not started. Its scope must come from the governing roadmap and a fresh plan.

## 17. Exact approval command

`APPROVE PHASE 11 AND START PHASE 12`
