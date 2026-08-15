# Phase 17 tutorial: from source to a reviewable deployment

The central idea is that a deployable artifact is more than an image. CareerPilot
binds source, locked dependencies, a non-root container, an SBOM, provenance, an
immutable digest and a reviewed infrastructure plan into one release candidate.

For local use, copy `.env.example` to `.env`, keep its values synthetic, and run
`docker compose up --build`. The default profile starts PostgreSQL, API and web;
`--profile specialists` adds fake model services and `--profile durable` adds
Temporal. Ports bind to loopback and the database network is internal.

`scripts/generate_sbom.py` inventories locked Python and production npm packages.
`scripts/generate_provenance.py` records the source revision and lock digests.
These local artifacts teach and test the contract; a release pipeline must also
attach BuildKit/Cloud Build attestations and a signature to each registry digest.

Terraform fixes residency to Zurich and separates environment projects. Run only
format, validate and plan until an owner explicitly approves cost and mutation.
ADC is for human planning; WIF is for CI. Long-lived JSON keys are prohibited.

The safe rollout order is infrastructure, backup evidence, migration job,
no-traffic revision, synthetic smoke test, gradual traffic, and observation.
Rollback normally moves traffic to the previous revision; database recovery is a
separate and deliberately slower decision because data rollback can lose writes.
