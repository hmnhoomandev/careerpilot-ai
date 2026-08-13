# Phase 06 Review: Typed Tools, Policy, and MCP

## Objective and delivered outcome

Phase 6 delivers a deterministic, model-free capability layer for later agents. Nine
narrow tools share strict Pydantic contracts, generated JSON Schema, one policy-aware
registry, one bounded executor, authenticated HTTP discovery/invocation, and safe
error envelopes. Four explicitly approved read-only tools are also available through
an official MCP stdio server for local learning and protocol verification.

## Security and privacy review

- Every call derives actor and tenant authority from server context and passes both
  generic tool permission and capability-specific authorization.
- Input and output fail closed against strict schemas; returned strings are bounded
  and stripped of control characters before crossing a transport boundary.
- Consequential tools require scoped idempotency keys, and every capability has a
  rate, timeout, retry, risk, side-effect, and audit policy.
- Audit records contain decision metadata and correlation identifiers, not tool input
  payloads. Tests prove foreign-tenant resources do not disclose data.
- MCP discovery is an exact four-tool allowlist. Pending approval creation performs no
  external action and cannot itself grant approval.
- Synthetic data only was used. No model call, external personal-data transfer, cloud
  resource, paid API, or recurring service was created.

## Dependency and architecture impact

ADR-0018 records the registry/executor and MCP boundary. The application uses official
MCP 1.28.1, which fixes all three advisories found in the initially compatible 1.23.3
release. Semgrep 1.172.0 still pins that older SDK transitively, so SAST runs in a
separately resolved `uvx` tool environment; the vulnerable dependency is absent from
the application lock, imports, and runtime.

The HTTP API remains the product interface. MCP is a narrow tool protocol and does not
replace A2A or authorize independently deployed agents. Registry rate/idempotency
state is intentionally process-local; durable/distributed enforcement is deferred.

## Evaluation and verification

Final evidence: Python format/lint and strict MyPy passed for 60 source files; default
Pytest passed 105 tests with 3 PostgreSQL-only skips, while the real local
PostgreSQL/pgvector run passed all 108 tests. Official in-memory MCP initialization,
discovery, schemas, allowlisting, and a read-only invocation passed. Web format/lint,
TypeScript, 5 tests, and production build passed. Markdown lint/link checks, 8 Mermaid
renders, governance validation, Semgrep, detect-secrets, and pre-commit passed. Python
and npm dependency audits found no known vulnerabilities; internal unpublished Python
packages were the expected audit skips.

## Known limitations

- Tool rate limits and idempotency results reset with the API process and do not
  coordinate across replicas.
- Matching, verification, taxonomy, and cost logic are deterministic educational
  baselines, not production semantic or model-backed implementations.
- Local stdio MCP uses a synthetic development identity. Remote transport, production
  OAuth/resource-server behavior, and deployed MCP are not enabled.
- MCP 1.28.1 currently emits a Pydantic Settings `lifespan` forward-reference warning
  at server construction; the contract test captures it explicitly and protocol
  behavior succeeds.
- Durable approval state and execution gates belong to Phase 8. Agent orchestration is
  absent until the separately approved Phase 7.

## Owner acceptance checklist

- [ ] Log in locally and list the nine HTTP tool capabilities and their schemas.
- [ ] Invoke `profile.lookup` or `cost.estimate` with synthetic data.
- [ ] Try audit lookup as the local member and confirm the request is denied.
- [ ] Repeat an approval request with the same idempotency key and confirm replay.
- [ ] Inspect audit events and confirm the invocation correlation identifier appears.
- [ ] Confirm MCP discovery contains only the four documented read-only tools.

## Next phase gate

Stop here. Phase 7 may start only after:

`APPROVE PHASE 6 AND START PHASE 7`
