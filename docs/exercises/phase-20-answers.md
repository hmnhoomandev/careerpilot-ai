# Phase 20 exercise answers

1. It lacks representative production environment, workload, duration, dependencies and operational observation; scope is insufficient.
2. `30 × 24 × 60 × 0.005 = 216` minutes. Request volume is uneven, so request-ratio burn and time approximation are not identical.
3. Exact immutable digest, trusted CI/workload identity, protected approval, verified provenance/SBOM, registry publication and signature/attestation verification.
4. Exit zero means the requested local regression gates passed; promotion separately requires all production-scoped gates.
5. Local: injected unavailable fake provider must fail visibly without fallback. Staging: terminate a worker or deny a managed dependency during representative traffic and prove recovery/SLO impact.
