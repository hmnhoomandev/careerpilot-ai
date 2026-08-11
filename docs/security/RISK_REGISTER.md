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
