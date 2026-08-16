# Project State

- **Project:** CareerPilot AI
- **Current phase:** Phase 20 — Production readiness, release candidate, and curriculum
- **Phase status:** Complete — awaiting owner review
- **Last updated:** 2026-08-16
- **Working tree at phase start:** Clean at `07b7858` on `main`
- **Production code:** Accepted through Phase 19; Phase 20 local release candidate awaits owner review
- **Cloud resources created:** None
- **Paid calls made:** None

## Binding owner decisions

- Individual job seekers are the first users; coaches and organizations are later.
- Launch baseline is Switzerland and the EU, with GDPR-oriented principles and
  Swiss FADP consideration; no claim of legal certification.
- English is the initial language; architecture must be internationalization-ready.
- Prefer Google Cloud `europe-west6` (Zurich); an EU fallback requires a recorded
  availability, residency, security, privacy, latency, and cost analysis.
- Environments are local, test/CI, staging, and production.
- Development and learning budget is CHF 0/month. Any cost requires explicit
  prior approval and a free/local alternative analysis.
- Identity uses an OIDC boundary, a local development adapter, and Google Identity
  Platform as the initial production reference.
- Gemini is the initial Google/LangGraph learning-path model; OpenAI remains in
  its bounded Agents SDK service; fakes are the default.
- Development uses synthetic personal data.
- User data supports access, correction, export, and deletion, with a default
  30-day recoverable deletion window subject to legal review.
- Job/company data begins with user input, approved APIs, and explicitly permitted
  sources; unrestricted scraping is forbidden.
- Initial availability design target is 99.5% monthly; no silent provider fallback.

## Current decisions

- Python 3.13 is the Phase 1 target runtime.
- Node.js 24 LTS is the Phase 1 target runtime.
- The production architecture is a modular core plus bounded specialist services,
  with event-driven integration where justified.
- Cloud Run is the first deployment target; GKE is a later reference.
- PostgreSQL/pgvector is authoritative production persistence.
- LangGraph and Temporal have separate graph and durable-process ownership.

## Phase 4 implementation state

- PostgreSQL 17/pgvector runs in the repository's local Docker profile.
- Alembic revision `0001` defines tenant-scoped profile, skills, experience,
  education, and evidence metadata tables.
- SQLAlchemy/Psycopg repository tests prove reconnect persistence, rollback,
  optimistic concurrency, and tenant isolation against real local PostgreSQL.
- Evidence intake is metadata-only and fail-closed in quarantine; no document bytes
  are persisted or sent to a scanner in this phase.

## Phase 5 implementation state

- Authenticated UTF-8 text and text-based PDF upload uses bounded validation,
  deterministic local scanning/parsing, opaque local storage, and injection labels.
- Alembic `0002` adds tenant-scoped documents/chunks, pgvector, generated English
  full-text vectors, and GIN/HNSW indexes.
- Both lexical and vector queries filter tenant, owner, active document, and index
  version before candidate ranking. Results are untrusted cited passages, not answers.
- Reindexing replaces derivatives; confirmed deletion removes local bytes and active
  chunks/vectors and soft-deletes provenance metadata.
- Versioned synthetic retrieval/injection fixtures gate recall@3, precision@3, MRR,
  grounding, citation correctness, prompt-injection labels, and empty results.

## Phase 5 verification evidence

- Python format/lint passed; strict MyPy passed for 51 source files.
- Full Pytest against real local PostgreSQL/pgvector: 101 passed, 0 skipped.
- Alembic upgrade/check: no new upgrade operations detected.
- Web Prettier, ESLint, TypeScript, 5 Vitest tests, and production build passed.
- Markdown lint: 82 files, 0 issues; external link check passed; 8 Mermaid
  diagrams rendered; governance validator passed with 89 Markdown files.
- Pip audit and both npm audits found no known vulnerabilities. Internal unpublished
  Python packages were the expected pip-audit skips.
- Semgrep local rules completed with exit 0; detect-secrets and all 5 pre-commit
  hooks passed.

## Phase 6 implementation state

- A registry describes nine narrow typed tools for profile lookup, cited retrieval,
  job ingestion, skill taxonomy, matching, evidence verification, pending approval,
  audit lookup, and deterministic cost estimation.
