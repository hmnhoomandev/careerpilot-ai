# ADR-0023: Bounded A2A registry and task lifecycle

**Status:** Accepted for Phase 11  
**Date:** 2026-08-14

## Context

CareerPilot has LangGraph, Google ADK, and OpenAI Agents runtimes with deliberately
different ownership. They need discoverable, versioned delegation without making an
advertised capability an authorization grant or allowing provider fallback.

## Decision

Use official `a2a-sdk` Agent Card and Task models behind a trusted application registry.
Publish one versioned skill per runtime, validate protocol/card/transport compatibility,
and route through a typed `RemoteAgentAdapter`. Every API operation reuses authenticated
tenant context and `analysis.run` authorization. Task identity is tenant-and-actor scoped;
same-ID/same-input is idempotent, while changed input conflicts. Timeout, outage,
cancellation, and incompatible versions are explicit and never trigger fallback.

Phase 11 uses deterministic in-process adapters. It does not expose an unauthenticated A2A
JSON-RPC endpoint: production service-to-service HTTP, workload identity, card trust,
durable task storage, and independently deployed SDK servers require later deployment and
security decisions. Card URLs are target deployment descriptors, not active local routes.

## Consequences

The three runtimes can be discovered and exercised through one policy-controlled local
contract at CHF 0. Official SDK validation reduces schema drift. Process-local tasks are
lost on restart and cooperative cancellation is not a distributed guarantee. Production
must replace the fake adapter and authenticate both caller and workload without putting
provider logic in the domain.

No database migration, external transfer, live model call, cloud resource, or paid service
is introduced. Retention, lawful basis, service credentials, remote card provenance, and
EU/Swiss deployment require security/privacy and professional legal review.
