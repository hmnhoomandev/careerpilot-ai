# Phase 04 Review: PostgreSQL Profile and Evidence Library

## 1. Phase objective

Establish durable, tenant-safe professional-profile persistence and a fail-closed
evidence metadata library using versioned PostgreSQL migrations, explicit
transactions, optimistic concurrency, and local/free infrastructure.

## 2. Delivered features

- PostgreSQL schema for profiles, skills, experience, education, evidence metadata,
  versions, timestamps, and deletion/purge lifecycle fields.
- Alembic revision `0001` with upgrade and disposable-environment downgrade.
- SQLAlchemy Core/Psycopg repository with explicit transaction boundaries and
  tenant predicates on every active data operation.
- Profile create/read/update API with structured sections and safe stale-write
  conflict handling.
- Evidence metadata registration/listing with 10 MiB limit, PDF/JPEG/PNG allowlist,
  basename normalization, extension consistency, and quarantine-by-default.
- `MalwareScanner` port documenting the fail-closed future scanner boundary.
- Authenticated web controls for profile versions/skills and metadata-only evidence
  registration with quarantine status.
- CI PostgreSQL service so production-semantic tests do not silently skip.

## 3. Explicitly not delivered

- Raw file upload/storage, content sniffing, malware-engine integration, document
  parsing, embeddings, pgvector retrieval, citations, or RAG.
- PostgreSQL persistence for local identity, membership, sessions, or audit events.
- Destructive deletion execution, legal holds, backup deletion propagation, or a
  durable human-approval workflow.
- PostgreSQL row-level security, production credentials, Cloud SQL, cloud resources,
  billing, deployment, or real personal data.
- Full experience/education web editor; these sections are available in domain,
  schema, and API contracts while the compact Phase 4 UI exposes skills first.

## 4. Files created/changed

- Persistence: `alembic.ini`, `migrations/`, and
  `apps/api/src/careerpilot_api/database.py`.
- Domain/application: models, ports, authorization permissions, services, and
  in-memory adapter under `packages/core/` and `apps/api/`.
- HTTP/UI: API contracts/composition plus the web API client, page, styles, and tests.
- Verification: unit, API, contract, integration, and updated CI configuration.
- Governance/learning: ADR-0016, annotated source, tutorial, glossary, exercises,
  dependency policy, security/privacy records, project state, and traceability.

## 5. Architecture decisions

- PostgreSQL is the only production relational target; SQLite is not used as a
  substitute for production-semantics evidence.
- SQLAlchemy Core owns mappings and transactions, Psycopg 3 owns connectivity, and
  Alembic owns immutable ordered revisions.
- Profile children update with the aggregate in one transaction. A constraint error
  rolls back both child changes and the profile version increment.
- Optimistic concurrency uses `WHERE version = expected_version`; a lost race maps
  to a safe HTTP `409` rather than last-write-wins behavior.
- Opaque IDs identify; authenticated tenant/ownership context authorizes.

## 6. Security/privacy review

- Cross-tenant and same-tenant ownership policy remains enforced before repository
  mutation; queries additionally scope tenant ID and active state.
- Composite tenant/profile foreign keys prevent cross-tenant child attachment.
- Successful and unavailable profile reads and profile/evidence mutations produce
  metadata-only audit facts.
- File names, declared types, and extensions are untrusted; Phase 4 only normalizes
  and allowlists metadata, and never treats an item as clean.
- Development and manual checks used synthetic data. Logs showed method/path/status,
  correlation, and timing only—not submitted content or session tokens.
- Final retention periods, exceptions, staff access, legal holds, and Swiss FADP/
  GDPR interpretations are flagged for qualified professional legal review. This
  documentation does not claim certification or guaranteed compliance.

## 7. Data/schema/migration impact

- New tables: `professional_profiles`, `profile_skills`, `profile_experiences`,
  `profile_education`, and `evidence_items`.
- Revision: `0001_profile_evidence_foundation`.
- `alembic check` against local PostgreSQL reported no new upgrade operations.
- Downgrade drops all five tables and is safe only for an explicitly disposable
  local/test database. For deployed environments, prefer a reviewed forward-fix
  migration rather than destructive downgrade.
- Deletion fields establish mechanics only; no deletion endpoint is activated.

## 8. Automated commands and exact results

