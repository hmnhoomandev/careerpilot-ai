# Optional GKE Reference Architecture

## Boundary

Cloud Run remains CareerPilot's production default. The files under
`infrastructure/kubernetes/base` are an educational deployment option and are
not imported by the application, Compose or Cloud Run Terraform.

## Runtime shape

The reference deploys API and web workloads behind namespace-local ClusterIP
services. No public Gateway or LoadBalancer is included. API and web use separate
Kubernetes and Google identities; migration uses a third identity and must finish
before a rollout. PostgreSQL remains managed Cloud SQL rather than an in-cluster
database.

## Trust boundaries

- Namespace Pod Security is `restricted`.
- All Pods and containers run non-root with runtime-default seccomp, read-only
  roots, no privilege escalation and no Linux capabilities.
- A default-deny NetworkPolicy is opened only for DNS, approved ingress,
  web-to-API, monitoring, and an explicit placeholder private service CIDR.
- Kubernetes service-account tokens are not mounted because these workloads use
  GKE Workload Identity, not the Kubernetes API.
- Database configuration references `database-connection`; no Secret object or
  value is committed. An approved deployment must create it through a managed
  secret integration and prevent plaintext from entering Terraform state or logs.

## Availability and scaling

Two initial replicas, topology spread, a PDB and zero-unavailable rolling updates
reduce common voluntary-disruption risks. HPA scales CPU-targeted replicas from
two to ten. These controls do not prove the 99.5% target: a live regional cluster,
load tests, failure injection, capacity analysis and dependency SLOs are still
required.

## Observability

Applications continue to emit the content-free OpenTelemetry and structured-log
contracts from Phase 15. A future cluster must deploy an approved collector and
managed logging/metrics path with redaction before export. No telemetry backend,
daemon set or customer-data logging is activated by this reference.

## Render-only verification

```bash
kubectl kustomize infrastructure/kubernetes/base
uv run pytest -q tests/architecture/test_gke_reference.py
trivy config --severity HIGH,CRITICAL --exit-code 1 infrastructure/kubernetes/base
```

Do not pipe the render to `kubectl apply`. The placeholder project, image digests,
secret, ingress namespace labels and private CIDR must be replaced and reviewed
before any separately approved staging deployment.
