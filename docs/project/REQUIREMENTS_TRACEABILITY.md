# Requirements Traceability

## Phase 0 design traceability

| Requirement group | Design evidence | Implementation | Test evidence | Status |
|---|---|---|---|---|
| FR-001–FR-024 | Product vision, journeys, domain model, architecture, ADRs | Deferred to assigned phases | Phase 0 validator confirms IDs | Accepted/design only |
| SEC-001–SEC-022 | Threat model, privacy assessment, architecture, ADRs | Deferred to assigned phases | Phase 0 validator confirms IDs | Accepted/design only |
| NFR-001–NFR-020 | Metrics, architecture, cost assumptions, ADRs | Deferred to assigned phases | Phase 0 validator confirms IDs | Accepted/design only |
| LEG-001–LEG-008 | Privacy assessment and legal-review register | Professional review deferred | Manual review | Flagged |
| NFR-003–NFR-007 | Cost/runtime policy, ADR-0011/0013, version files, lockfiles | `.python-version`, `.node-version`, `pyproject.toml`, npm manifests | lock checks, dependency audits | Implemented in Phase 1 |
| NFR-009–NFR-012 | CI, contracts foundation, telemetry/model-test boundaries | CI and offline test markers/fake-first structure | Pytest, Vitest, CI config tests | Partially implemented |
| NFR-015–NFR-018 | Environment structure, documentation quality, i18n-ready UI shell, architecture boundary | workspace, VS Code, web shell, AST boundary test | Ruff, MyPy, Pytest, ESLint, TypeScript, build | Implemented in Phase 1 |
| SEC-006/SEC-014/SEC-019 | Secret boundary, synthetic/offline default, dependency/security scanning | `.env.example`, secret baseline, SAST/SCA/CI configs | detect-secrets, pip-audit, npm audit, Semgrep | Implemented foundation |
| FR-001 | Minimal local profile creation design | Core profile model/service, versioned profile endpoint, Phase 2 UI | Unit, API, UI, and end-to-end tests | Partially implemented; durable evidence profile deferred to Phase 4 |
| FR-001 | Phase 4 profile aggregate and persistence ADR | Versioned profile, skills, experience, education; PostgreSQL adapter and UI editing | Service/API/UI and real PostgreSQL reconnect/concurrency tests | Implemented for Phase 4 scope |
| FR-002 | Evidence lifecycle and quarantine design | Evidence metadata model, allowlist validation, quarantine state, API/UI flow | Validation, malicious filename, API/UI, and PostgreSQL tests | Implemented as metadata-only foundation; bytes/scanning deferred |
| SEC-008 | Threat model and ADR-0016 | Size/type/extension/name validation, quarantine, scanner port | Parameterized upload-policy and API tests | Partially implemented; real scanner and byte validation deferred |
| NFR-019 | ADR-0016 and Phase 4 plan | Alembic `0001`, explicit transaction boundary, optimistic version predicate | Offline SQL render plus real upgrade/downgrade/reconnect/rollback test | Implemented for initial schema |
| FR-003 | User-supplied job-description input | Strict analysis request and accessible UI field | API invalid-input, UI, and end-to-end tests | Implemented for synthetic Phase 2 slice |
| FR-004 | Structured job analysis design | Deterministic exact-term result only | Service and end-to-end assertions | Placeholder foundation; extraction/RAG deferred to Phases 5–7 |
| NFR-002 | Correlatable API/error measurement foundation | Correlation middleware and duration metadata | API header/body and log tests | Partially implemented; production metrics/SLOs deferred to Phase 15 |
| NFR-010 | OpenTelemetry correlation foundation | OTel API span plus response/log correlation IDs | API and end-to-end correlation assertions | Partially implemented; exporter disabled |
| NFR-011 | Logs, traces, errors, and runbook impact for new behavior | Metadata-only JSON logs, safe errors, health paths, tutorial | Observability unit and API tests | Implemented for Phase 2 behavior |
| NFR-017 | Accessible English-first UI behavior | Labeled bounded inputs, focus styles, live result/error region | Testing Library and axe-core smoke test | Implemented for Phase 2 page |
| SEC-009/SEC-014 | PII-safe telemetry and synthetic development data | Allow-listed log fields, no request bodies/spans, synthetic fixtures | Formatter exclusion and journey tests | Implemented Phase 2 foundation |
| SEC-001 | OIDC/provider abstraction and safe local development adapter | `IdentityVerifier`, `ExternalIdentity`, `InMemoryIdentityAccess` | Local environment gate and context tests | Implemented boundary; live production adapter deferred |
| SEC-002 | Deny-default RBAC plus contextual ABAC | `Role`, `Permission`, `AccessPolicy`, resource attributes | Exhaustive permission matrix and ABAC tests | Verified Phase 3 foundation |
| SEC-003/SEC-004 | Tenant isolation at activated API/service/repository boundaries; document/tool policy foundation | Auth middleware, authorized service, tenant repository, fail-closed permissions | Forgery, cross-tenant, same-tenant IDOR, repository, document/tool tests | Verified for active Phase 3 boundaries |
| SEC-005 | Auditable security success/denial and tamper-evident design | Frozen audit events, SHA-256 chain, authorized tenant viewer | Completeness, filtering, role, denial, last-owner, integrity tests | Implemented temporary foundation; durable/signed audit deferred |
| NFR-009/NFR-011 | Versioned identity/audit/error contracts and operational evidence | API v0.3, 401/403/404/409 envelopes, correlation/audit actions | OpenAPI and API contract tests | Implemented for Phase 3 APIs |
| FR-002/FR-005 | ADR-0017 and secure ingestion design | Bounded text/PDF storage, chunks, vectors, cited passages, reindex/delete API and UI | Document API, processing, evaluation, and PostgreSQL tests | Verified for Phase 5 local scope |
| SEC-003/SEC-004 | Retrieval data-boundary invariant | Tenant/owner/active/index predicates inside full-text and vector SQL | Cross-tenant pgvector integration and foreign-profile API tests | Verified for activated retrieval boundary |
| SEC-008/SEC-010 | Upload, parser, and injection controls | Bounded validation/scanning plus visible `UNTRUSTED` labels | Rejection tests and versioned injection corpus | Baseline verified; production scanner/sandbox deferred |
| NFR-013/NFR-019 | Evaluated, migrated retrieval | Versioned quality fixture and Alembic `0002` with GIN/HNSW indexes | Metrics gate, offline SQL, real migration/pgvector test | Verified locally |
| SEC-003/SEC-004/SEC-011 | ADR-0018 tool boundary | Registry/executor authorization, strict schemas, timeout/retry, idempotency, rate limits, sanitization, safe errors, audit | All-tool API tests plus denial, timeout, duplicate, rate, and sanitization tests | Implemented for local Phase 6 scope |
| SEC-017 | Tool abuse and denial-of-wallet design | Per-tenant/actor/tool local window plus bounded payload/timeout/retries | Rate-limit and exhausted-timeout tests | Local baseline; distributed enforcement deferred |
| NFR-009 | Versioned capability contracts and MCP allowlist | API v0.6 discovery/invoke schemas and official MCP v1 server | OpenAPI plus in-memory MCP protocol discovery/call tests | Verified Phase 6 contract boundary |
| FR-020 | Human approval before consequential action | `approval.request` creates pending metadata and executes nothing | Idempotent replay/conflict and catalog tests | Foundation only; durable approval lifecycle is Phase 8 |
| FR-004/FR-006/FR-007/FR-010 | ADR-0019 and Phase 7 graph | Typed analysis graph, structured requirements, cited match/gaps/verification/explanation | Graph API/unit, grounding, path, state, checkpoint tests | Verified for fake-first local scope |
| SEC-003/SEC-004/SEC-006/SEC-011 | Tenant-safe graph/provider boundary | Server context, scoped run IDs, untrusted source labels, deterministic citations | Cross-tenant API, strict output, injection/grounding tests | Verified Phase 7 local boundary |
| NFR-003/NFR-010/NFR-012/NFR-013 | Fake-first cost, correlation, opt-in live, retry/resume semantics | Fake default, provider identity, node events/checkpointer, live marker | API progress/correlation, retry/cancel/replay tests | Verified locally; durable recovery deferred |
| FR-008/FR-009 | ADR-0020 evidence-linked versioned drafts | Claim/citation graph, immutable resume/letter versions, blocked edits | Draft API, invented-claim, citation tests | Verified deterministic Phase 8 scope |
| FR-011/FR-012/FR-020 | Exact-version approval state machine | PostgreSQL records, version/hash/revision binding, LangGraph interrupt, A2UI messages | Transition, stale/concurrent, restart/resume, protocol tests | Verified locally with PostgreSQL |
| SEC-003/SEC-006/SEC-007/SEC-009 | Draft privacy/truth/tenant controls | Tenant repository predicates, PII/bias gates, metadata audit | Cross-tenant, PII/policy, audit, PostgreSQL tests | Phase 8 baseline verified; legal review open |
| FR-013/FR-014 | ADR-0021 bounded company/job research | Isolated ADK agent, approved-source tool, structured cited result | ADK unit/API contract/citation tests | Verified for supplied-source fake-first scope |
| SEC-003/SEC-006/SEC-010/SEC-011 | ADK service and model boundary | Service identity, scoped sessions, safety callback, consent/transfer gate, no fallback | Injection, cross-tenant, disabled/live-denial tests | Phase 9 local baseline verified |
| NFR-003/NFR-009/NFR-010/NFR-012 | Cost-safe specialist reliability | Fake default, stable timeout/quota/outage errors, metadata metrics, opt-in live marker | Failure injection, OpenAPI, live skip tests | Verified locally; production telemetry/deployment deferred |
| FR-015/FR-016 | ADR-0022 interview simulation and feedback | SDK manager/interviewer/feedback agents and equivalent orchestration modes | Handoff/agent-tool/manager comparison tests | Verified for synthetic fake-first scope |
| FR-020/SEC-011 | Human-gated feedback action | SDK approval tool plus serialized exact-action state/revision | Approval approve/reject/resume/stale/hash tests | Verified locally; no publication side effect exists |
| SEC-006/SEC-009/NFR-003/NFR-010/NFR-012 | OpenAI provider, privacy, cost, and observability boundary | Fake default, deterministic guards, redacted traces, live budget/transfer gate | Guardrail/session/trace/budget/live-skip tests | Phase 10 local baseline verified |
| FR-004/FR-013/FR-015/NFR-009 | ADR-0023 A2A capability interoperability | Official versioned cards/tasks, trusted registry, three runtime adapters | Card, compatibility, lifecycle, API contract tests | Verified for local fake-first Phase 11 scope |
| SEC-001/SEC-003/SEC-006/NFR-010/NFR-012 | Tenant-safe delegated task control | Authenticated resource policy, scoped IDs, correlation, timeout/cancel/error mapping, no fallback | Unauthorized, foreign tenant, duplicate, timeout, outage tests | Verified locally; production transport deferred |
| FR-012/FR-013/FR-020/NFR-013 | ADR-0024 durable application preparation | Temporal workflow, exact approval signal, tracking/follow-up activities, cancellation and reverse compensation | Time-skipping, restart, signal/query, cancellation, compensation and replay tests | Verified with local Temporal test server; production adapters deferred |
| NFR-002/NFR-003/NFR-009/NFR-010/NFR-011/NFR-016/NFR-020 | Versioned cost-free durable execution boundary | Opaque history contracts, versioned task queue/patch, activity timeout/retry/heartbeat/idempotency, fake ledger | Contract, heartbeat, retry-after-commit, MyPy and complete regression gates | Phase 12 local baseline verified |

## Mapping rules for future phases

Every implemented requirement row must add:

1. Concrete source or configuration path.
2. Automated test path and test name.
3. Manual evidence where applicable.
4. Migration and observability evidence where applicable.
5. Status transition from Accepted to Implemented and then Verified.

No requirement is considered verified merely because design documentation exists.
