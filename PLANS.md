# CareerPilot AI Execution Plans

## Plan format

Every phase plan must state:

1. Objective and approved phase.
2. In-scope requirements and acceptance criteria.
3. Deliverables and expected files.
4. Architecture and security decisions.
5. Privacy, migration, deployment, and cost impact.
6. Risks and mitigations.
7. Automated verification commands.
8. Manual verification steps and expected results.
9. Explicit exclusions.
10. Stop condition and exact next approval command.

Plans are living documents. Update status without erasing decisions or evidence.

## Active implementation plan: Phase 11

**Objective:** connect the LangGraph application, Google ADK specialist, and OpenAI
Agents specialist through versioned, discoverable, policy-controlled A2A capabilities and
a complete local task lifecycle using the official Python SDK.

### Scope and acceptance mapping

- Publish official A2A Agent Cards for all three runtimes with versioned skills, security
  declarations, input/output modes, capabilities, and local URLs.
- Implement a tenant-safe capability registry, discovery/compatibility checks, bounded
  remote-agent port, authentication/authorization, correlation, idempotent task creation,
  status, cancellation, timeout, and stable remote error mapping.
- Exercise cross-service delegation through deterministic in-process transports; no model
  call, provider fallback, or network service is required by default tests.
- Use official `a2a-sdk` card/task types at the application boundary; do not recreate
  protocol schemas manually. The production HTTP JSON-RPC server surface remains deferred
  with independently deployed services.

### Deliverables and expected files

- An SDK-backed interoperability adapter and application routes in the API layer, with
  cards identifying the existing bounded LangGraph, ADK, and OpenAI services.
- Unit/contract/e2e tests for cards, discovery, version compatibility, capability policy,
  task lifecycle, duplicate IDs, timeout, cancellation, unavailable agents, and tenancy.
- ADR, agent registry/capability documentation, annotated source, tutorial, exercises,
  security/privacy/traceability/state/roadmap updates, and mandatory phase review.
- Add official `a2a-sdk>=0.3.22,<0.4` after lock, license, compatibility, and audit review.

### Architecture, security, privacy, migration, deployment, and cost

- Agent Cards advertise capabilities and authentication requirements; they confer no
  authorization. Every operation rechecks server-derived caller identity and capability.
- The registry stores descriptors/adapters, not secrets or customer content. Task IDs are
  scoped by tenant/caller; duplicate payload conflicts fail closed and foreign tasks are
  non-enumerating.
- Correlation metadata excludes payload content. Remote inputs/outputs are strict,
  minimized, bounded, and treated as untrusted at both ends.
- Default transport is in-process fake; production HTTP/OAuth/workload identity, remote
  discovery trust/signatures, durable task storage, deployment, and retention are deferred.
- No migration, cloud resource, deployment, billing, live model, or external transfer.

### Risks and mitigations

- Malicious/stale cards: trusted registry allowlist, protocol/skill version checks, strict
  official SDK validation, and incompatible-card tests.
- Cross-tenant/privilege delegation: caller context, deny-default capability grants,
  tenant/task binding, non-enumerating access, and hostile tests.
- Duplicate/cancelled tasks: idempotency fingerprint, deterministic state machine,
  terminal-state rules, cooperative cancellation, and lifecycle tests.
- Remote outage/timeout/error leakage: bounded timeout, stable taxonomy, no fallback, and
  explicit degraded/unavailable results.
- Data leakage: minimized typed payloads, no hidden reasoning, metadata-only correlation,
  synthetic fixtures, and documented retention/legal gaps.

### Automated verification

- Agent Card schema/contract and capability compatibility tests; cross-runtime lifecycle,
  auth, duplicate, timeout, cancellation, unavailable-agent, and tenant-isolation tests.
- Complete Ruff, MyPy, Pytest, frontend/build, dependency audits, SAST, secrets,
  docs/links/Mermaid, pre-commit, governance, and diff review.

### Manual verification

- Discover all three cards and inspect skills/security/protocol versions.
- Delegate synthetic analysis to LangGraph, research to ADK, and interview to OpenAI.
- Observe correlated task transitions; cancel a submitted task and deny an unauthorized one.
- Disable a remote adapter and confirm explicit degradation without provider fallback.

### Explicit exclusions

- Public internet registry, dynamic untrusted card enrollment, real OAuth/mTLS, signed
  cards, remote deployment, streaming/push notification, durable tasks, customer data,
  model calls, Temporal, Pub/Sub, and Phase 12 work.

### Stop condition

Complete `docs/reviews/phase-11-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 11 AND START PHASE 12`

## Completed implementation plan: Phase 10

**Objective:** deliver an isolated OpenAI Agents SDK interview-simulation service and
learning laboratory that compares manager delegation, agent-as-tool, and direct handoff
using equivalent synthetic fixtures and fake execution by default.

### Scope and acceptance mapping

- Define interview manager, interviewer, and feedback specialist agents with structured
  outputs; demonstrate direct handoff and agent-as-tool using the real SDK definitions.
- Provide a deterministic fake runtime for default tests, scoped sessions, input/output/
  tool guardrails, approval pause/serialize/resume, and metadata-only local tracing.
- Expose a narrow authenticated service API and explicit disabled/unavailable behavior.
- Keep OpenAI imports inside `services/openai-agents`; no provider fallback or live call.
- Add an opt-in live test with an explicit per-run budget ceiling and cost approval gate.

### Deliverables and expected files

- New uv workspace package under `services/openai-agents/` with SDK agent definitions,
  contracts, fake/live ports, orchestration comparison, guardrails, sessions, approvals,
  traces, configuration, and API.
- Unit/contract/live tests for handoff paths, agent-as-tool comparison, session isolation,
  guardrails, approval serialization/resume/stale decisions, trace redaction, disabled
  service, and budget gating.
- ADR, annotated source, tutorial, exercises/answers, security/privacy/traceability,
  decision/learning/state/roadmap updates, and mandatory phase review.

### Architecture, security, privacy, migration, deployment, and cost

