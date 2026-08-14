"""Explicit Google Pub/Sub transport adapter with no resource-creation behavior."""

from __future__ import annotations

from typing import Protocol

from careerpilot_api.eventing import DeliveryOutcome
from careerpilot_core import EVENT_SCHEMA_VERSION, IntegrationEvent


class PublishFuture(Protocol):
    def result(self, timeout: float | None = None) -> str: ...


class PublisherClient(Protocol):
    def topic_path(self, project: str, topic: str) -> str: ...

    def publish(
        self,
        topic: str,
        data: bytes,
        *,
        ordering_key: str,
        **attrs: str,
    ) -> PublishFuture: ...


class GooglePubSubPublisher:
    """Publish validated events to a pre-provisioned topic using aggregate ordering."""

    def __init__(
        self,
        client: PublisherClient,
        *,
        project_id: str,
        topic_id: str,
        timeout_seconds: float = 5,
    ) -> None:
        if not project_id or not topic_id or timeout_seconds <= 0:
            raise ValueError("pubsub_configuration_invalid")
        self._client = client
        self._topic_path = client.topic_path(project_id, topic_id)
        self._timeout_seconds = timeout_seconds

    def publish(self, event: IntegrationEvent) -> str:
        future = self._client.publish(
            self._topic_path,
            event.to_json(),
            ordering_key=event.aggregate_id,
            event_id=event.event_id,
            event_type=event.event_type,
            schema_version=str(EVENT_SCHEMA_VERSION),
            tenant_ref=event.tenant_id,
            correlation_id=event.correlation_id,
        )
        return future.result(timeout=self._timeout_seconds)


class SubscriberMessage(Protocol):
    data: bytes

    def ack(self) -> None: ...

    def nack(self) -> None: ...


class BytesConsumer(Protocol):
    def consume_bytes(self, raw: bytes) -> DeliveryOutcome: ...


class PubSubSubscriberBoundary:
    """Acknowledge only processed, duplicate, or safely dead-lettered deliveries."""

    def __init__(self, consumer: BytesConsumer) -> None:
        self._consumer = consumer

    def handle(self, message: SubscriberMessage) -> DeliveryOutcome:
        outcome = self._consumer.consume_bytes(message.data)
        if outcome is DeliveryOutcome.RETRY:
            message.nack()
        else:
            message.ack()
        return outcome
