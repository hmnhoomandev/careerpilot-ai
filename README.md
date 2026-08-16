# CareerPilot AI

CareerPilot AI is an evidence-grounded, human-controlled career intelligence and
job-application platform. The repository contains local source release candidate
`0.20.0-rc.1`. It is suitable for synthetic local evaluation and is explicitly
`NO-GO` for production until the release blockers are closed.

Start with:

- [Product vision](docs/product/PRODUCT_VISION.md)
- [Requirements](docs/product/REQUIREMENTS.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Project state](docs/project/PROJECT_STATE.md)
- [Roadmap](docs/project/ROADMAP.md)
- [User guide](docs/guides/USER_GUIDE.md)
- [Developer guide](docs/guides/DEVELOPER_GUIDE.md)
- [Operator guide](docs/guides/OPERATOR_GUIDE.md)
- [Release decision](release/GO_NO_GO_REPORT.md)
- [Curriculum](docs/curriculum/INDEX.md)

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
Sessions and several local adapters remain process-local. Profiles, evidence, documents,
drafts and approvals use PostgreSQL only when `CAREERPILOT_DATABASE_URL` is configured
and migrations have run. This is not a production login.

For local PostgreSQL, copy `.env.example` to ignored `.env`, choose a local-only
password, start `make db-up`, export the values into the shell, and run
`make db-migrate`. Use only synthetic evidence. The local document path accepts bounded UTF-8 text and
text-based PDF content, scans/parses/indexes locally and treats retrieved text as untrusted.

The complete macOS and VS Code guide is in
[`docs/tutorials/phase-01-developer-setup.md`](docs/tutorials/phase-01-developer-setup.md).

All development uses synthetic data and CHF 0 local/fake infrastructure unless
the owner explicitly approves a cost.

Run `make release-readiness` for bounded local load/recovery evidence. A passing
command does not change the production `NO-GO` decision.
