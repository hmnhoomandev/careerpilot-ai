# Annotated source: Phase 17 deployment artifacts

- `docker/python-service.Dockerfile` installs the locked workspace in a builder and copies only the virtual environment into a numeric non-root runtime.
- `apps/web/Dockerfile` uses Next.js standalone output to avoid shipping development dependencies.
- `compose.yaml` applies read-only roots, dropped capabilities, loopback ports, an internal data network and fake specialist providers.
- `infrastructure/terraform/main.tf` encodes regional managed services, private database access, bounded identities, backup policy and digest-only Cloud Run revisions.
- `scripts/generate_sbom.py` normalizes both lock ecosystems into deterministic CycloneDX 1.6 JSON.
- `scripts/generate_provenance.py` emits a SLSA v1 in-toto statement without secrets or environment data.
- `tests/architecture/test_deployment_artifacts.py` makes residency, least privilege, hardening, fake defaults and SBOM coverage executable policy.
