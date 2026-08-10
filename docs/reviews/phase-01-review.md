# Phase 1 Review

## 1. Phase objective

Create a reproducible, quality-gated repository foundation without product
behavior, paid services, cloud resources, or live model calls.

## 2. Delivered features

- Python 3.13 `uv` workspace with dependency-free core and API shell packages.
- Node.js 24 Next.js, React, and strict TypeScript web foundation.
- Backend, frontend, services, infrastructure, packages, tests, labs, tools, and
  documentation ownership structure.
- Exact Python and npm lockfiles plus runtime version and engine enforcement.
- Ruff, MyPy, Pytest, ESLint, Prettier, TypeScript, Vitest, pre-commit,
  detect-secrets, pip-audit, npm audit, and isolated Semgrep gates.
- PostgreSQL/pgvector Compose definition with a required non-secret password.
- Three-job GitHub Actions workflow for Python, frontend, and documentation.
- Architecture import-boundary test and repository-configuration tests.
- Markdown lint, external-link, and rendered-Mermaid validation.
- macOS/VS Code tutorial, annotated source, exercises, and answers.

## 3. Explicitly not delivered

- Profile, job analysis, application tracking, or any other product journey.
- API endpoint, database schema/migration, authentication, authorization, or UI
  workflow.
- Agent, model, retrieval, MCP, A2A, or external-service integration.
- Cloud project, billing, deployment, paid API call, or recurring service.
- ADK scaffold, which remains gated to its approved implementation phase.

## 4. Architecture and dependency decisions

ADR-0013 records the workspace and quality-gate choices. The core package must
remain independent of web frameworks, persistence, provider SDKs, and service
packages; an AST test enforces the boundary. Python uses a cross-platform `uv`
lock and npm uses one exact lock per JavaScript workspace. Configuration examples
contain safe local values and variable names only.

The normal Python environment has no known audited vulnerability. Semgrep 1.172.0
currently pins vulnerable `mcp==1.23.3`, so it is isolated in a non-default SAST
group, run with metrics disabled, and its MCP server is never started. This is a
documented, review-triggered tooling exception rather than a production
dependency acceptance.

## 5. Security and privacy review

Default tests are synthetic and offline. No customer data, credentials, model
provider, paid service, or cloud resource was used. Secret scanning covers
tracked and not-yet-tracked repository files. Semgrep scans untracked source too
while excluding generated dependencies and build output. Compose binds the local
database port to loopback and requires the password through environment input.

Residual Phase 1 risks are dependency supply-chain compromise, the isolated
Semgrep transitive finding, and untested production controls. The latter belong
to later security, identity, data, and deployment phases.

## 6. Data, schema, migration, deployment, and cost impact

There is no application schema or migration. The Compose file is developer
infrastructure syntax only; it created no container because the local daemon is
not running. No deployment was attempted. Cloud/model spend remains CHF 0.

## 7. Automated verification and exact results

| Gate | Exact result |
|---|---|
| `uv lock --check` | Resolved 112 packages; lock current |
| Ruff format/lint | 74 files formatted; all checks passed |
| strict MyPy | No issues in 11 source files |
| Pytest | 5 passed |
| Frontend format/lint/typecheck | Passed under Node.js 24 |
| Vitest | 1 file and 1 test passed |
| Next production build | Passed; static `/` and `/_not-found` generated |
| `pip-audit` | No known vulnerabilities; two internal packages skipped as not on PyPI |
| npm audits | Web: 0 vulnerabilities; documentation tools: 0 vulnerabilities |
| Semgrep | 3 rules on 11 Python targets; 0 findings |
| detect-secrets | Passed for tracked and untracked non-ignored files |
| pre-commit | All five hooks passed |
| markdownlint | 57 files; 0 issues |
| external-link check | Passed |
| Phase 0 structural validator | 24 files, 74 IDs, and 64 Markdown files passed |
| Mermaid render validator | 8 diagrams rendered |
| Compose config | Passed with synthetic local password |
| clean setup simulation | Python workspace and both npm workspaces installed from locks |

Semgrep printed a macOS signal-handler warning but completed successfully with
zero blocking findings. npm kept optional/unapproved install scripts disabled for
`fsevents`, `unrs-resolver`, and documentation Puppeteer; Puppeteer's browser
download was intentionally disabled. One documentation transitive package emitted
a deprecation warning. None changed the successful gate results.

## 8. Failures encountered and corrections

- Early npm processes became orphaned and produced an incomplete generated
  install. The exact generated `node_modules` content was removed and recreated
  from the lockfile; source files were not discarded.
- TypeScript 7 conflicted with current framework peer ranges, so the supported
  exact TypeScript 6.0.3 release was selected.
- The initial Phase 0 validator traversed generated dependency Markdown after
  dependencies were installed. It now excludes generated directories.
- The initial documentation glob missed a second nested directory level. The
  lint command now includes the architecture diagram directory.
- The initial Semgrep invocation considered only Git-tracked files. Local security
  verification now uses `--no-git-ignore` plus explicit generated-file exclusions.
- Next.js normalized `tsconfig.json`; Prettier then normalized that framework
  change and the final hook passed.
- The sandbox initially blocked the default uv cache and external links. The same
  checks passed with scoped cache and read-only network approval.

## 9. Manual verification checklist

| Check | Actual result |
|---|---|
| Inspect repository ownership and boundaries | Pass |
| Validate Compose syntax without creating resources | Pass |
| Start PostgreSQL and inspect health | Pending: Docker daemon is not running |
| Follow clean setup in a temporary repository copy | Pass |
| Confirm VS Code selects Python 3.13 and discovers tasks/tests | Pending owner UI check |
| Run aggregate local feedback hooks | Pass: all pre-commit hooks |

The two pending checks require the owner's desktop Docker/VS Code applications;
they do not hide a failed automated gate.

## 10. Requirements traceability

`docs/project/REQUIREMENTS_TRACEABILITY.md` maps the Phase 1 implementation and
test evidence for runtime/cost, CI, environment, architecture, secret, synthetic
data, and dependency-control requirements. Product requirements remain deferred.

## 11. Known limitations and rollback

CI configuration is locally parsed/tested but will obtain its first hosted-run
evidence only after a GitHub push. Docker runtime health is unverified without the
daemon. The web page is deliberately a non-product foundation.

No external state needs rollback. Before acceptance, changes are repository-local
and uncommitted. Preserve any desired review copy, then remove only the exact
Phase 1 paths listed by Git; destructive rollback requires owner confirmation.

## 12. Learning summary

The owner can now distinguish manifest constraints from locks, workspace members
from one default package, local hooks from clean CI, framework adapters from the
domain core, and SAST/SCA/secret scanning from one another. The tutorial and
exercises provide repeatable setup and failure-diagnosis practice.

## 13. Owner acceptance checklist

- [ ] Repository structure and boundary direction are understandable.
- [ ] Python 3.13 and Node.js 24 enforcement are accepted.
- [ ] Local, CI, security, and documentation gates are adequate.
- [ ] The isolated Semgrep exception and review trigger are accepted.
- [ ] Docker daemon and VS Code manual checks are understood.
- [ ] Phase 2 remains limited to the deterministic walking skeleton.

## 14. Proposed next phase

Phase 2 — Deterministic walking skeleton. It will connect the smallest typed,
offline application path across the approved boundaries without introducing
agents, live models, or cloud resources.

## 15. Exact approval command

`APPROVE PHASE 1 AND START PHASE 2`
