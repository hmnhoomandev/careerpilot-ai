# Infrastructure

Infrastructure is split by deployment boundary:

- `terraform/` models the Zurich-first Cloud Run production default.
- `kubernetes/base/` is the optional render-only GKE reference from Phase 18.

Neither directory authorizes an apply. No cloud or Kubernetes resource exists
because of these files; cost and mutation require separate explicit approval.
