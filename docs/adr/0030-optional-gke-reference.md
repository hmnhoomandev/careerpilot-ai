# ADR-0030: Keep GKE as an optional reference deployment

- **Status:** Accepted for Phase 18 reference scope
- **Date:** 2026-08-15

## Context

CareerPilot already has a Cloud Run production design. Kubernetes can provide
Pod-level scheduling, sidecars, granular network policy and richer rollout
control, but also introduces cluster lifecycle, capacity, policy, upgrade,
security and support responsibilities. The current CHF 0 development budget does
not authorize a cluster.

## Decision

Keep Cloud Run as the default production target. Maintain an environment-neutral
Kustomize reference for GKE only. Consider adopting GKE after measured evidence
shows that at least one Kubernetes-native requirement cannot be met adequately
on Cloud Run and that the organization can own the operational burden.

The reference uses digest-pinned images, restricted Pod security, requests and
limits, three probes, HPA, PDB, topology spreading, default-deny NetworkPolicy,
separate workload identities and a one-shot migration Job. Secret values remain
outside Git. Google service-account keys and automatic migration init containers
are prohibited.

## Decision criteria

GKE may be preferable when CareerPilot needs several of these capabilities:

- Kubernetes-native sidecars or scheduling controls that are material to safety.
- Pod-to-Pod policy or internal multi-service traffic control beyond Cloud Run.
- Custom rollout, admission or platform-tenancy controls backed by an operations team.
- Sustained, measured workloads where cluster economics beat serverless economics.

Cloud Run remains preferable for scale-to-zero, lower operational load, simpler
patching, and the current early-stage traffic profile. Familiarity or curiosity
alone is not an adoption criterion.

## Consequences

The reference is renderable and testable without a cluster, but it is not a
deployment claim. A real adoption needs an approved cost estimate, private GKE
design, IP allocation, IAM bindings, Secret Manager CSI or equivalent integration,
Cloud SQL connectivity, ingress/TLS/WAF, admission policy, monitoring, backup,
upgrade and incident ownership, followed by staging evidence.

No legal certification or availability guarantee follows from these manifests.