- The manager pattern retains final-response ownership; direct handoff transfers active
  conversation ownership. Equivalent fixtures make this difference observable.
- Only a bounded feedback-publication demonstration requires approval; it performs no
  external publication, email, submission, or profile mutation after approval.
- SDK tracing export is disabled by default and sensitive trace data is excluded. Local
  trace evidence contains IDs, route, outcome, turns, and provider only.
- Fake runtime is default. Live OpenAI requires explicit provider selection, credentials,
  consent/transfer authority, cost approval, and a positive CHF ceiling; no fallback.
- No schema migration, cloud resource, deployment, paid call, or external transfer.

### Risks and mitigations

- Wrong specialist/control transfer: explicit route enum, equivalent scenario tests, SDK
  shape assertions, and stable route trace metadata.
- Guardrail gaps: deterministic blocking input/output/tool gates outside model authority.
- Approval replay/race: exact session/run/action hash and revision binding plus serialized
  pending state and terminal transition tests.
- PII/hidden reasoning leakage: synthetic fixtures, minimized contracts, redacted traces,
  no prompts/tool payloads in telemetry, and concise decision summaries only.
- Unbounded spend: fake default, max turns, live marker, explicit CHF budget gate, no
  retries/fallback, and zero live execution under current approval.

### Automated verification

- Focused service tests, then complete Ruff, MyPy, Pytest, frontend/build, dependency
  audits, SAST, secrets, docs/links/Mermaid, pre-commit, governance, and diff review.
- Live OpenAI test must skip unless explicit cost/data authorization and budget exist.

### Manual verification

- Start the synthetic interview through direct handoff and inspect active specialist.
- Run the same fixture through agent-as-tool and inspect manager-owned final output.
- Trigger an input/tool/output guardrail and inspect the safe error.
- Pause a feedback action, serialize, approve/reject, resume, and inspect redacted traces.

### Explicit exclusions

- Real candidate data, automatic communications/submissions/profile mutations, voice or
  realtime interview, hosted tools, web search, A2A, deployment, cloud tracing, durable
  production sessions, Temporal, and Phase 11 work.

### Stop condition

Complete `docs/reviews/phase-10-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 10 AND START PHASE 11`

## Completed implementation plan: Phase 9

**Objective:** deliver an isolated, bounded Google ADK specialist service for
company/job research over explicitly supplied sources, with fake-first execution and an
explicitly authorized Gemini path.

### Scope and acceptance mapping

- Implement one ADK research specialist with structured cited output, per-session state,
  allowlisted source tools, safety callbacks, and metadata-only telemetry.
- Expose a narrow authenticated service API plus an in-process fake adapter used by the
  main application and all default tests; disabling the specialist degrades explicitly.
- Keep Google ADK/Gemini imports inside the specialist boundary. No unrestricted web
  scraping, silent provider fallback, profile mutation, or external side effect.
- Classify timeout, quota, malformed output, and provider outage into stable safe errors.
- Provide an opt-in live Gemini evaluation that is skipped unless explicit configuration
  and cost authorization are present.

### Deliverables and expected files

- A prototype-first ADK service workspace under `services/google-adk/`, including an
  agents-cli manifest/spec, agent, tools, callbacks, session boundary, schemas, API,
  telemetry, fake/live provider composition, and evaluation fixture.
- Unit, service-contract, failure-injection, session-isolation, safety, structured-output,
  citation, disabled-service, and opt-in live-evaluation tests.
- An ADR, ADK-versus-LangGraph tutorial, annotated source, exercises/answers, threat/privacy
  updates, requirements traceability, learning/state/roadmap updates, and phase review.
- Pin official `google-adk>=2.5,<2.6` only after lock, license, compatibility, and audit
  checks. Use Python 3.13 and no deployment dependencies.

### Architecture, security, privacy, migration, deployment, and cost

- The service receives minimized user-supplied company/job source excerpts with stable
  source IDs. Its only tool retrieves from that request-local allowlist; citations must
  bind every factual finding to one supplied source.
- A deterministic fake provider is the default. Gemini requires an explicit enable flag,
  consent/authorization metadata, configured model, timeout, and credentials; failures
  never trigger fallback.
- Session IDs are tenant/actor scoped and request content is not recorded in telemetry.
  Structured schemas reject extra fields and safety callbacks reject prompt-injection,
  unsupported-source, and sensitive-transfer violations before model execution.
- Phase 9 creates no cloud resources, database migration, paid call, billing, deployment,
  unrestricted browsing, or real-person data transfer. Live evaluation remains opt-in.

### Risks and mitigations

- Hallucinated research: closed source set, required citations, post-validation, and
  fail-closed malformed/unsupported citation tests.
- Cross-session or tenant leakage: scoped session keys, request-local tools, no global
  source cache, authorization contract, and isolation tests.
- Prompt injection and PII transfer: untrusted-data framing, deterministic inspection,
  minimization/consent checks, and synthetic fixtures.
- Provider instability/cost: bounded timeout, stable quota/outage errors, no retry or
  fallback by default, fake tests, explicit live/cost gates, and metadata-only telemetry.
- Framework coupling: service-only ADK imports and a typed HTTP/client contract keep the
  core and FastAPI application independent.

### Automated verification

- Run focused fake/provider/service tests followed by complete Ruff, strict MyPy, Pytest,
  web checks, build, dependency/security audits, secrets, docs/links/Mermaid, pre-commit,
  governance validation, and complete diff review.
- Keep live Gemini evaluation marked and skipped by default; record the exact opt-in
  command without executing it in the CHF 0 workflow.

### Manual verification

- Run one synthetic fixture through fake configuration and inspect structured findings,
  source citations, session metadata, and telemetry.
- Disable the service and confirm explicit `specialist_unavailable` degradation.
- With separate explicit cost/data approval, run the same fixture through Gemini and
  compare its schema/citations; this is not authorized by the phase-start command.
- Read and exercise the ADK-versus-LangGraph tutorial.

### Explicit exclusions

