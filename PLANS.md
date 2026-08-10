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
