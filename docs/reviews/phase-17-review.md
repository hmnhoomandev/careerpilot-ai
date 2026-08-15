# Phase 17 review — complete

## 1. Phase objective

Produce hardened local containers, supply-chain evidence and Zurich-first Cloud
Run infrastructure-as-code without cloud mutation or cost. All Phase 17 local
native gates have run successfully.

## 2. Delivered features

Multi-stage numeric non-root API/web images; hardened Compose profiles for the
application, one-shot Alembic migration, fake specialists and Temporal; a
runnable synthetic worker; CycloneDX SBOM and SLSA provenance generators;
plan-only Cloud Build/GitHub workflows; Zurich-only Terraform for networking,
Artifact Registry, regional secrets/KMS/Pub/Sub, private Cloud SQL, Cloud Run
and a migration job.

## 3. Explicitly not delivered

No cloud project, API, registry, WIF pool, key, secret, database, workload,
deployment, DNS, paid service, live model call, signature or customer-data
transfer was created. GKE and later comparison phases were not started.

## 4. Files created/changed

See the Phase 17 diff. Principal paths are `docker/`, `apps/web/Dockerfile`,
`compose.yaml`, `infrastructure/terraform/`, supply-chain scripts/workflow,
ADR-0029, deployment runbook, tutorial, exercises and policy tests.

## 5. Architecture decisions

ADR-0029 fixes Zurich, digest-only releases, separate runtime/migration identity,
ADC/WIF without keys, protected approval, and CI that cannot apply production.

## 6. Security/privacy review

Containers drop capabilities, forbid privilege escalation and use read-only
roots. The database has no public address; the internal API uses restricted
ingress; Pub/Sub persistence and managed secret/key locations are Zurich-only.
Final legal, retention and support-access review remains professional work.

## 7. Data/schema/migration impact

No application schema changed. A fresh local PostgreSQL instance successfully
ran migrations 0001 through 0003 before API startup. Terraform defines the same
one-shot Alembic migration job and protected Cloud SQL backup/PITR architecture.

## 8. Automated commands and exact results

- Ruff format/lint passed; strict MyPy passed 114 source files.
- Full Pytest passed 230, with six expected skips and four existing ADK warnings.
- Five deployment/config tests passed; Compose all-profile config passed.
- Frontend format/lint/typecheck/build and ten Vitest tests passed.
- SBOM and provenance generation passed; license policy scanned 148 distributions.
- Markdown lint passed 166 files; governance passed 175 Markdown files/74 IDs;
  link checks and 13 Mermaid renders passed.
- Semgrep scanned 148 Python files with zero findings; the secrets gate passed.
- API and web images built, run as numeric user/group 10001, passed runtime import
  and health smoke checks, and had zero fixable High/Critical Trivy findings.
- Default Compose services, both fake specialists, Temporal server/UI and the
  synthetic worker started successfully; migration exited zero before API startup.
- OpenTofu 1.12.5 initialized signed Google providers, formatted and validated the
  module, and produced reviewed synthetic test/staging/production plans, each with
  19 add, 0 change and 0 destroy.
- Trivy found zero High/Critical Terraform misconfigurations.

## 9. Manual test checklist

- [x] Build API/web images and inspect numeric runtime users.
- [x] Start default, specialist and durable profiles; verify health and adapters.
- [x] Inspect generated CycloneDX and SLSA JSON locally.
- [x] Run Terraform format, validate, security scan and three environment plans.
- [x] Review every plan for secrets, public database, broad IAM and residency drift.

## 10. Requirements traceability

NFR-003/015/019 and SEC-006/012 are mapped in requirements traceability. Native
container, Compose, supply-chain and IaC evidence is complete.

## 11. Example requests/responses

`CAREERPILOT_POSTGRES_PASSWORD=synthetic docker compose --profile specialists
--profile durable config --quiet` exits zero without starting a service.

## 12. Known limitations, debt, and risks

Cloud cost, state backend, WIF, edge/TLS, alert destinations and signing setup
must be approved before deployment. The Node 24.10 build emits a dev-only jsdom
engine advisory for 24.15+, while the production Next.js build remains green.

## 13. Rollback/recovery instructions

Use `docs/runbooks/DEPLOYMENT_ROLLBACK_AND_MIGRATION.md`. Local Compose resources
can be removed with `docker compose down`; no external state exists to undo.

## 14. Learning summary

Phase 17 demonstrates that reproducibility spans source locks, runtime hardening,
SBOM/provenance/digest identity, infrastructure plan and controlled promotion.

## 15. Owner acceptance checklist

- [x] All native container/IaC gates are green.
- [x] Limitations and future paid cost are documented.
- [x] No cloud mutation or cost occurred.
- [ ] Complete diff is accepted by the owner.

## 16. Proposed next phase

Phase 18 is an optional GKE reference architecture only after Phase 17 receives
the exact gate. It has not started.

## 17. Exact approval command

Phase 17 is complete. The exact gate is:

`APPROVE PHASE 17 AND START PHASE 18`
