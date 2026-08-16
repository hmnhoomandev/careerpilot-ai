# Release checklist for 0.20.0-rc.1

## Candidate integrity

- [x] Semantic candidate version and manifest exist.
- [x] Root and service locks are committed and reviewed.
- [x] Local readiness, quality, evaluation, security and documentation gates are defined.
- [ ] Source commit is recorded in the manifest after the release commit.
- [ ] Immutable container digests are built in trusted CI and attached to the manifest.
- [ ] SBOM/provenance attestations are verified against those exact digests.
- [ ] Artifacts are keylessly signed by approved workload identity in a protected environment.

## Environment and data

- [ ] Zurich staging project, network, identity, secrets, database, backups and monitoring are approved.
- [ ] Migrations and forward recovery pass against a disposable staging database.
- [ ] Representative synthetic/consented load, soak, chaos and recovery meet targets.
- [ ] Access, deletion, restore tombstones, tenant isolation and incident evidence pass.
- [ ] Current cost estimate, quotas, alerts and shutdown owner are approved.

## Product and operations

- [ ] Owner completes the full journey and accessibility/browser/device checks.
- [ ] Legal/privacy/security reviews close or formally accept every release blocker.
- [ ] On-call owners, alert routes, support hours and incident communication are active.
- [ ] Go/no-go meeting records evidence, risks, rollback owner and explicit approval.

Any unchecked required item blocks production. This checklist does not authorize apply,
publish, signing, customer traffic or spend.
