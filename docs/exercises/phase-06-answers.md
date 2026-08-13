# Phase 6 Exercise Answers

1. The first permission controls access to the tool surface; the second restricts the
   underlying kind of operation. Resource services then apply actual object ownership.
2. A key from another user/tool cannot replay an operation, and changing validated
   input under the same key becomes a conflict instead of an ambiguous duplicate.
3. Retry reruns a failed attempt under a bounded policy. Replay returns the saved result
   of a successfully completed idempotent invocation without executing it again.
4. It records a request for human review but cannot perform the external or irreversible
   action. Phase 8 will govern the durable decision lifecycle.
5. MCP has a deliberately smaller read-only allowlist. Audit data is privileged and
   approval creation mutates state, even though current state is process-local.
6. MCP invokes a narrow capability. A2A later communicates with an independently
   deployed agent that owns its own contract, identity, reasoning, and lifecycle.
