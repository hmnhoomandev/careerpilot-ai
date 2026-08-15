"""Provider-neutral production key-management and envelope-encryption boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class KeyManagementPort(Protocol):
    """Wrap data keys through an approved regional KMS without exposing master keys."""

    def wrap_data_key(self, plaintext_key: bytes, *, key_version: str) -> bytes:
        """Return a provider ciphertext for one ephemeral data key."""

    def unwrap_data_key(self, wrapped_key: bytes, *, key_version: str) -> bytes:
        """Recover a data key only inside an authorized workload boundary."""


@dataclass(frozen=True, slots=True)
class KeyRotationPlan:
    """Explicit versions needed for a resumable rotation and rollback window."""

    active_version: str
    previous_version: str | None
    rotation_id: str

    def validate(self) -> None:
        """Reject ambiguous rotation state before any provider mutation."""
        if not self.active_version or not self.rotation_id:
            raise ValueError("incomplete_rotation_plan")
        if self.previous_version == self.active_version:
            raise ValueError("key_versions_must_differ")
