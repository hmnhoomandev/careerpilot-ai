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
