# CareerPilot AI

CareerPilot AI is an evidence-grounded, human-controlled career intelligence and
job-application platform. The repository is currently in Phase 4: a PostgreSQL
profile and quarantined evidence-metadata foundation around the authenticated
deterministic journey. It uses only synthetic identities and makes no model or
external-provider calls.

Start with:

- [Product vision](docs/product/PRODUCT_VISION.md)
- [Requirements](docs/product/REQUIREMENTS.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Project state](docs/project/PROJECT_STATE.md)
- [Roadmap](docs/project/ROADMAP.md)
- [Phase 1 review](docs/reviews/phase-01-review.md)
- [Phase 2 tutorial](docs/tutorials/phase-02-deterministic-walking-skeleton.md)
- [Phase 3 tutorial](docs/tutorials/phase-03-local-identity-and-authorization.md)
- [Phase 4 tutorial](docs/tutorials/phase-04-postgresql-profile-evidence.md)

## Development quick start

Use Python 3.13 and Node.js 24 LTS, then run:

```sh
make setup
make check
```

Start the local API and web application together with:

```sh
make dev
```

Open `http://127.0.0.1:3000`. Choose Ada, Grace, or Sam as a synthetic local user.
Sessions, memberships, and audit events remain process-local. Profiles and evidence
metadata are durable only when `CAREERPILOT_DATABASE_URL` is set and the Phase 4
migration has run; otherwise the explicit in-memory local adapter is used. This is
not a production login.

For local PostgreSQL, copy `.env.example` to ignored `.env`, choose a local-only
password, start `make db-up`, export the values into the shell, and run
`make db-migrate`. Evidence registration sends metadata only in Phase 4: selected
file bytes never leave the browser and records remain quarantined.

The complete macOS and VS Code guide is in
[`docs/tutorials/phase-01-developer-setup.md`](docs/tutorials/phase-01-developer-setup.md).

All development uses synthetic data and CHF 0 local/fake infrastructure unless
the owner explicitly approves a cost.
