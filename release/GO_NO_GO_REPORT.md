# Go/no-go report: 0.20.0-rc.1

## Decision

**GO for continued local evaluation and an explicitly approved staging-validation
project. NO-GO for production deployment or customer data.**

## Evidence supporting the candidate

- The complete default backend/frontend product and policy suites run locally with
  synthetic data and fake providers.
- A bounded readiness profile measures concurrency, load, soak, restore isolation,
  visible provider outage and CHF 0 default behavior.
- Temporal recovery, PostgreSQL migrations/integration, security adversarial checks,
  accessibility, containers, supply chain and IaC have dedicated local evidence.
- Release, architecture, operations, user/developer/API guides and curriculum are
  versioned with the candidate.

Exact final command results belong in `docs/reviews/phase-20-review.md` after verification.

## Production blockers

1. No approved Zurich staging/production resources or representative traffic evidence.
2. Production identity, workload authorization, secrets, encryption and edge controls are unverified.
3. Managed Cloud SQL backup/PITR restore and Temporal production recovery are unexercised.
4. Immutable registry images are not built, published, attested or signed in trusted CI.
5. Production SLIs, alerts, error-budget burn and on-call routes are not operating.
6. Provider quality, privacy terms, region, quota, outage and reconciled cost are unverified.
7. Final retention/lawful-basis/data-processing and incident duties require professional legal review.
8. Browser/device/screen-reader and representative capacity/security testing needs approved staging.

The owner must explicitly authorize costs and mutation before closing any cloud blocker.
Closing local tests alone cannot change this decision.
