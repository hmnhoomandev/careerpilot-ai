# Decision Log

| ID | Date | Decision | Status | ADR |
|---|---|---|---|---|
| DEC-001 | 2026-08-09 | Individual job seekers are the initial user | Accepted | ADR-0001 |
| DEC-002 | 2026-08-09 | Use a modular core with bounded specialist services | Accepted | ADR-0001 |
| DEC-003 | 2026-08-09 | Python 3.13 and Node.js 24 LTS are project targets | Accepted | ADR-0002 |
| DEC-004 | 2026-08-09 | PostgreSQL plus pgvector owns production data and retrieval indexes | Accepted | ADR-0003 |
| DEC-005 | 2026-08-09 | LangGraph owns agent graphs; Temporal owns durable business processes | Accepted | ADR-0004 |
| DEC-006 | 2026-08-09 | Model providers are bounded and never silently substituted | Accepted | ADR-0005 |
| DEC-007 | 2026-08-09 | Next.js App Router owns the English-first, i18n-ready web UI | Accepted | ADR-0006 |
| DEC-008 | 2026-08-09 | Cloud Run in Zurich is preferred; EU fallback needs a fresh assessment | Accepted | ADR-0007 |
| DEC-009 | 2026-08-09 | OpenTelemetry is the telemetry foundation with redaction before export | Accepted | ADR-0008 |
| DEC-010 | 2026-08-09 | RAG is hybrid, cited, tenant-filtered, versioned, and evaluated | Accepted | ADR-0009 |
| DEC-011 | 2026-08-09 | OIDC isolates identity providers from the domain | Accepted | ADR-0010 |
| DEC-012 | 2026-08-09 | CHF 0 is a hard development cost ceiling without approval | Accepted | ADR-0011 |
| DEC-013 | 2026-08-09 | A2UI compatibility means a versioned internal safe component-message contract until an external target is approved | Accepted | ADR-0012 |
| DEC-014 | 2026-08-09 | Use locked uv/npm workspaces and automated architecture/quality gates | Accepted | ADR-0013 |
| DEC-015 | 2026-08-09 | Isolate Semgrep's vulnerable MCP transitive dependency in an unused SAST-only environment | Accepted with review trigger | ADR-0013 |
| DEC-016 | 2026-08-10 | Prove the first journey with exact-term comparison and process-local persistence | Accepted for Phase 2 | ADR-0014 |
| DEC-017 | 2026-08-10 | Derive tenant authority from server-side membership and combine RBAC with resource ABAC | Accepted for Phase 3 | ADR-0015 |
| DEC-018 | 2026-08-10 | Use a local-only opaque-session adapter and hash-chained temporary audit evidence | Accepted with documented limitations | ADR-0015 |
| DEC-019 | 2026-08-11 | Use SQLAlchemy Core, Psycopg 3, and Alembic for tenant-scoped PostgreSQL profile/evidence persistence | Accepted | ADR-0016 |
| DEC-020 | 2026-08-11 | Accept evidence metadata only in Phase 4 and keep every item quarantined behind a scanner port | Accepted | ADR-0016 |
| DEC-021 | 2026-08-11 | Use a bounded local document pipeline and deterministic hash vectors for the free Phase 5 baseline | Accepted for Phase 5 | ADR-0017 |
| DEC-022 | 2026-08-11 | Authorize inside lexical/vector SQL and return cited untrusted passages without generated answers | Accepted | ADR-0017 |
| DEC-023 | 2026-08-11 | Route every tool through one typed registry/executor with policy, idempotency, rate, timeout, output, and audit controls | Accepted | ADR-0018 |
| DEC-024 | 2026-08-11 | Expose four read-only capabilities through an explicit official-SDK MCP allowlist | Accepted for Phase 6 | ADR-0018 |
| DEC-025 | 2026-08-13 | Use LangGraph 1.2.x for the bounded typed analysis graph and keep Temporal ownership separate | Accepted | ADR-0019 |
| DEC-026 | 2026-08-13 | Use fake provider by default and an explicitly authorized, no-fallback Google Gen AI adapter | Accepted | ADR-0019 |
| DEC-027 | 2026-08-13 | Store immutable evidence-linked draft versions and bind approval to exact version/hash/revision | Accepted | ADR-0020 |
| DEC-028 | 2026-08-13 | Use LangGraph interrupt for review interaction and PostgreSQL for authoritative restart-safe approval records | Accepted for Phase 8 | ADR-0020 |
| DEC-029 | 2026-08-13 | Isolate Google ADK as a supplied-source research specialist with fake default and no fallback | Accepted for Phase 9 | ADR-0021 |
| DEC-030 | 2026-08-13 | Upgrade OpenTelemetry API to 1.42.x for ADK 2.5 compatibility without enabling export | Accepted | ADR-0021 |
| DEC-031 | 2026-08-14 | Isolate OpenAI Agents SDK as a fake-first interview orchestration laboratory | Accepted for Phase 10 | ADR-0022 |
| DEC-032 | 2026-08-14 | Use direct handoff only when the specialist should own the conversation; otherwise retain manager ownership | Accepted | ADR-0022 |