- One executor enforces strict input/output schemas, server-derived authorization,
  bounded timeout/retry, scoped idempotency, process-local rate limits, output
  sanitization, safe errors, and metadata-only audit decisions for HTTP and MCP.
- MCP exposes only four allowlisted read-only capabilities over the local stdio
  demonstration; high-risk, audit, matching, verification, and ingestion tools are
  absent from protocol discovery.
- The approval tool creates a pending request only and never performs the requested
  action. All tools are deterministic and make no model, cloud, or paid call.
- The application uses official MCP 1.28.1. Pinned Semgrep resolves separately through
  `uvx` because its CLI dependency graph contains vulnerable MCP 1.23.3; that isolated
  transitive package is absent from the application lock and runtime.

## Phase 6 verification evidence

- Python format/lint and strict MyPy passed for 60 source files.
- Default Pytest passed 105 tests with 3 PostgreSQL-marked skips; a separate full run
  against the real local PostgreSQL/pgvector container passed all 108 tests.
- The official in-memory MCP protocol smoke initialized, listed the exact four-tool
  allowlist, exchanged schemas, and invoked a read-only cost tool successfully.
- Web Prettier, ESLint, TypeScript, 5 Vitest tests, and production build passed.
- Markdown lint/link checks, 8 Mermaid renders, governance validation, Semgrep,
  detect-secrets, and pre-commit passed.
- Pip audit and both npm audits found no known vulnerabilities; the two unpublished
  internal Python packages were expected pip-audit skips.

## Known blockers and constraints

- Docker Desktop and the local PostgreSQL container must be running for marked
  integration tests; default tests remain offline.
- Global Node.js 26 differs from the repository target; Phase 1 verification used
  Node.js 24. Python verification used the selected Python 3.13 runtime.
- Google Cloud CLI cannot write its default config under the current sandbox.
- Final legal retention periods and regulatory interpretations require qualified
  professional legal review.
- No paid service may be used under the current CHF 0 budget.

## Phase 7 implementation and verification evidence

- A typed LangGraph coordinates Manager/Intake, Job Analysis, Retrieval, Match, Gap,
  Evidence, and Explanation roles with disjoint state ownership and ordered events.
- Deterministic-first routing, structured fake extraction, policy-enforced tools,
  citations, uncertainty, cancellation, retry, failure routing, and in-memory
  checkpoints are implemented. Gemini is disabled by default behind a fail-closed
  Google Gen AI adapter with no fallback.
- Default Pytest passed 113 tests with 3 PostgreSQL-marked skips; the complete suite
  against local PostgreSQL/pgvector passed all 116 tests.
- Ruff, strict MyPy (68 files), web format/lint/type, 5 Vitest tests, production build,
  docs/link/Mermaid, Semgrep (0 findings), detect-secrets, pre-commit, and governance
  validation passed. Python and npm audits found no known vulnerabilities.
- No live model, external personal-data transfer, cloud resource, or paid call occurred.

## Phase 8 implementation and verification evidence

- Immutable resume/cover-letter versions contain only cited supported claims; invented
  edits are blocked. Deterministic PII/bias gates and A2UI-compatible review messages
  are active.
- Approval supports pending, approved, edited-and-approved, rejected, more-information,
  expired, and cancelled states with exact version/hash/revision binding.
- Alembic `0003` and tenant-safe PostgreSQL persistence make draft/approval business
  records restart-safe; LangGraph interrupt proves pause/resume interaction semantics.
- Default Pytest passed 128 with 4 PostgreSQL skips; real PostgreSQL/pgvector passed all
  131 tests. Ruff, strict MyPy (82 files), and dependency audits passed.
- No model, external data transfer, cloud resource, external action, or paid call occurred.

## Phase 9 implementation and verification evidence

- An isolated Google ADK 2.5 specialist researches only supplied/approved company or job
  excerpts through a request-local tool and returns strict cited findings.
- Fake execution is the default. Gemini requires explicit configuration, per-request
  consent and transfer authorization, and separate cost approval; there is no fallback.
- ADK sessions, structured output, pre-model safety callback, citation validation,
  metadata telemetry, internal API identity, and stable provider errors are implemented.
- Default Pytest passed 136 with four PostgreSQL skips and one intentionally skipped live
  Gemini evaluation. Ruff and strict MyPy passed 91 source/test/script files.
