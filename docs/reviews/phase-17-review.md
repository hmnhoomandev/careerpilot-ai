# Phase 17 review — in progress

## 1. Phase objective

Produce hardened local containers, supply-chain evidence and Zurich-first Cloud
Run infrastructure-as-code without cloud mutation or cost. Implementation is
substantially present, but the phase is not complete until the blocked native
container and Terraform checks run successfully.

## 2. Delivered features

Multi-stage numeric non-root API/web images; hardened Compose profiles for the
application, fake specialists and Temporal; a runnable synthetic worker;
CycloneDX SBOM and SLSA provenance generators; plan-only Cloud Build/GitHub
workflows; Zurich-only Terraform for networking, Artifact Registry, regional
secrets/KMS/Pub/Sub, private Cloud SQL, Cloud Run and migration job.

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

No application schema changed and no migration ran. Terraform defines a one-shot
Alembic migration job and protected Cloud SQL backup/PITR architecture.

## 8. Automated commands and exact results

- Ruff format/lint passed; strict MyPy passed 142 source files.
- Non-Temporal Pytest passed 225, with six expected skips and four existing ADK warnings.
- Five deployment/config tests passed; Compose all-profile config passed.
- Frontend format/lint/typecheck/build and ten Vitest tests passed.
- SBOM and provenance generation passed; license policy scanned 148 distributions.
- Markdown lint passed 165 files; governance passed 174 Markdown files/74 IDs.
- Full Pytest was not green: five Temporal tests could not spawn the local binary under sandbox; the remaining prior config assertion was updated and passed.
- Docker build was attempted twice but the daemon escalation reviewer timed out before execution.
- Terraform/OpenTofu is absent, so native fmt/validate/plan has not run.
- Mermaid Chromium launch and link checks were blocked by the restricted environment/network.
- Semgrep was blocked by the sandboxed tool trust-store initialization.

## 9. Manual test checklist

- [ ] Build API/web images and inspect numeric runtime users.
- [ ] Start default, specialist and durable profiles; verify health and one synthetic journey.
- [x] Inspect generated CycloneDX and SLSA JSON locally.
- [ ] Run Terraform format, validate, security scan and three environment plans.
- [ ] Review every plan for secrets, public database, broad IAM and residency drift.

## 10. Requirements traceability

NFR-003/015/019 and SEC-006/012 are mapped in requirements traceability. Status
is static verification only until native artifact/IaC checks complete.

## 11. Example requests/responses

`CAREERPILOT_POSTGRES_PASSWORD=synthetic docker compose --profile specialists
--profile durable config --quiet` exits zero without starting a service.

## 12. Known limitations, debt, and risks

Native image correctness, vulnerability findings, Terraform provider-schema
correctness and plan contents remain unproven. Cloud cost, state backend, WIF,
edge/TLS, alert destinations and signing setup must be approved before deployment.

## 13. Rollback/recovery instructions

Use `docs/runbooks/DEPLOYMENT_ROLLBACK_AND_MIGRATION.md`. Local changes are
uncommitted and can be reviewed selectively; no external state exists to undo.

## 14. Learning summary

Phase 17 demonstrates that reproducibility spans source locks, runtime hardening,
SBOM/provenance/digest identity, infrastructure plan and controlled promotion.

## 15. Owner acceptance checklist

- [ ] All native container/IaC gates are green.
- [ ] Limitations and future paid cost are understood.
- [ ] No cloud mutation or cost occurred.
- [ ] Complete diff is accepted.

## 16. Proposed next phase

Phase 18 is an optional GKE reference architecture only after Phase 17 completes
and receives the exact gate. It has not started.

## 17. Exact approval command

Not yet actionable. After Phase 17 completes, the gate will be:

`APPROVE PHASE 17 AND START PHASE 18`
