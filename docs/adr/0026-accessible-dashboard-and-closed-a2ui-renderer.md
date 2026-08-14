# ADR-0026: Accessible dashboard and closed A2UI renderer

- Status: Accepted
- Date: 2026-08-14

## Context

The web application exposed several phases through one long development-preview page. It
did not provide a coherent journey, durable navigation model, explicit degraded states, or
a reusable boundary for server-supplied A2UI-compatible presentation messages.

## Decision

Use a responsive Next.js dashboard with semantic landmarks, in-page workspace navigation,
visible focus, a skip link, independent feature panels and centralized status messaging.
FastAPI remains authoritative for identity, tenancy, policy and business transitions.

Treat every A2UI message as untrusted data. Render only schema `careerpilot.a2ui.v1`, the
`editable_career_draft` and `approval_review` components, and their closed action allowlist.
React text escaping is mandatory; arbitrary HTML, URLs, components and actions fail closed.
An A2UI action is a presentation intent and never grants permission.

Do not add a component framework, icon package, state library, browser persistence or visual
regression service. Existing React, CSS, Testing Library and axe provide a smaller zero-cost
boundary. Reconsider only when repeated components or stable screenshot infrastructure show
measurable maintenance value.

## Consequences

The workspace is useful across mobile and desktop and exposes unavailable capabilities
honestly. Some panels remain local demonstrations because their production gateways are not
activated. Full translations, production sessions, deep-link routing, server rendering of
authenticated data and screenshot baselines remain later decisions.