- No model call, personal-data transfer, cloud resource, deployment, billing change, or
  paid operation occurred. ADK emits four upstream deprecation warnings during import.

## Phase 10 implementation and verification evidence

- An isolated OpenAI Agents SDK 0.8 laboratory defines manager, interviewer, feedback,
  direct handoff, agent-as-tool, structured output, approval tool, session, and safe trace
  configuration while using deterministic fake execution by default.
- Equivalent fixtures expose conversation/final-output ownership across all three modes.
- Input/output/tool guardrails, tenant-scoped sessions, exact-action approval pause/resume,
  internal API identity, redacted trace events, provider abstraction, and live budget/data
  gates are implemented. No provider fallback exists.
- Pytest passed 146 with four PostgreSQL and two live-provider skips. Ruff and strict
  MyPy passed 105 files; dependency, SAST, frontend, docs, hooks, and governance passed.
- No live model, data transfer, cloud resource, deployment, billing, or paid call occurred.

## Phase 11 implementation and verification evidence

- Official A2A SDK cards and tasks describe three versioned runtime capabilities behind a
  trusted registry and bounded fake adapter; no JSON-RPC service is exposed yet.
- Authenticated resource policy, tenant/actor task scoping, idempotency, cancellation,
  timeout/outage mapping, exact compatibility checks, and explicit no-fallback behavior
  are implemented.
- Python verification passed 156 tests with four PostgreSQL and two live-model skips;
  Ruff and strict MyPy passed 109 files. Frontend checks/build, Markdown lint, governance,
  pre-commit, secrets, and Semgrep (zero findings) passed.
- External link, npm advisory, and pip advisory checks were inconclusive because network
  access/review timed out. Mermaid rendering was blocked by a closed local browser process.
- No live model, external transfer, cloud resource, deployment, billing, or paid operation
  occurred.

## Phase 12 implementation and verification evidence

- A dedicated Temporal 1.30 worker coordinates analysis, research, drafts, exact approval,
  tracking, a durable follow-up timer, cancellation, and reverse compensation while all
  effects remain heartbeat-aware idempotent activities.
- Frozen validated contracts limit workflow history to opaque references. The official
  local time-skipping server proves signals, queries, week-long timers, worker replacement,
  retry after commit, cancellation, compensation, patching, and history replay.
- Full Python checks passed: Ruff, strict MyPy on 116 files, and 164 Pytest tests with four
  PostgreSQL and two explicitly unauthorized live-model skips. Four upstream ADK
  deprecation warnings remain.
- Frontend format/lint/type, five Vitest tests and build passed. Markdown lint, ten Mermaid
  renders, governance, pre-commit, secrets, Semgrep (zero findings), pip-audit and both npm
  audits passed. External link checking remained inconclusive with network `Status: 0` on
  pre-existing links.
- No live model, customer data, Temporal Cloud, cloud resource, deployment, billing, paid
  call, external communication, or submission occurred.

## Phase 13 implementation state

- A strict metadata-only version 1 event envelope, transaction-shaped outbox/inbox store,
  acknowledged dispatcher, aggregate ordering, bounded retry, digest-only poison quarantine,
  dead-letter and explicit replay behavior are implemented with local fakes.
- The injected Google Pub/Sub publisher/subscriber boundary creates no resources and assumes
  at-least-once delivery. Dapr is deferred by ADR-0025 for lack of demonstrated value.
- Authenticated tenant/actor-scoped in-app notification preferences, listing, and read
  receipts are available. No email, external send, live broker, or database migration exists.
- Lock/Ruff/strict MyPy passed; full Pytest passed 182 with six expected skips and four ADK
  deprecation warnings. Frontend checks/build, Markdown lint, governance, Mermaid rendering,
  and secret detection passed. Registry-dependent advisory/link checks were inconclusive
  because DNS was unavailable; Semgrep was blocked by its sandboxed uv tool cache.

## Phase 14 implementation and verification evidence

- The former long development preview is now a responsive dashboard with skip/navigation
  landmarks, overview metrics, profile/evidence, job and cited result views, workflow status,
  draft approval, interview/tracker states, notifications, audit and safe recovery messaging.
- A closed A2UI renderer accepts only the versioned draft/review components and allowed actions,
  escapes content as text, blocks unknown messages and leaves authorization to FastAPI.
