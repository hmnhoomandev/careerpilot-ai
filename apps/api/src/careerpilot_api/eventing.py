"""Transactional event adapters, delivery policy, and notification projection."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Protocol

from careerpilot_core import (
    EVENT_CATEGORIES,
    AccessPolicy,
    AuthorizationContext,
    InAppNotification,
    IntegrationEvent,
    NotificationCategory,
    NotificationPreference,
    Permission,
    ResourceAttributes,
)

MAX_DELIVERY_ATTEMPTS = 3


class DeliveryOutcome(StrEnum):
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    RETRY = "retry"
    DEAD_LETTERED = "dead_lettered"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    PUBLISHED = "published"


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    event: IntegrationEvent
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0
    transport_message_id: str | None = None


@dataclass(frozen=True, slots=True)
class DeadLetterRecord:
    dead_letter_id: str
    reason: str
    attempts: int
    event: IntegrationEvent | None
    raw_digest: str


class EventPublisher(Protocol):
    def publish(self, event: IntegrationEvent) -> str: ...


class InMemoryEventStore:
    """Transaction-shaped local adapter; PostgreSQL replaces it in production."""

    def __init__(self) -> None:
        self.business_state: dict[tuple[str, str], str] = {}
        self.outbox: dict[str, OutboxRecord] = {}
        self.inbox: set[tuple[str, str]] = set()
        self.sequence_cursor: dict[tuple[str, str, str], int] = {}
        self.delivery_attempts: dict[tuple[str, str], int] = {}
        self.dead_letters: dict[str, DeadLetterRecord] = {}
        self.notifications: dict[str, InAppNotification] = {}
        self.preferences: dict[tuple[str, str], NotificationPreference] = {}

    def commit_change_and_event(
        self,
        *,
        tenant_id: str,
        state_key: str,
        state_value: str,
        event: IntegrationEvent,
        fail_before_outbox: bool = False,
    ) -> None:
        """Atomically model one business mutation and its outbox record."""
        if tenant_id != event.tenant_id:
            raise ValueError("event_tenant_mismatch")
        key = (tenant_id, state_key)
        previous = self.business_state.get(key)
        self.business_state[key] = state_value
        try:
            if fail_before_outbox:
                raise RuntimeError("synthetic_transaction_failure")  # noqa: TRY301
            existing = self.outbox.get(event.event_id)
            if existing is not None and existing.event != event:
                raise ValueError("event_id_conflict")  # noqa: TRY301
            self.outbox[event.event_id] = existing or OutboxRecord(event)
        except Exception:
            if previous is None:
                self.business_state.pop(key, None)
            else:
                self.business_state[key] = previous
            raise

    def preference(self, tenant_id: str, actor_id: str) -> NotificationPreference:
        return self.preferences.get(
            (tenant_id, actor_id),
            NotificationPreference(
                tenant_id,
                actor_id,
                frozenset(NotificationCategory),
            ),
        )


class OutboxDispatcher:
    """Publish pending records and mark only acknowledged sends as complete."""

    def __init__(self, store: InMemoryEventStore, publisher: EventPublisher) -> None:
        self._store = store
        self._publisher = publisher

    def dispatch(self) -> int:
        published = 0
        for event_id, record in tuple(self._store.outbox.items()):
            if record.status is OutboxStatus.PUBLISHED:
                continue
            attempts = record.attempts + 1
            try:
                message_id = self._publisher.publish(record.event)
            except Exception:  # noqa: BLE001 - transport implementations define failures
                self._store.outbox[event_id] = replace(record, attempts=attempts)
                continue
            self._store.outbox[event_id] = replace(
                record,
                status=OutboxStatus.PUBLISHED,
                attempts=attempts,
                transport_message_id=message_id,
            )
            published += 1
        return published


class LocalEventTransport:
    """Deterministic local sink that can replay, duplicate, or reorder deliveries."""

    def __init__(self, *, fail_event_ids: set[str] | None = None) -> None:
        self.messages: list[IntegrationEvent] = []
        self.fail_event_ids = fail_event_ids or set()

    def publish(self, event: IntegrationEvent) -> str:
        if event.event_id in self.fail_event_ids:
            raise ConnectionError("local_transport_unavailable")
        self.messages.append(event)
        return f"local:{event.event_id}"


class EventConsumer:
    """Deduplicate, order, quarantine, and project safe in-app notifications."""

    def __init__(
        self,
        store: InMemoryEventStore,
        *,
        consumer_name: str = "notification-projector-v1",
        max_attempts: int = MAX_DELIVERY_ATTEMPTS,
    ) -> None:
        self._store = store
        self._consumer_name = consumer_name
        self._max_attempts = max_attempts

    def consume(
        self, event: IntegrationEvent, *, fail_handler: bool = False
    ) -> DeliveryOutcome:
        receipt = (self._consumer_name, event.event_id)
        if receipt in self._store.inbox:
            return DeliveryOutcome.DUPLICATE
        cursor_key = (event.tenant_id, self._consumer_name, event.aggregate_id)
        expected = self._store.sequence_cursor.get(cursor_key, 0) + 1
        if event.sequence != expected:
            reason = "sequence_gap" if event.sequence > expected else "stale_sequence"
            return self._retry_or_dead_letter(event, reason)
        try:
            notification = self._notification(event)
            if fail_handler:
                raise RuntimeError("synthetic_handler_failure")  # noqa: TRY301
            if notification is not None:
                self._store.notifications[notification.notification_id] = notification
            self._store.inbox.add(receipt)
            self._store.sequence_cursor[cursor_key] = event.sequence
            self._store.delivery_attempts.pop(receipt, None)
        except Exception:  # noqa: BLE001 - handler failures must trigger retry policy
            return self._retry_or_dead_letter(event, "handler_rejected")
        return DeliveryOutcome.PROCESSED

    def consume_bytes(self, raw: bytes) -> DeliveryOutcome:
        try:
            event = IntegrationEvent.from_json(raw)
        except (TypeError, ValueError):
            digest = hashlib.sha256(raw).hexdigest()
            dead_letter_id = f"raw:{digest[:32]}"
            self._store.dead_letters[dead_letter_id] = DeadLetterRecord(
                dead_letter_id=dead_letter_id,
                reason="invalid_envelope",
                attempts=1,
                event=None,
                raw_digest=digest,
            )
            return DeliveryOutcome.DEAD_LETTERED
        return self.consume(event)

    def replay(self, dead_letter_id: str) -> DeliveryOutcome:
        record = self._store.dead_letters.get(dead_letter_id)
        if record is None or record.event is None:
            raise ValueError("dead_letter_not_replayable")
        self._store.dead_letters.pop(dead_letter_id)
        self._store.delivery_attempts.pop(
            (self._consumer_name, record.event.event_id), None
        )
        return self.consume(record.event)

    def _retry_or_dead_letter(
        self, event: IntegrationEvent, reason: str
    ) -> DeliveryOutcome:
        key = (self._consumer_name, event.event_id)
        attempts = self._store.delivery_attempts.get(key, 0) + 1
        self._store.delivery_attempts[key] = attempts
        if attempts < self._max_attempts:
            return DeliveryOutcome.RETRY
        dead_letter_id = f"event:{event.event_id}"
        self._store.dead_letters[dead_letter_id] = DeadLetterRecord(
            dead_letter_id=dead_letter_id,
            reason=reason,
            attempts=attempts,
            event=event,
            raw_digest=hashlib.sha256(event.to_json()).hexdigest(),
        )
        return DeliveryOutcome.DEAD_LETTERED

    def _notification(self, event: IntegrationEvent) -> InAppNotification | None:
        fields = dict(event.data)
        if set(fields) != {"actor_id", "subject_ref"}:
            raise ValueError("notification_event_data_invalid")
        actor_id = fields["actor_id"]
        category = EVENT_CATEGORIES[event.event_type]
        preference = self._store.preference(event.tenant_id, actor_id)
        if category not in preference.enabled_categories:
            return None
        return InAppNotification(
            notification_id=f"notification:{event.event_id}",
            tenant_id=event.tenant_id,
            actor_id=actor_id,
            event_id=event.event_id,
            category=category,
            subject_ref=fields["subject_ref"],
            message_key=f"notification.{event.event_type}",
            created_at=event.occurred_at,
        )


class NotificationService:
    """Authorize tenant-scoped notification preferences, reads, and read receipts."""

    def __init__(self, store: InMemoryEventStore, policy: AccessPolicy) -> None:
        self._store = store
        self._policy = policy

    @staticmethod
    def _resource(context: AuthorizationContext) -> ResourceAttributes:
        return ResourceAttributes(context.tenant_id, context.actor_id)

    def set_preference(
        self,
        context: AuthorizationContext,
        categories: frozenset[NotificationCategory],
    ) -> NotificationPreference:
        self._policy.require(
            context, Permission.NOTIFICATION_MANAGE, self._resource(context)
        )
        preference = NotificationPreference(
            context.tenant_id, context.actor_id, categories
        )
        self._store.preferences[(context.tenant_id, context.actor_id)] = preference
        return preference

    def preference(self, context: AuthorizationContext) -> NotificationPreference:
        self._policy.require(
            context, Permission.NOTIFICATION_READ, self._resource(context)
        )
        return self._store.preference(context.tenant_id, context.actor_id)

    def list_notifications(
        self, context: AuthorizationContext
    ) -> tuple[InAppNotification, ...]:
        self._policy.require(
            context, Permission.NOTIFICATION_READ, self._resource(context)
        )
        return tuple(
            item
            for item in self._store.notifications.values()
            if item.tenant_id == context.tenant_id and item.actor_id == context.actor_id
        )

    def mark_read(
        self, context: AuthorizationContext, notification_id: str, *, read_at: str
    ) -> InAppNotification:
        self._policy.require(
            context, Permission.NOTIFICATION_MANAGE, self._resource(context)
        )
        item = self._store.notifications.get(notification_id)
        if (
            item is None
            or item.tenant_id != context.tenant_id
            or item.actor_id != context.actor_id
        ):
            raise NotificationNotFoundError
        updated = replace(item, read_at=read_at)
        self._store.notifications[notification_id] = updated
        return updated


class NotificationNotFoundError(LookupError):
    """Keep missing and cross-tenant notification lookups non-enumerating."""
