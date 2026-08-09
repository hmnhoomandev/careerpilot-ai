# CareerPilot AI Repository Instructions

## Mission

Build CareerPilot AI as a production-grade, educational, multi-tenant career
intelligence platform. The first user is an individual job seeker. Preserve
future organization and career-coach boundaries without activating them early.

## Governing agreement

- Read `CAREERPILOT_CODEX_MASTER_PROMPT.md`, `PLANS.md`, and
  `docs/project/PROJECT_STATE.md` before starting work.
- Work on exactly one approved phase. Never begin the next phase implicitly.
- Use English for code, documentation, tests, schemas, UI text, and examples.
- Follow Inspect, Plan, Explain, Implement, Verify, Review, Teach, Report, Stop.
- Keep decisions and current state in repository files, not only in chat.
- Begin implementation phases from a clean working tree. Report existing changes
  and obtain direction before touching overlapping files.
- Do not make unrelated changes or install dependencies without documenting
  purpose, license, alternatives, security, and ADR impact.
- Do not claim a check passed unless its exit status was observed.
- Default tests must not make live or paid model calls.
- Never place secrets or real personal data in source, fixtures, logs, examples,
  screenshots, or documentation. Use synthetic data during development.
- Do not create paid resources, enable billing, call a paid API, or begin a
  recurring service without explicit owner approval.
- Do not silently switch model providers.

## Product invariants

- Deny access by default and enforce tenant isolation at every data boundary.
- Every material generated career claim must cite verified user evidence.
- Missing evidence produces an explicit suggestion requiring confirmation, not a
  fabricated fact.
- Human approval precedes external communication, submission, sharing,
  publishing, inferred profile mutation, deletion, sensitive transfer,
  high-risk tooling, irreversible action, or spending.
- Minimize and redact personal data before any authorized external model call.
- Do not expose hidden reasoning; provide concise decision summaries and sources.

## Architecture boundaries

- FastAPI owns the HTTP API; Next.js owns the web application.
- PostgreSQL and pgvector own production relational and vector persistence.
- LangGraph owns the primary in-process agent graph.
- Temporal owns long-running durable business workflows.
- Google ADK and OpenAI Agents SDK live in isolated specialist services.
- A2A connects independently deployed agents; MCP exposes narrow reusable tools.
- Pub/Sub carries asynchronous integration events.
- Dapr is optional and requires a demonstrated-value ADR.
- DBOS, Restate, and GKE are bounded comparison/reference paths, not production
  defaults.

## Required quality and documentation

- Production Python must be typed and important public APIs documented.
- Explain intent, invariants, trade-offs, and security decisions rather than
  translating syntax in comments.
- Important source files require a corresponding `docs/annotated-source/` entry.
- Keep requirements traceability, project state, roadmap, decision log, learning
  log, and the current phase review synchronized.
- Run phase-relevant format, lint, type, test, security, build, and documentation
  checks; disclose warnings, skips, and limitations.
- Review the complete diff before ending a phase.

## Phase gate

At the end of Phase N, stop until the owner gives the exact command:

`APPROVE PHASE <N> AND START PHASE <N+1>`

Anything else is feedback on the current phase.