- Unrestricted web search/scraping, managed Google Search/RAG, real customer data, live or
  paid model calls, cloud resources, deployment/IaC, durable production sessions, A2A,
  OpenAI Agents SDK, Temporal, Pub/Sub, and Phase 10 work.

### Stop condition

Complete `docs/reviews/phase-09-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 9 AND START PHASE 10`

## Completed implementation plan: Phase 8

**Objective:** generate versioned resume and cover-letter drafts whose material claims
are evidence-linked, then pause behind a durable, exact-version human approval gate.

### Scope and acceptance mapping

- Implement Resume Tailoring, Cover Letter, Privacy/PII, Bias/Compliance, and Approval
  Coordinator roles with explicit non-responsibilities and state ownership.
- Build a claim-to-evidence graph; unsupported skills, dates, employers, qualifications,
  and metrics are blocked or returned only as suggestions requiring confirmation.
- Store immutable draft versions and editable structured sections; every material claim
  carries citations and validation status.
- Implement pending, approved, edited-and-approved, rejected, more-information,
  expired, and cancelled approval states with exact draft-version/hash binding.
- Pause and resume human review using LangGraph interrupt/Command semantics and a
  checkpointer; use PostgreSQL for restart-safe production records and local fakes in
  default tests.
- Emit allowlisted A2UI-compatible draft/approval messages that contain presentation
  data only and never authorize an action.

### Deliverables and expected files

- Draft, claim, citation, approval, transition, and repository protocols in core.
- PostgreSQL tables/Alembic `0003`, tenant-safe repository, generation/policy service,
  approval graph, strict API contracts/routes, and application composition.
- Unit/API/contract/e2e/PostgreSQL tests for state machine, restart/resume, stale and
  concurrent approval, edit/versioning, PII, bias, invented claims/dates, and A2UI.
- ADR, role dossiers, annotated source, tutorial, exercises/answers, security/privacy,
  traceability, learning log, and `docs/reviews/phase-08-review.md`.
- Add official `langgraph-checkpoint-postgres>=3.1,<3.2` (MIT, Python 3.10+) if its
  lock/audit remains compatible; no live model dependency or call is needed.

### Architecture, security, privacy, migration, deployment, and cost

- Generation is deterministic/fake-first and may only transform authorized profile and
  cited evidence. Verification, privacy, and bias policy are deterministic gates after
  generation; no reviewer can convert unsupported content into fact.
- Approval is a deterministic state machine. Every decision includes expected draft
  version and content hash under optimistic concurrency and tenant authorization.
- LangGraph interrupt is the interaction checkpoint; PostgreSQL draft/approval records
  are authoritative durable business evidence. Temporal remains future owner of timers,
  schedules, and cross-service recovery.
- Drafts contain high-risk personal data. Store minimized structured content, exclude
  it from logs/audit, and document encryption/retention/deletion/legal review gaps.
- Migration is forward versioned and tested on disposable PostgreSQL. No cloud resource,
  deployment, billing, external transfer, or paid/model call is authorized.

### Risks and mitigations

- Fabricated career claims: claim graph, citation requirements, invented-value corpus,
  fail-closed verification, and confirmation-only suggestions.
- Stale/raced approval: exact version/hash binding, atomic compare-and-update, terminal
  state rules, and concurrency tests.
- Approval bypass: separate generate/review/use permissions, pending by default, no
  external side effect, server-derived context, and audit transitions.
- PII leakage: deterministic detection, user-visible flags, minimized response/A2UI,
  metadata-only telemetry, tenant-filtered persistence, and synthetic fixtures.
- Checkpoint mismatch: scoped thread IDs, interrupt payload version/hash, durable record
  reconciliation, restart/resume tests, and explicit recovery failure.
- UI/schema injection: A2UI message types/components/actions are allowlisted and content
  is data, not executable markup or authority.

### Automated verification

- State-transition matrix, terminal/expiry/cancel, edit/version/hash, stale/concurrent
  decisions, restart/resume, graph interrupt, and repository transaction tests.
- Unsupported/invented claim/date/metric corpus, citation integrity, PII/bias policy,
  A2UI allowlist, cross-tenant/IDOR, OpenAPI, and audit/correlation tests.
- Existing Python/web/PostgreSQL suites plus format, lint, type, build, migration drift,
  SAST/SCA, secrets, docs/links/Mermaid, pre-commit, and complete diff review.

### Manual verification

- Generate synthetic resume/letter drafts; open every claim citation and inspect blocked
  suggestions. Edit one draft and observe a new version/hash.
- Approve exact version, reject another with feedback, request more information, cancel,
  and verify stale approval is refused.
- Restart while pending using PostgreSQL, reload the record/checkpoint, resume safely,
  and inspect correlated audit plus A2UI-compatible review payload.

### Explicit exclusions

- Automatic email/submission/sharing, profile mutation, real resume export/PDF styling,
  provider/model calls, company research, ADK, OpenAI Agents SDK, A2A, Temporal timers,
  Pub/Sub, cloud deployment, production key management, and final legal certification.

### Stop condition

Complete `docs/reviews/phase-08-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 8 AND START PHASE 9`

## Completed implementation plan: Phase 7

**Objective:** build a typed, checkpointed LangGraph job-analysis workflow that
coordinates bounded specialist roles and returns cited match, gap, evidence, and
explanation results using fake providers by default and no paid calls.

### Scope and acceptance mapping

- Define explicit graph, node, model, retrieval, and audit state with ownership rules.
- Implement Manager, Intake, Job Analysis, Retrieval, Match, Skill Gap, Evidence
  Verification, and Explanation nodes; use deterministic routing for known paths and
  expose an evaluated model router only for ambiguous fixture cases.
- Produce validated structured job requirements, cited supported matches, missing and
  uncertain gaps, explicit insufficient-evidence state, and concise explanations.
- Add bounded node timeouts/retries, a terminal error node, cooperative cancellation,
  in-memory checkpoints/resume for local/test, and metadata-only trace events.
- Add a fake provider as the default and a fail-closed Gemini adapter requiring
  explicit live configuration, authorization/consent metadata, and no fallback.
