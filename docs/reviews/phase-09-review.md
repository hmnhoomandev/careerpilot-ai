# Phase 9 Review: Bounded Google ADK/Gemini Specialist

## 1. Phase objective

Deliver an isolated, independently testable Google ADK specialist for cited company/job
research over supplied approved sources, with local fake execution by default.

## 2. Delivered features

- Official ADK `Agent`, `App`, `Runner`, in-memory session, request-local function tool,
  structured output, safety callback, and configurable Gemini model.
- Narrow internal HTTP contract and explicit disabled-service degradation.
- Consent/transfer gate, no fallback, one provider attempt, timeout, quota, malformed
  output, outage, injection, citation, and tenant-session isolation controls.
- Metadata-only telemetry and an opt-in synthetic Gemini evaluation.

## 3. Explicitly not delivered

No open web search/scraping, customer data, live model call, A2A, deployment, CI/CD,
cloud resource, durable production session, billing change, or Phase 10 feature exists.

## 4. Files created/changed

The new `services/google-adk/` workspace contains its manifest/spec, package, agent,
provider, safety, session/service, API, telemetry, and eval fixture. Root tests cover unit,
contract, failures, and live opt-in behavior. ADR-0021, annotated source, tutorial,
exercises, security/privacy, traceability, state, roadmap, plan, and locks were updated.

## 5. Architecture decisions

LangGraph remains the primary application graph. ADK owns only supplied-source research
inside its specialist package; neither ADK nor Gemini imports enter the domain. The fake
provider is default. Gemini is explicit, receives one attempt, and cannot fall back.
OpenTelemetry API moved to 1.42.1 because ADK 2.5 requires it; no exporter is enabled.

## 6. Security/privacy review

The source tool is request-local, unknown IDs are denied, and citations must match the
request allowlist. Source text is scanned before execution and by an ADK callback. Content
is absent from telemetry. The service header is development-only; workload identity/mTLS,
encryption, retention, legal basis, provider terms, region, and data-subject handling need
review before customer-data use. No compliance claim is made.

## 7. Data/schema/migration impact

No database or migration changed. ADK sessions and metrics are process-local and not
production durable. The uv workspace/lock gained Google ADK 2.5.0 and its transitive
dependencies; OpenTelemetry API changed from 1.37.0 to 1.42.1.

## 8. Automated commands and exact results

- Ruff passed; strict MyPy passed for 91 source/test/script files.
- Pytest: 136 passed, four PostgreSQL and one live Gemini test skipped.
- Focused ADK/service suite: 8 passed, live evaluation skipped.
- Pip-audit and production/full npm audits: zero known vulnerabilities; three internal
  workspace packages were expected pip-audit skips.
- Semgrep: 97 Python targets, three rules, zero findings. Its macOS signal warning did
  not prevent success. Detect-secrets passed.
- Markdown lint (108 files), external links, eight Mermaid diagrams, pre-commit, and
  governance validation passed.
- Frontend format/lint/typecheck, five Vitest tests, and production build passed.
- `agents-cli info` recognized deployment `none` and Zurich `europe-west6`; its optional
  npm skill-list query timed out without affecting validation.

ADK emitted four upstream `BaseAgentConfig` deprecation warnings during tests. PostgreSQL
was not rerun because the environment variable was unset and Phase 9 changes no schema.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Run synthetic fake fixture | Structured cited output, no network | Automated pass; owner pending |
| Inspect every source ID | Only supplied IDs occur | Automated pass; owner pending |
| Disable specialist | Explicit `specialist_unavailable` | Automated pass; owner pending |
| Run live Gemini fixture | Same schema/citation contract | Not authorized; intentionally skipped |
| Read ADK/LangGraph tutorial | Ownership difference is clear | Owner pending |

## 10. Requirements traceability

FR-013/014 map to the specialist and cited results. SEC-003/006/010/011 map to service
identity, scoped sessions, safety and transfer policy. NFR-003/009/010/012 map to fake
cost control, contracts, telemetry, and stable failure tests. Exact paths are recorded in
`docs/project/REQUIREMENTS_TRACEABILITY.md`.

## 11. Example request/response

Send `POST /v1/research` with `X-CareerPilot-Service: careerpilot-main-api`, scoped IDs, a
question, and `sources[{source_id,title,content}]`. The fake response contains `summary`,
`findings[{statement,source_ids}]`, and `questions_to_verify`; it contains no hidden
reasoning or external action.

## 12. Known limitations, debt, and risks

- Static internal identity is not production authentication.
- Process-local sessions do not survive restart or coordinate replicas.
- Pattern detection is not a complete prompt-injection defense.
- Provider error classification is bounded until ADK exposes a stable taxonomy.
- ADK emits an upstream deprecation warning; monitor the pinned release line.
- Legal/privacy review and live provider evaluation remain outstanding.

## 13. Rollback/recovery instructions

Before Phase 10, revert the Phase 9 commit. Remove the service workspace member and restore
the previous OpenTelemetry constraint/lock. There is no database or cloud rollback.

## 14. Learning summary

The phase demonstrates ADK agent/tool/session/callback/schema concepts while preserving
LangGraph ownership, deterministic authority, provider isolation, fake-first testing, and
post-model evidence validation.

## 15. Owner acceptance checklist

- Inspect the fake result and each citation.
- Observe disabled-service degradation.
- Review ADR-0021 and the comparison tutorial.
- Confirm the live evaluation remains separately gated.
- Accept the documented production and legal gaps.

## 16. Proposed next phase

Phase 10 is the isolated OpenAI Agents SDK service and handoff laboratory. It is not
started or implicitly approved by this review.

## 17. Exact approval command

`APPROVE PHASE 9 AND START PHASE 10`
