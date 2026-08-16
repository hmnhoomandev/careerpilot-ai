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

## Phase 3

Concepts introduced:

- Authentication versus authorization and external identity versus internal actor.
- Personal tenant, membership, role, permission, and server-derived context.
- RBAC candidate permissions followed by contextual ABAC and deny-by-default.
- Ownership, explicit delegation, sensitivity, purpose, state, and IDOR controls.
- Layered API, service, repository, document, and tool authorization.
- Local opaque bearer sessions versus a production OIDC verifier port.
- Append-only immutable audit values, hash chaining, and tenant-filtered views.
- Non-enumerating cross-tenant responses and last-owner invariants.

Tutorial: `docs/tutorials/phase-03-local-identity-and-authorization.md`

Exercises: `docs/exercises/phase-03-exercises.md`

Answers: `docs/exercises/phase-03-answers.md`

Remaining gaps intentionally deferred:

- Live OIDC provider validation, MFA, recovery, and production sessions.
- Durable tenant/profile/audit persistence and migrations (Phase 4+).
- Activated organization and explicit coach delegation workflows (later).
- Audit retention, signing/anchoring, incident access, and legal review (Phase 16+).

## Phase 4 — PostgreSQL profile and evidence foundation

- Learned aggregate transactions: profile and child rows commit or roll back together.
- Implemented optimistic concurrency and mapped stale writes to a safe HTTP `409`.
- Distinguished opaque identifiers from tenant authorization predicates.
- Ran Alembic downgrade/upgrade and repository tests against real PostgreSQL 17.
- Practiced fail-closed evidence handling: basename normalization, allowlists,
  metadata minimization, quarantine, and a malware-scanner interface.
- Kept SQLite out of production-semantics evidence and documented why.

## Phase 5 — Secure document ingestion and RAG

- Treated source text as evidence without granting it instruction authority.
- Put tenant/owner filters inside lexical and vector SQL before candidates materialize.
- Practiced bounded parsing, chunk provenance, local object keys, versioned derivatives,
  reciprocal-rank fusion, and deletion propagation.
- Gated quality with recall, precision, MRR, grounding, citations, leakage, injection,
  reindexing, and deletion evidence.
- Kept the default offline and distinguished a reproducible hash-vector baseline from
  production semantic retrieval.

Tutorial: `docs/tutorials/phase-05-secure-document-retrieval.md`

Exercises: `docs/exercises/phase-05-exercises.md`

Answers: `docs/exercises/phase-05-answers.md`

## Phase 6 — Typed tools, policy, and MCP

- Distinguished a narrow deterministic tool from an autonomous agent and from A2A.
- Generated input/output JSON Schema from strict Pydantic contracts.
- Centralized capability permissions, risk, timeout, retry, idempotency, rate, audit,
  and MCP exposure metadata in one registry.
- Practiced server-derived authorization, safe error taxonomies, output sanitization,
  scoped replay, and bounded timeout retry.
- Used the official MCP SDK with an explicit read-only allowlist and in-memory protocol
  test while keeping the default workflow model-free and CHF 0.

Tutorial: `docs/tutorials/phase-06-tools-and-mcp.md`

Exercises: `docs/exercises/phase-06-exercises.md`

Answers: `docs/exercises/phase-06-answers.md`

## Phase 7 — LangGraph state and bounded agent coordination

- Distinguished node updates, graph state, checkpoints, application state, workflow
  state, session state, memory, and audit history.
- Implemented deterministic-first routing, structured provider output, manager
  delegation, disjoint role ownership, bounded retry, cancellation, and replay.
- Kept model authority separate from authorization, truth, tools, and provider choice.
- Practiced cited match/gap explanations and explicit insufficient evidence.

Tutorial: `docs/tutorials/phase-07-langgraph-analysis.md`

Exercises: `docs/exercises/phase-07-exercises.md`

Answers: `docs/exercises/phase-07-answers.md`

