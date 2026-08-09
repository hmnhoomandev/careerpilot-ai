# ADR-0012: Versioned Safe UI Message Contract

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

The master specification requests A2UI compatibility but does not select an
external schema, version, or interoperability conformance target.

## Decision

Define a versioned internal allowlisted component-message contract for approval,
citations, timelines, and editable drafts. Call it A2UI-compatible only in the
architectural sense until Phase 14 selects and records an authoritative external
target. Never render arbitrary model-produced components, HTML, scripts, or URLs.

## Consequences

Phase 14 needs a follow-up ADR and unsafe-content renderer tests. Documentation
must not claim external conformance before those exist.
