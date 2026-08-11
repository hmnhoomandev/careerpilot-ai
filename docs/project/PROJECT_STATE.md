# Project State

- **Project:** CareerPilot AI
- **Current phase:** Phase 5 — secure document ingestion and evaluated RAG
- **Phase status:** Complete; awaiting owner acceptance
- **Last updated:** 2026-08-11
- **Working tree at phase start:** Clean at `669db40` on `main`
- **Production code:** Accepted Phase 4 foundation plus completed Phase 5 local retrieval candidate
- **Cloud resources created:** None
- **Paid calls made:** None

## Binding owner decisions

- Individual job seekers are the first users; coaches and organizations are later.
- Launch baseline is Switzerland and the EU, with GDPR-oriented principles and
  Swiss FADP consideration; no claim of legal certification.
- English is the initial language; architecture must be internationalization-ready.
- Prefer Google Cloud `europe-west6` (Zurich); an EU fallback requires a recorded
  availability, residency, security, privacy, latency, and cost analysis.
- Environments are local, test/CI, staging, and production.
- Development and learning budget is CHF 0/month. Any cost requires explicit
  prior approval and a free/local alternative analysis.
- Identity uses an OIDC boundary, a local development adapter, and Google Identity
  Platform as the initial production reference.
- Gemini is the initial Google/LangGraph learning-path model; OpenAI remains in
  its bounded Agents SDK service; fakes are the default.
- Development uses synthetic personal data.
- User data supports access, correction, export, and deletion, with a default
  30-day recoverable deletion window subject to legal review.
- Job/company data begins with user input, approved APIs, and explicitly permitted
  sources; unrestricted scraping is forbidden.
- Initial availability design target is 99.5% monthly; no silent provider fallback.

## Current decisions

- Python 3.13 is the Phase 1 target runtime.
- Node.js 24 LTS is the Phase 1 target runtime.
- The production architecture is a modular core plus bounded specialist services,
  with event-driven integration where justified.
- Cloud Run is the first deployment target; GKE is a later reference.
- PostgreSQL/pgvector is authoritative production persistence.
- LangGraph and Temporal have separate graph and durable-process ownership.

## Phase 4 implementation state

- PostgreSQL 17/pgvector runs in the repository's local Docker profile.
- Alembic revision `0001` defines tenant-scoped profile, skills, experience,
  education, and evidence metadata tables.
- SQLAlchemy/Psycopg repository tests prove reconnect persistence, rollback,
  optimistic concurrency, and tenant isolation against real local PostgreSQL.
- Evidence intake is metadata-only and fail-closed in quarantine; no document bytes
  are persisted or sent to a scanner in this phase.

## Phase 5 implementation state

- Authenticated UTF-8 text and text-based PDF upload uses bounded validation,
  deterministic local scanning/parsing, opaque local storage, and injection labels.
- Alembic `0002` adds tenant-scoped documents/chunks, pgvector, generated English
  full-text vectors, and GIN/HNSW indexes.
- Both lexical and vector queries filter tenant, owner, active document, and index
  version before candidate ranking. Results are untrusted cited passages, not answers.
- Reindexing replaces derivatives; confirmed deletion removes local bytes and active
  chunks/vectors and soft-deletes provenance metadata.
- Versioned synthetic retrieval/injection fixtures gate recall@3, precision@3, MRR,
  grounding, citation correctness, prompt-injection labels, and empty results.

## Phase 5 verification evidence

- Python format/lint passed; strict MyPy passed for 51 source files.
- Full Pytest against real local PostgreSQL/pgvector: 101 passed, 0 skipped.
- Alembic upgrade/check: no new upgrade operations detected.
- Web Prettier, ESLint, TypeScript, 5 Vitest tests, and production build passed.
- Markdown lint: 82 files, 0 issues; external link check passed; 8 Mermaid
  diagrams rendered; governance validator passed with 89 Markdown files.
- Pip audit and both npm audits found no known vulnerabilities. Internal unpublished
  Python packages were the expected pip-audit skips.
- Semgrep local rules completed with exit 0; detect-secrets and all 5 pre-commit
  hooks passed.

## Known blockers and constraints

- Docker Desktop and the local PostgreSQL container must be running for marked
  integration tests; default tests remain offline.
- Global Node.js 26 differs from the repository target; Phase 1 verification used
  Node.js 24. Python verification used the selected Python 3.13 runtime.
- Google Cloud CLI cannot write its default config under the current sandbox.
- Final legal retention periods and regulatory interpretations require qualified
  professional legal review.
- No paid service may be used under the current CHF 0 budget.

## Next action

Review and manually accept Phase 5. Phase 6 remains stopped until:

`APPROVE PHASE 5 AND START PHASE 6`
