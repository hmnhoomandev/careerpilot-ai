# Risk Register

Scale: likelihood and impact are Low, Medium, High, or Critical. Owners are roles,
not named individuals.

| ID | Risk | Likelihood | Impact | Mitigation / trigger | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-001 | Fabricated candidate claim harms trust or opportunity | High | Critical | Claim-evidence enforcement and adversarial evals before drafting release | AI/QA | Open |
| RSK-002 | Cross-tenant disclosure | Medium | Critical | Deny default, tenant queries, IDOR/retrieval/tool tests | Security | Open |
| RSK-003 | Sensitive data leaks through telemetry/provider | Medium | Critical | Synthetic data, minimization, redaction, content-off tracing | Privacy/Platform | Open |
| RSK-004 | Scope across 21 phases becomes unmaintainable | High | High | Phase gates, vertical slices, explicit exclusions, modular core | Product/Architecture | Mitigated |
| RSK-005 | Development authentication is mistaken for production security | Medium | Critical | Local-only construction gate, synthetic UI warning, no password/provider emulation, production OIDC port | Security | Mitigated locally; production open |
| RSK-006 | In-memory audit chain is rewritten by a privileged process | Medium | High | Frozen values, hash integrity checks; durable restricted store and signing/anchoring review later | Security/Legal | Open |
| RSK-005 | CHF 0 blocks managed-service/live-model verification | High | Medium | Fakes/emulators; stop and present cost proposal when unavoidable | Owner/Platform | Accepted constraint |
| RSK-006 | Zurich lacks a required service/feature | Medium | High | Service-by-service check and documented EU exception | Platform/Privacy | Open |
| RSK-007 | Framework/API churn breaks planned integration | High | Medium | Pin versions, adapters, phase-time doc verification, contract tests | Architecture | Open |
| RSK-008 | Python/Node runtime mismatch blocks setup | High | Medium | Enforce Python 3.13, Node 24 LTS; document version setup | Developer Experience | Open for Phase 1 |
| RSK-009 | Docker Compose unavailable locally | Certain | Medium | Diagnose and remediate/document in Phase 1 | Developer Experience | Open for Phase 1 |
| RSK-010 | In-process PDF parsing exhausts resources | Medium | High | Current strict limits; production parser isolation/time limits | Security | Reduced, open |
| RSK-011 | Local scanner misses malicious content | High | High | No antivirus claim; production scanner required before deployment | Security | Open |
| RSK-012 | Hash-vector collisions reduce precision | Medium | Medium | Similarity floor, lexical search, metrics; versioned provider replacement | Retrieval | Accepted locally |
| RSK-013 | Tool registry exposes a privileged capability | Medium | Critical | Deny-default lookup, permissions, MCP equality allowlist, discovery tests | Security | Reduced, open |
| RSK-014 | Process-local quotas/idempotency diverge across replicas | Certain in scale-out | High | Local-only label; durable/distributed store required before production | Platform | Open |
| RSK-015 | MCP SDK/Pydantic compatibility warning or protocol drift | Medium | Medium | Exact pin, asserted warning, protocol smoke test, upgrade review trigger | Platform | Accepted temporarily |
| RSK-010 | Prompt injection causes tool abuse or exfiltration | High | Critical | Untrusted labels, tool policy, allowlists, injection corpus | Security/AI | Open |
| RSK-011 | Bias or profiling causes discriminatory guidance | Medium | High | No employer ranking, limitation notices, evals, human review, legal review | Compliance/AI | Open |
| RSK-012 | Deletion fails to remove derived data | Medium | Critical | Source-linked lifecycle, deletion jobs, propagation tests | Privacy/Data | Open |
| RSK-013 | Coach architecture grants excessive access later | Medium | High | Candidate-scoped ABAC delegation and revocation | Security/Product | Open |
| RSK-014 | Unsupported scraping creates legal/source risk | Medium | High | User input/approved APIs only; source review gate | Legal/Product | Mitigated |
| RSK-015 | Durable workflow and graph ownership overlap | Medium | High | ADR-0004 and explicit state mapping tests | Architecture | Mitigated |
| RSK-016 | Approval races or stale versions authorize wrong action | Medium | Critical | Version binding, idempotency, expiry, concurrency tests | Workflow/Security | Open |
| RSK-017 | Free tier converts to paid usage | Medium | High | Quotas, alerts, billing checks, explicit enablement gate | Platform/Owner | Open |
| RSK-018 | Documentation claims compliance without review | Medium | High | Legal-review register and wording review | Product/Legal | Mitigated |
| RSK-019 | A2UI ambiguity leads to unsafe rendering | Medium | High | Internal allowlisted contract and Phase 14 follow-up ADR | Frontend/Security | Mitigated |
| RSK-020 | Backup improves durability but conflicts with deletion | Medium | High | Bounded retention, restore-time deletion ledger, legal review | Data/Privacy | Open |
| RSK-021 | Browser-declared file metadata disguises malicious content | High | High | Allowlist, basename normalization, quarantine, scanner/parser isolation before trust | Security | Partially mitigated; byte scanning deferred |
| RSK-022 | Concurrent profile edits silently lose user data | Medium | High | Version predicate, safe 409 conflict, transaction test | Data | Mitigated for Phase 4 profile updates |
| RSK-023 | Graph checkpoint/run state leaks across tenants | Medium | Critical | Scope IDs/stores by tenant/actor/run; hostile-tenant tests; durable store later | Security/AI | Open |
| RSK-024 | Model extraction invents job/candidate facts | Medium | Critical | Structured schema, fake evaluations, verification/citations, uncertainty | AI/Product | Open |
| RSK-025 | Gemini data/cost used without approval | Low | Critical | Disabled default, explicit transfer flag, opt-in live marker, no fallback | AI/Owner | Open |
| RSK-026 | Human approval applies to changed draft | Low | Critical | Version/hash/revision binding and atomic compare-update | Security/Workflow | Mitigated locally |
| RSK-027 | Draft persistence conflicts with privacy deletion | Medium | Critical | Source linkage, retention design, deletion propagation and legal review later | Privacy/Data | Open |
| RSK-028 | ADK specialist cites unsupported or cross-session source data | Medium | Critical | Request-local tool, scoped session key, schema/citation validation, hostile tests | Security/AI | Mitigated locally |
| RSK-029 | Gemini incurs cost or transfers personal data without authority | Low | Critical | Fake default, explicit provider, consent/transfer/cost gates, no fallback | Privacy/Owner | Open until production review |
| RSK-030 | Agent handoff transfers control or context to the wrong specialist | Medium | High | Explicit routes, bounded agents, equivalent ownership tests, redacted trace metadata | Security/AI | Mitigated locally |
| RSK-031 | OpenAI tracing or live execution leaks interview data or incurs cost | Low | Critical | Export/sensitive trace off, fake default, consent/transfer/budget gates, no fallback | Privacy/Owner | Open until production review |
