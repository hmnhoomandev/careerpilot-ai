# Annotated Source: Phase 7 LangGraph Analysis

`careerpilot_core/agents.py` defines provider-neutral structured values, the routing
enum, provider protocol, and runtime role dossiers. Core imports no LangGraph or Google
SDK, preserving dependency direction.

`model_providers.py` supplies the offline fake and bounded Gemini adapter. The fake
finds only explicit taxonomy terms. Gemini receives a fixed instruction that source
text is untrusted and validates JSON through Pydantic; construction fails unless an
external transfer was explicitly authorized. There is no fallback.

`analysis_graph.py` declares serializable typed state. The `events` channel uses an
append reducer while every other role owns disjoint last-value fields. Nodes call the
existing policy executor rather than bypassing tool authorization. Conditional routing
has a closed destination map. Only structured extraction retries, and only for a
transient connection error. `InMemorySaver` proves checkpoint semantics locally.

`analysis_service.py` scopes run and thread identifiers to tenant, actor, and run. It
reauthorizes start/read/cancel and deliberately returns the same safe not-found result
for missing and foreign runs. Process memory is disclosed as a limitation.

`analysis_contracts.py` and `main.py` expose strict start/status/cancel contracts. The
response includes progress, provider identity, citations, gaps, errors, and correlation
without prompts or hidden reasoning. Tests cover paths, state ownership, retry,
checkpoint replay, cancellation, schema validation, grounding, and tenant isolation.
