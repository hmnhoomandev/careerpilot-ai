"""Unit evidence for timeout retry, output validation, and sanitization."""

import asyncio
from typing import Annotated, Any, cast

import pytest
from pydantic import BaseModel, ConfigDict, Field

from careerpilot_api.audit import InMemoryAuditLog
from careerpilot_api.tool_runtime import (
    LocalRateLimiter,
    ToolDefinition,
    ToolExecutor,
    ToolRegistry,
)
from careerpilot_core import (
    AccessPolicy,
    AuthorizationContext,
    Permission,
    Role,
    ToolCapability,
    ToolErrorCode,
    ToolExecutionError,
    ToolRisk,
)


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: Annotated[str, Field(min_length=1)]


class Output(BaseModel):
    value: str


def _context() -> AuthorizationContext:
    return AuthorizationContext(
        actor_id="actor-test",
        tenant_id="tenant-test",
        role=Role.OWNER,
        purpose="personal_career_support",
        correlation_id="tool-runtime-test",
    )


def _capability(*, timeout: float = 0.01, retries: int = 1) -> ToolCapability:
    return ToolCapability(
        name="test.read",
        version="1.0.0",
        description="Test capability.",
        permission=Permission.TOOL_INVOKE,
        risk=ToolRisk.READ_ONLY,
        side_effects=False,
        approval_required=False,
        timeout_seconds=timeout,
        max_retries=retries,
        idempotency_required=False,
        rate_limit=10,
        rate_window_seconds=60,
        audit_action="tool.test.read",
        mcp_exposed=False,
    )


@pytest.mark.asyncio
async def test_timeout_retries_then_returns_sanitized_output() -> None:
    attempts = 0

    async def handler(_context: AuthorizationContext, payload: Input) -> Output:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            await asyncio.sleep(0.02)
        return Output(value=f"{payload.value}\x00safe")

    registry = ToolRegistry()
    registry.register(ToolDefinition(_capability(), Input, Output, handler))
    executor = ToolExecutor(registry, AccessPolicy(), InMemoryAuditLog())
    result = await executor.execute("test.read", _context(), {"value": "synthetic"})
    assert attempts == 2
    assert result.output == {"value": "syntheticsafe"}


@pytest.mark.asyncio
async def test_exhausted_timeout_has_safe_taxonomy() -> None:
    async def handler(_context: AuthorizationContext, _payload: Input) -> Output:
        await asyncio.sleep(0.02)
        return Output(value="unreachable")

    registry = ToolRegistry()
    registry.register(ToolDefinition(_capability(retries=0), Input, Output, handler))
    executor = ToolExecutor(
        registry, AccessPolicy(), InMemoryAuditLog(), LocalRateLimiter()
    )
    with pytest.raises(ToolExecutionError) as captured:
        await executor.execute("test.read", _context(), {"value": "synthetic"})
    assert captured.value.code is ToolErrorCode.TIMEOUT


@pytest.mark.asyncio
async def test_invalid_handler_output_is_rejected_before_transport() -> None:
    async def handler(_context: AuthorizationContext, _payload: Input) -> Output:
        return cast("Output", cast("Any", {"unexpected": "unsafe"}))

    registry = ToolRegistry()
    registry.register(ToolDefinition(_capability(), Input, Output, handler))
    executor = ToolExecutor(registry, AccessPolicy(), InMemoryAuditLog())
    with pytest.raises(ToolExecutionError) as captured:
        await executor.execute("test.read", _context(), {"value": "synthetic"})
    assert captured.value.code is ToolErrorCode.INTERNAL
    assert captured.value.message == "Tool output validation failed."
