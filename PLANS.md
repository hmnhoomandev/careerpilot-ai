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
