# Phase 2 Review

## 1. Phase objective

Prove one visible deterministic journey across the browser, HTTP API,
application service, and temporary repository without models, agents, cloud
resources, paid services, or real personal data.

## 2. Delivered behavior

- Create a minimal local profile from display name and professional summary.
- Submit a user-supplied job description through a second versioned endpoint.
- Return sorted exact shared terms with an explicit non-AI disclaimer.
- Display the result, safe errors, and correlation ID in an accessible web page.
- Publish liveness, readiness, and OpenAPI endpoints.
- Start the API and web processes together with `make dev`.

## 3. Architecture and contracts

ADR-0014 records the vertical-slice boundary. Core contains frozen values, the
repository protocol, and deterministic service. The FastAPI adapter contains
strict Pydantic contracts, an in-memory repository, the composition root, error
mapping, CORS, logging, and tracing hooks. The browser owns a typed HTTP client.

Endpoints introduced:

- `POST /api/v1/profiles`
- `POST /api/v1/analyses`
- `GET /health/live`
- `GET /health/ready`

There is no schema, migration, event, queue, provider, or external API.

## 4. Security and privacy review

Inputs are bounded at browser and API boundaries: display name 2–100, summary
20–1,000, and job description 50–5,000 characters. Unknown JSON fields are
rejected. The UI and fixtures instruct synthetic-data use. Local servers bind to
loopback, and CORS allows only the two documented local web origins.

Logs and spans exclude display names, summaries, job descriptions, response
content, and request bodies. They include operation metadata and opaque
correlation IDs. Validation, missing-profile, and unexpected errors return safe
envelopes without stack traces or submitted content. Authentication,
authorization, tenant isolation, and audit are intentionally not claimed; they
are Phase 3 gates before this slice can serve multiple users.

## 5. Observability and operational behavior

Middleware validates or creates a UUID correlation ID, exposes it as
`X-Correlation-ID`, includes it in analysis/errors, records request method/path/
status/duration in JSON logs, and adds safe attributes to an OpenTelemetry span.
The OpenTelemetry API uses its default no-op provider; no exporter or telemetry
service is configured. Liveness and readiness are separate even though readiness
has no external dependency yet.

## 6. Persistence, restart, and recovery

Profiles live in a lock-protected process dictionary. A restart creates an empty
repository, and an old profile ID returns a safe 404. An automated restart test
and the tutorial make this limitation explicit. Phase 4 owns PostgreSQL schema,
migrations, durability, deletion, backup, and restore behavior.

## 7. Dependencies and cost

Runtime adds Apache-2.0 OpenTelemetry API 1.37.0. That compatible line is required
by the single workspace lock because isolated Semgrep pins it below 1.38. Tests
add BSD-3-Clause `httpx2` 2.10.0 and MPL-2.0 `axe-core` 4.13.0. All audits pass.
Cloud/model spend is CHF 0; no billing or external resource was created.

## 8. Automated verification

| Gate | Exact result |
|---|---|
| uv lock check | 116 packages resolved; lock current |
| Ruff | 96 files format-clean; lint passed |
| strict MyPy | No issues in 27 source files |
| Pytest | 15 passed |
| OpenAPI contract | Four required paths and stable error schema passed |
| Vitest | 1 file, 3 tests passed |
| axe-core smoke | Initial page: 0 automatic violations; color contrast excluded in jsdom |
| Next.js production build | Passed; static `/` and `/_not-found` generated |
| pip-audit | No known vulnerabilities; two internal packages skipped as non-PyPI |
| npm audits | Web and documentation tools: 0 vulnerabilities |
| Semgrep | 3 rules on 27 Python targets; 0 findings |
| detect-secrets | Passed for tracked and untracked non-ignored files |
| markdownlint | 63 files; 0 issues before review creation |
| external links | Passed before review creation |

Semgrep again emitted its known macOS signal-handler warning but completed with
zero findings. npm kept the previously documented optional install scripts
disabled.

## 9. Real localhost verification

`make dev` started Uvicorn on `127.0.0.1:8000` and Next.js on `127.0.0.1:3000`.
Observed results:

- Web root: HTTP 200.
- Readiness: HTTP 200 with `{"status":"ready"}`.
- Profile creation: HTTP 201.
- Analysis: HTTP 201 with `accessible`, `data`, `engineer`, `python`, and
  `reliable`; response body and header used the same correlation ID.
- Invalid profile: HTTP 422 with `invalid_request`, field messages, and a
  correlation ID; no stack trace or submitted value.
- Control-C stopped both processes cleanly.

## 10. Failures encountered and corrections

- FastAPI could not resolve a dependency type declared inside the app factory
  under postponed annotations. Injection remains at the factory boundary, and
  route closures use that injected service.
- Starlette deprecated its `httpx` fallback. The supported `httpx2` package was
  selected after two unavailable version-range attempts; no failed range was
  retained.
- Unexpected exception responses bypassed normal middleware header injection.
  The handler now sets the correlation header directly, proven by a regression
  test.
- Vitest did not automatically clean the DOM between tests. Explicit cleanup now
  prevents cross-test elements.
- `next dev` generated two unrequested agent-guidance files. `agentRules: false`
  prevents regeneration, and only those generated files were removed.
- Next development rewrote generated route references; `next typegen` now runs
  before TypeScript so clean environments are reproducible.

## 11. Manual owner checklist

| Check | Actual result |
|---|---|
| Start both services with one command | Pass in terminal verification |
| Submit synthetic inputs through API boundaries | Pass via localhost requests |
| See deterministic result and correlation ID | Pass in response; browser owner check pending |
| Trigger understandable invalid input | Pass via localhost request; browser owner check pending |
| Stop/restart and understand data loss | Pass in automated restart test; owner walkthrough pending |

The pending items are visual/browser confirmation by the owner, not skipped
backend or frontend automation.

## 12. Traceability and learning

Traceability maps FR-001, FR-003, FR-004, NFR-002, NFR-010, NFR-011, NFR-017,
SEC-009, and SEC-014 to source and tests with partial-status caveats. The tutorial,
annotated source, exercises, and answers explain dependency inversion,
determinism, validation, telemetry minimization, accessibility, and restart loss.

## 13. Known limitations and debt

- This is exact-term overlap, not evidence-grounded fit or skill analysis.
- State is process-local and unsuitable for production.
- No identity, authorization, tenant isolation, or audit exists yet.
- Browser client and Python end-to-end tests form composite vertical evidence;
  a real-browser network automation framework is deferred until the UI expands.
- Axe cannot evaluate real rendered color contrast in jsdom; manual visual and
  later browser accessibility testing remain required.
- Hosted CI evidence begins after a push; local equivalents pass.

## 14. Rollback

No external state exists. Before acceptance, rollback affects only uncommitted
Phase 2 repository changes. Preserve any desired review copy, identify exact
Phase 2 paths with Git, and obtain owner confirmation before destructive removal.

## 15. Owner acceptance checklist

- [ ] The deterministic result is clearly distinguished from AI/fit analysis.
- [ ] API, application, port, adapter, and UI boundaries are understandable.
- [ ] Input bounds, safe errors, and telemetry minimization are adequate.
- [ ] In-memory restart loss and Phase 4 persistence ownership are accepted.
- [ ] Phase 3 identity/tenancy/authorization/audit scope is accepted.

## 16. Proposed next phase

Phase 3 — Identity, tenancy, authorization, and audit. It will add the safe local
authentication adapter, OIDC boundary, tenant context, deny-by-default policy,
RBAC/ABAC, and audit evidence before broader data access.

## 17. Exact approval command

`APPROVE PHASE 2 AND START PHASE 3`
