# ADR-0025: Versioned events, direct Pub/Sub, and local notifications

- Status: Accepted
- Date: 2026-08-14

## Context

CareerPilot needs asynchronous integration without turning broker delivery into business
truth. Duplicate, delayed, reordered, malformed, and poison messages are normal failure
modes. The CHF 0 development limit prohibits provisioned cloud resources.

## Decision

Use a strict metadata-only version 1 event envelope. The application transaction writes
the business change and outbox record together; a dispatcher marks an event published only
after transport acknowledgement. Consumers use `(consumer, event_id)` inbox receipts,
per-aggregate sequence cursors, bounded retry, and a digest-only dead-letter record.

Google Pub/Sub is the reference transport through an injected adapter. Assume at-least-once
delivery even where broker exactly-once features exist. Use the aggregate ID as ordering key.
The local deterministic transport remains the default. No topic, subscription, emulator,
credential, billing, or cloud resource is created in Phase 13.

Deliver only authenticated in-app notifications and user preferences. No email, push,
external communication, or silent transport/provider fallback is authorized.

Do not adopt Dapr now. Direct ports already provide the required testability and isolation;
a sidecar adds deployment, identity, policy, upgrade, observability, and failure surfaces
without demonstrated Phase 13 value. Reconsider only with a measured cross-runtime need.

## Consequences

PostgreSQL must eventually replace the process-local outbox, inbox, cursors, preferences,
dead letters, and notification projection in one migration-reviewed design. Operators need
lag, retry, dead-letter, ordering-gap, and replay controls. Production Pub/Sub setup requires
Zurich availability, IAM, encryption, retention, residency, cost, quota, and legal review.
