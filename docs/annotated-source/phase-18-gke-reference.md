# Annotated source: Phase 18 GKE reference

## Kustomization and namespace

`infrastructure/kubernetes/base/kustomization.yaml` is the single render entry.
It composes resources and adds stable ownership labels; it performs no network or
cluster operation. `namespace.yaml` requests Kubernetes' restricted Pod Security
profile so a compatible admission controller rejects weaker Pods.

## Identities and configuration

`service-accounts.yaml` separates API, web and migration identities. The
`iam.gke.io/gcp-service-account` values are visible placeholders for Workload
Identity bindings, not credentials. Token automount is disabled because the
workloads do not call the Kubernetes API. `configmap.yaml` contains only
non-secret settings; database configuration is an unresolved Secret reference.

## Workloads and services

`deployments.yaml` defines digest-only API/web Pods, non-root security, bounded
resources, startup/readiness/liveness probes, topology spread and conservative
rolling updates. EmptyDir volumes provide only the explicit writable paths needed
under a read-only root. They are ephemeral and must never be mistaken for durable
evidence storage. `services.yaml` exposes only namespace-local ClusterIP ports.

## Availability controls

`autoscaling.yaml` sets an intentionally bounded CPU HPA. Real values require
load evidence. `disruption-budgets.yaml` protects one replica during voluntary
disruption; it cannot protect against software faults, regional outages or
dependency failure.

## Network and migration controls

`network-policies.yaml` begins with deny-all and adds named paths for DNS,
approved ingress, web-to-API, monitoring and a placeholder private service CIDR.
The real CNI and CIDRs require staging proof. `migration-job.yaml` gives schema
change a separate identity and zero automatic retries, making human inspection
and forward recovery explicit before workload rollout.

## Executable policy

`tests/architecture/test_gke_reference.py` renders through local Kustomize twice,
parses every object, and rejects missing digests, security controls, resource
bounds, probes, identity isolation, network deny policy, HPA/PDB or migration
ordering. It also rejects committed Secret objects. Trivy supplies a complementary
Kubernetes misconfiguration rule set.
