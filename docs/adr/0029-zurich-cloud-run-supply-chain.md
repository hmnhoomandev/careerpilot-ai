# ADR-0029: Zurich Cloud Run and verifiable supply chain

- **Status:** Accepted for Phase 17
- **Date:** 2026-08-15

## Context

CareerPilot needs repeatable local containers and production-shaped Google Cloud
infrastructure without spending the current CHF 0 budget or weakening residency,
identity, or human-approval controls.

## Decision

Use hardened multi-stage containers with numeric non-root users. Use separate
Terraform stacks/projects for test, staging, and production, with `europe-west6`
Zurich fixed by validation. Cloud Run v2 runs the web and internal API; Cloud SQL
PostgreSQL uses private IP and backups; Pub/Sub persistence is restricted to
Zurich; Secret Manager and KMS are regional. Runtime and migration service
accounts are distinct and narrowly authorized.

CI builds and scans but never applies infrastructure. Future Google Cloud CI
authentication must use Workload Identity Federation. Images must be referenced
by digest, accompanied by CycloneDX SBOM and SLSA provenance, and signed before a
production release. Protected-environment approval must precede deployment.

## Consequences

Cloud Run is the production default and GKE remains a Phase 18 comparison only.
Zurich Tier 2 pricing and Cloud SQL dominate likely baseline cost; exact estimates
must be reviewed before any staging/production creation. Terraform state backend,
real project IDs, WIF pool, domain/TLS edge, alert destinations, signing keys and
secret versions remain deployment prerequisites, not Phase 17-created resources.

## Availability and legal review

Official availability was rechecked on 2026-08-15 for Cloud Run, Cloud SQL,
Artifact Registry, Cloud Build, Secret Manager, KMS and Pub/Sub. No core service
needs an EU fallback. Data-processing terms, final retention, cross-border support
access and incident duties require professional legal review; this ADR makes no
claim of certified or guaranteed compliance.
