"""Contract tests for explicit Pub/Sub publish and subscriber semantics."""

from __future__ import annotations

from datetime import UTC, datetime

from careerpilot_api.eventing import DeliveryOutcome, EventConsumer, InMemoryEventStore
from careerpilot_api.pubsub_adapter import (
    GooglePubSubPublisher,
    PubSubSubscriberBoundary,
)
from careerpilot_core import IntegrationEvent


def event() -> IntegrationEvent:
    return IntegrationEvent.create(
        event_id="event-1",
        event_type="approval.requested",
        tenant_id="tenant-ada",
        aggregate_id="draft-1",
        sequence=1,
        correlation_id="correlation-1",
        data=(("actor_id", "actor-ada"), ("subject_ref", "draft-1")),
        occurred_at=datetime(2026, 8, 14, tzinfo=UTC),
    )


class Future:
    def result(self, timeout: float | None = None) -> str:
        assert timeout == 5
        return "message-1"


class Client:
    def __init__(self) -> None:
        self.call: tuple[object, ...] | None = None

    def topic_path(self, project: str, topic: str) -> str:
        return f"projects/{project}/topics/{topic}"

    def publish(
        self, topic: str, data: bytes, *, ordering_key: str, **attrs: str
    ) -> Future:
        self.call = (topic, data, ordering_key, attrs)
        return Future()


class Message:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.acked = False
        self.nacked = False

    def ack(self) -> None:
        self.acked = True

    def nack(self) -> None:
        self.nacked = True


def test_publisher_uses_canonical_bytes_and_aggregate_ordering_key() -> None:
    client = Client()
    item = event()
    assert (
        GooglePubSubPublisher(client, project_id="project", topic_id="events").publish(
            item
        )
        == "message-1"
    )
    assert client.call is not None
    assert client.call[0:3] == (
        "projects/project/topics/events",
        item.to_json(),
        "draft-1",
    )


def test_subscriber_acks_success_and_nacks_retry() -> None:
    consumer = EventConsumer(InMemoryEventStore())
    boundary = PubSubSubscriberBoundary(consumer)
    successful = Message(event().to_json())
    assert boundary.handle(successful) is DeliveryOutcome.PROCESSED
    assert successful.acked
    gap = Message(event().to_json().replace(b'"sequence":1', b'"sequence":3'))
    assert boundary.handle(gap) is DeliveryOutcome.DUPLICATE
    # A distinct out-of-order event requests broker redelivery.
    retry_data = (
        event()
        .to_json()
        .replace(b'"event_id":"event-1"', b'"event_id":"event-2"')
        .replace(b'"sequence":1', b'"sequence":3')
    )
    retry = Message(retry_data)
    assert boundary.handle(retry) is DeliveryOutcome.RETRY
    assert retry.nacked
