# ADR-0021: Bounded Google ADK Research Specialist

- **Status:** Accepted for Phase 9
- **Date:** 2026-08-13

## Context

CareerPilot needs a justified Google ADK learning boundary without transferring ownership
of the core application graph from LangGraph. Company/job research is useful but carries
hallucination, source licensing, prompt-injection, privacy, cost, and provider risks.

## Decision

Create `services/google-adk` as a prototype-only, independently testable specialist. It
uses Google ADK 2.5.x, a single request-scoped agent, structured Pydantic output, an
allowlisted user-supplied-source tool, an ADK pre-model safety callback, in-memory local
sessions, and metadata-only telemetry. The default provider is deterministic and fake.
Gemini is explicitly selected, has one attempt, requires per-request consent and transfer
authorization, and never falls back. The service validates every returned citation.

The internal HTTP surface requires a service-identity header. Production workload
identity/mTLS remains mandatory before deployment. OpenTelemetry API moves from 1.37.x to
1.42.x because ADK 2.5 requires 1.39–1.42.1; no exporter is enabled.

## Consequences

The framework and provider remain outside the domain and main API. Default development is
offline and CHF 0. Live evaluation is a separately authorized operation. In-memory
sessions, a static development service identity, and process-local telemetry are not
production controls. No scraping, managed search, A2A, cloud deployment, or durable
session storage is introduced.