## Phase 8 — Truthful drafts and human approval

- Modeled claims separately from prose and required citations for factual output.
- Practiced immutable versions, content hashes, optimistic revisions, stale decision
  rejection, terminal states, and restart-safe approval persistence.
- Distinguished LangGraph interrupt/checkpoint state from authoritative business state.
- Created allowlisted A2UI-compatible presentation messages without granting authority.

Tutorial: `docs/tutorials/phase-08-truthful-drafts-and-approval.md`

Exercises: `docs/exercises/phase-08-exercises.md`

Answers: `docs/exercises/phase-08-answers.md`

## Phase 9 — Google ADK specialist boundary

- Used official prototype scaffolding as a reference without importing deployment/A2A.
- Built a request-scoped ADK `Agent`/`App`, tool closure, schema, callback, and session.
- Distinguished framework sessions from authorization, durable business state, and audit.
- Practiced explicit provider selection, no fallback, cost/consent gates, stable failures,
  citation post-validation, and metadata-only telemetry.

Tutorial: `docs/tutorials/phase-09-adk-versus-langgraph.md`

Exercises: `docs/exercises/phase-09-exercises.md`

Answers: `docs/exercises/phase-09-answers.md`

## Phase 10 — OpenAI Agents SDK orchestration laboratory

- Compared direct handoff, agent-as-tool, and manager delegation on one fixture.
- Practiced SDK agent definitions, function-tool approval, sessions, structured output,
  safe run configuration, exact-action resume, and redacted trace evidence.
- Kept authorization, guardrails, spending, truth, and external action outside the model.
- Preserved fake-first execution and a separate live cost/data gate with no fallback.

Tutorial: `docs/tutorials/phase-10-openai-agent-orchestration.md`

Exercises: `docs/exercises/phase-10-exercises.md`

Answers: `docs/exercises/phase-10-answers.md`

## Phase 11 — A2A interoperability and registry

- Separated capability advertisement, registry trust, caller authorization, and task
  lifecycle instead of treating discovery as authority.
- Used official A2A Agent Card and Task models with explicit protocol/skill versions.
- Practiced tenant-scoped idempotency, cancellation, timeout, outage, version mismatch,
  metadata-only correlation, and explicit no-fallback behavior.
- Kept JSON-RPC deployment, workload identity, durable tasks, and real runtimes outside the
  fake-first local boundary.

Tutorial: `docs/tutorials/phase-11-a2a-interoperability.md`

Exercises: `docs/exercises/phase-11-exercises.md`

Answers: `docs/exercises/phase-11-answers.md`

## Phase 12 — Temporal durable application workflow

- Separated deterministic workflow history from activity side effects, LangGraph state,
  PostgreSQL business records, specialist sessions, and audit evidence.
- Practiced durable signals, queries, timers, worker restart recovery, activity retry,
  heartbeat, idempotency, cancellation, reverse compensation, patching, and replay.
- Demonstrated at-least-once activity behavior by failing after a fake effect committed.
- Restricted workflow history to bounded opaque references rather than personal content.

Tutorial: `docs/tutorials/phase-12-temporal-durable-workflows.md`

Exercises: `docs/exercises/phase-12-exercises.md`

Answers: `docs/exercises/phase-12-answers.md`

## Phase 13 — asynchronous events and notifications

- Separated source-of-truth transactions, transport acknowledgement, and consumer effects.
- Practiced outbox dispatch, inbox deduplication, aggregate ordering, bounded retry,
  dead-letter quarantine, and explicit replay under at-least-once delivery.
- Kept event payloads metadata-only and notification access tenant/actor scoped.
- Evaluated Dapr against an actual need and deferred it rather than adding an unused runtime.

Tutorial: `docs/tutorials/phase-13-events-and-notifications.md`

Exercises: `docs/exercises/phase-13-exercises.md`

Answers: `docs/exercises/phase-13-answers.md`

## Phase 14 — accessible product UI and safe A2UI

