# Annotated Source: Phase 2 Walking Skeleton

## Boundary map

```text
page.tsx -> careerpilot-api.ts -> FastAPI contracts -> CareerJourneyService
                                                    -> ProfileRepository protocol
                                                    -> in-memory adapter
```

The arrows point inward toward business behavior. Core never imports FastAPI,
React, OpenTelemetry, or the temporary adapter.

## Core

`models.py` uses frozen, slotted dataclasses so values are explicit and cannot be
silently mutated. `ports.py` defines what the application needs from persistence,
not how storage works. `services.py` normalizes text, removes a small fixed stop
word set, intersects exact terms, and sorts the result. Given the same profile,
job text, and injected IDs, it returns the same content.

The disclaimer is part of the result contract. It prevents the simple term
intersection from being presented as inferred skill, ranking, fit, or hiring
advice.

## API and adapter

`contracts.py` rejects unknown fields and bounds every user-entered string.
`main.py` creates isolated application instances, validates/generates UUID
correlation IDs, adds the ID to responses, maps validation and missing-profile
failures to safe error envelopes, and publishes separate liveness/readiness paths.
Unexpected exceptions become an `internal_error` envelope with the same
correlation ID and no exception or submitted content.

`repository.py` implements the core protocol with a locked dictionary. Its state
belongs to one process and deliberately disappears on restart. This behavior is
an executable limitation, not a hidden persistence claim.

`observability.py` allow-lists log fields. Request bodies, display names, profile
summaries, and job descriptions are never copied into logs or span attributes.
The OpenTelemetry API uses its no-op provider until a later observability phase
approves an exporter.

## Web

`careerpilot-api.ts` owns the browser HTTP contract and converts safe API errors
into one typed error. `page.tsx` uses native labels, help associations, length
constraints, focus indicators, a disabled submit state, and a polite live region.
The result includes its disclaimer and correlation ID.

## Tests

- Unit tests inject sequential IDs and a fake repository.
- API tests cover health, invalid input, not-found errors, and correlation.
- Contract tests inspect generated OpenAPI.
- Python end-to-end tests cross HTTP, application, and temporary persistence.
- Frontend tests cross the UI/client boundary, exercise errors, and run axe-core.
- The restart test proves data loss after a new application instance.
