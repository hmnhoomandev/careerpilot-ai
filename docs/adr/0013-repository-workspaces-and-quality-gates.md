# ADR-0013: Repository Workspaces and Quality Gates

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

CareerPilot needs reproducible Python and TypeScript foundations, fast local
feedback, and architecture boundaries before product implementation.

## Decision

Use one `uv` workspace and lockfile for the Python API and core packages, and one
npm lockfile for the Next.js application. Use Python 3.13 and Node.js 24 LTS.
Ruff, strict MyPy, Pytest, ESLint, Prettier, TypeScript, Vitest, pre-commit,
detect-secrets, pip-audit, and Semgrep form the Phase 1 quality baseline. CI runs
locked installs and the same checks.

## Consequences

A shared Python environment does not itself prevent undeclared cross-package
imports, so an AST architecture test is mandatory. The npm workspace remains
separate because JavaScript dependency management has different semantics.
Tooling costs CHF 0 but public registry access is required for setup.

## Sources

- [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
- [Next.js installation](https://nextjs.org/docs/app/getting-started/installation)
