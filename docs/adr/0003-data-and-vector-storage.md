# ADR-0003: PostgreSQL and pgvector

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

PostgreSQL owns production transactional data and tenant-scoped metadata;
pgvector stores derived embeddings beside authorized filters. Object storage owns
document bytes. SQLite is allowed only in explicitly bounded unit examples.

## Consequences

Production semantics need PostgreSQL integration tests. Vector deletion follows
source deletion. Retrieval authorization is part of the query, not a post-filter.

## Phase 4 implementation note

SQLAlchemy Core owns mappings and explicit transaction boundaries, Psycopg 3 is
the PostgreSQL driver, and Alembic owns immutable ordered schema revisions. Every
repository query combines tenant and resource predicates. SQLite is not used to
claim PostgreSQL behavior.
