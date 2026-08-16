# Capacity, resilience, and disaster recovery

## Local evidence

The Phase 20 harness warms the in-process FastAPI application, sends 400 liveness
requests with concurrency 16, sends 1,000 sequential readiness requests as a bounded
soak, verifies tombstone-aware isolated restore, and proves provider outage is visible
with no fallback. This detects gross regressions; it does not simulate Cloud Run,
Cloud SQL, TLS, network latency, cold starts, multi-instance contention or real models.

## Initial capacity assumptions

- Stateless API/web/specialist instances scale horizontally; PostgreSQL and Temporal
  remain authoritative state boundaries.
- Cloud Run min instances default to zero outside an approved availability decision.
- Per-instance concurrency, CPU, memory, connection pool and maximum instances remain
  measured staging inputs, not fixed production promises.
- Load profiles must cover profile/document CRUD, retrieval, analysis, approval waits,
  notifications and workflow queries—not health endpoints alone.
- Data shape includes document count/size, chunk count, vector index size, workflow
  history length and tenant skew using synthetic or consented minimized fixtures.

## Approved staging test design

Before go-live, run at expected, 2× expected and bounded saturation traffic for at
least one hour; a 24-hour soak; concurrent tenant isolation; cold-start and autoscaling;
Cloud SQL pool exhaustion; Temporal worker loss; Pub/Sub duplicate/reorder; provider
timeout/quota/malformed output; and dependency/network denial. Stop on security,
integrity, budget or error-budget breach.

## Recovery objectives requiring approval

Proposed starting objectives are RPO ≤ 24 hours and RTO ≤ 8 hours for account/profile/
evidence business data, with stricter workflow/approval requirements determined after
business-impact and legal review. They are proposals, not measured commitments.

Quarterly drills must restore a managed backup/PITR point into an isolated project,
verify checksums/schema/tenant scope, apply deletion tombstones, run synthetic smoke and
authorization tests, record actual RPO/RTO, and destroy the isolated target under an
approved change. Multi-region recovery is not designed or claimed.
