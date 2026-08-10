# Tutorial: Run the Deterministic Walking Skeleton

## What this teaches

This tutorial follows one request across browser, API contract, application
service, and temporary repository. Use synthetic data only. No model, agent,
cloud resource, or paid service participates.

## Prerequisites

Complete the Phase 1 setup and select Python 3.13 and Node.js 24. Confirm locked
dependencies with `make setup`.

## Start the system

From the repository root:

```sh
make dev
```

This starts FastAPI on `http://127.0.0.1:8000` and Next.js on
`http://127.0.0.1:3000`. Both bind locally. Press Control-C once to stop both.

## Complete the journey

1. Open `http://127.0.0.1:3000`.
2. Keep or replace the synthetic display name and summary.
3. Enter a synthetic job description of at least 50 characters.
4. Select **Run deterministic comparison**.
5. Read the exact shared terms, disclaimer, and correlation ID.

The output is a lexical intersection. It does not prove a skill, score fit, infer
experience, or predict a hiring outcome.

## Observe a safe failure

Temporarily shorten the display name to one character or the summary below 20
characters. Browser validation prevents submission. API behavior is independently
tested with the same bounds and returns a structured `invalid_request` response
without a stack trace or submitted content.

## Understand restart behavior

The UI creates a new profile immediately before each analysis. The API stores it
in a process-local dictionary. After Control-C and a restart, old profile IDs no
longer exist; the API returns `profile_not_found`. This limitation is intentional
until Phase 4 adds PostgreSQL schemas and migrations.

## Inspect the API

- OpenAPI UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Liveness: `http://127.0.0.1:8000/health/live`
- Readiness: `http://127.0.0.1:8000/health/ready`

## Run relevant tests

```sh
uv run pytest
npm --prefix apps/web test
make check
```

The automated suite includes unit, HTTP, OpenAPI contract, UI/client,
accessibility-smoke, end-to-end, and restart tests.