- Add authenticated API start/status/resume/cancel routes and workflow progress that
  remains tenant-scoped and does not expose hidden reasoning.

### Deliverables and expected files

- Graph state, contracts, provider port, role dossiers, and orchestration service in
  `packages/core/` and `apps/api/` without provider imports in the domain package.
- LangGraph graph builder/checkpointer and Google Gen AI adapter in the API adapter
  layer; HTTP schemas/routes and versioned OpenAPI updates.
- Unit, API, contract, end-to-end, failure-injection, transition, routing, checkpoint,
  cancellation, grounding, and hallucination evaluation tests with synthetic fixtures.
- ADR, agent-role dossiers, annotated source, tutorial, exercises/answers, security,
  privacy, traceability, learning log, and `docs/reviews/phase-07-review.md`.
- Add `langgraph>=1.2.9,<1.3` (MIT, Python 3.10+) and
  `google-genai>=2.13,<2.14` (Apache-2.0, Python 3.10+) after lock/audit review.

### Architecture, security, privacy, migration, deployment, and cost

- LangGraph owns only the bounded in-process analysis run. Temporal remains the owner
  of durable business waits, schedules, compensation, and cross-service recovery.
- Nodes return partial state updates and cannot mutate fields owned by other roles.
  Deterministic routes are the default; no model decides authorization or truth.
- Retrieved text stays labeled untrusted. Evidence verification is deterministic and
  every supported result carries source/chunk citations; missing evidence stays
  uncertain or unsupported rather than being fabricated.
- The provider port accepts minimized, redacted structured prompts. The Gemini adapter
  has no credentials by default, never silently falls back, and live tests remain
  opt-in behind explicit cost and data-policy confirmation.
- Local/test checkpoints are process-local and synthetic. No migration, cloud
  deployment, paid resource, billing, or recurring service is authorized in Phase 7.

### Risks and mitigations

- State corruption or accidental overwrite: typed state, narrow node-update models,
  ownership tests, and checkpoint transition assertions.
- Hallucinated requirements or qualifications: structured validation, citations,
  deterministic verification, insufficient-evidence branches, and evaluation corpus.
- Prompt injection: source/job text is data, never instructions; fixed system policy,
  minimized prompts, injection labels, and adversarial fixtures.
- Retry duplication: only retry side-effect-free nodes; make trace identifiers stable
  and distinguish attempt, replay, resume, and fallback explicitly.
- Provider/API churn and cost: pin supported minor lines, fake-first tests, lazy/live
  client configuration, explicit provider identity, no fallback, and zero default cost.
- Checkpoint tenant leakage: thread identity is scoped by tenant/actor/run and every
  status/resume/cancel operation reauthorizes server-derived context.

### Automated verification

- Graph path/state ownership, deterministic/model router fixtures, structured output,
  delegation/handoff, timeout/retry/error, cancellation, checkpoint/resume tests.
- Grounding/hallucination evaluation for citations, supported/missing/uncertain gaps,
  prompt injection, and insufficient evidence; live Gemini marker remains skipped.
- Authenticated cross-tenant API and OpenAPI contract tests plus all existing suites.
- Python/web/PostgreSQL format, lint, type, test, build, SAST/SCA, secret, docs/link,
  Mermaid, pre-commit, governance validation, and complete diff review.

### Manual verification

- Submit a synthetic job-analysis run and inspect ordered node progress, cited evidence,
  match, gaps, concise explanation, provider name, and correlation ID.
- Submit a role with no supporting evidence and confirm explicit uncertainty.
- Inject a transient node failure, observe bounded retry/error state, then resume from
  the checkpoint; cancel a separate run and confirm no later node executes.
- Compare deterministic and fake model routing on documented fixtures without a live
  provider or paid call.

### Explicit exclusions

- Resume/cover-letter generation, human approval lifecycle, editable drafts, and
  LangGraph human interrupts (Phase 8).
- Temporal workflows, durable database checkpointing, schedules, email, application
  submission/tracking, company scraping/research, remote agents, ADK, OpenAI Agents
  SDK, A2A, cloud deployment, and production Gemini calls.

### Stop condition

Complete `docs/reviews/phase-07-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 7 AND START PHASE 8`

## Completed implementation plan: Phase 6

**Objective:** create a secure, typed capability layer for future agents and expose
only an approved read-only subset through MCP, with no model or cloud dependency.

### Scope and acceptance mapping

- Add nine narrow capabilities: profile lookup, evidence retrieval, job ingestion,
  skill taxonomy, deterministic matching, evidence verification, approval request,
  tenant audit lookup, and cost estimation.
- Give every tool strict Pydantic input/output contracts and generated JSON Schema;
  reject unknown fields and sanitize bounded outputs.
- Centralize capability metadata: version, description, risk, permissions, side
  effects, approval requirement, timeout, retry, idempotency, rate limit, audit
  policy, and MCP exposure.
- Enforce authenticated tenant context, deny-by-default tool permissions, per-tool
  authorization, in-memory local rate limits, bounded timeout/retry, idempotency
  replay, stable error taxonomy, correlation IDs, and audit outcomes.
- Add versioned OpenAPI discovery/invocation endpoints and an official MCP Python
  SDK server exposing only approved read-only capabilities.
- Keep approval requests as deterministic pending records only; Phase 8 owns the
  durable approval lifecycle and no consequential action executes here.

### Expected files and dependencies

- Tool domain contracts/metadata under `packages/core/`.
- Pydantic schemas, registry, executor, adapters, API routes, and MCP server under
  `apps/api/`.
- Unit/API/contract/MCP tests covering every capability plus invalid schema,
  authorization, timeout, retry, duplicate, rate limit, and sanitization cases.
- ADR, annotated source, tutorial, exercises/answers, security/privacy updates,
  traceability, learning log, and `docs/reviews/phase-06-review.md`.
- Add official `mcp>=1.28.1,<1.29` (MIT, Python 3.10+) to include the upstream
  security fixes. Resolve pinned Semgrep separately with `uvx` because its CLI
  dependency graph still requires vulnerable `mcp==1.23.3`; that version must not
  enter the application lock or runtime. A handwritten JSON-RPC implementation is
  rejected due to protocol/security maintenance risk. No MCP CLI extra is needed.

