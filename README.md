# CareerPilot AI

CareerPilot AI is an evidence-grounded, human-controlled career intelligence and
job-application platform. The repository is currently in Phase 2: a deterministic
local walking skeleton. It contains one synthetic profile-to-job comparison path
and makes no model or external-provider calls.

Start with:

- [Product vision](docs/product/PRODUCT_VISION.md)
- [Requirements](docs/product/REQUIREMENTS.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Project state](docs/project/PROJECT_STATE.md)
- [Roadmap](docs/project/ROADMAP.md)
- [Phase 1 review](docs/reviews/phase-01-review.md)
- [Phase 2 tutorial](docs/tutorials/phase-02-deterministic-walking-skeleton.md)

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

Open `http://127.0.0.1:3000`. The profile repository is process-local: restarting
the API deletes the temporary profiles created during this phase.

The complete macOS and VS Code guide is in
[`docs/tutorials/phase-01-developer-setup.md`](docs/tutorials/phase-01-developer-setup.md).

All development uses synthetic data and CHF 0 local/fake infrastructure unless
the owner explicitly approves a cost.
