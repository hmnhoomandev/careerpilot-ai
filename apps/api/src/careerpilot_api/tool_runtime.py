"""Policy-enforcing registry and executor shared by HTTP and MCP adapters."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ValidationError

from careerpilot_core import (
    AccessDeniedError,
    AccessPolicy,
    AuditEventDraft,
    AuthorizationContext,
    Permission,
    ResourceAttributes,
    ToolCapability,
    ToolErrorCode,
    ToolExecutionError,
)

if TYPE_CHECKING:
    from careerpilot_core import AuditSink
    from careerpilot_core.audit import AuditOutcome

type Handler[InputT: BaseModel, OutputT: BaseModel] = Callable[
    [AuthorizationContext, InputT], Awaitable[OutputT]
]
MAX_OUTPUT_STRING = 5_000
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass(frozen=True, slots=True)
class ToolDefinition[InputT: BaseModel, OutputT: BaseModel]:
    """Bind capability policy to its schemas and implementation handler."""

    capability: ToolCapability
    input_model: type[InputT]
    output_model: type[OutputT]
    handler: Handler[InputT, OutputT]


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    """Validated output plus replay metadata for transport adapters."""

    capability: ToolCapability
    output: dict[str, object]
    idempotent_replay: bool


class ToolRegistry:
    """Deny duplicate or unknown capabilities and expose generated schemas."""

    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition[Any, Any]] = {}

    def register(self, definition: ToolDefinition[Any, Any]) -> None:
        name = definition.capability.name
        if name in self._definitions:
            raise ValueError("duplicate_tool_name")
        self._definitions[name] = definition

    def get(self, name: str) -> ToolDefinition[Any, Any] | None:
        return self._definitions.get(name)

    def definitions(self) -> tuple[ToolDefinition[Any, Any], ...]:
        return tuple(self._definitions[name] for name in sorted(self._definitions))

    def mcp_definitions(self) -> tuple[ToolDefinition[Any, Any], ...]:
        return tuple(
            definition
            for definition in self.definitions()
            if definition.capability.mcp_exposed
        )


class LocalRateLimiter:
    """Process-local fixed-window guard keyed by tenant, actor, and tool."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._calls: dict[tuple[str, str, str], deque[float]] = defaultdict(deque)

    def require(
        self, context: AuthorizationContext, capability: ToolCapability
    ) -> None:
        now = self._clock()
        key = (context.tenant_id, context.actor_id, capability.name)
        calls = self._calls[key]
        cutoff = now - capability.rate_window_seconds
        while calls and calls[0] <= cutoff:
            calls.popleft()
        if len(calls) >= capability.rate_limit:
            raise ToolExecutionError(
                ToolErrorCode.RATE_LIMITED, "Tool rate limit exceeded."
            )
        calls.append(now)


