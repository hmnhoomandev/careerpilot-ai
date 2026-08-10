# Tutorial: Phase 1 Developer Setup on macOS and VS Code

## What the tools do

- `uv` installs Python 3.13, resolves one workspace lockfile, creates `.venv`, and
  runs Python tools at locked versions.
- Node.js 24 LTS runs Next.js, TypeScript, tests, and documentation tooling.
- npm lockfiles make the web and documentation installs reproducible.
- Docker Compose describes local PostgreSQL/pgvector. A Docker-compatible daemon
  must be running; the repository does not silently start one.
- pre-commit runs fast checks before a commit; CI repeats the full clean checks.

## 1. Verify or install prerequisites

```sh
git --version
uv --version
python3.13 --version
node --version
npm --version
docker --version
docker compose version
code --version
```

Expected project lines are Python 3.13 and Node.js 24. The global shell may use a
different Python because `uv` selects the project interpreter. Use `nvm`, `fnm`,
or Homebrew to select Node 24 before npm commands.

Homebrew examples, reviewed before execution:

```sh
brew install uv node@24 docker docker-compose
```

Docker Desktop supplies a daemon but has licensing terms that organizations must
review. Colima is an open-source local alternative:

```sh
brew install colima
colima start
```

Do not install or start either option without understanding local resource and
license implications.

## 2. Create local configuration

```sh
cp .env.example .env
```

Set `CAREERPILOT_POSTGRES_PASSWORD` in `.env` to a unique local-only value. Never
commit `.env`; `.gitignore` excludes it. The example intentionally contains no
credential.

## 3. Reproduce dependencies

```sh
make setup
```

This runs `uv sync --all-packages --locked` and `npm ci` in both npm packages.
The documentation install skips a browser download and uses an installed Chrome
for Mermaid rendering.

Expected results:

- `.venv` uses Python 3.13.
- `uv lock --check` reports the lockfile is current.
- Both npm directories contain generated, ignored `node_modules` directories.
- No model, cloud, or paid service is called.

## 4. Configure VS Code

Open the repository root:

```sh
code .
```

Install recommended extensions when prompted. Confirm:

1. Python interpreter is `.venv/bin/python` and reports 3.13.
2. The Test panel discovers five Python tests and one frontend test.
3. Ruff formats Python and Prettier formats frontend files.
4. `Terminal → Run Task → CareerPilot: all quality checks` runs `make check`.

## 5. Validate local infrastructure configuration

Before starting services:

```sh
docker compose config --quiet
```

With a running daemon, use:

```sh
docker compose up -d postgres
docker compose ps
```

Expected: PostgreSQL becomes healthy and binds only to `127.0.0.1`. Phase 1 does
not run migrations or store product data. Stop it with `docker compose down`;
named-volume data remains until an explicitly approved removal.

## 6. Run quality gates

```sh
make check
```

Individual targets include `format-check`, `lint`, `typecheck`, `test`, `audit`,
`security`, `docs-check`, and `frontend-check`. Live-model calls are absent.

## Common failures

- **Wrong Node engine:** switch to Node 24 and rerun `npm ci`.
- **Compose unknown command:** install the Compose plugin and verify Docker's CLI
  plugin path.
- **Cannot connect to Docker:** start Docker Desktop or Colima; this differs from
  installing the Docker CLI.
- **Lockfile changed during setup:** stop and inspect manifest/lock drift; CI uses
  locked mode and should not resolve upgrades.
- **Semgrep MCP advisory:** the SAST group is isolated and never starts its MCP
  server; see the dependency policy for the temporary exception.