### Architecture, security, privacy, and cost decisions

- One registry is the authority for both HTTP and MCP discovery; adapters cannot
  bypass the executor or publish unregistered handlers.
- Tool identity never implies user authority. Server-derived authorization context
  enters every invocation, and underlying services/repositories retain their checks.
- MCP exposure is an explicit allowlist limited initially to read-only profile,
  retrieval, taxonomy, and cost capabilities. Audit data, job mutation, matching,
  verification, and approval creation remain HTTP/internal only.
- Idempotency keys are required for state-changing tools and scoped to tenant,
  actor, tool, and validated input hash. Reuse with different input fails closed.
- Rate limits are local deterministic safeguards for Phase 6, not distributed
  production enforcement. They contain no billing and reset on restart.
- Tools do not call models or external APIs. Cost estimates are deterministic CHF
  zero for current local implementations and never authorize spending.
- Inputs/outputs and retrieved content are not written to logs or audit records.
  Development fixtures remain synthetic.

### Risks and mitigations

- Tool privilege escalation: deny-default registry, permission metadata, context
  validation, MCP allowlist, underlying service checks, and hostile-tenant tests.
- Schema or adapter drift: derive JSON Schema from Pydantic and compare registry,
  OpenAPI, and MCP discovery in contract tests.
- Replay/duplicate mutation: scoped idempotency cache and input fingerprint conflict.
- Denial of service/wallet: payload limits, timeout, bounded retries, and per-actor/
  tenant/tool rate counters; distributed quotas remain Phase 15/16 work.
- Sensitive output leakage: response-model validation, recursive control-character
  removal/size bounds, retrieval `UNTRUSTED` labels, and sanitization tests.
- MCP ecosystem churn: pin the current stable v1 line below v2 and record a review
  trigger before migration.

### Automated verification

- Unit and contract tests for all nine tools and every capability schema.
- Invalid schema, foreign tenant, permission denial, timeout, retry, duplicate,
  idempotency conflict, rate-limit, sanitization, and audit/correlation tests.
- Official MCP in-memory protocol smoke test for list and read-only call plus proof
  that non-approved tools are absent.
- Existing Python/web/PostgreSQL suites, OpenAPI, format/lint/type/build, dependency,
  secret/SAST, documentation/link/Mermaid, pre-commit, and complete diff review.

### Manual verification

- Sign in locally, list capabilities and inspect schemas/metadata, successfully call
  one read-only tool, attempt one unauthorized call, repeat an idempotent mutation,
  trigger a rate limit, and inspect correlated audit facts.
- Start the local MCP server, list its allowlisted tools, call one read-only tool with
  synthetic context, and verify privileged/internal tools are not discoverable.

### Explicit exclusions

- LangGraph, LLM agents, model calls, provider fallback, live taxonomy/API sources,
  automatic browsing, scraping, email, submission, or external side effects.
- Durable approvals and restart recovery (Phase 8/12), distributed rate limiting,
  production OAuth for MCP, remote MCP deployment, and production credentials.
- Cloud resources, paid calls, billing, or recurring services.

### Stop condition

Complete `docs/reviews/phase-06-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 6 AND START PHASE 7`

## Completed implementation plan: Phase 5

**Status:** Complete on 2026-08-11; awaiting owner acceptance. Phase 6 has not
started.

**Objective:** ingest synthetic user documents safely and provide evaluated,
cited, tenant-isolated hybrid retrieval without a live model or paid service.

### Scope and acceptance mapping

- Accept bounded text/PDF bytes through authenticated multipart upload; validate
  name, declared type, magic bytes, size, hash, and a local scanner policy before
  moving content out of quarantine.
- Store raw bytes behind a `DocumentStorage` port using a local adapter; production
  object storage remains an explicit adapter boundary.
- Parse UTF-8 text and bounded PDF text, normalize deterministically, preserve page
  provenance, chunk with overlap, label every chunk untrusted, and detect a versioned
  indirect prompt-injection pattern set.
- Generate deterministic local hash embeddings for default/free behavior and store
  them in PostgreSQL `vector` columns beside a full-text index.
- Combine tenant/document-authorized lexical and vector candidates with reciprocal
  rank fusion, deterministic token-overlap reranking, bounded context assembly, and
  document/chunk/page citations.
- Add index-version metadata and an explicit re-index operation.
- Propagate an explicitly confirmed document deletion to raw local bytes, chunks,
  vectors, and retrieval results; keep the limitation of synchronous Phase 5
  approval visible until the durable Phase 8 approval workflow exists.
- Add a versioned synthetic retrieval dataset and thresholds for recall@k,
  precision@k, MRR, grounding, and citation correctness.

### Expected files and migrations

- Document/retrieval domain values and ports under `packages/core/`.
- Local storage/scanner/parser, deterministic embedder, RAG service, and PostgreSQL
  repository under `apps/api/`.
- Alembic revision `0002` enabling pgvector and adding documents/chunks/index fields.
- Authenticated upload, search, re-index, and confirmed-deletion API/UI flows.
- Unit/API/PostgreSQL/evaluation/injection/deletion/tenant-leakage test suites.
- ADR, annotated source, tutorial, exercises, security/privacy updates, traceability,
  and `docs/reviews/phase-05-review.md`.

### Architecture, dependency, security, privacy, and cost decisions

- PostgreSQL owns metadata, lexical search, and vectors; raw bytes stay behind an
  object-storage port. Local development uses `.data/documents`, which is ignored.
- `pgvector` (BSD-3-Clause) supplies SQLAlchemy/Psycopg vector types; `pypdf`
  (BSD-3-Clause) supplies bounded text extraction; `python-multipart` (Apache-2.0)
  enables FastAPI streaming multipart parsing. Direct custom vector encoding, a
  custom multipart parser, and PDF subprocess tooling are rejected as less mature.
