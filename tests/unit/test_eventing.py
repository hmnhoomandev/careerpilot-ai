"""Failure-oriented tests for the Phase 13 event delivery boundary."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from careerpilot_api.eventing import (
    DeliveryOutcome,
    EventConsumer,
    InMemoryEventStore,
    LocalEventTransport,
    NotificationService,
    OutboxDispatcher,
    OutboxStatus,
)
from careerpilot_core import AccessPolicy, AuthorizationContext, IntegrationEvent, Role


def event(event_id: str = "event-1", *, sequence: int = 1) -> IntegrationEvent:
    return IntegrationEvent.create(
        event_id=event_id,
        event_type="application.preparation.completed",
        tenant_id="tenant-ada",
        aggregate_id="application-1",
        sequence=sequence,
        correlation_id="correlation-1",
        data=(("actor_id", "actor-ada"), ("subject_ref", "application-1")),
        occurred_at=datetime(2026, 8, 14, tzinfo=UTC),
    )


def context(
    actor: str = "actor-ada", tenant: str = "tenant-ada"
) -> AuthorizationContext:
    return AuthorizationContext(
        actor, tenant, Role.OWNER, "personal_career_support", "c-1"
    )


def test_envelope_round_trip_is_canonical_and_strict() -> None:
    original = event()
    assert IntegrationEvent.from_json(original.to_json()) == original
    with pytest.raises(ValueError, match="shape"):
        IntegrationEvent.from_json(original.to_json()[:-1] + b',"extra":1}')
    with pytest.raises(TypeError, match="type"):
        IntegrationEvent.from_json(
            original.to_json().replace(b'"event_id":"event-1"', b'"event_id":7')
        )


def test_business_change_and_outbox_are_atomic() -> None:
    store = InMemoryEventStore()
    with pytest.raises(RuntimeError, match="synthetic"):
        store.commit_change_and_event(
            tenant_id="tenant-ada",
            state_key="application-1",
            state_value="prepared",
            event=event(),
            fail_before_outbox=True,
        )
    assert store.business_state == {}
    assert store.outbox == {}


def test_dispatch_marks_only_acknowledged_publish() -> None:
    store = InMemoryEventStore()
    item = event()
    store.commit_change_and_event(
        tenant_id=item.tenant_id,
        state_key=item.aggregate_id,
        state_value="prepared",
        event=item,
    )
    transport = LocalEventTransport(fail_event_ids={item.event_id})
    dispatcher = OutboxDispatcher(store, transport)
    assert dispatcher.dispatch() == 0
    assert store.outbox[item.event_id].status is OutboxStatus.PENDING
    transport.fail_event_ids.clear()
    assert dispatcher.dispatch() == 1
    assert store.outbox[item.event_id].status is OutboxStatus.PUBLISHED


def test_duplicate_is_idempotent_and_handler_failure_is_retryable() -> None:
    store = InMemoryEventStore()
    consumer = EventConsumer(store)
    assert consumer.consume(event(), fail_handler=True) is DeliveryOutcome.RETRY
    assert store.notifications == {}
    assert consumer.consume(event()) is DeliveryOutcome.PROCESSED
    assert consumer.consume(event()) is DeliveryOutcome.DUPLICATE
    assert len(store.notifications) == 1


def test_out_of_order_event_dead_letters_then_replays() -> None:
    store = InMemoryEventStore()
    consumer = EventConsumer(store)
    second = event("event-2", sequence=2)
    assert consumer.consume(second) is DeliveryOutcome.RETRY
    assert consumer.consume(second) is DeliveryOutcome.RETRY
    assert consumer.consume(second) is DeliveryOutcome.DEAD_LETTERED
    assert consumer.consume(event()) is DeliveryOutcome.PROCESSED
    assert consumer.replay("event:event-2") is DeliveryOutcome.PROCESSED


def test_poison_payload_is_quarantined_without_retaining_content() -> None:
    store = InMemoryEventStore()
    outcome = EventConsumer(store).consume_bytes(b"private unstructured content")
    assert outcome is DeliveryOutcome.DEAD_LETTERED
    record = next(iter(store.dead_letters.values()))
    assert record.event is None
    assert "private" not in repr(record)


def test_preferences_and_authorization_scope_notifications() -> None:
    store = InMemoryEventStore()
    service = NotificationService(store, AccessPolicy())
    service.set_preference(context(), frozenset())
    assert EventConsumer(store).consume(event()) is DeliveryOutcome.PROCESSED
    assert service.list_notifications(context()) == ()
    assert service.list_notifications(context(tenant="tenant-grace")) == ()
