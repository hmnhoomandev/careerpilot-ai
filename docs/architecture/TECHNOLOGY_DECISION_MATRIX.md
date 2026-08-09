# Technology Decision Matrix

Scores use 1 (poor) to 5 (strong) for CareerPilot AI's constraints. Scores are
comparative design judgments, not vendor benchmarks.

| Decision | Selected | Fit | Local/CHF 0 | Maturity | Learning value | Reason |
|---|---|---:|---:|---:|---:|---|
| Backend API | FastAPI | 5 | 5 | 5 | 5 | Typed Python, OpenAPI, async ecosystem |
| Web UI | Next.js/React | 5 | 5 | 5 | 5 | Accessible full-product UI and server/client boundaries |
| Production database | PostgreSQL | 5 | 5 | 5 | 5 | Transactions, constraints, RLS potential, mature tooling |
| Vector store | pgvector | 5 | 5 | 4 | 5 | Keeps transactional metadata and tenant filters close |
| In-process agent graph | LangGraph | 5 | 5 | 4 | 5 | Typed graph state, checkpoints, interrupts, explicit routing |
| Durable business workflow | Temporal | 5 | 4 | 5 | 5 | Durable timers, signals, replay, recovery, compensation |
| Google specialist | Google ADK | 4 | 4 | 4 | 5 | Bounded Gemini and Google-agent learning objective |
| OpenAI specialist | OpenAI Agents SDK | 4 | 4 | 4 | 5 | Bounded handoff, session, guardrail, tracing comparison |
| Tool interoperability | MCP | 5 | 5 | 4 | 5 | Narrow tool/resource contracts |
| Remote agent interoperability | A2A | 4 | 5 | 3 | 5 | Capability discovery and remote task lifecycle |
| Async events | Google Pub/Sub | 4 | 3 | 5 | 4 | Managed production event transport; emulator/local adapter needed |
| Service abstraction | Dapr (conditional) | 2 | 4 | 4 | 4 | Added only if an ADR proves value over direct adapters |
| Telemetry | OpenTelemetry | 5 | 5 | 5 | 5 | Vendor-neutral propagation and export |
| Initial deployment | Cloud Run | 5 | 3 | 5 | 5 | Lower operational burden than Kubernetes |
| Reference deployment | GKE (later) | 2 | 1 | 5 | 5 | Educational option, not default production path |

## Runtime selection

| Runtime | Selected | Alternatives considered | Decision |
|---|---|---|---|
| Python | 3.13 | Installed 3.14; conservative 3.12 | 3.13 has documented FastAPI support and reduces 3.14 ecosystem risk while remaining modern. Recheck all dependencies in Phase 1. |
| Node.js | 24 LTS | Installed 26; older 22 LTS | 24 LTS provides a supported stable line and exceeds current Next.js minimum requirements. Recheck exact Next.js support in Phase 1. |

## Rejected production-path combinations

- Temporal, DBOS, and Restate do not share one production workflow.
- LangGraph, ADK, and OpenAI Agents SDK do not own the same orchestration.
- SQLite does not stand in for PostgreSQL production semantics.
- A vector-only database does not become the source of candidate truth.
- Kubernetes is not required for local development or first deployment.