- `UploadFile` is read with a 10 MiB plus one-byte bound; oversized inputs fail closed.
  PDF page/content-stream limits reduce, but cannot eliminate, parser/decompression
  risk. Scanner and parser isolation remain production hardening work.
- Deterministic embeddings are a tested local adapter, not a quality-equivalent
  production embedding model. No provider fallback or external disclosure occurs.
- Retrieved text is always untrusted data and never instruction. Injection matches
  label and constrain results rather than attempting to interpret them.
- Every retrieval SQL query includes tenant, owner/delegation, active document,
  and index-version predicates before ranking.
- Development uses synthetic fixtures. No cloud resource, paid API, model call, or
  recurring service is authorized or required.

### Risks and mitigations

- Parser bombs/exploits: strict byte/page/content-stream/output limits, quarantine,
  safe errors, pinned/scanned dependency, and no OCR/script execution.
- Tenant leakage: authorization before storage/retrieval plus predicates inside both
  lexical and vector candidate queries and hostile-ID integration tests.
- Retrieval quality illusion: versioned fixtures and numeric thresholds; disclose
  deterministic embedding limitations and empty results.
- Stale indexes: explicit component/index versions and transactional replacement.
- Deletion/object-store inconsistency: remove local bytes first, then transactionally
  delete derivatives; a metadata retry may be required if the DB step fails.
- Prompt injection: versioned detection corpus, untrusted labels, quoted context,
  and no agent/tool execution in this phase.

### Automated verification

- Ruff, strict MyPy, Pytest, OpenAPI, frontend format/lint/type/test/build.
- Alembic upgrade/downgrade/drift and real PostgreSQL/pgvector integration tests.
- Chunk/provenance, parser-limit, tenant leakage, hybrid retrieval, injection,
  re-index, deletion-propagation, empty-result, and evaluation-threshold tests.
- Dependency/secret/SAST scans, documentation/link/Mermaid checks, pre-commit,
  and complete diff review.

### Manual verification

- Start PostgreSQL, migrate, upload a synthetic text/PDF resume, inspect processing
  and citations, search known/unknown facts, upload injection text, re-index, confirm
  deletion, and verify the document disappears after API restart.

### Explicit exclusions

- OCR and searchable image content; image-to-text/model processing.
- Live/local neural embedding model downloads or external model calls.
- Generated answers, match/gap reasoning, LangGraph, agents, or tools.
- Cloud object storage, malware-engine service, sandbox/container isolation, RLS,
  unrestricted URL fetch, scraping, or external sources.
- Durable multi-state approval workflow, which remains Phase 8.

### Stop condition

Complete `docs/reviews/phase-05-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 5 AND START PHASE 6`

## Active implementation plan: Phase 4

**Objective:** replace process-local profile persistence with a versioned,
tenant-safe PostgreSQL profile and evidence-metadata foundation while keeping
development local, synthetic, and free.

### Scope and acceptance mapping

- Add versioned PostgreSQL migrations for profiles, skills, experience,
  education, evidence metadata, and deletion lifecycle fields.
- Define explicit repository transaction boundaries and tenant predicates.
- Support create/read/update profile operations with optimistic concurrency.
- Add evidence metadata intake with filename, media-type, and size validation;
  new evidence starts quarantined behind a malware-scanner port.
- Preserve the in-memory adapter for default unit/API tests and add opt-in real
  PostgreSQL migration, constraint, transaction, concurrency, and isolation tests.
- Extend the authenticated UI for profile editing and evidence registration.
- Map FR-001, FR-002, SEC-001, SEC-002, SEC-008, and NFR-019 to evidence.

### Expected files and migrations

- Richer domain models/services/ports under `packages/core/`.
- PostgreSQL tables, adapter, unit of work, and Alembic configuration under
  `apps/api/` and `migrations/`.
- Versioned profile/evidence HTTP contracts and authenticated web controls.
- Unit, API, contract, migration, PostgreSQL integration, upload-security,
  concurrency, transaction, and tenant-isolation tests.
- ADR, annotated source, tutorial, exercises, project records, and Phase 4 review.

### Architecture, dependency, security, and privacy decisions

- PostgreSQL is authoritative in configured environments; SQLite is not used as
  evidence for PostgreSQL behavior.
- SQLAlchemy 2 provides explicit transaction and mapping primitives, Psycopg 3
  is the PostgreSQL driver, and Alembic owns schema versions. All use permissive
  licenses. Direct SQL/custom migration runners were rejected because they add
  maintenance and recovery risk; an ORM does not replace authorization checks.
- The binary Psycopg distribution is convenient locally but bundles native
  libraries that must remain dependency-scanned and be reviewed for hardened
  production images.
- Every query includes tenant scope. IDs never authorize access by themselves.
- Stale profile versions fail atomically. Evidence metadata is minimized, and
  filenames are normalized before persistence. No raw bytes are retained in this
  phase; real object storage and scanner adapters remain later work.
- Soft-deletion timestamps and a default 30-day purge target establish lifecycle
  semantics; final retention periods and exceptions require legal review.

### Risks and mitigations

- The Docker daemon is unavailable: keep PostgreSQL tests opt-in, report them as
  blocked until a real server runs, and never substitute SQLite results.
- Schema/application drift: test Alembic head and metadata agreement plus a
  forward-recovery rehearsal.
- IDOR or tenant leaks: enforce policy in service/repository and test hostile IDs.
- Malicious uploads: accept bounded metadata only, use an allowlist, normalize
  names, quarantine by default, and expose a scanner interface with fail-closed
  behavior.
- Accidental overwrite: use integer versions in the update predicate and return a
  safe conflict response.
- Cost/cloud impact: none; no resource creation, billing, paid API, or model call.

### Automated verification

- Lock freshness; Ruff format/lint; strict MyPy; Pytest; API/OpenAPI contracts.
- Alembic upgrade/downgrade/forward-recovery and PostgreSQL repository tests when
  `CAREERPILOT_TEST_DATABASE_URL` points to an explicitly disposable database.
- Frontend format/lint/type/test/build; dependency, secret, and Semgrep scans.
- Documentation, Mermaid, pre-commit, migration review, and complete diff review.

