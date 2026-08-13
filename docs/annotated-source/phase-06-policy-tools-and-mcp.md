# Annotated Source: Phase 6 Policy Tools and MCP

## Domain metadata

`careerpilot_core.tooling` defines stable risk and error enums plus the immutable
`ToolCapability`. This file has no FastAPI, Pydantic, MCP, model, or database imports;
future agent runtimes can reason about capability policy without depending on adapters.

## Contracts and registry

`tool_contracts.py` uses strict Pydantic models. `extra="forbid"` prevents clients or
models from smuggling undeclared fields. Pydantic generates JSON Schema used by HTTP,
registry discovery, tests, and MCP function signatures.

`tool_catalog.py` is the one auditable capability inventory. Handler closures adapt
existing profile, retrieval, analysis, and audit services. Taxonomy, matching, approval
request, verification, and cost behavior are deterministic. The approval handler only
creates a pending identifier; it has no downstream action capability.

## Executor policy order

`ToolExecutor.execute` performs these steps:

1. Resolve an allowlisted name and validate its input schema.
2. Require generic `tool.invoke` and the capability-specific permission.
3. Apply a tenant/actor/tool rate limit.
4. Fingerprint validated input and enforce scoped idempotency where required.
5. Run a handler inside its timeout and bounded retry policy.
6. Validate the handler output against its declared model.
7. Recursively strip control characters and bound strings.
8. Cache idempotent output and append a content-free audit fact.

Unknown names and all failures use a stable safe taxonomy. Inputs, outputs, retrieved
passages, and reasons supplied by users never enter tool audit records.

## Transport adapters

FastAPI exposes authenticated discovery and invocation. `mcp_server.py` uses the
official SDK but registers only four read-only functions; every MCP call re-enters the
same executor with server-derived context. An equality assertion makes registry/MCP
allowlist drift fail during server construction.

`run_local_mcp.py` composes stdio transport with the synthetic local Ada identity. It
is a development demonstration, not production authentication or a remote service.
