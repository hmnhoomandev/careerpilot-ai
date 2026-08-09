# ADR-0007: Zurich-First Cloud Run Deployment

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

Cloud Run is the initial production compute target and `europe-west6` Zurich is
preferred. Cloud SQL PostgreSQL and regional object storage are available there.
Pub/Sub requires explicit message-storage and endpoint policy. Any EU fallback
requires a new documented assessment of availability, residency, security,
privacy, latency, and cost before creation.

## Consequences

Zurich Cloud Run uses Tier 2 pricing. Service-by-service availability and pricing
must be rechecked before deployment. Phase 0 creates nothing; CHF 0 is the current
hard budget.

## Sources

- [Cloud Run locations](https://cloud.google.com/run/docs/locations)
- [Cloud SQL locations](https://cloud.google.com/sql/docs/postgres/region-availability-overview)
- [Cloud Storage locations](https://cloud.google.com/storage/docs/locations)
- [Pub/Sub message storage policies](https://cloud.google.com/pubsub/docs/resource-location-restriction)
