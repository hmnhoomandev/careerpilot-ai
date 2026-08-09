# Requirements

Requirement IDs are stable. Status values are `Proposed`, `Accepted`,
`Implemented`, or `Verified`. Phase 0 accepts the requirements; later phases
provide code and test evidence.

## Functional requirements

| ID | Requirement | Target phase | Status |
|---|---|---:|---|
| FR-001 | A user can create and maintain a verified professional profile. | 4 | Accepted |
| FR-002 | A user can add evidence with provenance and processing status. | 4 | Accepted |
| FR-003 | The system accepts user-supplied job descriptions and company information. | 2/5 | Accepted |
| FR-004 | The system extracts structured job requirements while treating source content as untrusted. | 5/7 | Accepted |
| FR-005 | Retrieval returns authorized evidence with document and chunk citations. | 5 | Accepted |
| FR-006 | The system produces an explainable candidate-to-job match grounded in evidence. | 7 | Accepted |
| FR-007 | The system identifies supported, missing, and uncertain skill gaps. | 7 | Accepted |
| FR-008 | Resume drafts are versioned and every material claim links to evidence or is blocked/suggested. | 8 | Accepted |
| FR-009 | Cover-letter drafts are versioned and every material claim links to evidence or is blocked/suggested. | 8 | Accepted |
| FR-010 | Users can inspect citations and concise decision summaries without hidden reasoning. | 7/14 | Accepted |
| FR-011 | Users can approve, reject, edit-and-approve, request information, expire, cancel, and resume approvals. | 8 | Accepted |
| FR-012 | Approval state survives process restart and binds to the exact proposal version. | 8/12 | Accepted |
| FR-013 | Users can track application status and follow-up milestones. | 12/14 | Accepted |
| FR-014 | The system supports interview preparation and simulation through bounded specialist services. | 9/10 | Accepted |
| FR-015 | Users can see workflow, agent, tool, source, approval, and audit status. | 14/15 | Accepted |
| FR-016 | Users can access, correct, export, and request deletion of personal data. | 16 | Accepted |
| FR-017 | Deletion propagates to chunks, embeddings, caches, replicas, and indexes. | 5/16 | Accepted |
| FR-018 | Coaches can later receive explicit, scoped, revocable candidate delegation. | Later | Accepted |
| FR-019 | The system supports English initially and externalizes user-facing text for future locales. | 1/14 | Accepted |
| FR-020 | Automatic email, sharing, submission, publishing, inference-based profile mutation, deletion, sensitive transfer, high-risk tooling, irreversible action, and spend require human approval. | 6+ | Accepted |
| FR-021 | The system records provider, model, purpose, authorization, consent basis, prompt version, and policy outcome for external model calls without unsafe content logging. | 7/15 | Accepted |
| FR-022 | The system never silently changes model or provider after a failure. | 7/15 | Accepted |
| FR-023 | Approved APIs and explicitly permitted sources require provenance and source-policy metadata. | 5+ | Accepted |
| FR-024 | Unrestricted website scraping is prohibited. | All | Accepted |

## Security and privacy requirements

| ID | Requirement | Target phase | Status |
|---|---|---:|---|
| SEC-001 | Authentication uses an OIDC boundary; provider logic does not enter the domain. | 3 | Accepted |
| SEC-002 | Authorization denies by default and combines RBAC with contextual ABAC. | 3 | Accepted |
| SEC-003 | Tenant isolation is enforced at API, service, repository, document, retrieval, agent, and tool boundaries. | 3+ | Accepted |
| SEC-004 | Cross-tenant and IDOR tests prove denied reads, writes, retrieval, and tool use. | 3+ | Accepted |
| SEC-005 | Security-relevant success and denial events are auditable and tamper-evident in design. | 3 | Accepted |
| SEC-006 | Secrets stay outside source and use a secret-manager/KMS boundary in production. | 1/16 | Accepted |
| SEC-007 | Logs and traces redact PII, secrets, prompts, retrieved content, and generated artifacts unless explicitly safe and necessary. | 2/15 | Accepted |
| SEC-008 | Uploads enforce size/type/name validation, quarantine, and a malware-scanning boundary. | 4 | Accepted |
| SEC-009 | Outbound retrieval and fetch tools prevent SSRF and restrict destinations. | 5/16 | Accepted |
| SEC-010 | Direct and indirect prompt injection is detected, labeled, constrained, and tested. | 5/16 | Accepted |
| SEC-011 | Tool inputs and outputs use validated schemas, authorization, sanitization, timeouts, idempotency, and rate limits. | 6 | Accepted |
| SEC-012 | Encryption protects data in transit and at rest; key rotation and recovery are documented. | 16/17 | Accepted |
| SEC-013 | Consent, purpose, minimization, and retention checks precede external model disclosure. | 7+ | Accepted |
| SEC-014 | Development and default tests use synthetic data and fake providers. | All | Accepted |
| SEC-015 | A 30-day recoverable deletion window is the default, with documented immediate-deletion exceptions and legal review. | 16 | Accepted |
| SEC-016 | Audit/security retention is separately justified, minimized, access-controlled, and pseudonymized where practical. | 16 | Accepted |
| SEC-017 | Rate limiting, abuse prevention, and denial-of-wallet controls apply at user, tenant, tool, and provider boundaries. | 6/16 | Accepted |
| SEC-018 | Backup, restore, incident response, and personal-data breach procedures are exercised. | 16/20 | Accepted |
| SEC-019 | Dependency pinning, SBOM, SAST, SCA, DAST, container/IaC, secret, and license scanning follow severity policy. | 1/16/17 | Accepted |
| SEC-020 | Bias and compliance checks report limitations and never make protected-trait employment decisions. | 8/16 | Accepted |
| SEC-021 | Legal-review items are labeled; documentation never claims certification or guaranteed compliance. | All | Accepted |
| SEC-022 | External source use is reviewed for license, terms, robots, copyright, provenance, retention, deletion, privacy, and rate limits. | 5+ | Accepted |

