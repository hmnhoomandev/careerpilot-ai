"""Privacy lifecycle, backup restoration, KMS boundary, and SSRF tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from careerpilot_api.security_hardening import (
    LocalRateLimiter,
    ProductionSecurityConfiguration,
    UnsafeDestinationError,
    validate_outbound_destination,
)
from careerpilot_core import (
    AuthorizationContext,
    BackupIntegrityError,
    BackupRecord,
    DataRequestStatus,
    DataRight,
    KeyRotationPlan,
    PrivacyControlError,
    PrivacyControlService,
    Role,
    create_backup_snapshot,
    restore_backup_snapshot,
)


def context(
    tenant: str = "tenant-ada", actor: str = "actor-ada"
) -> AuthorizationContext:
    return AuthorizationContext(
        actor, tenant, Role.OWNER, "personal_career_support", "corr"
    )


def test_data_rights_require_step_up_and_exact_approval() -> None:
    service = PrivacyControlService()
    with pytest.raises(PrivacyControlError, match="step_up_required"):
        service.request(
            context(),
            DataRight.EXPORT,
            step_up_verified=False,
            approval_reference="approval-1",
        )
    with pytest.raises(PrivacyControlError, match="approval_required"):
        service.request(
            context(),
            DataRight.EXPORT,
            step_up_verified=True,
            approval_reference="request-1",
        )


def test_recoverable_deletion_can_cancel_and_becomes_purge_due() -> None:
    service = PrivacyControlService()
    now = datetime(2026, 8, 14, tzinfo=UTC)
    first = service.request(
        context(),
        DataRight.DELETION,
        step_up_verified=True,
        approval_reference="approval-delete-1",
        now=now,
    )
    assert first.status is DataRequestStatus.RECOVERABLE_DELETION
    assert first.purge_after == now + timedelta(days=30)
    assert (
        service.cancel_deletion(context(), first.request_id, now=now).status
        is DataRequestStatus.CANCELLED
    )

    second = service.request(
        context(),
        DataRight.DELETION,
        step_up_verified=True,
        approval_reference="approval-delete-2",
        now=now,
    )
    assert service.due_for_purge(now + timedelta(days=30)) == (
        replace(second, status=DataRequestStatus.PURGE_DUE),
    )


def test_deletion_cannot_be_cancelled_cross_tenant() -> None:
    service = PrivacyControlService()
    item = service.request(
        context(),
        DataRight.DELETION,
        step_up_verified=True,
        approval_reference="approval-delete-1",
    )
    with pytest.raises(PrivacyControlError, match="request_unavailable"):
        service.cancel_deletion(context("tenant-grace", "actor-grace"), item.request_id)


@pytest.mark.parametrize(
    ("url", "addresses"),
    [
        ("http://example.test/data", ("93.184.216.34",)),
        (  # pragma: allowlist secret - synthetic URL-userinfo attack fixture
            "https://user:pass@example.test/data",  # pragma: allowlist secret
            ("93.184.216.34",),
        ),
        ("https://example.test/data", ("127.0.0.1",)),
        ("https://example.test/data", ("169.254.169.254",)),
        ("https://unapproved.test/data", ("93.184.216.34",)),
    ],
)
def test_ssrf_policy_rejects_unsafe_destinations(
    url: str, addresses: tuple[str, ...]
) -> None:
    with pytest.raises(UnsafeDestinationError):
        validate_outbound_destination(
            url, resolved_addresses=addresses, allowed_hosts=frozenset({"example.test"})
        )


def test_ssrf_policy_accepts_only_approved_public_https() -> None:
    result = validate_outbound_destination(
        "https://example.test/data",
        resolved_addresses=("93.184.216.34",),
        allowed_hosts=frozenset({"example.test"}),
    )
    assert result.hostname == "example.test"
    assert result.port == 443


def test_rate_limiter_is_bounded_and_recovers_after_window() -> None:
    limiter = LocalRateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("tenant:actor", now=0)
    assert limiter.allow("tenant:actor", now=1)
    assert not limiter.allow("tenant:actor", now=2)
    assert limiter.allow("tenant:actor", now=11)


def test_production_security_configuration_fails_closed() -> None:
    with pytest.raises(ValueError, match="https_origin_required"):
        ProductionSecurityConfiguration(
            public_origin="http://careerpilot.test",
            managed_configuration_provider="gcp",
            kms_key_resource="key",
            edge_rate_limit_enabled=True,
        ).validate()
    with pytest.raises(ValueError, match="managed_key_boundary_required"):
        ProductionSecurityConfiguration(
            public_origin="https://careerpilot.test",
            managed_configuration_provider="",
            kms_key_resource="",
            edge_rate_limit_enabled=True,
        ).validate()
    with pytest.raises(ValueError, match="edge_rate_limit_required"):
        ProductionSecurityConfiguration(
            public_origin="https://careerpilot.test",
            managed_configuration_provider="gcp",
            kms_key_resource="key",
            edge_rate_limit_enabled=False,
        ).validate()


def test_backup_restore_applies_tombstones_and_tenant_scope() -> None:
    snapshot = create_backup_snapshot(
        (
            BackupRecord("tenant-ada", "profile-1", "profile"),
            BackupRecord("tenant-ada", "document-deleted", "document"),
            BackupRecord("tenant-grace", "profile-2", "profile"),
        ),
        ("document-deleted",),
    )
    assert restore_backup_snapshot(snapshot, isolated_tenant_id="tenant-ada") == (
        BackupRecord("tenant-ada", "profile-1", "profile"),
    )
    with pytest.raises(BackupIntegrityError):
        restore_backup_snapshot(
            replace(snapshot, sha256="0" * 64), isolated_tenant_id="tenant-ada"
        )


def test_key_rotation_plan_rejects_same_version() -> None:
    with pytest.raises(ValueError, match="key_versions_must_differ"):
        KeyRotationPlan("key-v1", "key-v1", "rotation-1").validate()
