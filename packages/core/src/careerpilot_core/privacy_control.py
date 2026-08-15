"""Framework-neutral privacy-rights and recoverable-deletion controls."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from threading import RLock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from careerpilot_core.access import AuthorizationContext

RECOVERY_WINDOW_DAYS = 30
MAX_PURPOSE_LENGTH = 80


class DataRight(StrEnum):
    """Supported data-subject request categories."""

    ACCESS = "access"
    CORRECTION = "correction"
    EXPORT = "export"
    DELETION = "deletion"


class DataRequestStatus(StrEnum):
    """Auditable lifecycle without implying physical deletion completed."""

    PENDING_REVIEW = "pending_review"
    READY = "ready"
    RECOVERABLE_DELETION = "recoverable_deletion"
    CANCELLED = "cancelled"
    PURGE_DUE = "purge_due"


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    """One purpose-specific consent signal; lawful basis remains legal review."""

    purpose: str
    granted: bool
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class DataInventoryItem:
    """Minimized category/count entry for access and export manifests."""

    category: str
    record_count: int
    lifecycle: str


@dataclass(frozen=True, slots=True)
class DataSubjectRequest:
    """Tenant/subject-bound request with exact approval and recovery state."""

    request_id: str
    tenant_id: str
    actor_id: str
    right: DataRight
    status: DataRequestStatus
    requested_at: datetime
    approval_reference: str
    purge_after: datetime | None = None


class PrivacyControlError(ValueError):
    """Raised for missing step-up, approval, or invalid lifecycle transitions."""


class PrivacyControlService:
    """Hold local privacy decisions behind tenant and subject scoped keys."""

    def __init__(self) -> None:
        self._requests: dict[str, DataSubjectRequest] = {}
        self._consents: dict[tuple[str, str, str], ConsentRecord] = {}
        self._lock = RLock()

    def inventory(self, context: AuthorizationContext) -> tuple[DataInventoryItem, ...]:
        """Describe in-scope stores without exposing their content."""
        del context
        return (
            DataInventoryItem("identity_and_membership", 1, "active"),
            DataInventoryItem("profile_and_evidence", 0, "source_linked"),
            DataInventoryItem("derived_and_vector_data", 0, "follows_source"),
            DataInventoryItem("workflow_and_events", 0, "metadata_only"),
            DataInventoryItem("security_and_audit", 0, "separate_legal_review"),
        )

    def record_consent(
        self, context: AuthorizationContext, purpose: str, *, granted: bool
    ) -> ConsentRecord:
        """Record or withdraw a bounded purpose-specific signal."""
        normalized = purpose.strip()
        if not normalized or len(normalized) > MAX_PURPOSE_LENGTH:
            raise PrivacyControlError("purpose_not_allowed")
        record = ConsentRecord(normalized, granted, datetime.now(UTC))
        with self._lock:
            self._consents[(context.tenant_id, context.actor_id, normalized)] = record
        return record

    def request(
        self,
        context: AuthorizationContext,
        right: DataRight,
        *,
        step_up_verified: bool,
        approval_reference: str,
        now: datetime | None = None,
    ) -> DataSubjectRequest:
        """Create an exact approved request; deletion remains recoverable."""
        if not step_up_verified:
            raise PrivacyControlError("step_up_required")
        if not approval_reference.startswith("approval-"):
            raise PrivacyControlError("approval_required")
        requested_at = now or datetime.now(UTC)
        if requested_at.tzinfo is None:
            raise PrivacyControlError("timezone_required")
        if right is DataRight.DELETION:
            status = DataRequestStatus.RECOVERABLE_DELETION
            purge_after = requested_at + timedelta(days=RECOVERY_WINDOW_DAYS)
        elif right in {DataRight.ACCESS, DataRight.EXPORT}:
            status = DataRequestStatus.READY
            purge_after = None
        else:
            status = DataRequestStatus.PENDING_REVIEW
            purge_after = None
        item = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            tenant_id=context.tenant_id,
            actor_id=context.actor_id,
            right=right,
            status=status,
            requested_at=requested_at,
            approval_reference=approval_reference,
            purge_after=purge_after,
        )
        with self._lock:
            self._requests[item.request_id] = item
        return item

    def cancel_deletion(
        self,
        context: AuthorizationContext,
        request_id: str,
        *,
        now: datetime | None = None,
    ) -> DataSubjectRequest:
        """Cancel only the subject's deletion before its purge deadline."""
        current_time = now or datetime.now(UTC)
        with self._lock:
            item = self._requests.get(request_id)
            if (
                item is None
                or item.tenant_id != context.tenant_id
                or item.actor_id != context.actor_id
            ):
                raise PrivacyControlError("request_unavailable")
            if item.status is not DataRequestStatus.RECOVERABLE_DELETION:
                raise PrivacyControlError("deletion_not_recoverable")
            if item.purge_after is None or current_time >= item.purge_after:
                raise PrivacyControlError("recovery_window_closed")
            cancelled = replace(item, status=DataRequestStatus.CANCELLED)
            self._requests[request_id] = cancelled
            return cancelled

    def due_for_purge(self, now: datetime) -> tuple[DataSubjectRequest, ...]:
        """Return due tombstones; a durable worker must perform physical purge."""
        if now.tzinfo is None:
            raise PrivacyControlError("timezone_required")
        with self._lock:
            due = []
            for request_id, item in self._requests.items():
                if (
                    item.status is DataRequestStatus.RECOVERABLE_DELETION
                    and item.purge_after is not None
                    and now >= item.purge_after
                ):
                    purge_item = replace(item, status=DataRequestStatus.PURGE_DUE)
                    self._requests[request_id] = purge_item
                    due.append(purge_item)
            return tuple(due)