## Quality and operational requirements

| ID | Requirement | Target phase | Status |
|---|---|---:|---|
| NFR-001 | Production availability is designed toward 99.5% monthly. | 15/20 | Accepted |
| NFR-002 | API latency, workflow completion/recovery, durability, restore, error, retrieval, provider-failure, and cost metrics are measurable. | 15+ | Accepted |
| NFR-003 | Default tests and development workflows incur CHF 0 model/cloud cost. | All | Accepted |
| NFR-004 | Paid resources, billing, paid calls, or recurring services require explicit prior owner approval. | All | Accepted |
| NFR-005 | A required cost proposal states why, provider/service, one-time/monthly estimate, free alternative, and waits for approval. | All | Accepted |
| NFR-006 | Free-tier quotas and billing-conversion risk are monitored before use. | 15/17 | Accepted |
| NFR-007 | Python 3.13 and Node.js 24 LTS are enforced as project runtimes unless superseded by ADR. | 1 | Accepted |
| NFR-008 | The web interface meets WCAG 2.2 AA-oriented testing for the core journey. | 14 | Accepted |
| NFR-009 | APIs and event/capability contracts are versioned and compatibility-tested. | 2/6/11/13 | Accepted |
| NFR-010 | OpenTelemetry correlation spans API, workflows, graphs, agents, tools, retrieval, approvals, and remote services. | 2/15 | Accepted |
| NFR-011 | New production behavior has logs, metrics, traces, errors, and runbook impact. | All implementation phases | Accepted |
| NFR-012 | Live-model tests are opt-in, budget-limited, and require explicit cost confirmation. | 7+ | Accepted |
| NFR-013 | Recovery distinguishes retry, replay, resume, compensation, and visible fallback. | 12+ | Accepted |
| NFR-014 | Cloud deployment prefers Zurich and documents every required EU-region exception across availability, residency, security/privacy, latency, and cost. | 17 | Accepted |
| NFR-015 | The four environments are local, test/CI, staging, and production with isolated configuration and identities. | 1/17 | Accepted |
| NFR-016 | Important production source is typed, documented, annotated, tested, and linked through traceability. | All implementation phases | Accepted |
| NFR-017 | The UI is English-first and internationalization-ready without embedding locale assumptions in domain contracts. | 1/14 | Accepted |
| NFR-018 | Architecture boundaries are enforced by automated dependency tests. | 1 | Accepted |
| NFR-019 | Data migrations are versioned, tested, recoverable, and tenant-safe. | 4+ | Accepted |
| NFR-020 | No warning, skipped check, degraded integration, or remaining risk is hidden. | All | Accepted |

## Professional legal review register

| ID | Topic requiring qualified review before production release |
|---|---|
| LEG-001 | Controller/processor roles and lawful bases under GDPR and Swiss FADP |
| LEG-002 | Final retention schedules, deletion exceptions, audit retention, and legal holds |
| LEG-003 | Cross-border transfers, subprocessors, model-provider terms, and data residency |
| LEG-004 | Data-subject access, correction, portability/export, deletion, and identity verification |
| LEG-005 | Automated profiling, bias, transparency, and employment-related AI obligations |
| LEG-006 | Coach delegation, confidentiality, organizational tenancy, and consent withdrawal |
| LEG-007 | Job/company source licensing, terms, robots rules, copyright, and permissible reuse |
| LEG-008 | Incident and personal-data-breach notification duties and timelines |
