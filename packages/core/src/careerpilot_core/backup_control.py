"""Synthetic backup integrity and deletion-tombstone restoration model."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


class BackupIntegrityError(ValueError):
    """Raised when an isolated restore sees modified backup metadata."""


@dataclass(frozen=True, slots=True)
class BackupRecord:
    """Opaque tenant-owned reference; career content is deliberately excluded."""

    tenant_id: str
    record_id: str
    category: str


@dataclass(frozen=True, slots=True)
class BackupSnapshot:
    """Deterministic local rehearsal artifact with integrity metadata."""

    schema_version: str
    records: tuple[BackupRecord, ...]
    deletion_tombstones: tuple[str, ...]
    sha256: str


def create_backup_snapshot(
    records: tuple[BackupRecord, ...], deletion_tombstones: tuple[str, ...]
) -> BackupSnapshot:
    """Create local content-free metadata; production encryption is separate."""
    payload = _canonical_payload(records, deletion_tombstones)
    return BackupSnapshot(
        schema_version="careerpilot.backup-rehearsal.v1",
        records=records,
        deletion_tombstones=tuple(sorted(set(deletion_tombstones))),
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def restore_backup_snapshot(
    snapshot: BackupSnapshot, *, isolated_tenant_id: str
) -> tuple[BackupRecord, ...]:
    """Verify integrity/scope and never reactivate a tombstoned record."""
    expected = hashlib.sha256(
        _canonical_payload(snapshot.records, snapshot.deletion_tombstones)
    ).hexdigest()
    if snapshot.schema_version != "careerpilot.backup-rehearsal.v1":
        raise BackupIntegrityError("schema_not_supported")
    if snapshot.sha256 != expected:
        raise BackupIntegrityError("integrity_check_failed")
    tombstones = frozenset(snapshot.deletion_tombstones)
    return tuple(
        record
        for record in snapshot.records
        if record.tenant_id == isolated_tenant_id and record.record_id not in tombstones
    )


def _canonical_payload(
    records: tuple[BackupRecord, ...], deletion_tombstones: tuple[str, ...]
) -> bytes:
    data = {
        "records": [
            {
                "category": item.category,
                "record_id": item.record_id,
                "tenant_id": item.tenant_id,
            }
            for item in records
        ],
        "tombstones": sorted(set(deletion_tombstones)),
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
