# Learning Log

## Phase 0

Concepts introduced:

- Product outcomes, jobs-to-be-done, and stable requirement identifiers.
- Quality attributes and measurable service-level objectives.
- Bounded contexts and modular-monolith versus service boundaries.
- Deterministic workflow versus agentic decision-making.
- Graph, application, workflow, session, memory, and audit state.
- Manager delegation, direct handoff, agent-as-tool, MCP, and A2A.
- STRIDE threat modeling, privacy by design, and data-flow trust boundaries.
- RBAC versus ABAC and authentication versus authorization.
- Retry, replay, recovery, compensation, and fallback.
- ADRs, traceability, risk registers, and phase gates.

Tutorial: `docs/tutorials/phase-00-architecture-baseline.md`

Exercises: `docs/exercises/phase-00-exercises.md`

Answers: `docs/exercises/phase-00-answers.md`

Remaining gaps intentionally deferred:

- Framework APIs and repository scaffolding (Phase 1 onward).
- Concrete schemas and authorization policies (Phases 3–4).
- Retrieval and agent evaluation implementation (Phases 5–10).
- Deployment, security operations, and production measurements (Phases 15–20).

## Phase 1

Concepts introduced:

- Manifest constraints versus exact cross-platform lockfiles.
- `uv` workspace membership and the need for `--all-packages` synchronization.
- Node LTS engine enforcement and peer-dependency compatibility.
- Inward dependency direction and AST architecture tests.
- Local pre-commit feedback versus clean-environment CI evidence.
- SAST, dependency auditing, secret baselines, and tool-risk isolation.
- Docker CLI, Compose plugin, and daemon as separate prerequisites.
- Markdown linting, remote link checking, and rendered Mermaid validation.

Tutorial: `docs/tutorials/phase-01-developer-setup.md`

Exercises: `docs/exercises/phase-01-exercises.md`

Answers: `docs/exercises/phase-01-answers.md`

Remaining gaps intentionally deferred:

- Product API/UI behavior and end-to-end persistence (Phase 2).
- Full identity and authorization implementation (Phase 3).
- Supply-chain signatures, SBOM/provenance, and hardened containers (Phase 17).

## Phase 2

Concepts introduced:

- Vertical slices across UI, HTTP, application, port, and adapter boundaries.
- Immutable domain values and dependency inversion through a repository protocol.
- Deterministic placeholder behavior versus model inference.
- Strict Pydantic contracts, OpenAPI evidence, and safe error envelopes.
- Correlation propagation, metadata-only structured logs, and no-op tracing APIs.
- Liveness versus readiness and process-local persistence limitations.
- Native form semantics, live regions, focus visibility, and axe smoke tests.
- Composite end-to-end evidence and restart-behavior tests.

Tutorial: `docs/tutorials/phase-02-deterministic-walking-skeleton.md`

Exercises: `docs/exercises/phase-02-exercises.md`

Answers: `docs/exercises/phase-02-answers.md`

Remaining gaps intentionally deferred:

- Identity, tenant context, authorization, and audit (Phase 3).
- Durable PostgreSQL storage, migrations, and profile evidence (Phase 4).
- Evaluated retrieval, agents, models, and workflow durability (Phases 5–12).
- Production telemetry export, SLO measurement, and cost routing (Phase 15).
