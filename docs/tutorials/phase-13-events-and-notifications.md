# Phase 13 tutorial: reliable events and in-app notifications

An event broker may deliver twice, late, or out of order. CareerPilot therefore does not
equate delivery with correctness. A business operation records its event in an outbox in the
same transaction. A dispatcher publishes it and records the acknowledgement. The consumer
checks an inbox receipt and aggregate sequence before projecting a notification.

Run the focused lesson with:

```bash
UV_CACHE_DIR=/tmp/careerpilot-uv-cache uv run pytest tests/unit/test_eventing.py tests/contract/test_pubsub_adapter.py tests/api/test_notifications_api.py -q
```

Change a test to deliver sequence 2 before sequence 1. Observe two retries and a dead letter,
then process sequence 1 and explicitly replay sequence 2. This is recovery, not silent
fallback. Also disable the application category and observe that the event is processed but
no notification is created.

Phase 13 stays local and free. The Pub/Sub class is only a tested adapter for a future,
separately approved deployment. Never use real personal data in these exercises.
