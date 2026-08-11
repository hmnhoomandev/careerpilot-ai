"""Append-only audit integrity tests."""

from __future__ import annotations

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_core import AuditEventDraft


def test_audit_events_are_hash_chained_and_tenant_filtered() -> None:
    audit = InMemoryAuditLog()
    first = audit.append(
        AuditEventDraft(
            tenant_id="tenant-ada",
            actor_id="actor-ada",
            action="profile.create",
            outcome="allowed",
            reason="created",
            correlation_id="correlation-001",
        )
    )
    second = audit.append(
        AuditEventDraft(
            tenant_id="tenant-grace",
            actor_id="actor-grace",
            action="profile.read",
            outcome="denied",
            reason="tenant_mismatch",
            correlation_id="correlation-002",
        )
    )

    assert second.previous_hash == first.event_hash
    assert audit.verify_chain()
    assert audit.list_for_tenant("tenant-ada") == (first,)
