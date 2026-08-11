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

## Mapping rules for future phases

Every implemented requirement row must add:

1. Concrete source or configuration path.
2. Automated test path and test name.
3. Manual evidence where applicable.
4. Migration and observability evidence where applicable.
5. Status transition from Accepted to Implemented and then Verified.

No requirement is considered verified merely because design documentation exists.
