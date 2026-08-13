# ADR-0018: Policy-Enforced Tool Registry and MCP Allowlist

- **Status:** Accepted for Phase 6
- **Date:** 2026-08-11

## Context

Future agents need capabilities, but a Python function exposed directly to a model has
no reliable security contract. Tool schemas alone do not provide authorization,
tenant isolation, timeouts, replay protection, quotas, output validation, or audit.
MCP discovery also risks publishing internal or consequential capabilities broadly.

## Decision

Use one registry as the authority for HTTP and MCP capability discovery. Every entry
binds strict Pydantic input/output models to immutable metadata and an async handler.
All calls traverse one executor that validates input, derives authorization from the
server context, rate-limits locally, enforces idempotency, bounds timeout/retry,
validates and sanitizes output, maps safe errors, and records metadata-only audit facts.
Underlying services retain their own resource authorization.

Expose only `profile.lookup`, `evidence.retrieve`, `skill.taxonomy`, and
`cost.estimate` through MCP. The other five tools remain HTTP/internal. MCP does not
replace A2A: MCP exposes narrow functions; A2A later connects independently deployed
agents with their own identity and lifecycle.

Use the official MCP Python SDK `>=1.28.1,<1.29` (MIT, Python 3.10+), the first stable
line that resolves all three advisories reported for 1.23.3 by the phase security
audit. Pinned Semgrep 1.172.0 still requires `mcp==1.23.3`, so run that CLI through
an isolated, separately resolved `uvx` environment instead of allowing a SAST-only
transitive dependency to downgrade the application runtime. A handwritten JSON-RPC
implementation was rejected because it would increase protocol, validation, and
security maintenance risk.

## Consequences

- HTTP and MCP schemas can be compatibility-tested from the same registry.
- Idempotency and rate-limit caches are intentionally process-local and reset on
  restart; distributed production enforcement is deferred.
- The approval tool creates only a pending request and never executes the requested
  action. Full durable approval states arrive in Phase 8.
- Local MCP uses synthetic Ada authority over stdio. Production MCP authentication,
  OAuth/resource-server behavior, remote transport, and deployment are not enabled.
- The isolated Semgrep environment contains the vulnerable MCP transitive dependency,
  but it is not shipped, imported, or reachable by the application. Revisit the
  isolation when Semgrep no longer pins that version.
- MCP 1.28.1 with the current Pydantic Settings version still emits a known
  `lifespan` forward-reference warning during server construction. The MCP contract
  test captures that exact warning so an upstream change remains visible; in-memory
  initialization, discovery, schema exchange, and tool calls remain successful.