### Manual verification

- Start PostgreSQL, apply migrations, start the app, create/edit a profile, add
  evidence metadata, reject an unsupported type, trigger a stale update, restart,
  and confirm persistence and tenant isolation.

### Explicit exclusions

- Parsing, object storage, embeddings, pgvector retrieval, and RAG (Phase 5).
- A real malware engine, cloud database, backups, deployment, or paid service.
- Destructive deletion UI without the later durable approval workflow.
- Model, agent, scraping, email, or automatic application behavior.

### Stop condition

Complete `docs/reviews/phase-04-review.md`, report all passed and blocked evidence,
and wait for:

`APPROVE PHASE 4 AND START PHASE 5`

## Completed plan: Phase 0

**Objective:** establish the complete product-discovery and architecture baseline
without production application code or cloud resources.

### Scope

- Product vision, personas, jobs-to-be-done, journeys, scope, metrics.
- Stable functional and non-functional requirements.
- Domain glossary and conceptual domain model.
- Architecture views, responsibility boundaries, and technology decisions.
- Agent-role classification and production-versus-lab separation.
- Initial STRIDE threat model, privacy assessment, risks, and cost assumptions.
- Durable repository governance, traceability, learning material, and review.

### Verification

- Run the Phase 0 document and requirement-ID validator.
- Run available Markdown and Mermaid checks without installing dependencies.
- Inspect links and the complete Git diff.
- Confirm no production application code or cloud resource exists.

### Exclusions

- Application or agent implementation.
- Dependency installation or workspace scaffolding.
- Database schemas or migrations.
- Cloud projects, APIs, billing, resources, deployments, or live-model calls.
- Phase 1 developer-environment remediation, including Docker Compose.

### Stop condition

Complete `docs/reviews/phase-00-review.md`, summarize the acceptance checklist,
and wait for:

`APPROVE PHASE 0 AND START PHASE 1`

## Completed implementation plan: Phase 1

**Objective:** create a reproducible, quality-gated repository foundation without
implementing product behavior.

### Scope and expected files

- Enforce Python 3.13 and Node.js 24 LTS through repository configuration.
- Create a `uv` workspace with an API shell and dependency-free core package.
- Create a Next.js/React/TypeScript web shell without a product journey.
- Add backend, frontend, services, packages, infrastructure, tests, labs, and
  documentation ownership structure.
- Pin runtime and development dependencies with committed lockfiles.
- Configure Ruff, strict MyPy, Pytest, pytest-asyncio, ESLint, Prettier, Vitest,
  pre-commit, detect-secrets, pip-audit, Semgrep, and repository secret scanning.
- Add Docker Compose syntax for local PostgreSQL/pgvector and document the missing
  local Compose plugin as a prerequisite issue.
- Add GitHub Actions quality gates and an architecture-boundary test.
- Add editor settings, tasks, `.env.example`, Makefile commands, setup tutorial,
  annotated source, exercises, answers, traceability, and the Phase 1 review.

### Architecture and security decisions

- The core package contains domain-safe primitives and cannot import frameworks,
  infrastructure, provider SDKs, or service code.
- The API depends inward on the core package; provider/service packages cannot be
  imported by core.
- Configuration examples contain names and safe local defaults only, never secrets.
- Default tests are offline and make no model or cloud calls.
- Dependency versions are exact in lockfiles; upgrades are intentional reviews.

### Risks and mitigations

- Installed runtimes differ from targets: use `uv`-managed Python 3.13 and enforce
  Node engines/version files; disclose any Node 26-only verification limitation.
- Docker Compose is missing: commit valid Compose configuration and a diagnostic,
  but do not mutate the owner's global Docker installation.
- Dependency downloads need public network access: use only official package
  registries and record licenses/security considerations.
- Tooling breadth can create noisy gates: pin configurations and distinguish
  mandatory failures from unavailable environmental integrations.

### Automated verification

- Python lock freshness, format, lint, strict typing, unit tests, architecture
  tests, dependency audit, Semgrep, and pre-commit.
- Frontend lockfile install, format, lint, type check, tests, and production build.
- Docker Compose config validation when the plugin is available; otherwise record
  the exact prerequisite failure.
- Secret scan, documentation validator, CI YAML parse/sanity checks, and Git diff
  review.

### Manual verification

- Follow macOS/VS Code setup from a clean-shell simulation.
- Confirm VS Code discovers Python, tests, formatting, and tasks.
- Run one aggregate quality command.
- Inspect directory ownership and local-service instructions.

### Exclusions

- Profile, job analysis, persistence adapters, API endpoints, or user journeys.
- Real authentication, model, agent, retrieval, or external service calls.
- Cloud resources, billing, deployment, or paid services.
- ADK/OpenAI agent scaffolding, deferred to their approved phases.

### Stop condition

Complete `docs/reviews/phase-01-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 1 AND START PHASE 2`

## Completed implementation plan: Phase 2

**Objective:** prove one deterministic, visible journey across the web, HTTP,
application, and temporary persistence boundaries without agents or live models.

### Scope and acceptance mapping

- Create a local professional profile from a display name and short summary.
- Submit a bounded, user-supplied job description.
- Return a deterministic placeholder match analysis and show it in the UI.
- Add versioned FastAPI contracts, application service, repository protocol,
  in-memory adapter, health/readiness, safe errors, and correlation IDs.
- Establish structured privacy-safe logs and OpenTelemetry propagation APIs.
- Add unit, API, contract, frontend accessibility-smoke, and end-to-end tests.
- Map FR-001, FR-003, NFR-002, NFR-010, NFR-011, and relevant security/privacy
  foundations to source and test evidence without claiming later-phase completion.

### Expected files

- Core domain/application modules under `packages/core/src/careerpilot_core/`.
- API contracts, adapters, telemetry, middleware, and app factory under
  `apps/api/src/careerpilot_api/`.
- UI form, API client, and tests under `apps/web/src/`.
- Phase 2 test suites under `tests/` plus updated CI and local commands.
- ADR/update notes, annotated source, tutorial, exercises, traceability, learning
  log, and `docs/reviews/phase-02-review.md`.

