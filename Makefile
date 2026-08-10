.PHONY: setup format format-check lint typecheck test audit security docs-check frontend-check check

setup:
	uv sync --all-packages --locked
	cd apps/web && npm ci
	cd tools/documentation && PUPPETEER_SKIP_DOWNLOAD=true npm ci

format:
	uv run ruff check --fix .
	uv run ruff format .
	cd apps/web && npm run format

format-check:
	uv run ruff format --check .
	cd apps/web && npm run format:check

lint:
	uv run ruff check .
	cd apps/web && npm run lint

typecheck:
	uv run mypy apps/api/src packages/core/src tests scripts
	cd apps/web && npm run typecheck

test:
	uv run pytest
	cd apps/web && npm test

audit:
	uv run pip-audit

security:
	uv run --isolated --only-group sast semgrep scan --no-git-ignore --config security/semgrep.yml --error --metrics off .
	uv run detect-secrets-hook --baseline .secrets.baseline $$(git ls-files -co --exclude-standard)

docs-check:
	cd tools/documentation && npm run lint
	cd tools/documentation && npm run links
	uv run python scripts/validate_mermaid.py

frontend-check:
	cd apps/web && npm run format:check
	cd apps/web && npm run lint
	cd apps/web && npm run typecheck
	cd apps/web && npm test
	cd apps/web && npm run build

check: format-check lint typecheck test audit security docs-check frontend-check
	uv run pre-commit run --all-files
	uv run python scripts/validate_phase0.py
