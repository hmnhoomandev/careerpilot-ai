# Annotated source: event delivery

`packages/core/src/careerpilot_core/events.py` defines the transport-independent envelope.
Opaque-value validation prevents accidental personal prose from crossing the bus, while
canonical JSON makes compatibility and digest checks deterministic.

`apps/api/src/careerpilot_api/eventing.py` demonstrates the transactional outbox, publish
acknowledgement, inbox idempotency, aggregate ordering, retry/dead-letter behavior, and the
notification projection. Its in-memory store is intentionally an adapter, not production
durability.

`apps/api/src/careerpilot_api/pubsub_adapter.py` is a narrow boundary around an injected
official client. It cannot create resources and it nacks only retryable deliveries.
`notification_contracts.py` and `main.py` expose authenticated preferences, listing, and
read receipts without exposing tenant or actor selection in request bodies.