class ToolExecutor:
    """Validate and policy-check every invocation before one bounded handler call."""

    def __init__(
        self,
        registry: ToolRegistry,
        access_policy: AccessPolicy,
        audit_sink: AuditSink,
        rate_limiter: LocalRateLimiter | None = None,
    ) -> None:
        self.registry = registry
        self._access_policy = access_policy
        self._audit_sink = audit_sink
        self._rate_limiter = rate_limiter or LocalRateLimiter()
        self._idempotency: dict[
            tuple[str, str, str, str], tuple[str, dict[str, object]]
        ] = {}

    async def execute(
        self,
        name: str,
        context: AuthorizationContext,
        arguments: dict[str, object],
        idempotency_key: str | None = None,
    ) -> ToolExecutionResult:
        definition = self.registry.get(name)
        if definition is None:
            raise ToolExecutionError(ToolErrorCode.NOT_FOUND, "Tool is unavailable.")
        capability = definition.capability
        try:
            payload = definition.input_model.model_validate(arguments)
        except ValidationError as error:
            self._audit(context, capability.audit_action, "denied", "invalid_input")
            raise ToolExecutionError(
                ToolErrorCode.INVALID_INPUT, "Tool input did not match its schema."
            ) from error
        self._authorize(context, capability)
        try:
            self._rate_limiter.require(context, capability)
        except ToolExecutionError:
            self._audit(context, capability.audit_action, "denied", "rate_limited")
            raise
        fingerprint = self._fingerprint(payload)
        cache_key = self._idempotency_key(context, capability, idempotency_key)
        if capability.idempotency_required and cache_key is None:
            self._audit(
                context, capability.audit_action, "denied", "idempotency_required"
            )
            raise ToolExecutionError(
                ToolErrorCode.INVALID_INPUT, "An idempotency key is required."
            )
        if cache_key is not None and cache_key in self._idempotency:
            previous_fingerprint, cached_output = self._idempotency[cache_key]
            if previous_fingerprint != fingerprint:
                self._audit(
                    context,
                    capability.audit_action,
                    "denied",
                    "idempotency_conflict",
                )
                raise ToolExecutionError(
                    ToolErrorCode.IDEMPOTENCY_CONFLICT,
                    "The idempotency key was already used with different input.",
                )
            self._audit(
                context, capability.audit_action, "allowed", "idempotent_replay"
            )
            return ToolExecutionResult(
                capability, cached_output, idempotent_replay=True
            )

        handler_output = await self._run_bounded(definition, context, payload)
        try:
            validated = definition.output_model.model_validate(
                handler_output
            ).model_dump(mode="json")
        except ValidationError as error:
            self._audit(
                context, capability.audit_action, "denied", "invalid_tool_output"
            )
            raise ToolExecutionError(
                ToolErrorCode.INTERNAL, "Tool output validation failed."
            ) from error
        sanitized = _sanitize(validated)
        if cache_key is not None:
            self._idempotency[cache_key] = (fingerprint, sanitized)
        self._audit(context, capability.audit_action, "allowed", "completed")
        return ToolExecutionResult(capability, sanitized, idempotent_replay=False)

    def _authorize(
        self, context: AuthorizationContext, capability: ToolCapability
    ) -> None:
        resource = ResourceAttributes(context.tenant_id, context.actor_id)
        try:
            self._access_policy.require(context, Permission.TOOL_INVOKE, resource)
            if capability.permission is not Permission.TOOL_INVOKE:
                self._access_policy.require(context, capability.permission, resource)
        except AccessDeniedError as error:
            self._audit(context, capability.audit_action, "denied", error.reason)
            raise ToolExecutionError(
                ToolErrorCode.UNAUTHORIZED,
                "You do not have permission to invoke this tool.",
            ) from error

    async def _run_bounded(
        self,
        definition: ToolDefinition[Any, Any],
        context: AuthorizationContext,
        payload: BaseModel,
    ) -> BaseModel:
        attempts = definition.capability.max_retries + 1
        for attempt in range(attempts):
            try:
                async with asyncio.timeout(definition.capability.timeout_seconds):
                    return cast("BaseModel", await definition.handler(context, payload))
            except TimeoutError as error:
                if attempt + 1 == attempts:
                    self._audit(
                        context, definition.capability.audit_action, "denied", "timeout"
                    )
                    raise ToolExecutionError(
                        ToolErrorCode.TIMEOUT, "Tool execution timed out."
                    ) from error
            except AccessDeniedError as error:
                raise ToolExecutionError(
                    ToolErrorCode.UNAUTHORIZED,
                    "You do not have permission to invoke this tool.",
                ) from error
            except LookupError as error:
                raise ToolExecutionError(
                    ToolErrorCode.NOT_FOUND, "The requested resource is unavailable."
                ) from error
            except ValueError as error:
                raise ToolExecutionError(
                    ToolErrorCode.INVALID_INPUT, "The tool request was not accepted."
                ) from error
            except Exception as error:
                self._audit(
                    context,
                    definition.capability.audit_action,
                    "denied",
                    "internal_error",
                )
                raise ToolExecutionError(
                    ToolErrorCode.INTERNAL, "Tool execution failed."
                ) from error
        raise ToolExecutionError(ToolErrorCode.INTERNAL, "Tool execution failed.")

    @staticmethod
    def _fingerprint(payload: BaseModel) -> str:
        encoded = json.dumps(
            payload.model_dump(mode="json"), separators=(",", ":"), sort_keys=True
        ).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _idempotency_key(
        context: AuthorizationContext,
        capability: ToolCapability,
        supplied: str | None,
    ) -> tuple[str, str, str, str] | None:
        return (
            (context.tenant_id, context.actor_id, capability.name, supplied)
            if supplied
            else None
        )

    def _audit(
        self,
        context: AuthorizationContext,
        action: str,
        outcome: AuditOutcome,
        reason: str,
    ) -> None:
        self._audit_sink.append(
            AuditEventDraft(
                tenant_id=context.tenant_id,
                actor_id=context.actor_id,
                action=action,
                outcome=outcome,
                reason=reason,
                correlation_id=context.correlation_id,
                resource_type="tool",
            )
        )


def _sanitize(value: Any) -> Any:
    """Recursively remove control characters and enforce output string bounds."""
    if isinstance(value, str):
        return CONTROL_CHARACTERS.sub("", value)[:MAX_OUTPUT_STRING]
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    return value
