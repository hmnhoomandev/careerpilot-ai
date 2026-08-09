# ADR-0001: Modular Core with Bounded Specialist Services

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

The roadmap needs strong domain boundaries and three agent frameworks but the CHF
0 learning environment cannot justify a microservice for every capability.

## Decision

Start with a modular core behind ports. Deploy ADK and OpenAI Agents SDK only as
bounded specialist services, and split other services only when independent
scaling, security, failure isolation, or ownership justifies it.

## Consequences

Architecture tests must prevent forbidden imports. Remote boundaries require
versioned contracts and degradation behavior. This avoids premature distributed
operations but demands disciplined modules.
