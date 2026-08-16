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

## Phase 11 additions

| Risk | Treatment | Residual status |
|---|---|---|
| Untrusted/stale Agent Card redirects or expands capability | Static allowlist and exact compatibility checks; add provenance/revocation before remote discovery | Open for production |
| Delegated task leaks across tenants | Server-derived context, resource policy, composite key, non-enumerating lookup, hostile tests | Low locally |
| Runtime outage silently changes provider | Stable failed/unavailable result and prohibition on fallback | Low locally |
| Process restart loses tasks/cancellation | Explicit prototype limitation; durable store required before production | Open |

## Phase 12 additions

| Risk | Treatment | Residual status |
|---|---|---|
| Personal content persists in workflow history | Opaque-prefix/character/length validation and synthetic tests | Low locally; gateway review open |
| Activity retry duplicates an external effect | Stable step key, ledger port and fail-after-commit test | Low locally; production transaction design open |
| Workflow code change breaks replay | Sandboxed deterministic code, patch marker and history replay test | Low for captured baseline |
| Unauthorized/stale approval signal | Exact draft/version/actor check; authoritative gateway verification required | Open for production |
| Cancelled process leaves partial effects | Reverse idempotent compensation and Temporal cancellation tests | Medium; not every real effect is reversible |
| Temporal history/visibility residency or retention conflicts | No cloud use; production region/retention/legal review required | Open |

## Phase 13 open risks

- Process-local event state is not durable; production activation requires transactional
  PostgreSQL tables, concurrency controls, migrations, backup/restore and load tests.
- Pub/Sub residency, IAM, retention, quotas, costs, dead-letter access and Zurich service
  availability are unverified because no cloud resource was authorized.
- Replay is an operator capability and requires production authorization, audit, rate limits,
  runbooks, and retention controls before activation.

## Phase 14 open risks

- Authenticated web state is tab-local and the local identity adapter is not production auth;
  production session, CSRF/cache/header and device-threat controls remain Phase 16/17 work.
- Interview and application tracking panels are labelled local fixtures; confusing them with
  active external automation is mitigated by disabled actions and explicit copy.
- Automated semantic/axe checks do not replace assistive-technology and browser/device testing;
  manual keyboard, zoom, screen-reader and mobile review remains required before release.

## Phase 15 open risks

- Local telemetry and budget/quota state is process-local; it cannot prove distributed limits,
  durable reconciliation, alerting or production SLOs.
- Cloud/BigQuery/LangSmith/provider adapters are intentionally disabled and their region, IAM,
  retention, cost and operational behavior remain unverified.
- Offline synthetic evaluation can regress differently from consented production traffic; live
  and LLM-judge evaluation needs separate data-transfer, region and budget approval.

## Phase 16 residual risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-038 | Rights API implies physical deletion/legal completion | Medium | Critical | Explicit states, purge boundary, legal labels | Privacy/Data | Open pending durable purge/legal review |
| RSK-039 | Restore reactivates deleted/foreign data | Low | Critical | Integrity, tenant isolation, tombstones, tests | Platform/Data | Open pending cloud restore |
| RSK-040 | SSRF bypass through DNS, redirect or address form | Medium | Critical | No fetcher, allowlist, address validation | Security | Open pending production egress |
| RSK-041 | Local rate limit is bypassed across instances | High | High | Require shared edge/application limits | Security/Platform | Open for Phase 17 |

## Phase 18 GKE reference risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-042 | Rendered reference is mistaken for deployed security | Medium | Critical | Explicit placeholders, no apply path, staging/admission evidence gate | Platform/Security | Open before deployment |
| RSK-043 | NetworkPolicy/CIDR error blocks dependencies or permits lateral movement | Medium | Critical | Default deny, policy tests, exact CNI/CIDR staging verification | Network/Security | Open before deployment |
| RSK-044 | Workload Identity or secret synchronization grants excess access | Medium | Critical | Separate identities, no keys/values, least-privilege IAM review | Security/Platform | Open before deployment |
| RSK-045 | GKE baseline creates unapproved recurring spend or operational overload | High | High | Cloud Run default, cost/staffing decision gate, no cluster creation | Owner/Platform | Mitigated in reference scope |

## Phase 19 durable-execution lab risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-046 | Comparison SDK becomes an accidental production dependency or route | Low | High | Separate projects/locks plus manifest and import-boundary tests | Architecture | Mitigated |
| RSK-047 | Runtime retry duplicates a committed external effect | Medium | Critical | Stable effect key and equivalent post-commit-failure tests | Workflow/Data | Mitigated in labs; production adapter remains open |
| RSK-048 | Tiny local lab is mistaken for production recovery/maturity evidence | Medium | High | Explicit scope, comparison limitations and new adoption ADR gate | Platform | Open before adoption |
| RSK-049 | Restate server use violates license terms or distribution constraints | Low | Critical | BSL boundary recorded; professional license review required | Legal/Owner | Open before adoption |
| RSK-050 | Durable history contains personal data outside deletion/residency controls | Medium | Critical | Synthetic opaque input only; privacy/residency/retention design gate | Privacy/Data | Open before adoption |
