"""Framework-independent capability metadata and stable tool error taxonomy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from careerpilot_core.access import Permission


class ToolRisk(StrEnum):
    """Consequential-risk classification used by policy and discovery."""

    READ_ONLY = "read_only"
    LOW = "low"
    HIGH = "high"


class ToolErrorCode(StrEnum):
    """Safe machine-readable failures shared by HTTP and MCP adapters."""

    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    INTERNAL = "internal_error"


@dataclass(frozen=True, slots=True)
class ToolCapability:
    """Immutable policy and operational contract for one registered tool."""

    name: str
    version: str
    description: str
    permission: Permission
    risk: ToolRisk
    side_effects: bool
    approval_required: bool
    timeout_seconds: float
    max_retries: int
    idempotency_required: bool
    rate_limit: int
    rate_window_seconds: int
    audit_action: str
    mcp_exposed: bool


class ToolExecutionError(RuntimeError):
    """Stable safe tool failure without handler or infrastructure details."""

    def __init__(self, code: ToolErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
