# Architecture handbook

CareerPilot is a modular core with ports and adapters plus isolated specialist services.
The first user is an individual job seeker; organization/coach concepts preserve future
tenant boundaries but are inactive.

## State and execution ownership

- PostgreSQL/pgvector owns authoritative business records and vector indexes.
- LangGraph owns bounded in-process agent graph state, branches and interrupts.
- Temporal owns long-running workflow history, waits, timers, retry and compensation.
- Specialist session state stays inside Google ADK/OpenAI service boundaries.
- Audit history records security/business facts, never hidden reasoning.
- Pub/Sub carries versioned metadata events with outbox/inbox semantics.

MCP exposes narrow reusable tools; A2A describes/delegates independently deployed agent
capabilities. Tool identity never grants user authority. DBOS/Restate are isolated labs.
Cloud Run is the production compute default; GKE is an optional reference requiring a new
decision. Provider/model selection is explicit and never silently falls back.

## Trust and truth

Identity establishes a subject; memberships and RBAC+ABAC authorize an action. Tenant
predicates remain inside repositories/retrieval. External documents and model output stay
untrusted. Every material career claim cites verified evidence; insufficient evidence
produces uncertainty or a confirmation request. Human approval precedes external,
irreversible, sensitive or costly action.

## Deployment and evolution

Zurich `europe-west6` is preferred. Any EU fallback needs service availability, residency,
security/privacy, latency and cost analysis. Production uses workload identity, managed
secrets/KMS, private PostgreSQL, immutable signed images, migration job, telemetry, backups
and incident ownership. Current Terraform/Kubernetes are non-applied plans/references.

Read ADRs in numeric order for decision history, diagrams for system/container/data flow,
annotated source for implementation intent, and the release report for evidence gaps.