### Architecture, security, and privacy decisions

- Core stays framework-independent; adapters depend inward through a protocol.
- Analysis is a pure deterministic function with no provider fallback.
- Inputs have explicit length/content validation and synthetic examples.
- Logs and traces carry opaque correlation IDs and operation metadata, not profile
  or job-description content.
- API errors use a stable safe envelope and do not expose stack traces.
- The in-memory repository is process-local and its restart data loss is visible,
  tested, and documented; PostgreSQL remains Phase 4 work.

### Risks and mitigations

- Browser/API origin mismatch: configure one explicit local public API URL and
  narrowly scoped local CORS behavior.
- Contract drift: validate OpenAPI plus shared fixtures at API/client boundaries.
- False product claims: label output deterministic placeholder analysis and avoid
  inferred skills, rankings, or evidence claims.
- Personal-data leakage: use minimized fields, bounded inputs, synthetic tests,
  and metadata-only telemetry.
- Scope creep into identity/database/agents: keep those adapters absent and record
  the phase ownership in docs and tests.

### Automated verification

- Lock freshness; Python and frontend format, lint, and strict typing.
- Unit, API, contract, frontend, accessibility-smoke, and end-to-end tests.
- OpenAPI schema and structured error/correlation assertions.
- Production frontend build, security scans, dependency audits, docs/link/Mermaid
  checks, pre-commit, and full diff review.

### Manual verification

- Start API and web through one documented command.
- Enter synthetic profile and job data and observe the deterministic analysis.
- Confirm the correlation ID is visible.
- Trigger invalid input and inspect the understandable safe error.
- Restart the API and confirm the documented in-memory persistence limitation.

### Exclusions

- Real identity, tenants, authorization, audit ledger, or organization features.
- PostgreSQL application persistence, schemas, or migrations.
- LLMs, agents, retrieval, uploads, scraping, or external provider calls.
- Cloud resources, deployment, paid APIs, or non-synthetic customer data.

### Stop condition

Complete `docs/reviews/phase-02-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 2 AND START PHASE 3`

## Completed implementation plan: Phase 3

**Objective:** establish a multi-tenant, deny-by-default security foundation with
provider-neutral identity, layered authorization, and auditable access.

### Scope and acceptance mapping

- Model actors, personal/future organization tenants, memberships, roles,
  permissions, policy inputs/decisions, delegations, and audit events.
- Define an OIDC-compatible identity-verifier port and a local-only development
  session adapter using synthetic users and opaque process-local tokens.
- Derive tenant context from authenticated memberships and reject forged tenant
  selection.
- Enforce RBAC plus contextual ABAC at API, application, and repository layers.
- Add document/tool permission decisions now, with features remaining inactive.
- Add hash-chained append-only audit evidence and an authorized audit viewer.
- Cover SEC-001–SEC-005 and relevant NFR/API/audit requirements with source and
  test evidence while flagging production identity and legal retention review.

### Expected files

- Identity/access/audit domain modules and policy tests under `packages/core/`.
- Local identity/session, tenant-safe repository, audit adapter, request context,
  versioned contracts, and routes under `apps/api/`.
- Local user/tenant controls and audit viewer under `apps/web/`.
- Permission, cross-tenant, IDOR, deny-default, audit, and error-contract tests.
- ADR, threat/privacy updates, annotated source, tutorial, exercises, traceability,
  learning log, and `docs/reviews/phase-03-review.md`.

### Architecture, security, and privacy decisions

- Authentication proves an external subject; internal membership determines
  tenant context and authority.
- The client may request an active tenant ID but cannot assert membership, role,
  actor ID, or permissions.
- RBAC grants a candidate action; ABAC must also allow tenant, ownership,
  delegation, purpose, sensitivity, and resource state. Any missing rule denies.
- Personal tenants are active initially. Organization and coach types exist in
  the model but their product workflows remain disabled.
- Local sessions are random, process-local, non-cookie bearer tokens and are
  refused outside the `local` environment. They are not production credentials.
- Audit payloads exclude career content and use stable IDs/action/outcome/reason;
  events are append-only and SHA-256 hash-chained in this temporary adapter.
- Cross-tenant identifiers return a non-enumerating response while recording a
  security denial.

### Risks and mitigations

- Header spoofing: resolve every actor/tenant/role server-side from the session.
- IDOR: scope repositories by authorized context and test foreign identifiers.
- Role confusion: centralize permission mappings and exhaustively matrix-test.
- Policy bypass: require context at service/repository methods and retain API
  guards; architecture tests reject insecure signatures/import directions.
- Audit PII/tampering: allow-list metadata, pseudonymous IDs, hash chaining, and
  completeness/integrity tests; final retention needs professional legal review.
- Development auth misuse: local-only environment gate, loopback services,
  prominent UI/docs warning, and no password/OIDC-provider imitation.

### Automated verification

- Permission matrix and unrecognized-action deny tests.
- Authentication, membership, tenant-forgery, role-change, and error-contract tests.
- Cross-tenant read/write and IDOR tests at API, service, and repository layers.
- Audit success/denial/completeness/hash-integrity/viewer-authorization tests.
- Existing deterministic journey, OpenAPI, frontend, accessibility, build,
  security, dependency, documentation, and architecture gates.

### Manual verification

- Log in as synthetic users belonging to different personal tenants.
- Create data in each tenant and verify the other user cannot access it.
- Change a synthetic membership role and observe permission changes.
- Inspect correlated success and denial events in the audit viewer.
- Restart and confirm local sessions, data, and audit events are intentionally lost.

### Exclusions

- Google Identity Platform resource creation, live OIDC calls, passwords, MFA,
  email verification, account recovery, or production key management.
- Activated organization administration or coach delegation workflows.
- PostgreSQL schemas/migrations, durable sessions/audit, or production retention.
- Documents, retrieval, tools, models, agents, cloud resources, or paid services.

### Stop condition

Complete `docs/reviews/phase-03-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 3 AND START PHASE 4`
