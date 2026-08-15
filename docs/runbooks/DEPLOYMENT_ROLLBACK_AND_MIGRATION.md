# Deployment, rollback, and migration runbook

## Preconditions

- Obtain explicit owner approval for cost and mutation; a reviewed plan alone is not approval.
- Confirm the protected environment, Zurich region, budget alerts, WIF identity and no service-account key.
- Verify image digest, vulnerability policy, SBOM, provenance and signature.
- Back up Cloud SQL and test restore evidence before a destructive migration.

## Release

1. Apply reviewed infrastructure separately from application rollout.
2. Run the migration job with an immutable image digest and record its execution ID.
3. Deploy a no-traffic Cloud Run revision, run health and synthetic tenant-isolation smoke tests.
4. Move traffic gradually while observing latency, errors, workflow completion and cost.
5. Record approver, plan hash, image digest, migration revision and release outcome.

## Rollback

Stop traffic movement on an SLO or security breach. Route traffic to the last
known-good digest-pinned revision. Do not silently change model providers. If the
schema is backward compatible, leave it forward-migrated. Otherwise stop writes,
execute the tested Alembic downgrade only with approval, or restore to a new Cloud
SQL instance and reconcile the bounded write gap. Never overwrite the damaged
instance before restore verification.

## Recovery verification

Check `/health/live` and `/health/ready`, cross-tenant denial, one synthetic journey,
outbox backlog, Temporal task queue, data counts/checksums and audit continuity.
Document RTO/RPO achieved, missing writes, affected tenants and follow-up actions.