| Command | Result |
|---|---|
| `uv lock` and `uv sync --all-packages --locked` | 124 packages resolved; Alembic 1.18.5, Psycopg 3.3.4, SQLAlchemy 2.0.51 installed |
| Full Pytest with local PostgreSQL URL | 81 passed in 2.90s; 0 skipped |
| Default offline Pytest without PostgreSQL URL | 79 passed, 2 PostgreSQL tests explicitly skipped |
| `ruff format --check .` | 128 files already formatted |
| `ruff check .` | All checks passed |
| strict MyPy including migrations | Success; 47 source files |
| Alembic offline SQL render | Passed inside contract suite |
| `alembic check` against PostgreSQL | No new upgrade operations detected |
| Frontend format/lint/type/test/build | Passed; 4 Vitest tests; static production build succeeded |
| `pip-audit` | No known vulnerabilities; internal workspace packages skipped as unpublished |
| Semgrep, 3 local rules | 47 targets, 0 findings; macOS signal-handler warning remains |
| Detect-secrets | Passed with committed baseline |
| Pre-commit, all files | 5 hooks passed after documenting the synthetic CI-only credential exception |
| Markdown lint/link and Mermaid validation | 76 Markdown files, 0 lint issues; links passed; 8 diagrams rendered |
| Phase 0 governance validator | 24 required files, 74 requirement IDs, 83 Markdown files |
| Frontend and documentation npm audits | 0 vulnerabilities in both workspaces |

Transient failures were not hidden: sandbox network access initially blocked the
PostgreSQL socket and public audit/tool downloads, then approved local/network runs
passed. One UI submit test and two Markdown spacing findings were corrected. Docker
was initially stopped; the local Docker application was started and PostgreSQL became
healthy before production-semantic claims were made.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Start local PostgreSQL 17/pgvector | Container becomes healthy on loopback | Passed |
| Apply/check migration | Head applies and metadata has no drift | Passed |
| Create synthetic profile | Version 1 profile returned | Passed |
| Edit profile | Version increments to 2 | Passed |
| Repeat stale version-1 edit | Safe `profile_version_conflict` response | Passed |
| Register path-like PDF metadata | Basename stored; state is `quarantined` | Passed |
| Register executable metadata | Safe `evidence_not_accepted` response | Passed |
| Restart API and reload profile | Version 2 and skill persist | Passed |
| Inspect runtime logs | No submitted content or session token | Passed |
| Owner visual/keyboard browser walkthrough | Controls and states are understandable and accessible | Pending owner check |

## 10. Requirements traceability

- FR-001: durable profile aggregate, versioned API/UI, reconnect persistence.
- FR-002: provenance-ready evidence metadata and explicit quarantine state.
- SEC-001–SEC-004: authenticated, policy-controlled, tenant-scoped active boundary.
- SEC-008: size/type/name/extension controls plus scanner interface; byte scanning
  remains explicitly incomplete.
- NFR-009/NFR-011: API v0.4 contracts, safe errors, audit/correlation evidence.
- NFR-019: versioned migration, downgrade/upgrade, drift, transaction, rollback,
  concurrency, and tenant-isolation evidence.

## 11. Example behavior

Accepted evidence metadata returns a normalized filename and `quarantined` state.
A stale profile edit returns HTTP 409 with code `profile_version_conflict`. Responses
contain a correlation ID where errors occur and never expose SQL or stack traces.

## 12. Known limitations, debt, and risks

- Browser media type and extension validation cannot inspect content because bytes
  intentionally do not enter Phase 4. Treating these records as trusted is forbidden.
- Identity/session/audit are still process-local, so restarting requires a new local
  login even though PostgreSQL profile/evidence metadata persists.
- The local database password and URL require manual ignored-environment setup.
- The browser's compact editor does not yet expose all structured experience and
  education fields.
- RLS, pooling/load tuning, backups/restore, encryption/KMS, production secrets,
  scanner/parser sandboxing, and deletion propagation remain future controls.

## 13. Rollback/recovery instructions

- Stop API/web processes before persistence recovery.
- Preserve the database before any destructive local experiment.
- For a disposable test database only, run `alembic downgrade base`; then rerun
  `alembic upgrade head` to rehearse forward recovery.
- For accepted/committed source changes, use a normal `git revert` checkpoint rather
  than resetting history. Never edit revision `0001` after deployment; add a new
  corrective migration.
- `docker compose down` stops local services without deleting the named volume;
  do not use volume deletion for data that must be recovered.

## 14. Learning summary

This phase taught aggregate transactions, migration ownership, PostgreSQL versus
SQLite semantics, optimistic concurrency, tenant predicates, constraint-backed
rollback, evidence trust states, metadata minimization, and fail-closed scanning
boundaries. The tutorial and exercises provide a reproducible learning path.

## 15. Owner acceptance checklist

- [ ] Create and edit a synthetic profile and observe the version increment.
- [ ] Add PDF/JPEG/PNG evidence metadata and observe `quarantined`.
- [ ] Attempt an unsupported file and see an understandable rejection.
- [ ] Simulate or review a stale update and see a safe conflict.
- [ ] Restart the API with PostgreSQL configured and confirm persistence.
- [ ] Confirm no claim is made that bytes were stored/scanned or privacy compliance
      is legally guaranteed.
- [ ] Confirm Phase 5 has not begun.

## 16. Proposed next phase

Phase 5 will add secure raw-document ingestion, parsing/normalization/chunking,
pgvector and hybrid retrieval, citations, deletion propagation, injection-aware
handling, and retrieval evaluation. It must not begin without the exact gate.

## 17. Exact approval command

`APPROVE PHASE 4 AND START PHASE 5`
