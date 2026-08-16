# Developer guide

## Setup and workflow

Use Python 3.13, Node.js 24 LTS, uv 0.11.29-compatible locking, npm and Docker Desktop.
Run `make setup`, then `make check`. Default tests use fake providers and synthetic data;
never add a live-provider test to the default path.

Production dependency direction is core → ports ← adapters. FastAPI owns HTTP, Next.js
presentation, PostgreSQL business/vector persistence, LangGraph bounded agent graphs,
Temporal durable processes and specialist SDKs isolated services. Comparison labs remain
outside the root workspace.

## Change process

1. Read `AGENTS.md`, `PLANS.md`, project state, relevant ADR and requirements.
2. Begin clean, plan one approved phase/change, and write strict contracts first.
3. Enforce server-derived tenant/actor authority and deny by default at every boundary.
4. Keep generated claims evidence-linked; use explicit confirmation for missing facts.
5. Minimize/redact/authorize/consent before external model transfer; never fallback silently.
6. Add unit, boundary, hostile, recovery and documentation evidence proportional to risk.
7. Run focused checks, then full regression/security/docs/release gates and inspect the diff.

Important source requires module/public API documentation and a matching annotated-source
entry. Migrations are Alembic-owned and use forward recovery. Dependency changes require
purpose, license, alternative, security and ADR review. No paid or mutable cloud operation
is implied by a coding task.

## Useful commands

- `make dev`: local API/web process.
- `make db-up`, `make db-migrate`, `make db-integration-test`: disposable PostgreSQL path.
- `make check`: complete standard quality/security/documentation/frontend path.
- `make release-readiness`: bounded local candidate evidence.
- `uv run pytest -m temporal`: Temporal recovery tests.

Generated `.artifacts/`, `.data/`, virtual environments and secrets stay ignored.
