# Phase 13 Review: Asynchronous Events and Notifications

## 1. Phase objective

Deliver a tenant-safe, fake-first asynchronous event and in-app notification foundation,
plus an explicit Pub/Sub adapter, without provisioning infrastructure or incurring cost.

## 2. Delivered features

- Strict canonical version 1 metadata-only integration-event envelope.
- Transaction-shaped business mutation/outbox recording and acknowledged dispatch.
- Consumer inbox deduplication, aggregate sequence enforcement, three-attempt policy,
  digest-only poison quarantine, dead-letter storage, and explicit replay.
- Injected Pub/Sub publisher and ack/nack subscriber boundaries using ordering keys.
- Authenticated notification preferences, listing, and read-receipt API routes.

## 3. Explicitly not delivered

No Pub/Sub resource/emulator/credential, Dapr sidecar, PostgreSQL event migration, email,
SMS, push, external communication, UI, deployment, live model, customer data, or paid call.

## 4. Files created/changed

Core event values; API eventing, Pub/Sub and notification modules/routes; permissions;
dependency lock; unit/API/contract tests; Phase 13 plan; ADR-0025; architecture and annotated
source; tutorial/exercises; security/privacy/dependency/risk notes; governance files and this
review changed.

## 5. Architecture decisions

Treat Pub/Sub as at-least-once regardless of broker options. Event IDs own deduplication,
aggregate IDs own ordering keys, sequences expose gaps, and source aggregates remain truth.
Use direct injected ports. Dapr is deferred until a measured cross-runtime need justifies its
operational and security surface.

## 6. Security/privacy review

Envelopes accept bounded opaque values only. Invalid raw payloads are not retained. Server-
derived identity scopes notification access to tenant and actor; foreign notification IDs
return the same not-found result as missing IDs. Production retention/deletion propagation,
broker residency/IAM/encryption, replay authority, lawful basis, and processor terms require
security/privacy and professional legal review. No compliance certification is claimed.

## 7. Data/schema/migration impact

No database schema or migration changed. Event, inbox, cursor, dead-letter, preference and
notification state is process-local and disposable. `google-cloud-pubsub` 2.39.1 and its
locked Apache-2.0-compatible transitive dependencies were added; no client was instantiated.

## 8. Automated commands and exact results

- Lock check, Ruff format/lint, and strict MyPy passed for 123 source files.
- Focused Phase 13 tests passed 11; full Pytest passed 182 with 6 expected skips and 4
  upstream ADK deprecation warnings. Four skips need local PostgreSQL and two live tests lack
  explicit model-cost/data-transfer approval.
- Frontend Prettier, ESLint, TypeScript, five Vitest tests, and Next.js build passed.
- Markdown lint passed 134 files; governance passed 24 required files, 74 requirement IDs,
  and 142 Markdown files; 11 Mermaid diagrams rendered; detect-secrets passed.
- External link validation was inconclusive (`Status: 0`) for pre-existing links because
  outbound DNS was unavailable. Pip and npm advisory audits were likewise inconclusive due
  unavailable registry DNS. Semgrep could not initialize its uv tool temporary directory in
  the sandbox; no Semgrep-pass claim is made. These are verification limitations, not found
  vulnerabilities.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Publish lifecycle | Pending remains on failure; acknowledged send becomes published | Automated pass; owner pending |
| Duplicate delivery | One notification | Automated pass; owner pending |
| Sequence gap/replay | Bounded retry, dead letter, then explicit recovery | Automated pass; owner pending |
| Poison bytes | Dead letter stores digest only | Automated pass; owner pending |
| Two tenants | No cross-tenant enumeration or read | Automated pass; owner pending |

## 10. Requirements traceability

FR-018 and NFR-009/012/013 map to notifications, versioned contracts and recoverable event
delivery. SEC-003/006/009/014 map to scoped authorization, metadata minimization, poison
quarantine, synthetic tests, and no live transport.

## 11. Example requests/responses

An authenticated user can `PUT /api/v1/notification-preferences` with
`{"enabled_categories":["approval"]}`, list `/api/v1/notifications`, and post to a selected
`/read` route. Responses expose opaque subject references and translation-ready message keys,
not career content or another actor's identifiers.

## 12. Known limitations, debt, and risks

- In-memory transactions do not prove database crash durability or concurrent leasing.
- Out-of-order policy lacks delayed scheduling/backoff timing; it proves bounded outcomes.
- Production Pub/Sub region, IAM, retention, quota, cost, monitoring and restore are open.
- Dead-letter replay needs operator authorization/audit/rate controls before production.
- Advisory/link scans need rerun when registry/network access is reliable; Semgrep needs a
  writable tool-cache execution environment.

## 13. Rollback/recovery instructions

Before Phase 14, revert the eventual Phase 13 commit and restore the lock. No database or
cloud rollback exists. Restarting the API discards all synthetic event/notification state.

## 14. Learning summary

Broker acknowledgement, consumer completion and business correctness are distinct. Outbox,
inbox, idempotency, ordering, bounded retry and explicit replay compose a recoverable design;
no broker feature removes the need for application-level effect safety.

## 15. Owner acceptance checklist

- Inspect ADR-0025 and the event-delivery architecture.
- Run focused tests and manually exercise duplicate, gap, poison and replay cases.
- Sign in as Ada and Grace and verify notification isolation/preferences.
- Accept process-local persistence and the disclosed scan/network limitations.

## 16. Proposed next phase

Phase 14 will implement the complete accessible UI and A2UI-compatible presentation only
after the exact phase gate. It is not started.

## 17. Exact approval command

`APPROVE PHASE 13 AND START PHASE 14`
