# Annotated Source: Phase 9 Google ADK Specialist

`agent.py` is the only agent-definition boundary. It constructs a request-scoped ADK
agent so the source-reading closure cannot retain another tenant's allowlist. The model
gets a strict `ResearchResult` output schema and a pre-model safety callback.

`provider.py` separates deterministic fake output from ADK/Gemini execution. The live
adapter uses ADK `App`, `Runner`, and `InMemorySessionService`; it parses only the final
structured response. It performs no fallback and configures a single model attempt.

`service.py` is the policy envelope. It checks enablement, consent and transfer authority,
applies timeout and stable provider error mapping, validates citations, scopes session
results by tenant/actor/session, and emits metadata-only metrics.

`api.py` is deliberately narrow. Its one route requires an internal development service
identity and strict request/response schemas. Production identity is intentionally not
simulated or claimed here.
