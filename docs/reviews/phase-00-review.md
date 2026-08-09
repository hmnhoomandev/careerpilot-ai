# Phase 0 Review

## 1. Phase objective

Create the complete product-discovery and architecture baseline for CareerPilot
AI without production application code, dependency installation, paid calls, or
cloud resources.

## 2. Delivered features

- Product vision, personas, jobs-to-be-done, journeys, scope, and metrics.
- 74 stable requirements: 24 functional, 22 security/privacy, 20 quality/
  operational, and 8 professional legal-review topics.
- Domain glossary, bounded contexts, conceptual model, and state ownership.
- System-context, container, component, data-flow/trust, workflow, and deployment
  diagrams.
- Technology matrix, production/lab map, and classification of all 19 target roles.
- Twelve ADRs covering architecture, runtimes, data, orchestration, providers, UI,
  deployment, observability, RAG, identity, cost, and safe UI messages.
- Initial STRIDE threat model, privacy assessment, risk register, and cost policy.
- Repository governance, readiness/done definitions, traceability, learning log,
  tutorial, exercises, answers, and a documentation validator.

## 3. Explicitly not delivered

- Production application or agent code.
- Python/Node workspace, dependency locks, or framework scaffold.
- Database schemas, migrations, APIs, UI, containers, or CI.
- Cloud project, billing, managed resource, deployment, or live-model call.
- Docker Compose remediation, which is assigned to Phase 1.
- Legal certification or a claim of guaranteed GDPR/FADP compliance.
- External A2UI conformance; Phase 14 must select a target through a follow-up ADR.

## 4. Files created or changed

Created root governance and index files; product, project, architecture, diagram,
ADR, security, cost, tutorial, exercise, annotated-source, and review documents;
and `scripts/validate_phase0.py`. Updated only Phase 0-created state and roadmap
files during closeout. The original master prompt was not modified.

## 5. Architecture decisions

- Modular core with bounded ADK and OpenAI specialist services.
- Python 3.13 and Node.js 24 LTS targets, enforced in Phase 1.
- PostgreSQL/pgvector production persistence.
- LangGraph for bounded agent graphs; Temporal for durable business workflows.
- Gemini in Google/LangGraph learning paths; OpenAI only in its bounded service;
  fakes by default and no silent provider fallback.
- OIDC identity boundary with RBAC plus ABAC and deny-by-default policy.
- Zurich-first Cloud Run deployment, subject to explicit future cost approval.
- OpenTelemetry with privacy-safe export.

## 6. Security and privacy review

The threat model covers spoofing, tampering, repudiation, disclosure, denial of
service, elevation, prompt injection, SSRF, malicious uploads, stale approvals,
cross-tenant retrieval, supply chain, and denial-of-wallet. Privacy design covers
purpose, minimization, consent, correction, export, deletion propagation,
retention, residency, provider disclosure, special-category data, and telemetry.
Eight legal-review topics are explicitly flagged. Residual risks remain open in
the risk register and must be tested in assigned phases.

## 7. Data, schema, and migration impact

No schema or migration exists. The conceptual model establishes tenant ownership,
claim-evidence links, immutable approved versions, derivative lifecycle, and
separate application/graph/workflow/session/memory/audit state. Phase 4 owns the
first production schema and migration evidence.

## 8. Automated commands and exact results

| Command | Exit | Exact result |
|---|---:|---|
| `git status --short --branch` at phase start | 0 | `## main...origin/main` (clean) |
| `git diff --check` | 0 | No output; no whitespace errors in tracked diff context |
| `uv run --no-project python scripts/validate_phase0.py` | 0 | Warning: no project was found; then `Phase 0 validation passed: 24 required files, 74 requirement IDs, 49 Markdown files.` |
| `PYTHONDONTWRITEBYTECODE=1 uv run --no-project python -m py_compile scripts/validate_phase0.py` | 0 | Warning: no project was found; no compiler error output |
| `rg -n 'TBD\|TODO\|FIXME\|PLACEHOLDER' --glob '*.md' --glob '*.py' --glob '!docs/reviews/phase-00-review.md' .` | 1 | No matches; review excluded because it records the literal search expression; ripgrep uses exit 1 for no matches |
| `git diff --check` after closeout | 0 | No output |

