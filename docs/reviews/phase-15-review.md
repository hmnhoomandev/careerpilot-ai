# Phase 15 Review: Observability, Evaluation, Routing, and Cost

## 1. Phase objective

Deliver an explainable, measurable and CHF-0-safe local platform foundation with content-free
telemetry, offline evaluation, explicit model routing and pre-execution cost controls.

## 2. Delivered features

- Versioned metadata-only telemetry across all planned operation kinds.
- Tenant-scoped bounded local collector with counts, p50/p95, errors, provider failures, tokens
  and estimated CHF cost; owner-only API and dashboard.
- Disabled Cloud/BigQuery/LangSmith exporter boundaries and proposed BigQuery metadata schema.
- Independent ADK `NO_CONTENT`, prompt-response upload/analytics and OpenAI trace export gates.
- Versioned prompt/model registries and capability/privacy/quality/latency/availability/cost route.
- CHF budget reservations, quotas, scoped cache policy and explicit no-fallback failures.
- Nine-family deterministic offline evaluation report and threshold gate.

## 3. Explicitly not delivered

No Cloud Trace/Logging, GCS, BigQuery, LangSmith, third-party SaaS, exporter traffic, credentials,
live model/LLM judge, managed ADK evaluation, dynamic model discovery, distributed quota/budget,
production alerts/SLO claims, database migration, cloud resource, deployment or paid call.

## 4. Files created/changed

Core platform controls/exports, API telemetry/contracts/composition/metrics route, ADK/OpenAI
configuration gates, web metrics card/client/test, permission and OpenAPI changes, synthetic
evaluation fixture/tests, Phase 15 plan, ADR-0027, architecture/BigQuery schema, annotated source,
tutorial/exercises, product/cost/security/privacy/risk/governance files and this review changed.

## 5. Architecture decisions

OpenTelemetry-compatible domain metadata stays vendor-neutral. Exporters receive only validated
events and are disabled. ADK completion upload is treated independently from trace capture. Routing
selects exactly one named route and returns one blocking reason; it never searches for fallback.
Default evaluation is deterministic and local; managed/model-judge paths require separate approval.

## 6. Security/privacy review

Telemetry rejects whitespace-rich content and bounds fields/attributes. Request paths are hashed;
dashboard queries are owner/tenant authorized. Prompts, responses, resumes, job/draft text, email,
secrets, exception details and hidden reasoning are absent. Production telemetry purpose, lawful
basis, region, processors, IAM, retention, sampling, data-subject rights and pseudonym rotation need
privacy/security and professional legal review. No compliance certification is claimed.

## 7. Data/schema/migration impact

No database migration or dependency changed. Telemetry, budgets and quotas are process-local. A
proposed content-free BigQuery JSON schema is documentation only and no dataset/table was created.
API version advanced to 0.15.0 with `/api/v1/platform/metrics`.

## 8. Automated commands and exact results

- Ruff format/lint passed; strict MyPy passed 128 source/test/script files.
- Focused platform/API/service/evaluation/access/OpenAPI suite passed 97 with four upstream ADK
  warnings; final hostile-path focused run passed 14.
- Full Pytest passed 202 with 6 expected skips and 4 ADK deprecation warnings. Four skips require
  local PostgreSQL; two live-model tests lack explicit data/cost approval.
- Frontend Prettier, ESLint, TypeScript, ten Vitest tests and Next.js build passed.
- Markdown lint passed 149 files; governance passed 24 required files, 74 requirement IDs and 157
  Markdown files; 13 Mermaid diagrams rendered; detect-secrets passed.
- Semgrep found zero findings across 134 tracked Python targets and a separate explicit scan of
  five new Python files; its macOS signal-handler warning did not prevent exit 0.
- Pip-audit and production/full npm audits found zero known vulnerabilities; pip-audit skipped five
  unpublished internal packages. No new dependency or lock change exists.
- External link validation was not rerun after repeated pre-existing network `Status: 0` results;
  no new external documentation links were added.
- The repository pre-commit suite passed after its `uv` cache was redirected to a writable temporary
  directory; the first attempt was blocked only by sandbox access to the global cache.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Correlated local journey | Request events share safe correlation metadata | Automated pass; owner pending |
| Metrics dashboard | Latency/outcome/cost shown; no content | Automated pass; owner pending |
| Paid/unavailable route | Explicit block and no fallback | Automated pass; owner pending |
| CHF 0/quota/cache | Spend blocked; quota visible; sensitive cache disabled | Automated pass; owner pending |
| Offline evaluation | All nine metrics meet versioned thresholds | Automated pass; owner pending |
| Export configuration | All external tiers disabled; ADK `NO_CONTENT` | Automated pass; owner pending |

## 10. Requirements traceability

NFR-002/010/011/014 map to the telemetry schema, correlation and local metrics. NFR-003/012/013
and MET-004/015–017 map to explicit routing, no fallback, budget/quota/cache and versioned offline
evaluation. Production targets remain design goals rather than achieved SLO claims.

## 11. Example requests/responses

An owner calls `GET /api/v1/platform/metrics` and receives schema version, event/error counts,
p50/p95 duration, token counts, estimated CHF cost, CHF 0 remaining budget, export status
`disabled_local_only` and content capture `NO_CONTENT`. No prompt or career text is returned.

## 12. Known limitations, debt, and risks

- Only authenticated HTTP requests emit the common event automatically; component-specific
  LangGraph/ADK/OpenAI telemetry has not yet migrated to this shared sink.
- Local memory is not durable/distributed and percentiles are exact small-sample calculations.
- Estimates are not invoices; price-versioning and provider reconciliation remain open.
- BigQuery schema/exporters are unprovisioned and production IAM/retention/load are untested.
- Offline aggregate fixture demonstrates gating mechanics, not live-agent quality or production SLOs.
- Metrics permission is owner-only; future organization observability roles need explicit design.

## 13. Rollback/recovery instructions

Before Phase 16, revert the eventual Phase 15 commit. No database/cloud rollback exists. Restarting
the API clears telemetry, budget and quota state. Restore the previous OpenAPI version with code.

## 14. Learning summary

Telemetry, evaluation, routing and spending answer different questions and require distinct policy.
Content capture controls can be independent. Explicit route failure is safer than helpful-looking
fallback, and budget reservation belongs before provider execution.

## 15. Owner acceptance checklist

- Run a synthetic journey and load the owner metrics dashboard.
- Inspect events/JSON for absence of career content and raw paths.
- Exercise routing privacy, quality, latency, outage, approval and zero-budget blocks.
- Run the offline evaluation and deliberately trigger a threshold miss.
- Review disabled exporter/ADK/OpenAI configuration and ADR-0027.

## 16. Proposed next phase

Phase 16 will harden security/privacy and add adversarial verification only after the exact phase
gate. It is not started.

## 17. Exact approval command

`APPROVE PHASE 15 AND START PHASE 16`
