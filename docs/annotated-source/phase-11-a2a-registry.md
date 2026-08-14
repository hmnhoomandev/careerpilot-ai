# Annotated source: Phase 11 A2A registry

`apps/api/src/careerpilot_api/a2a_registry.py` is the interoperability adapter. `_card`
constructs official SDK models with explicit versions, JSON modes, disabled streaming and
push, and a development security declaration. `A2ARegistry` validates compatibility and
capability before creating an official Task. Its composite key and fingerprint prevent
cross-tenant reads and ambiguous duplicate work.

`execute` records `working` before invoking the bounded adapter. `asyncio.wait_for` makes
the time budget enforceable; errors are translated to safe categories and do not select a
different agent. `cancel` rejects terminal tasks. `FakeRemoteAgentAdapter` is intentional:
default verification remains deterministic, offline, synthetic, and free.

`a2a_contracts.py` constrains public input, while `main.py` authenticates, supplies owned
resource attributes to centralized policy, audits the decision, and exposes discovery,
delegate/status/cancel application endpoints. `defer_execution` exists only to exercise
the submitted-to-canceled path locally; it is not a durable queue.
