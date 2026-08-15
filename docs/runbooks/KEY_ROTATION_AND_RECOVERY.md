# Key Rotation and Recovery Runbook

1. Create a rotation ID and inventory the key version, encrypted data classes, region, workload
   identities and backups. Never export a master key.
2. Create/enable the new Zurich-region version only after cost/IAM/residency approval in Phase 17.
3. Switch new envelope encryption to the new version; keep the old version decrypt-only.
4. Rewrap data keys in bounded idempotent batches; record opaque progress and failures.
5. Verify decrypt/read, backup restore and rollback with synthetic/authorized data.
6. Disable the old version only after all stores/backups and recovery requirements are confirmed.
7. Destroying a key is irreversible and requires explicit human approval plus legal/retention review.

The Phase 16 `KeyManagementPort` and `KeyRotationPlan` validate the boundary only. No Google Cloud
KMS key, Secret Manager secret, billing or cryptographic production claim exists yet.
