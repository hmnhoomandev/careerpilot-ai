# Backup, Restore, and Deletion Rehearsal

## Local rehearsal

Run `uv run pytest tests/unit/test_privacy_control.py -k backup`. The synthetic snapshot contains
only opaque tenant/category IDs. Restore verifies SHA-256 integrity, selects one isolated tenant and
applies deletion tombstones before returning records. Tampering aborts restoration.

## Production sequence

1. Authorize an isolated target and verify backup provenance, encryption key and retention window.
2. Disable external sends/models and restrict operators with time-bounded access.
3. Restore, then replay the durable deletion ledger/tombstones before application access.
4. Run tenant isolation, counts, integrity, migration and deletion propagation checks.
5. Destroy the rehearsal environment under approval and audit.

SHA-256 provides rehearsal integrity, not confidentiality or authenticity. Production backups need
KMS-backed authenticated encryption, immutable provenance, tested recovery objectives and scheduled
expiry. Final retention/deletion/legal-hold rules are `LEGAL REVIEW`.