`markdownlint`, `markdownlint-cli2`, Mermaid CLI, `lychee`, and
`markdown-link-check` were not installed. No dependency was downloaded during
this documentation-only phase. The validator checked H1s, Mermaid fence balance,
local Markdown links, required documents, stable ID sequences, and a narrow
secret-literal pattern. It does not replace a full Markdown parser, remote HTTP
link checker, or Mermaid grammar validator; Phase 1 will establish pinned tooling.

One exploratory shell command for a regex-based secret scan was malformed by
shell quoting and exited before running; it was corrected by using the validator's
Python regex and the final validator passed. The first two `uv` verification
attempts also failed before running Python because the sandbox denied access to
`~/.cache/uv`; the validator and compiler were rerun with scoped cache access and
completed with the results above.

## 9. Manual test checklist

| Check | Expected result | Actual result |
|---|---|---|
| Explain target user/problem in under two minutes | Individual job seeker receives truthful, cited, controlled application help | Pass in product vision |
| Follow main journey | Profile/evidence through analysis, drafts, approval, tracking | Pass in journey and workflow diagram |
| Identify technology ownership | One primary responsibility per technology | Pass in architecture map |
| Separate production from labs | Temporal/LangGraph/Cloud Run separate from DBOS/Restate/GKE labs | Pass in production/lab map |
| Find assumptions and exclusions | Budget, residency, legal, provider, and scope limits are explicit | Pass across state, ADRs, privacy, and cost docs |
| Inspect legal claims | No certification claim; legal-review items labeled | Pass in requirements and privacy assessment |
| Owner accepts architecture and phase order | Explicit owner review | Pending owner |

## 10. Requirements traceability

All accepted requirement groups map to Phase 0 design evidence in
`docs/project/REQUIREMENTS_TRACEABILITY.md`. No requirement is marked implemented
or verified by application tests because no application code exists.

## 11. Screenshots or example requests/responses

Not applicable to a documentation-only phase. Mermaid source is included for all
required architecture views.

## 12. Known limitations, debt, and risks

- Full Markdown, remote-link, and Mermaid syntax tools are deferred to Phase 1.
- Service availability and prices are time-sensitive and require revalidation
  before cloud planning or creation.
- The OpenAI docs connector was registered during research but its tools require a
  fresh session; only official OpenAI web documentation was used as fallback.
- Docker Compose is unavailable locally.
- Global Python 3.14 and Node.js 26 differ from selected project targets.
- Legal retention, lawful basis, cross-border transfer, employment-AI, source-
  licensing, and incident duties require professional review.
- Recovery, retrieval, grounding, availability, latency, durability, and cost
  targets are unmeasured design targets until their assigned phases.

## 13. Rollback and recovery instructions

No database, dependency, or external resource requires rollback. Before acceptance,
Phase 0 consists only of uncommitted new documentation/tooling files. A safe
rollback would first preserve any desired review copy, then remove only the exact
new paths listed by `git status`; destructive execution requires owner
confirmation. The original tracked master prompt and initial commit remain intact.

## 14. Learning summary

The owner can now distinguish product outcomes from framework choices; state
owners; deterministic and agentic work; manager delegation, handoff, agent-as-
tool, MCP, and A2A; retry/replay/recovery/compensation/fallback; RBAC/ABAC;
authentication/authorization; and STRIDE/privacy architecture. Exercises and
separate answers reinforce these concepts.

## 15. Owner acceptance checklist

- [ ] Product vision and first journey match intent.
- [ ] Requirements and exclusions are understandable.
- [ ] Every technology has a justified bounded responsibility.
- [ ] Production and comparison paths are clearly separated.
- [ ] Security, privacy, cost, residency, and legal-review boundaries are adequate.
- [ ] Python 3.13 and Node.js 24 LTS are accepted for Phase 1 enforcement.
- [ ] Phase order and Phase 1 scope are accepted.

## 16. Proposed next phase

Phase 1 — Repository foundation and developer experience. It will establish
version-managed runtimes, `uv` and Next.js workspaces, pinned tools, repository
structure, Docker Compose remediation, CI, quality gates, and setup teaching. It
will not implement product features.

Recommend a Git checkpoint after owner acceptance and before Phase 1 begins.

## 17. Exact approval command

`APPROVE PHASE 0 AND START PHASE 1`
