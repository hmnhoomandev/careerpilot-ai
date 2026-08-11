# Project State

- **Project:** CareerPilot AI
- **Current phase:** Phase 3 — identity, tenancy, authorization, and audit
- **Phase status:** Implementation and verification complete; awaiting owner acceptance
- **Last updated:** 2026-08-10
- **Working tree at phase start:** Clean at `5f2386a` on `main`, tracking `origin/main`
- **Production code:** Accepted deterministic slice plus Phase 3 security foundation in progress
- **Cloud resources created:** None
- **Paid calls made:** None

## Binding owner decisions

- Individual job seekers are the first users; coaches and organizations are later.
- Launch baseline is Switzerland and the EU, with GDPR-oriented principles and
  Swiss FADP consideration; no claim of legal certification.
- English is the initial language; architecture must be internationalization-ready.
- Prefer Google Cloud `europe-west6` (Zurich); an EU fallback requires a recorded
  availability, residency, security, privacy, latency, and cost analysis.
- Environments are local, test/CI, staging, and production.
- Development and learning budget is CHF 0/month. Any cost requires explicit
  prior approval and a free/local alternative analysis.
- Identity uses an OIDC boundary, a local development adapter, and Google Identity
  Platform as the initial production reference.
- Gemini is the initial Google/LangGraph learning-path model; OpenAI remains in
  its bounded Agents SDK service; fakes are the default.
- Development uses synthetic personal data.
- User data supports access, correction, export, and deletion, with a default
  30-day recoverable deletion window subject to legal review.
- Job/company data begins with user input, approved APIs, and explicitly permitted
  sources; unrestricted scraping is forbidden.
- Initial availability design target is 99.5% monthly; no silent provider fallback.

## Current decisions

- Python 3.13 is the Phase 1 target runtime.
- Node.js 24 LTS is the Phase 1 target runtime.
- The production architecture is a modular core plus bounded specialist services,
  with event-driven integration where justified.
- Cloud Run is the first deployment target; GKE is a later reference.
- PostgreSQL/pgvector is authoritative production persistence.
- LangGraph and Temporal have separate graph and durable-process ownership.

## Known blockers and constraints

- Docker Compose 5.4.0 is installed and its configuration validates, but the
  local Docker daemon is not running.
- Global Node.js 26 differs from the repository target; Phase 1 verification used
  Node.js 24. Python verification used the selected Python 3.13 runtime.
- Google Cloud CLI cannot write its default config under the current sandbox.
- Final legal retention periods and regulatory interpretations require qualified
  professional legal review.
- No paid service may be used under the current CHF 0 budget.

## Next action

Review `docs/reviews/phase-03-review.md` and stop for:

`APPROVE PHASE 3 AND START PHASE 4`
