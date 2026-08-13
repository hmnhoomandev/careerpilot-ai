# Tutorial: Typed Tools, Policy, and MCP

## Mental model

A tool is a small capability contract, not an agent. It should do one bounded job and
return structured data. A registry answers “what exists?” Metadata answers “under what
rules?” The executor answers “may this authenticated actor call it now?” The handler
then performs the smallest operation, while its underlying service checks the actual
resource again.

MCP is a transport/discovery boundary for tools. It does not grant permission and it
does not turn a function into an autonomous agent. CareerPilot publishes only four
read-only tools through MCP.

## HTTP walkthrough

1. Run `make dev`, open API documentation at `http://127.0.0.1:8000/docs`, and create
   a synthetic local session through the existing login endpoint.
2. Supply the bearer token and `X-CareerPilot-Tenant-ID: tenant-ada`.
3. Call `GET /api/v1/tools`. Inspect input/output JSON Schema, permission, risk,
   timeout, retry, idempotency, rate limit, audit action, and MCP exposure.
4. Invoke `cost.estimate` with `{"arguments":{"workflow":"retrieval","units":2}}`.
   The result is CHF 0 and explicitly does not authorize spending.
5. Invoke `approval.request` twice with the same input and idempotency key. The second
   response sets `idempotent_replay=true` and returns the same pending approval ID.
6. Reuse that key with different input and observe a safe conflict.
7. Sign in as Sam and invoke `audit.lookup`; observe a safe permission denial.

## MCP walkthrough

Run `make mcp-local` from an MCP-compatible stdio host configuration. Discovery exposes
only profile lookup, cited retrieval, local taxonomy, and cost estimation. The local
server uses synthetic Ada context, contains no model/provider call, and loses its local
state on restart. Remote HTTP MCP and production OAuth are intentionally unavailable.
