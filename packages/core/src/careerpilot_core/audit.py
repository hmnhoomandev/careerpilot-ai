"""Immutable-style security audit contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

AuditOutcome = Literal["allowed", "denied"]


@dataclass(frozen=True, slots=True)
class AuditEventDraft:
    tenant_id: str
    actor_id: str
    action: str
    outcome: AuditOutcome
    reason: str
    correlation_id: str
    resource_type: str | None = None
    resource_id: str | None = None


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    occurred_at: str
    tenant_id: str
    actor_id: str
    action: str
    outcome: AuditOutcome
    reason: str
    correlation_id: str
    resource_type: str | None
    resource_id: str | None
    previous_hash: str
    event_hash: str


class AuditSink(Protocol):
    def append(self, draft: AuditEventDraft) -> AuditEvent:
        """Append and return one immutable, integrity-linked event."""

    def list_for_tenant(self, tenant_id: str) -> tuple[AuditEvent, ...]:
        """Return events in append order for one tenant."""