- Frontend Prettier, ESLint, TypeScript, nine Vitest tests including two axe scans, and the
  Next.js build passed. Full Python regression passed 182 with six expected skips and four ADK
  deprecation warnings; Ruff and strict MyPy passed 123 source files.
- Markdown lint passed 141 files, governance passed 149 Markdown files/74 requirement IDs,
  12 Mermaid diagrams rendered, secret detection passed, Semgrep scanned 129 Python targets
  with zero findings, pip-audit found no known vulnerabilities (five internal packages skipped),
  and both production/full npm audits found zero vulnerabilities. External link checking stayed
  inconclusive for pre-existing links with network `Status: 0`.
- Applicable pre-commit hooks passed across all Phase 14 modified/untracked files; Python-only
  Ruff hooks had no matching file in that explicit file set and the complete Ruff gate passed.
- No live model, real personal data, cloud resource, deployment, billing, paid operation,
  external communication or automatic submission occurred.

## Phase 15 implementation and verification evidence

- `careerpilot.telemetry.v1` rejects content-like metadata and supports HTTP/workflow/graph/
  agent/tool/approval/retrieval/prompt/model kinds, version identifiers, durations, tokens and
  estimated CHF cost. A bounded collector provides tenant-scoped p50/p95/outcome/provider/cost.
- Authenticated owners can inspect a content-free local metrics API/UI. Request paths are hashed
  before telemetry. Cloud/BigQuery/LangSmith exporters, ADK prompt-response/analytics tiers and
  OpenAI trace export are fail-closed; ADK capture remains `NO_CONTENT`.
- Versioned prompt/model registries, explicit no-fallback route policy, CHF budget reservation,
  workflow quotas, privacy-aware tenant cache keys and a nine-metric offline evaluation gate exist.
- Full Pytest passed 202 with six expected skips and four ADK deprecation warnings. Focused Phase
  15 tests passed 97 before the final hostile-path test; frontend passed ten Vitest tests plus
  Prettier/ESLint/TypeScript/build; Ruff and strict MyPy passed 128 files.
- Markdown lint passed 148 files; governance passed 156 Markdown files/74 requirement IDs;
  13 Mermaid diagrams rendered; secrets passed. Semgrep found zero issues across 134 tracked
  Python targets and five new Phase 15 files. Pip/npm audits found no known vulnerabilities;
  pip-audit skipped five unpublished internal packages.
- No live/managed ADK evaluation, LLM judge, exporter, cloud analytics resource, personal-data
  transfer, model call, deployment, billing or paid operation occurred.

## Phase 16 implementation and verification evidence

- Owner-only inventory, consent/withdrawal, rights states, minimized portable export, step-up/exact
  approval contract and a 30-day recoverable deletion/cancel/purge-due lifecycle exist locally.
- Headers/no-store, identity rate control, path hashing, SSRF policy, active-PDF rejection,
  production config/KMS boundaries and tombstone-aware isolated backup restore are implemented.
- A nine-case corpus covers injection, exfiltration, tool/auth abuse, SSRF, malicious files,
  denial-of-wallet and a benign control.
- Full Pytest passed 227 with six expected skips/four ADK warnings. Ruff and strict MyPy (117 files),
  frontend checks/ten tests/build, three-probe DAST and 148-distribution license policy passed.
- Secrets passed; Semgrep scanned 144 Python files with zero findings; 13 Mermaid diagrams rendered;
  Markdown lint passed 159 files and governance passed 167 Markdown files/74 IDs.
- Registry-backed pip/npm advisory checks were inconclusive because DNS was unavailable. Container,
  SBOM and IaC scans are not applicable until Phase 17 and were not called passing.
- No real data, model, transfer/fetch, cloud KMS/WAF/scanner/backup, deployment, billing or paid API.

## Phase 17 implementation and verification evidence

- Hardened API/web images run as numeric non-root user 10001 with read-only roots, dropped
  capabilities, runtime health checks and no fixable High/Critical Trivy findings.
- Fresh local PostgreSQL ran Alembic migrations 0001–0003 before API startup. Default,
  specialist and durable Compose profiles reached healthy state using only synthetic data/fakes.
- OpenTofu 1.12.5 format/validate and synthetic test/staging/production plans passed; every plan
  contained 19 additions, no changes/destruction, and no cloud apply. Terraform Trivy was clean.
