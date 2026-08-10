# ADR-0014: Deterministic Walking-Skeleton Boundaries

- **Status:** Accepted for Phase 2
- **Date:** 2026-08-10

## Context

CareerPilot needs proof that its browser, HTTP, application, persistence, error,
and telemetry boundaries connect before identity, databases, retrieval, or agents
increase the failure surface. The proof must remain truthful and cost CHF 0.

## Decision

Implement the first slice as an exact-term comparison:

- Framework-independent dataclasses and application service live in core.
- Core owns a profile-repository protocol; the API supplies a locked in-memory
  adapter.
- FastAPI exposes `/api/v1/profiles` and `/api/v1/analyses` with strict Pydantic
  contracts, health/readiness, safe errors, and correlation headers.
- The web client performs those two calls and labels the result as a deterministic
  placeholder, never an AI assessment.
- OpenTelemetry API spans and privacy-safe JSON logs carry operation metadata and
  opaque IDs only. Export remains disabled.
- Profile state is lost at process restart. PostgreSQL integration remains Phase 4.

## Consequences

The system proves dependency direction and visible data flow without inventing
qualifications or incurring provider cost. It is not suitable for real customer
data, concurrent production use, durable recovery, or hiring decisions. Phase 3
must add identity and authorization before broader access; Phase 4 must replace
temporary persistence through the existing port.

## Alternatives rejected

- PostgreSQL now would pull Phase 4 schema and migration decisions forward.
- An LLM placeholder would create cost, nondeterminism, and misleading product
  behavior before evaluation and provider-policy phases.
- Browser-only state would not prove HTTP, application, repository, or telemetry
  boundaries.
