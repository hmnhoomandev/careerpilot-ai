# Phase 7 Tutorial: Stateful Analysis Without Autonomous Authority

A graph is useful when several bounded steps share evolving state and failures must be
visible. A node reads the current state and returns only its update. A reducer appends
progress events; ordinary fields keep the latest value. Explicit ownership prevents
two roles from silently competing over one fact.

CareerPilot routes known job-analysis requests with rules. Structured model extraction
is justified only where language interpretation adds value, and tests use a fake. The
model cannot authorize tools or establish a candidate fact. Retrieval and verification
remain deterministic policy-controlled components.

`InMemorySaver` associates snapshots with a tenant/actor/run-scoped thread ID. Reusing
that ID can replay/resume graph execution. This is graph recovery within one process,
not Temporal durability after infrastructure loss.

Run the local product with `make dev`, create a synthetic profile/evidence document,
then POST a 50–5000 character job description to `/api/v1/agent-runs`. Inspect ordered
events, cited passages, supported/missing/uncertain gaps, provider, and correlation ID.
No Gemini credential or paid call is needed.
