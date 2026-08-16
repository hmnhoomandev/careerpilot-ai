# Phase 18 tutorial: deciding on and validating GKE

## What this phase teaches

Cloud Run and GKE can run the same container, but they assign different work to
the product team. Cloud Run owns most host, scheduler and revision operations.
GKE exposes Kubernetes primitives and therefore makes the team responsible for
more configuration, upgrades, policies, capacity and incident diagnosis.

## Read the reference safely

Render locally:

```bash
kubectl kustomize infrastructure/kubernetes/base > /tmp/careerpilot-gke.yaml
```

This command does not contact a cluster. Inspect the result for 21 resources and
placeholder values. Do not apply it: a render proves composition, not cloud IAM,
network enforcement, admission behavior or runtime health.

## Follow one API Pod

The Deployment selects the API's dedicated Kubernetes service account. GKE
Workload Identity would map it to a Google service account without a stored key.
The Pod runs as UID/GID 10001 with seccomp, no capabilities and a read-only root.
Requests/limits give the scheduler and runtime explicit bounds. Three probes
distinguish slow startup, temporary unready state and a dead process.

The default-deny policy blocks traffic until a narrow rule allows it. The database
URL comes from a named secret boundary and not source. The reference does not
create that Secret because its safe source and synchronization are deployment
decisions.

## Understand availability mechanisms

Replicas, topology spread, rolling-update bounds, HPA and PDB address different
failure modes. None guarantees availability. HPA needs useful metrics and spare
capacity; PDB applies only to voluntary disruption; topology labels need a real
regional cluster; readiness depends on meaningful dependency checks.

## Release and recover

Run schema migration as a separate Job before changing workload image digests.
If the workload fails, return to the last verified digest. If the schema is no
longer compatible, use forward recovery rather than assuming Pod rollback can
undo database state.

## Decide instead of defaulting

Choose GKE only after a measured need for Kubernetes-native networking,
scheduling, sidecars, admission or platform tenancy, together with staffing and
cost approval. For CareerPilot's current scale-to-zero and CHF 0 constraints,
Cloud Run remains the recorded production default.
