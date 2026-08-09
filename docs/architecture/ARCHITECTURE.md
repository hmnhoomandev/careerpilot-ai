# Architecture Baseline

## Style

CareerPilot AI begins as a modular core with strict ports and bounded contexts,
plus separately deployable specialist agent services only where the roadmap has a
specific interoperability or educational objective. This limits distributed
systems cost while preserving future service boundaries.

## Responsibility map

| Technology | One primary responsibility |
|---|---|
| FastAPI | Versioned HTTP and streaming gateway |
| Next.js/React | Accessible user-facing web application |
| PostgreSQL | Authoritative transactional and audit-reference data |
| pgvector | Tenant-filtered derived vector indexes |
| Pydantic | Validated settings and boundary contracts |
| LangGraph | Primary in-process agent graph, routing, and checkpoints |
| Temporal | Long-running durable business-process orchestration |
| Google ADK | Bounded Google/Gemini specialist service |
| OpenAI Agents SDK | Bounded handoff/session/guardrail learning service |
| A2A | Remote-agent discovery and task lifecycle |
| MCP | Narrow reusable tool/resource exposure |
| Pub/Sub | Asynchronous domain/integration event transport |
| OpenTelemetry | Vendor-neutral telemetry model and propagation |
| Cloud Run | First managed production compute target |

## Control-flow rule

Use deterministic code for validation, authorization, calculations, state
transitions, approval enforcement, retention, routing with known rules, and
external effects. Use models only for bounded interpretation or generation whose
quality is evaluated and whose outputs are structured and policy-checked.

## State rule

Application records remain authoritative. Graph checkpoints, workflow histories,
sessions, memories, indexes, caches, traces, and audit events have separate owners,
purposes, retention rules, and authorization. None may silently become the source
of truth for candidate qualifications.

## Interaction distinctions

- A manager delegates when it retains user interaction and requests a specialist
  result; this is preferred for the main LangGraph experience.
- A direct handoff transfers conversational control and is intentionally explored
  only in the OpenAI Agents SDK service.
- Agent-as-tool performs a bounded specialist call without transferring control.
- MCP calls a reusable tool/resource; A2A delegates a task to an independently
  deployed agent with discovery and lifecycle semantics.

## Recovery distinctions

- Retry repeats a failed operation under bounded policy.
- Replay rebuilds workflow state from deterministic history.
- Recovery restores or resumes after interruption.
- Compensation semantically counteracts an already completed external effect.
- Fallback is an explicit alternative path. Provider fallback requires policy and
  user-visible disclosure; silent provider switching is forbidden.

## Source references

- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Google ADK](https://adk.dev/)
- [ADK sessions, state, and memory](https://adk.dev/sessions/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Cloud Run locations](https://cloud.google.com/run/docs/locations)
- [Cloud SQL PostgreSQL locations](https://cloud.google.com/sql/docs/postgres/region-availability-overview)

These links are decision inputs, not compatibility guarantees. Versions and
service availability must be rechecked in the implementation phase.
