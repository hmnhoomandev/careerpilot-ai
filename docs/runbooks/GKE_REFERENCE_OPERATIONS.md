# GKE Reference Operations

## Preconditions for any future deployment

Obtain explicit owner approval for cost and mutation. Then produce a reviewed
Terraform plan covering a private regional GKE cluster in `europe-west6`, VPC/IP
ranges, Workload Identity bindings, Artifact Registry, Cloud SQL connectivity,
managed secret integration, ingress/TLS/WAF, logging/metrics, budgets and alerts.
Professional legal review remains required for final retention and support-access
arrangements.

## Release sequence

1. Verify signed image digests, SBOM, provenance and vulnerability policy.
2. Render the exact environment overlay and pass schema, policy and diff review.
3. Create/update secret references through the approved manager; never command-line literals.
4. Run the migration Job with the migration identity and inspect its exit status.
5. Update Deployment image digests and wait for `rollout status` in staging.
6. Run authenticated health, authorization, tenant-isolation and synthetic journey checks.
7. Promote only with human approval and current rollback/database recovery evidence.

The reference repository intentionally supplies no apply script.

## Rollback

If a workload rollout fails, stop promotion and use deployment revision history to
return to the last verified digest. Do not reverse a database migration by rolling
back a Pod: follow the forward-recovery process in
`docs/runbooks/DEPLOYMENT_ROLLBACK_AND_MIGRATION.md`. A PDB does not protect against
bad releases, node exhaustion or dependency failure.

## Incident containment

Block ingress, preserve metadata-only evidence, revoke the affected Workload
Identity binding, rotate referenced secrets, and follow the incident/data-breach
runbook. Do not collect personal payloads for debugging. Re-enable traffic only
after authorization, tenant isolation and recovery checks pass.
