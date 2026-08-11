"""Process-local append-only audit adapter with hash-chain integrity evidence."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict
from datetime import UTC, datetime

from careerpilot_core import AuditEvent, AuditEventDraft


class InMemoryAuditLog:
    """Append audit events; callers receive immutable values, never the list."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, draft: AuditEventDraft) -> AuditEvent:
        previous_hash = self._events[-1].event_hash if self._events else "0" * 64
        event_id = str(uuid.uuid4())
        occurred_at = datetime.now(UTC).isoformat()
        canonical = json.dumps(
            {
                **asdict(draft),
                "event_id": event_id,
                "occurred_at": occurred_at,
                "previous_hash": previous_hash,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        event_hash = hashlib.sha256(canonical.encode()).hexdigest()
        event = AuditEvent(
            event_id=event_id,
            occurred_at=occurred_at,
            previous_hash=previous_hash,
            event_hash=event_hash,
            **asdict(draft),
        )
        self._events.append(event)
        return event

    def list_for_tenant(self, tenant_id: str) -> tuple[AuditEvent, ...]:
        return tuple(event for event in self._events if event.tenant_id == tenant_id)

    def all_events(self) -> tuple[AuditEvent, ...]:
        """Testing/operations view; application routes must use tenant filtering."""
        return tuple(self._events)

    def verify_chain(self) -> bool:
        previous_hash = "0" * 64
        for event in self._events:
            if event.previous_hash != previous_hash:
                return False
            draft_fields = {
                key: value
                for key, value in asdict(event).items()
                if key not in {"event_hash", "previous_hash", "event_id", "occurred_at"}
            }
            canonical = json.dumps(
                {
                    **draft_fields,
                    "event_id": event.event_id,
                    "occurred_at": event.occurred_at,
                    "previous_hash": event.previous_hash,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            if hashlib.sha256(canonical.encode()).hexdigest() != event.event_hash:
                return False
            previous_hash = event.event_hash
        return True