- Full Pytest passed 230 with six intentional skips and four ADK deprecation warnings; frontend
  format/lint/typecheck, ten tests and production build passed.
- No cloud resource, billing, paid/model call, external data transfer or real personal data was used.

## Phase 18 implementation and verification evidence

- A Kustomize base renders 21 Kubernetes 1.33 resources for restricted API/web workloads,
  separate Workload Identity placeholders, migration, HPA/PDB, probes and default-deny networks.
- Kubeconform strict schema validation accepted all 21 resources; four GKE policy tests and three
  Phase 17 deployment regression tests passed; Trivy found zero High/Critical misconfigurations.
- Full Pytest passed 234 with six expected skips/four ADK warnings; Ruff, strict MyPy (115 files),
  frontend format/lint/typecheck/ten tests/build, Semgrep (149 targets), secrets and hooks passed.
- Documentation lint/links, 13 Mermaid renders and governance validation passed. No application
  dependency, schema/migration, cloud/Kubernetes resource, customer data, model call or cost exists.

## Phase 19 implementation and verification evidence

- DBOS 2.22.0 and Restate SDK 1.0.3 live in independent projects and locks outside the root uv
  workspace. Temporal remains the only production durable-workflow dependency and route.
- Both labs implement the same opaque synthetic preparation effect and recover a single injected
  failure after commit with two attempts and one unique effect.
- DBOS uses a temporary local SQLite system database. Restate uses the official harness with a
  pinned local Restate 1.7.0 container. No cloud, model, personal data or paid operation is used.
- DBOS and Restate each passed Ruff, strict MyPy and two framework tests. Root Pytest passed 237
  with six intentional skips and four known ADK deprecation warnings; all five Temporal integration
  tests passed, including retry-after-commit recovery.
- Root Ruff and strict MyPy (144 files), frontend format/lint/typecheck/ten tests/build, Semgrep
  (156 targets), secrets, 148-distribution license policy, root/lab advisory checks and pre-commit
  passed. Markdown lint/links, 13 Mermaid renders and governance validation also passed.
- No application route/dependency/schema/migration, cloud resource, personal data, model call,
  billing or paid operation was introduced. Restate server BSL review remains an adoption gate.

## Phase 20 implementation state

- Release candidate `0.20.0-rc.1` has a scope-aware local readiness policy and explicit
  production `NO-GO` manifest. No artifact is published, deployed or claimed signed.
- The bounded harness measures 400 concurrent health requests, a 1,000-request soak, local
  restore isolation, visible provider outage/no fallback and CHF 0 behavior. Production targets
  remain missing by design and cannot pass from local evidence.
- SLO/error-budget, capacity/DR, support/on-call, release, user, operator, developer, API,
  architecture and curriculum documents are complete. Local gates passed; production remains
  `NO-GO` because staging/production evidence, signing, publishing and operational approval are absent.

## Phase 20 verification evidence

- The readiness harness passed 400 concurrent local health requests at 100% success and 35.188 ms
  p95, a 1,000-request soak at 100%, three isolated restore checks, explicit provider-outage
  visibility/no fallback and CHF 0 execution. The report correctly returned `no_go_production`.
- Full Pytest passed 244 tests with six intentional external PostgreSQL/live-provider skips and four
  known upstream ADK deprecation warnings. Disposable PostgreSQL migrations `0001`–`0003` and
  `alembic check` passed; DBOS and Docker-backed Restate labs each passed two tests.
- Ruff, strict MyPy (155 files), frontend format/lint/typecheck/10 tests/production build, DAST,
  red-team tests, Semgrep (161 targets, zero findings), secret detection, license policy, Python/npm
  audits and all pre-commit hooks passed.
- Markdown lint passed 199 files; external links passed, 13 Mermaid diagrams rendered, and governance
  validation passed 213 Markdown files and 74 requirement IDs. Local SBOM and unsigned provenance
  JSON were generated and parsed successfully.
- The Phase 20 ephemeral PostgreSQL container was removed and the existing repository PostgreSQL
  service was stopped without deleting its user-owned volume. No cloud, registry, model or paid call
  occurred.

## Next action

Review the terminal Phase 20 release-candidate evidence. Production promotion remains a separate,
explicitly authorized future decision; no later roadmap phase is approved.
