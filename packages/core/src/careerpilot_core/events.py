"""Versioned integration-event and in-app notification domain values."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum

SAFE_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
MAX_EVENT_FIELDS = 12
EVENT_SCHEMA_VERSION = 1
SUPPORTED_EVENT_TYPES = frozenset(
    {
        "application.preparation.completed",
        "application.follow_up.due",
        "approval.requested",
    }
)


class NotificationCategory(StrEnum):
    APPLICATION = "application"
    FOLLOW_UP = "follow_up"
    APPROVAL = "approval"


EVENT_CATEGORIES = {
    "application.preparation.completed": NotificationCategory.APPLICATION,
    "application.follow_up.due": NotificationCategory.FOLLOW_UP,
    "approval.requested": NotificationCategory.APPROVAL,
}


def _require_safe(value: str, field_name: str) -> None:
    if SAFE_VALUE.fullmatch(value) is None:
        raise ValueError(f"{field_name}_must_be_an_opaque_value")


@dataclass(frozen=True, slots=True)
class IntegrationEvent:
    """Immutable metadata-only envelope shared across transport boundaries."""

    event_id: str
    event_type: str
    schema_version: int
    occurred_at: str
    tenant_id: str
    aggregate_id: str
    sequence: int
    correlation_id: str
    data: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        string_fields = (
            "event_id",
            "event_type",
            "occurred_at",
            "tenant_id",
            "aggregate_id",
            "correlation_id",
        )
        if not all(isinstance(getattr(self, field), str) for field in string_fields):
            raise TypeError("event_field_type_invalid")
        if not isinstance(self.schema_version, int) or isinstance(
            self.schema_version, bool
        ):
            raise TypeError("event_schema_version_type_invalid")
        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool):
            raise TypeError("event_sequence_type_invalid")
        for field_name in ("event_id", "tenant_id", "aggregate_id", "correlation_id"):
            _require_safe(getattr(self, field_name), field_name)
        if self.event_type not in SUPPORTED_EVENT_TYPES:
            raise ValueError("event_type_unsupported")
        if self.schema_version != EVENT_SCHEMA_VERSION:
            raise ValueError("event_schema_version_unsupported")
        if self.sequence < 1:
            raise ValueError("event_sequence_must_be_positive")
        parsed = datetime.fromisoformat(self.occurred_at)
        if parsed.tzinfo is None:
            raise ValueError("occurred_at_requires_timezone")
        if len(self.data) > MAX_EVENT_FIELDS or len(
            {key for key, _ in self.data}
        ) != len(self.data):
            raise ValueError("event_data_invalid")
        for key, value in self.data:
            _require_safe(key, "event_data_key")
            _require_safe(value, "event_data_value")

    @classmethod
    def create(  # noqa: PLR0913 - fields mirror the explicit transport envelope
        cls,
        *,
        event_id: str,
        event_type: str,
        tenant_id: str,
        aggregate_id: str,
        sequence: int,
        correlation_id: str,
        data: tuple[tuple[str, str], ...],
        occurred_at: datetime | None = None,
    ) -> IntegrationEvent:
        timestamp = occurred_at or datetime.now(UTC)
        return cls(
            event_id=event_id,
            event_type=event_type,
            schema_version=EVENT_SCHEMA_VERSION,
            occurred_at=timestamp.isoformat(),
            tenant_id=tenant_id,
            aggregate_id=aggregate_id,
            sequence=sequence,
            correlation_id=correlation_id,
            data=data,
        )

    def to_json(self) -> bytes:
        """Serialize canonically for transport and compatibility tests."""
        payload = asdict(self)
        payload["data"] = dict(self.data)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def from_json(cls, raw: bytes) -> IntegrationEvent:
        """Validate an untrusted transport payload into the current schema."""
        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or set(parsed) != {
            "event_id",
            "event_type",
            "schema_version",
            "occurred_at",
            "tenant_id",
            "aggregate_id",
            "sequence",
            "correlation_id",
            "data",
        }:
            raise ValueError("event_envelope_shape_invalid")
        data = parsed.pop("data")
        if not isinstance(data, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in data.items()
        ):
            raise ValueError("event_data_shape_invalid")
        return cls(data=tuple(sorted(data.items())), **parsed)


@dataclass(frozen=True, slots=True)
class NotificationPreference:
    tenant_id: str
    actor_id: str
    enabled_categories: frozenset[NotificationCategory]


@dataclass(frozen=True, slots=True)
class InAppNotification:
    notification_id: str
    tenant_id: str
    actor_id: str
    event_id: str
    category: NotificationCategory
    subject_ref: str
    message_key: str
    created_at: str
    read_at: str | None = None
