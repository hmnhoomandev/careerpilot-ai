# ADR-0016: PostgreSQL Profile and Evidence Foundation

- **Status:** Accepted for Phase 4
- **Date:** 2026-08-11

## Context

The process-local profile adapter cannot survive restart or prove PostgreSQL
constraint, transaction, and concurrency behavior. Evidence also needs a safe
state before raw-document ingestion exists.

## Decision

Use PostgreSQL 17 with an immutable Alembic revision, SQLAlchemy 2 Core mappings,
and Psycopg 3. A profile aggregate contains skills, experience, and education.
Integer versions provide compare-and-swap updates. Tenant ID participates in all
repository predicates and child foreign keys.

Evidence intake accepts only minimized metadata for PDF, JPEG, or PNG files up to
10 MiB, normalizes the basename, and persists `quarantined`. The Phase 4 browser
does not transmit bytes. A `MalwareScanner` port defines the future trust boundary;
requesting a scan will never itself mean that content is clean.

Profiles and evidence include `deleted_at` and `purge_after`. The intended default
recoverable window is 30 days, but destructive workflows wait for durable human
approval and final retention rules require professional legal review.

## Dependencies and alternatives

- SQLAlchemy (MIT) provides mature Core SQL, mapping, and transactions.
- Alembic (MIT) provides ordered, reviewable, forward/reverse migrations.
- Psycopg (LGPL-3.0 with exceptions) provides the PostgreSQL protocol driver. The
  binary package bundles native libraries and must remain SCA-scanned.
- Direct driver SQL plus a custom migration runner was rejected because it would
  recreate established transaction/migration machinery and increase recovery risk.
- SQLite was rejected for integration evidence because its locking, constraints,
  types, and concurrency differ from PostgreSQL.

## Consequences

Local development can remain in-memory by omitting the database URL. Production-
semantic tests require an explicitly disposable PostgreSQL URL. Schema changes
must be new revisions; deployed revisions must never be edited. Object storage,
real bytes, malware scanning, parsing, pgvector retrieval, RLS, backup/restore,
and durable audit/identity persistence remain future work.
