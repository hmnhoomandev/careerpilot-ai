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
