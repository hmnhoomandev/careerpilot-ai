# Production and Comparison Boundaries

| Capability | Production path | Bounded learning/reference path |
|---|---|---|
| Core agent analysis | LangGraph in primary application | ADK graph concepts compared later |
| Long-running process | Temporal | Equivalent DBOS and Restate labs in Phase 19 |
| Google agent framework | Isolated ADK specialist service | Fake provider and explicit live opt-in |
| OpenAI orchestration | Isolated Agents SDK specialist service | Handoff versus agent-as-tool fixtures |
| Deployment | Cloud Run | Render-only GKE Kustomize reference |
| Database | PostgreSQL/pgvector | SQLite only in explicitly bounded unit examples |
| Events | Pub/Sub through an adapter | Local fake/emulator; Dapr only if justified |

## Isolation tests required later

- Production packages cannot import lab packages.
- Production dependency locks do not acquire DBOS or Restate through labs.
- Cloud Run/local profiles do not require GKE tooling; only Phase 18 reference
  rendering uses the existing kubectl-integrated Kustomize client.
- The LangGraph core remains available when ADK or OpenAI services are disabled.
- Default tests use fake providers and make no paid calls.
