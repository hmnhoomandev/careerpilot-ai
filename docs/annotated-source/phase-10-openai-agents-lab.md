# Annotated Source: Phase 10 OpenAI Agents Laboratory

`sdk_agents.py` is the only SDK-definition boundary. The manager has a real handoff to
the interviewer and exposes the feedback specialist through `Agent.as_tool()`. The
feedback preparation function uses `needs_approval=True`. Trace export and sensitive
trace content are disabled.

`provider.py` supplies deterministic equivalent results without importing provider
credentials or calling a model. The route changes active/final ownership while keeping
the interview question constant for comparison.

`service.py` checks deterministic input/output gates, stores results under a tenant/
actor/session key, and emits metadata-only trace events. `approval.py` serializes a
pending exact-action hash and rejects stale, terminal, or wrong-action decisions.

`config.py` keeps fake execution as default. Selecting OpenAI without both explicit cost
approval and a positive CHF ceiling fails closed before a live provider can be built.