- Reorganized API demonstrations into a coherent responsive career workspace.
- Practiced landmarks, heading/focus order, skip navigation, live regions, reduced motion,
  keyboard interaction, mobile collapse and automated axe checks.
- Treated A2UI as untrusted presentation data with closed components/actions and text escaping.
- Distinguished UI affordance from server authorization and honest demo state from capability.

Tutorial: `docs/tutorials/phase-14-accessible-product-ui.md`

Exercises: `docs/exercises/phase-14-exercises.md`

Answers: `docs/exercises/phase-14-answers.md`

## Phase 15 — observability, evaluation, routing, and cost control

- Separated telemetry, evaluation, routing and budget authority with versioned contracts.
- Practiced content-free events, tenant-scoped aggregation, percentiles and correlation.
- Implemented explicit route decisions, no fallback, budget reservation, quota and safe cache keys.
- Distinguished deterministic offline gates from opt-in ADK generation/LLM-as-judge evaluation.
- Kept ADK prompt-response upload, BigQuery, Cloud, LangSmith and OpenAI trace export disabled.

Tutorial: `docs/tutorials/phase-15-observability-routing-and-evaluation.md`

Exercises: `docs/exercises/phase-15-exercises.md`

Answers: `docs/exercises/phase-15-answers.md`

## Phase 16 — security hardening and adversarial verification

- Separated identity, authorization, validation, approval, audit and recovery controls.
- Modeled deletion across source, derivatives and backups instead of one SQL statement.
- Validated scheme, host and every resolved IP before outbound connection or redirect.
- Distinguished backup integrity from KMS-backed production confidentiality/authenticity.
- Treated SAST, SCA, DAST, secrets, licenses, container and IaC as complementary evidence.
- Kept lawful bases, retention and breach-notification duties under professional legal review.

Tutorial: `docs/tutorials/phase-16-defense-in-depth.md`

Exercises: `docs/exercises/phase-16-exercises.md`

Answers: `docs/exercises/phase-16-answers.md`

## Phase 17 — containers, supply chain, IaC, and Cloud Run

- Connected locked dependencies, minimal runtime images, SBOM, provenance, digest and signature as one chain of evidence.
- Practiced defense-in-depth container controls and isolated local networks/profiles.
- Modeled Zurich residency, private managed PostgreSQL, regional messaging/secrets/keys and least-privilege identities in Terraform.
- Separated plan from apply, runtime from migration identity, compute rollback from data recovery, and CI identity from service-account keys.

Tutorial: `docs/tutorials/phase-17-containers-supply-chain-iac.md`

Exercises: `docs/exercises/phase-17-exercises.md`

Answers: `docs/exercises/phase-17-answers.md`

## Phase 18 — optional GKE reference architecture

- Compared serverless operational ownership with Kubernetes control and responsibility.
- Practiced Kustomize composition, restricted Pod security, Workload Identity, default-deny
  networking, probes, resources, HPA, PDB, topology spread and safe rolling updates.
- Separated secret reference from secret value and schema migration from workload rollout.
- Kept render/schema/policy evidence distinct from live cluster, IAM, network and SLO evidence.

Tutorial: `docs/tutorials/phase-18-gke-reference.md`

Exercises: `docs/exercises/phase-18-exercises.md`

Answers: `docs/exercises/phase-18-answers.md`

## Phase 19 — durable-execution comparison labs

- Proved that durable retry and effect idempotency are separate responsibilities.
- Compared Temporal activities, DBOS steps and Restate durable runs using one synthetic contract.
- Used independent locks and negative import tests to protect production architecture from a lab.
- Distinguished permissive SDK licensing from the Restate server's BSL boundary.
- Kept local executable evidence separate from production maturity, migration, SLO and cost claims.

Tutorial: `docs/tutorials/phase-19-durable-execution-comparison.md`

Exercises: `docs/exercises/phase-19-exercises.md`

Answers: `docs/exercises/phase-19-answers.md`
