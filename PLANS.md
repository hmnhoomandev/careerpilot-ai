# CareerPilot AI Execution Plans

## Plan format

Every phase plan must state:

1. Objective and approved phase.
2. In-scope requirements and acceptance criteria.
3. Deliverables and expected files.
4. Architecture and security decisions.
5. Privacy, migration, deployment, and cost impact.
6. Risks and mitigations.
7. Automated verification commands.
8. Manual verification steps and expected results.
9. Explicit exclusions.
10. Stop condition and exact next approval command.

Plans are living documents. Update status without erasing decisions or evidence.

## Completed implementation plan: Phase 19

**Objective:** compare DBOS and Restate with CareerPilot's existing Temporal durable-workflow
scenario in small, executable, isolated labs without changing production routing or dependencies.

**Status:** Complete on 2026-08-16. The repository is stopped at the Phase 19 gate; Phase 20 has not
started.

### Scope and acceptance mapping

- Implement one bounded, metadata-only application-preparation effect in DBOS and Restate using the
  same idempotent happy-path and failure-after-commit recovery semantics already tested in Temporal.
- Prove each lab completes the happy path once and recovers a synthetic post-commit failure without
  duplicating its durable effect.
- Compare programming model, durable state, retry/recovery, observability, deployment, testing,
  lock-in, maturity, licensing and operational cost using executable evidence and primary sources.
- Prove DBOS, Restate and their test harnesses remain absent from production dependency graphs and
  runtime routing. Temporal remains the production durable-workflow owner.

### Deliverables and expected files

- Independent `labs/dbos/` and `labs/restate/` Python projects, each with its own manifest, lock,
  source, tests and usage notes; neither becomes a root uv workspace member.
- A shared synthetic scenario contract plus architecture tests that enforce lab isolation.
- ADR-0031, durable-execution comparison, annotated source, tutorial, exercises/answers, dependency
  assessment, traceability, decision/learning/state/roadmap updates and Phase 19 review.

### Architecture, security, privacy, migration, deployment, and cost

- Labs accept opaque tenant/application identifiers only; they contain no document text, secrets,
  customer data, external model calls or network integration.
- Idempotency is explicit at the effect boundary. A retry after a simulated failure that occurs
  after commit must return the prior result and must not duplicate the effect.
- DBOS may use an isolated local SQLite system database for tests. Restate may use its local test
  harness/container. Neither database, service or SDK is a production dependency or migration.
- All work is local and CHF 0. No cloud resource, paid API, deployment or production route is
  authorized. Adoption of either comparison technology requires a new ADR, license/security review,
  operational estimate and explicit phase approval.

### Risks and mitigations

- Misleading equivalence: use one versioned scenario and identical observable assertions while
  documenting semantic differences instead of claiming framework interchangeability.
- Duplicate side effects: require a stable idempotency key and test failure after the first commit.
- Dependency contamination: use separate lockfiles and an architecture test over root manifests and
  production source imports.
- License or maturity surprise: inventory direct/transitive packages and explicitly record the
  Restate server license boundary before any future adoption.
- Container/tool availability: keep harness prerequisites explicit and report skips or limitations;
  do not substitute simulated framework behavior while claiming integration evidence.

### Automated verification

- Run each lab's Ruff, MyPy and Pytest commands inside its independent uv project.
- Run the equivalent targeted Temporal recovery test and root architecture isolation tests.
- Run existing backend/frontend, security, supply-chain, documentation, Mermaid, pre-commit and
  governance regression checks relevant to the complete diff.

### Manual verification

- Inspect each lab's successful response, attempt count and unique-effect count for happy/recovery
  cases, then compare them with the Temporal test evidence.
- Inspect root and production dependency graphs/imports and confirm no DBOS/Restate/runtime route.
- Trace comparison claims to executable tests and primary documentation; confirm no production or
  cloud process was started.

### Explicit exclusions

- Production adoption, routing, migration, deployment, benchmarking, cloud resources, paid calls,
  real personal data, external models, customer traffic and claims of legal/compliance approval.
- Replacing Temporal, combining multiple durable engines in one business workflow, exposing a new
  public API, or beginning Phase 20 production-readiness work.

### Stop condition

Complete `docs/reviews/phase-19-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 19 AND START PHASE 20`

## Completed implementation plan: Phase 18

**Objective:** provide a validated, educational GKE reference deployment for CareerPilot while
keeping Cloud Run as the production default, preserving CHF 0 local development, and creating no
cloud or Kubernetes resources.

**Status:** Complete on 2026-08-16. The repository is stopped at the Phase 18 gate; Phase 19 has not
started.

### Scope and acceptance mapping

- Record the measurable decision criteria that could justify GKE over Cloud Run; GKE remains an
  optional reference and may not become a production dependency implicitly.
- Add Kustomize-renderable Kubernetes resources for namespace, workload identities, API/web
  deployments and services, one-shot migration, configuration, probes, resource bounds,
  autoscaling, disruption budgets and default-deny network policies.
- Reference external secret material without committing values; use GKE Workload Identity rather
  than service-account keys and document Secret Manager/Cloud SQL integration prerequisites.
- Document Zurich regionality, private-cluster/network assumptions, observability, rollout,
  rollback, migration ordering, Pod Security, image provenance and operational ownership.
- Compare Cloud Run and GKE cost/complexity honestly and identify the paid baseline that would
  require a fresh estimate and explicit approval before any deployment.

### Deliverables and expected files

- `infrastructure/kubernetes/base/` and environment-neutral reference manifests rendered by the
  kubectl-integrated Kustomize version; no new runtime dependency or cluster is required.
- Policy/schema tests under `tests/architecture/` covering digest-only images, non-root security,
  resource requests/limits, probes, identity, autoscaling, disruption and network isolation.
- ADR-0030, GKE operations/decision documentation, annotated source, tutorial, exercises/answers,
  cost/security records, traceability, roadmap/state/learning/decision updates and Phase 18 review.

### Architecture, security, privacy, migration, deployment, and cost

- Cloud Run remains the production default. GKE becomes preferable only for demonstrated needs
  such as Kubernetes-native scheduling, sidecars, fine-grained Pod networking or platform tenancy.
- Reference workloads use digest-only images, restricted security contexts, read-only roots,
  dropped capabilities, bounded resources, probes and least-privilege Kubernetes service accounts.
- Workload Identity maps Kubernetes identities to separately managed Google service accounts;
  service-account keys and committed Kubernetes Secret values are prohibited.
- Default-deny ingress/egress is explicit. Real cluster, DNS, ingress, TLS, Cloud Armor, private
  control-plane access, authorized networks and exact Cloud SQL CIDRs remain pre-deployment work.
- The migration Job is a separately invoked release gate and never runs automatically from a Pod
  startup hook. It must complete before workload rollout and retains no schema secret in source.
- A GKE cluster, control plane, load balancer, nodes, NAT/egress, logging and support can incur
  recurring cost. No API enablement, cluster creation, image push, apply or paid call is authorized.

### Risks and mitigations

- Reference drift: render manifests in tests and enforce security/identity/image policies in code.
- False production confidence: label placeholders and prerequisites; a local render is not a live
  cluster, network, IAM, cost, performance, residency or availability proof.
- Secret leakage: reference secret names only, deny literal secret resources/data, scan repository.
- Lateral movement: namespace default-deny policies plus narrow web-to-API and monitoring ingress.
- Availability illusion: HPA/PDB/topology spread are documented mechanisms, not an SLO guarantee;
  live multi-zone disruption evidence remains a separately approved production-readiness task.
- Cost/operational burden: keep GKE out of local/Cloud Run dependencies and require decision and
  cost gates before adoption.

### Automated verification

- `kubectl kustomize` deterministic render and client-side structural checks without cluster access.
- Pytest manifest-policy tests for image digests, security contexts, resources, probes, network,
  identity, HPA, PDB, migration ordering and absence of secret values/cloud mutation commands.
- Trivy Kubernetes/IaC configuration scan with High/Critical release policy.
- Existing Ruff/MyPy/Pytest, frontend, supply-chain, documentation, Mermaid, secrets, Semgrep,
  pre-commit and governance regression checks as relevant to the diff.

### Manual verification

- Render the reference and inspect every resource without applying it.
- Compare GKE/Cloud Run criteria and confirm Cloud Run/local Compose behavior is unchanged.
- Trace identity, network, secret, migration, rollout and rollback paths in the documentation.

### Explicit exclusions

- `kubectl apply`, Terraform apply, cluster/project/API/IAM/network/resource creation, image push,
  live admission validation, GKE credential retrieval, billing/free-tier use or deployment.
- A public Ingress/Gateway, DNS, TLS certificate, Cloud Armor, production secret value, real project
  identity, customer data, model call, external communication, production SLO or compliance claim.
- DBOS/Restate comparison labs (Phase 19) and production-readiness/load/chaos work (Phase 20).

### Stop condition

Complete `docs/reviews/phase-18-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 18 AND START PHASE 19`

## Completed implementation plan: Phase 17

**Objective:** create a reproducible, hardened and supply-chain-aware Cloud Run release path with
local container/IaC evidence while preserving the CHF 0 budget and performing no cloud mutation.

**Status:** Complete on 2026-08-15. The repository is stopped at the Phase 17 gate; Phase 18 has not
started.

### Scope and acceptance mapping

- Build multi-stage non-root containers for the FastAPI API, Next.js web app and bounded specialist
  services; use read-only/runtime-minimized filesystems where practical and explicit health probes.
- Extend Compose into a complete local profile for PostgreSQL/pgvector, API, web, specialist
  services and Temporal development dependencies, with loopback exposure and health ordering.
- Generate CycloneDX/SPDX SBOMs, vulnerability/secret/license policy evidence, image metadata and
  unsigned local provenance; define keyless signing/attestation gates for authorized CI releases.
- Add Terraform for isolated test/staging/production inputs and Zurich-first Artifact Registry,
  Cloud Run services/jobs, Cloud SQL architecture, regional storage, Pub/Sub location policy,
  regional Secret Manager/KMS, observability, networking, IAM, backups and migration jobs.
- Use separate runtime and CI service accounts, least privilege and WIF/OIDC; never store a long-
  lived Google service-account key or provider credential.
- Add plan-only CI with format/validate/security/policy gates, immutable-image promotion and an
  explicit protected-environment approval before production. No workflow may auto-apply production.
- Add deployment, migration, rollback, restore and incident runbooks plus local smoke tests.

### Deliverables and expected files

- Root/service Dockerfiles, `.dockerignore`, health/entrypoint configuration, expanded `compose.yaml`
  and container contract/security tests.
- `infrastructure/terraform` root/module/environment variable files and policy tests; plan output
  stays ignored and contains no secrets. Provider/tool versions are pinned and documented.
- Supply-chain scripts/workflows for SBOM, provenance statement, container/IaC scanners and policy;
  generated verification artifacts go to an ignored local reports directory, not source control.
- ADR-0029, deployment/residency/cost architecture, annotated source, tutorial/exercises,
  runbooks, traceability/state/roadmap/security/privacy/learning and mandatory Phase 17 review.
- No production application dependency is planned. Free development tooling may be downloaded only
  from official sources with pinned versions/checksums and documented licenses/alternatives.

### Architecture, security, privacy, migration, deployment, and cost

- Cloud Run remains the production compute target; GKE remains Phase 18 reference-only. Services
  use one async process and scale horizontally; sizing is a tested input, not an asserted optimum.
- `europe-west6` is available for Cloud Run, Cloud SQL, Artifact Registry, Cloud Build, regional
  Secret Manager and Cloud KMS as of 2026-08-15. No core-service EU fallback is proposed.
- Pub/Sub topics explicitly allow only `europe-west6` and enforce in-transit location policy.
  Regional endpoints and organization policy remain production-administration decisions.
- Cloud SQL is private-IP architecture with deletion protection in production, PITR/backups,
  separate database/runtime identities and a migration job; no public database endpoint is planned.
- Web ingress may be public behind the approved identity/edge design; API/specialists are private
  and authenticated. Current local auth cannot be activated in production and startup must fail.
- Secrets use regional Secret Manager references; CMEK uses Zurich Cloud KMS. Terraform values and
  CI logs contain resource names only, never secret payloads or long-lived keys.
- Terraform plan is the review artifact. Apply/deploy/API enablement/project/IAM/resource mutation
  requires a new explicit owner approval and a current cost estimate; this phase authorizes none.
- Estimated paid staging/production shapes and shutdown controls are documented separately. Local
  builds, scans, emulators and plans must remain CHF 0.

### Risks and mitigations

- Supply-chain substitution: pinned base/tool/action versions, digest lock records, SBOM, SCA,
  provenance subject digests, protected promotion and keyless signing design.
- Root/escape/writable-container abuse: numeric non-root users, dropped capabilities, no-new-
  privileges, read-only roots, bounded tmpfs and container policy tests.
- Secret/image leakage: narrow build contexts, `.dockerignore`, BuildKit secret prohibition tests,
  secret scan, no credentials in layers/args/provenance and private Artifact Registry repositories.
- Terraform drift/destruction: remote versioned state design, locking, plan review, lifecycle guards,
  protected production environment and no apply in Phase 17.
- Cross-environment/tenant leakage: separate project IDs/service accounts/databases/secrets/state,
  explicit environment validation and deny-default IAM.
- Residency drift: fixed Zurich variables/policies, CI policy assertions and a documented exception
  workflow before any EU fallback.
- Cost surprise: min instances default zero for non-production plans, bounded max/concurrency,
  budgets/alerts architecture, no apply and explicit paid-deployment gate.
- Tool unavailable: use official pinned local binaries/images where authorized; record exact
  blocked build/plan/scan evidence rather than weakening policy or claiming success.

### Automated verification

- Docker/Compose syntax, multi-architecture build where locally possible, non-root/read-only/health
  smoke, container vulnerability/misconfiguration/secret scan and SBOM/provenance validation.
- Terraform/OpenTofu format, init-backend=false, validate and plan with synthetic project IDs;
  IaC security/policy tests for Zurich, IAM, ingress, secrets, encryption, backups and deletion guards.
- CI workflow/YAML and protected-promotion contract tests; no cloud credentials or apply command.
- Complete Ruff/MyPy/Pytest, frontend format/lint/type/test/build, SAST/SCA/secrets/licenses,
  docs/link/Mermaid/governance, pre-commit and complete diff review.
- Staging smoke is represented by a reusable script and contract tests only. It is not run against
  cloud because no staging resource/cost approval exists.

### Manual verification

- Build/start the full local Compose profile, inspect health and use the visible local product.
- Inspect every runtime user, Linux capabilities, writable mounts, exposed ports and image history.
- Generate and inspect SBOM/provenance subjects and run local container/IaC policies.
- Review test/staging/production Terraform plans and confirm the plan contains no secret values,
  public database, broad runtime role or non-Zurich data service.
- Verify staging/production workflows require WIF and production environment approval.
- Rehearse local migration, smoke, rollback and isolated restore procedures without cloud mutation.

### Explicit exclusions

- Terraform apply, `gcloud services enable`, project/resource/IAM creation, Artifact Registry push,
  Cloud Build execution, Cloud Run/SQL/Pub/Sub/KMS/Secret Manager creation or staging deployment.
- Billing enablement, paid/free-tier cloud consumption, live model/provider call, customer data,
  DNS/domain/certificate changes, email/submission or external communication.
- GKE/Kubernetes manifests or deployment (Phase 18), DBOS/Restate labs, production load/soak/chaos
  and final go-live decision (Phase 20).
- Claiming local SBOM/provenance is a signed release, claiming plan equals deployed security, or
  claiming legal compliance/data-residency certification.

### Stop condition

Complete `docs/reviews/phase-17-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 17 AND START PHASE 18`

## Completed implementation plan: Phase 16

**Objective:** harden CareerPilot's local/API security and privacy posture and prove the
controls with deterministic adversarial tests, without claiming legal compliance or creating
cloud, paid, production-network, or container/IaC resources owned by Phase 17.

### Scope and acceptance mapping

- Complete the STRIDE threat/control/residual-risk mapping for every activated trust boundary.
- Add tenant-safe data-subject access, correction-plan, portable export, recoverable deletion,
  consent withdrawal and retention-plan workflows with explicit step-up/approval boundaries.
- Define fail-closed secret-manager/KMS/envelope-encryption ports, key rotation/recovery runbook,
  and production configuration rules; local implementations use no real secrets or cloud KMS.
- Add API security headers/CSP, cache prevention, bounded request/rate controls, trusted-host and
  HTTPS-production policy, plus a DNS/IP/redirect-safe outbound URL policy with no network fetch.
- Strengthen upload/scanner boundary and test malicious signatures, polyglots, parser limits and
  path traversal. Preserve quarantine and fail-closed behavior.
- Add a versioned agent red-team corpus for direct/indirect injection, exfiltration, tool abuse,
  authorization bypass, malicious files and denial-of-wallet; gate deterministic protections.
- Add local DAST, backup/export/restore rehearsal and data-deletion propagation verification.
- Define severity/blocking policy and CI gates for SAST, SCA, DAST, secrets and licenses. Container,
  SBOM and IaC scans are configured/documented for Phase 17 artifacts but cannot claim a pass
  before those artifacts exist.

### Deliverables and expected files

- Core privacy lifecycle, consent, retention and security-policy types/services with API adapters
  and strict contracts; no provider SDK in the domain.
- Security middleware/policies, SSRF destination validator, hardened local upload scanner, local
  DAST and backup/restore verification scripts, synthetic adversarial fixtures and tests.
- CI/Makefile/security policy updates using already locked tools where possible; no production
  dependency is planned unless inspection proves it necessary and the dependency policy is updated.
- ADR-0028, complete threat/control matrix, privacy lifecycle and incident/key/backup runbooks,
  annotated source, tutorial, exercises/answers, traceability/governance and Phase 16 review.

### Architecture, security, privacy, migration, deployment, and cost

- Domain services express lifecycle decisions; FastAPI authenticates and reauthorizes every data-
  subject action. Export/deletion are consequential actions and require exact, auditable approval.
- Recoverable deletion defaults to 30 days and is a state transition, not immediate erasure. Legal
  holds, identity verification, exceptions and final schedules remain `LEGAL REVIEW`.
- Backup rehearsal uses encrypted-by-boundary synthetic local artifacts and an isolated restore
  target. It proves integrity/tenant scoping, not production durability or cloud recovery.
- SSRF policy resolves/validates all addresses, rejects private/reserved/link-local/metadata ranges,
  credentials, non-HTTPS schemes and redirects unless each destination is revalidated. Phase 16
  introduces no unrestricted fetch or scraping.
- Browser/API headers are local-safe and production-fail-closed. CSP permits the current local UI
  contract only; production TLS/WAF/CDN policy is documented for Phase 17 deployment decisions.
- No database migration is planned: lifecycle orchestration is a bounded local reference over the
  existing repositories. Production durable deletion/backup ledgers require later migration review.
- CHF cost remains zero: no model, cloud scanner, KMS, WAF, DAST SaaS, paid API or resource is used.

### Risks and mitigations

- False compliance claim: label engineering controls and every unresolved legal determination;
  keep LEG-001–008 explicit in the review and user-facing workflow documentation.
- Export leakage/IDOR: owner/subject binding, step-up evidence, exact approval, minimized manifest,
  deterministic archive shape, safe errors, tenant and hostile-ID tests.
- Deletion incompleteness: source-to-derivative inventory, explicit pending/recoverable/purge states,
  idempotency, deletion ledger, backup tombstone handling and failure-injection tests.
- SSRF/DNS rebinding: canonical URL parsing, address classification, bounded resolver interface,
  destination allowlist and redirect revalidation; no socket call in default tests.
- Header/rate-control regressions: route-aware deterministic middleware, proxy-trust assumptions,
  retry guidance and DAST assertions without using attacker-controlled high-cardinality keys.
- Red-team overfitting: versioned category-balanced corpus, expected policy outcomes and mutation/
  bypass variants; report deterministic detector limits and keep model-based red teaming excluded.
- Scanner/tool supply-chain gaps: fail closed when scanner is unavailable, keep strict input limits,
  scan locks/licenses/advisories, and defer container/IaC evidence honestly to Phase 17.

### Automated verification

- Ruff format/lint, strict MyPy and complete Pytest, including data-subject, retention/deletion,
  consent, cross-tenant/privilege, headers/CSP/rate, SSRF, upload and adversarial-agent tests.
- OpenAPI/contract tests, local DAST baseline, isolated synthetic backup/restore/deletion rehearsal,
  architecture boundaries and deterministic red-team threshold gate.
- Frontend format/lint/type/test/build; Semgrep SAST, pip/npm SCA, secret and license policy checks;
  Markdown/link/Mermaid/governance, pre-commit and complete diff review.
- Record skipped PostgreSQL/live-model/network/container/IaC checks precisely; never substitute one
  class of security test for another or claim absent Phase 17 artifacts were scanned.

### Manual verification

- Sign in as a synthetic owner, inspect/access/export the account manifest, request correction,
  withdraw consent, request recoverable deletion, cancel within the window and inspect audit events.
- Attempt the same actions across tenants and as a non-owner; observe non-enumerating denial.
- Inspect response security headers/CSP/cache policy and exceed a local rate limit safely.
- Run SSRF and agent red-team fixtures and inspect categorized allow/block decisions.
- Create a synthetic local backup, restore into an isolated temporary store, apply deletion
  tombstones and verify deleted material is not reactivated.
- Review STRIDE residual risks, incident/key-rotation runbooks and all `LEGAL REVIEW` items.

### Explicit exclusions

- Legal certification, guaranteed GDPR/FADP compliance, final lawful bases/retention/notification
  timelines, production identity proofing, real customer data or legal-hold adjudication.
- Cloud KMS/Secret Manager, WAF/CDN, managed malware scanning, real outbound fetch, cloud backup,
  cloud deployment, paid DAST/red-team service, credentials, billing or any paid/live provider call.
- Container build/hardening, SBOM/signing/provenance and concrete IaC plans/scans, which belong to
  Phase 17; only their release-blocking policy and expected interfaces are prepared here.
- Immediate irreversible account purge, automatic external communication/submission, unrestricted
  scraping, organization/coach activation, Phase 17 implementation or later comparison labs.

### Stop condition

Complete `docs/reviews/phase-16-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 16 AND START PHASE 17`

## Completed implementation plan: Phase 15

**Objective:** make CareerPilot measurable and cost-controlled through privacy-safe local
telemetry, deterministic evaluation, explicit model/prompt registries and a fail-closed routing/
budget policy, while keeping all cloud/export/live-provider integrations disabled by default.

### Scope and acceptance mapping

- Define a versioned metadata-only telemetry event spanning HTTP, workflow, graph, agent, tool,
  approval, retrieval, prompt and model operations with correlation/run identifiers, duration,
  outcome, provider/model/prompt versions, tokens and estimated CHF cost where applicable.
- Add local metrics aggregation for latency percentiles, completion/error/provider failure,
  retrieval/grounding/tool/handoff/safety quality and cost per workflow; expose an authenticated,
  tenant-safe local dashboard contract.
- Define Cloud Logging/Trace, BigQuery Agent Analytics, LangSmith and OpenAI/ADK trace adapter
  boundaries. Export is opt-in and disabled; prompt/response content capture is `NO_CONTENT`.
- Implement versioned prompt/model registry entries and explicit routing by capability, privacy,
  quality, latency, cost, availability and approval. A route failure is visible; no provider/model
  fallback occurs implicitly.
- Implement per-tenant/workflow CHF budgets, quotas, deterministic estimates and cache policy.
  CHF 0 permits only zero-cost fake/local routes; any positive cost requires explicit approval.
- Build a versioned offline evaluation harness/dashboard for retrieval, routing, tools, handoffs,
  grounding, safety, latency and cost with threshold failures and machine-readable reports.

### Deliverables and expected files

- Framework-neutral telemetry, registry, routing, budget and evaluation values/services in core;
  local collector/export adapter/API composition in FastAPI; local dashboard presentation in web.
- BigQuery analytics schema and exporter/privacy configuration documentation; adapters perform no
  network calls or resource creation in Phase 15.
- Decision-table, budget/quota/cache/no-fallback, telemetry redaction/propagation, aggregation,
  adapter, API authorization and evaluation threshold tests using synthetic fixtures.
- ADR-0027, observability/evaluation architecture, annotated source, tutorial/exercises,
  security/privacy/cost/traceability/state/roadmap/learning and mandatory Phase 15 review.
- No new dependency is planned: existing OpenTelemetry API/SDK and transitive LangSmith types are
  sufficient; direct vendor SDK imports are avoided in the core.

### Architecture, security, privacy, migration, deployment, and cost

- Business services emit typed metadata to a port. Local memory is the default sink; exporters
  receive already-redacted events and never prompts, resumes, job text, drafts or hidden reasoning.
- ADK prompt-response GCS/BigQuery upload stays disabled independently from trace content capture;
  `NO_CONTENT` is the required trace/event mode. OpenAI SDK export remains disabled.
- Tenant and actor IDs are pseudonymous operational references and dashboard queries reauthorize
  tenant ownership. Retention, lawful basis and production analytics access need legal review.
- Routing is deterministic policy, not an LLM decision. Provider/model names are explicit outputs;
  unavailable or over-budget selections fail rather than switch silently.
- Cache keys use tenant, capability, prompt/model version and minimized input digest; sensitive
  payloads are never cached by default. Cache hits cannot bypass authorization or evidence policy.
- No migration, exporter endpoint, credentials, BigQuery dataset, Cloud Trace/Logging resource,
  LangSmith project, live call, deployment, billing or paid service is authorized.

### Risks and mitigations

- PII/secret leakage: closed telemetry schema, unsafe-key/value rejection, content-free adapters,
  adversarial redaction tests and disabled content capture/export.
- High-cardinality/cost explosion: bounded identifiers/labels, local aggregation, quotas, retention
  design, no histogram exporter yet and explicit production sampling/cardinality review.
- Misrouting/silent fallback: versioned decision table, one selected route, reason codes, explicit
  unavailable/quality/privacy/cost failures and exhaustive tests.
- Budget race/estimate drift: atomic local ledger semantics, reservations, reconciliation records,
  conservative estimates and production durable transaction requirement.
- Evaluation gaming/drift: versioned fixtures/thresholds, multiple metric families, explicit skips,
  deterministic fake baseline and separately authorized live evaluations.
- Vendor lock-in: OpenTelemetry/core ports own semantics; Cloud, LangSmith, ADK and OpenAI are
  bounded adapters whose configuration cannot change domain policy.

### Automated verification

- Telemetry schema/redaction/cardinality tests and end-to-end correlation propagation.
- Routing decision matrix across capability/privacy/quality/latency/cost/availability; no-fallback,
  budget/quota/reservation/cache and provider-failure tests.
- Evaluation report thresholds for retrieval, route, tool, handoff, grounding, safety, latency and
  cost; default fake execution only. ADK live behavioral evaluation remains opt-in and unauthorized.
- Complete Ruff/MyPy/Pytest, frontend format/lint/type/test/build, SAST/SCA/secrets,
  docs/link/Mermaid, governance, pre-commit and complete diff review with warnings disclosed.

### Manual verification

- Run one synthetic journey and follow correlation/run IDs across HTTP and local component events.
- Inspect the metrics dashboard for latency, outcome, provider/model/prompt, token and CHF estimate
  without career text, prompts, secrets or hidden reasoning.
- Route a zero-cost fake workflow; request a paid/unavailable route and observe explicit blocking
  with no fallback. Exceed a synthetic budget/quota and inspect the visible reason.
- Run the offline evaluation harness, deliberately lower one result and observe threshold failure.
- Inspect disabled Cloud/BigQuery/LangSmith/ADK/OpenAI export configuration and `NO_CONTENT` policy.

### Explicit exclusions

- Provisioning/configuring Cloud Logging, Cloud Trace, GCS, BigQuery, LangSmith or third-party SaaS;
  real exporter traffic, credentials, customer data, paid/live model evaluation, production alerting,
  final sampling/retention, autoscaling/capacity, Phase 16 security hardening and deployment.
- Dynamic model discovery, automatic provider fallback, semantic prompt cache, production billing
  reconciliation, hidden chain-of-thought capture and claims of production SLO achievement.

### Stop condition

Complete `docs/reviews/phase-15-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 15 AND START PHASE 16`

## Completed implementation plan: Phase 14

**Objective:** replace the development-preview page with a coherent, responsive,
keyboard-accessible CareerPilot workspace that exposes the already implemented journey,
evidence, citations, agent progress, drafts/approval, notifications, tracking and audit
concepts without expanding backend authority or exposing hidden reasoning.

### Scope and acceptance mapping

- Build a dashboard shell with skip link, landmark navigation, workspace identity, clear
  focus, mobile/desktop layouts, and English copy structured for later localization.
- Present profile/evidence management, job workspace, match/gap results, cited retrieval,
  workflow timeline, agent activity, editable draft/approval inbox, interview preparation,
  application tracker, notifications/settings and audit controls using activated APIs where
  available and explicit local/demo states where backend behavior remains future work.
- Add a strict A2UI-compatible renderer for allowlisted `text`, `citation`, `status`, and
  `action` presentation components. Render all content as React text; unknown components,
  unsafe URLs/HTML and unapproved actions fail closed.
- Cover loading, empty, denied, offline, partial-failure, stale-data and cancellation states
  with actionable, non-technical recovery guidance and correlation references.
- Display concise decision summaries, source provenance and state transitions only. Never
  display prompts, hidden chain-of-thought, model reasoning, secrets or raw audit payloads.

### Deliverables and expected files

- Modular web components, view models and API adapters under `apps/web/src`, replacing the
  single-page preview while preserving existing safe local workflows.
- Component/integration tests for navigation, keyboard/focus behavior, responsive semantics,
  citations, unsafe A2UI content, loading/empty/error/offline/stale/cancel states, draft review,
  notifications and audit authorization; maintain the axe accessibility gate.
- ADR-0026, UI architecture/annotated source/tutorial/exercises, product/security/privacy,
  traceability/state/roadmap/learning updates and mandatory Phase 14 review.
- No new production dependency is planned. Use React/Next.js, CSS and existing test tools.

### Architecture, security, privacy, migration, deployment, and cost

- Next.js owns presentation and interaction state; FastAPI remains the authority for identity,
  tenancy, permissions, business transitions and validation. Browser state never grants access.
- A2UI messages are untrusted presentation data. The renderer uses a closed discriminated
  union and action registry; it never evaluates HTML, scripts, arbitrary URLs or component names.
- Forms retain server-derived tenant/session headers, bounded fields, explicit confirmation for
  deletion/approval/cancellation and safe non-enumerating errors. Sensitive career content is
  excluded from browser persistence, URLs, logs and telemetry.
- UI strings use stable message keys/view labels and centralized navigation metadata as an
  i18n-ready boundary; translation delivery remains later work.
- No schema migration, cloud resource, deployment, model call, external send, billing change,
  paid dependency or real personal data is authorized. Local synthetic APIs/fakes remain default.

### Risks and mitigations

- UI implying unavailable capability: visibly label local/demo-only states and disable actions
  whose production backend is not activated; test the labels and disabled semantics.
- Authorization bypass through hidden buttons/routes: server remains authoritative; UI also
  presents denied state without assuming absence of controls is security.
- A2UI injection/action abuse: closed schemas, text rendering, no `dangerouslySetInnerHTML`,
  allowlisted action IDs, safe citation references, and adversarial tests.
- Accessibility regression: semantic landmarks/headings, skip link, focus-visible styles,
  live regions, keyboard tests, axe checks, motion preference and responsive CSS.
- State overload and partial failure: independent workspace panels, explicit status model,
  retry controls, last-updated/stale labels and cancellation confirmation.
- Privacy in the browser: tab-local state only, no localStorage/sessionStorage, minimized errors,
  synthetic fixtures and documented production session/retention gaps.

### Automated verification

- Vitest/Testing Library component and integration coverage including axe, keyboard navigation,
  A2UI allowlist/unsafe content, citations, loading/error/offline/stale/cancel and responsive
  landmark tests; Next.js production build and TypeScript/ESLint/Prettier gates.
- Existing OpenAPI and backend regression suites plus Ruff/MyPy/Pytest, architecture checks,
  secret/SAST/SCA, documentation/link/Mermaid, governance, pre-commit and complete diff review.
- Visual regression is evaluated but not added unless a stable local screenshot runner exists;
  semantic component/state tests are the zero-cost maintainable baseline.

### Manual verification

- Sign in as Ada and complete profile → job comparison → cited evidence → review workspace,
  using keyboard only; confirm focus order, visible focus and status announcements.
- Test at 375px and desktop widths; zoom to 200%; inspect navigation and no horizontal overflow.
- Open citations, edit a draft presentation, inspect approval controls and confirm unavailable
  consequential actions are disabled or require explicit confirmation.
- Simulate offline, denied, partial error, stale and cancellation states and follow recovery copy.
- Inspect A2UI output and page source to confirm no executable markup or hidden reasoning.

### Explicit exclusions

- New backend business workflows, real Temporal gateway, automatic application submission,
  email/SMS/push, scraping, live interviews/models, file export/PDF generation, organization/
  coach activation, production authentication, browser persistence, analytics and deployment.
- Arbitrary A2UI component loading, arbitrary links/actions, hidden reasoning, final translations,
  paid visual-regression services and Phase 15 observability/routing/cost work.

### Stop condition

Complete `docs/reviews/phase-14-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 14 AND START PHASE 15`

## Completed implementation plan: Phase 13

**Objective:** add reliable, tenant-safe asynchronous integration events and in-app
notification foundations through a transactional outbox/inbox design, a local deterministic
transport, and a bounded Google Pub/Sub adapter without creating cloud resources.

### Scope and acceptance mapping

- Define a strict versioned event envelope with opaque identifiers, event type/schema
  version, aggregate ordering key/sequence, occurrence time, correlation, and bounded data.
- Implement atomic application-change plus outbox recording, dispatch acknowledgement,
  inbox deduplication, per-aggregate ordering, retry/backoff, poison-message quarantine,
  dead-letter replay, and stable failure taxonomy.
- Add notification preferences and a tenant/actor-authorized in-app notification inbox;
  event handlers may create local notifications but never send email or mutate profiles.
- Provide an official Google Pub/Sub publisher adapter and subscriber message boundary;
  default tests use a deterministic local transport with duplicate/reorder/failure controls.
- Decide Dapr through ADR evidence. Do not add it when direct ports/adapters remain simpler.

### Deliverables and expected files

- Framework-neutral event/notification contracts and ports in `packages/core`, with local
  repositories/transport, dispatcher/consumer, and Pub/Sub adapter in `apps/api`.
- Authenticated notification preference/list/read routes and event/outbox contract tests.
- Tests for schema compatibility, atomicity, duplicate delivery, ordering, retry, poison
  messages, dead-letter/replay, tenant isolation, notification authorization, and redaction.
- `google-cloud-pubsub>=2.39,<2.40` (Apache-2.0; Python 3.13 supported), locked and audited.
- ADR-0025, event architecture/annotated source/tutorial/exercises, security/privacy,
  traceability/state/roadmap/learning updates, and mandatory Phase 13 review.

### Architecture, security, privacy, migration, deployment, and cost

- PostgreSQL is the future authoritative outbox/inbox/notification store. Phase 13 uses
  transaction-shaped in-memory adapters for default tests and documents the later migration.
- Producers never publish inside a business transaction. They atomically persist state and
  outbox; a dispatcher publishes, then marks acknowledged. Consumers record inbox receipt
  and notification in one transaction-shaped operation before acknowledging transport.
- Pub/Sub is treated as at-least-once. Application event IDs provide deduplication;
  aggregate ID is the ordering key and sequence gaps are retried then dead-lettered visibly.
- Envelopes contain allowlisted metadata and opaque references, not resumes, job text,
  drafts, prompts, secrets, email addresses, or hidden reasoning. Payloads are untrusted.
- Every read/write and handler is tenant-scoped. Notifications do not grant authority and
  deep links remain opaque internal references.
- Local transport is default. The Pub/Sub adapter requires explicit project/topic/config
  and does not create resources. No emulator, cloud connection, deployment, billing,
  external message, email, paid call, or database migration occurs.
- Dapr is rejected for now: it would add runtime/configuration/sidecar surface without
  demonstrating value beyond the narrow event ports. Revisit only with measurable benefit.

### Risks and mitigations

- State committed but event lost: transactional outbox and atomicity failure tests.
- Duplicate/redelivered event: durable-design inbox uniqueness and idempotent handler tests.
- Out-of-order delivery: per-aggregate sequence cursor, bounded retry, explicit dead letter,
  and tests that unrelated ordering keys continue.
- Poison or malicious payload: strict envelope/schema allowlist, size/control-character
  bounds, safe errors, attempt ceiling, quarantine/dead-letter, and manual replay policy.
- Cross-tenant notification leak: tenant/actor predicates at service and repository layers,
  non-enumerating reads, and hostile tests.
- PII in broker/history: opaque references, payload allowlist/redaction tests, minimized
  retention, message-storage policy documentation, and legal/security review.
- Publish acknowledgment ambiguity: stable event ID, outbox retry, subscriber deduplication,
  no exactly-once assumption, and metrics deferred to Phase 15.

### Automated verification

- Envelope JSON/schema backward-compatibility and invalid/oversized payload tests.
- Atomic mutation/outbox rollback; dispatch ack ambiguity; duplicate, reorder, retry,
  poison, dead-letter and replay tests; notification preference/auth/tenant tests.
- Official Pub/Sub adapter contract test with a fake publisher client; no network call.
- Complete Ruff, MyPy, Pytest, frontend/build, audits, Semgrep, secrets, docs/link/Mermaid,
  pre-commit, governance and diff review, disclosing all warnings/skips.

### Manual verification

- Record a synthetic application event and inspect its pending/published outbox lifecycle.
- Deliver it twice and confirm one notification; deliver sequence two before one and inspect
  bounded retry/order recovery; send poison data and inspect dead letter.
- Replay a corrected dead letter and confirm exactly one authorized notification.
- Sign in as two tenants and confirm neither can enumerate the other's notifications.
- Inspect the Pub/Sub adapter configuration and Dapr ADR without connecting to cloud.

### Explicit exclusions

- Cloud Pub/Sub topics/subscriptions/IAM, emulator installation, staging/production,
  PostgreSQL event migrations, email/SMS/push delivery, automatic submission/sharing,
  Dapr runtime/sidecar, Phase 14 UI, analytics/metrics dashboards, and paid services.
- Exactly-once business-effect claims, global total ordering, cross-region ordering claims,
  final retention/legal certification, and unbounded replay.

### Stop condition

Complete `docs/reviews/phase-13-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 13 AND START PHASE 14`

## Completed implementation plan: Phase 12

**Objective:** implement a crash-resilient Temporal job-application preparation workflow
that durably coordinates analysis, research, truthful drafts, exact human approval,
application tracking, a follow-up timer, cancellation, and compensation without placing
model calls or external side effects in deterministic workflow code.

### Scope and acceptance mapping

- Add a dedicated Temporal worker boundary with versioned, data-minimized workflow,
  signal, query, activity, status, and result contracts.
- Orchestrate analysis, supplied-source research, resume/cover-letter preparation,
  approval wait, tracking, and one scheduled follow-up through activities.
- Implement activity retry/timeouts/heartbeat policy, scoped idempotency, approval and
  cancellation signals, read-only status queries, reverse-order compensation, workflow
  versioning, and metadata-only correlation.
- Distinguish Temporal workflow state from LangGraph graph state, application records,
  agent sessions, audit history, and external effects in source, tests, and documentation.
- Cover FR-012/013/020 and NFR-002/003/009/010/011/013/016/020 without claiming that
  the local fake activity ledger is production persistence.

### Deliverables and expected files

- New `services/temporal-worker/` uv workspace package containing contracts, deterministic
  workflow, activities/ports, worker/client composition, and a local fake implementation.
- Tests for time skipping, signals/queries, exact approval, restart/recovery, retry,
  idempotency, cancellation, compensation, heartbeat, and replay compatibility.
- `temporalio>=1.30,<1.31` (MIT; Python 3.13 supported) plus a locked dependency review.
- ADR-0024, workflow-state architecture note, annotated source, tutorial, exercises and
  answers, traceability/security/privacy/state/roadmap updates, and Phase 12 review.

### Architecture, security, privacy, migration, deployment, and cost

- Temporal owns durable orchestration history, waits, timers, retries, signals, queries,
  and compensation. PostgreSQL remains authoritative for product/business records;
  LangGraph owns only bounded agent-graph execution and checkpoints.
- Workflow code performs no network, filesystem, database, random wall-clock, model, or
  authorization side effect. Activities reauthorize and operate through bounded ports.
- Workflow inputs/history contain opaque tenant, actor, resource, correlation, artifact,
  and idempotency identifiers rather than resume, job, research, or draft content.
- Approval signals bind the expected draft reference/version and cannot themselves email,
  submit, publish, spend, or mutate inferred profile facts.
- Local tests use the free Temporal time-skipping test server and synthetic fake activities.
  No Temporal Cloud, cloud resource, deployment, billing, paid call, or live model is used.
- No PostgreSQL migration is planned. Production task queues, namespace, TLS/workload
  identity, persistence retention, visibility, and deployment remain later decisions.

### Risks and mitigations

- Non-deterministic replay: sandboxed workflow imports, deterministic APIs only, explicit
  version marker, history replay tests, and no I/O in workflow code.
- Duplicate activity effects: tenant/workflow/step idempotency keys, an activity ledger,
  retry tests, and compensation that is itself idempotent.
- Approval spoofing/staleness: server-owned workflow identity, expected draft reference and
  version in the signal, one terminal decision, and rejected mismatch tests.
- Cancellation during side effects: heartbeat-aware activities, cancellation signal plus
  Temporal cancellation tests, reverse-order compensation, and visible terminal state.
- Sensitive history growth/leakage: identifier-only contracts, bounded status summaries,
  no prompts/content/hidden reasoning, and retention/legal-review documentation.
- Test-server download/platform limits: verify the official local server explicitly; if it
  is unavailable, keep unit/activity/replay evidence distinct and report the blocked gate.

### Automated verification

- Temporal time-skipping integration tests for approval wait and scheduled follow-up.
- Workflow query/signal, retry, activity heartbeat, duplicate/idempotency, cancellation,
  compensation, worker restart/recovery, and replay/determinism tests.
- Ruff, strict MyPy, complete Pytest, architecture boundaries, frontend/build regression,
  dependency/license audit, SAST, secrets, docs/link/Mermaid, pre-commit, governance, and
  complete diff review with every skip/warning/environment limitation disclosed.

### Manual verification

- Start a synthetic workflow, query its stage, and observe it pause for exact approval.
- Stop the worker while approval is pending, restart it, send approval, and observe resume.
- Advance the local test clock and inspect the scheduled follow-up result.
- Inject a transient activity failure and observe retry without a duplicate effect.
- Cancel after preparatory work and inspect reverse-order compensation and terminal status.

### Explicit exclusions

- Temporal Cloud, production namespace/worker deployment, paid resources, real credentials,
  customer data, model calls, emails, submissions, external sharing, browser automation,
  Pub/Sub, Dapr, notifications, Phase 13, and DBOS/Restate comparisons.
- Production PostgreSQL workflow projections/outbox, final retention schedules, encryption
  keys, backups, multi-region recovery, and production SLO/load claims.

### Stop condition

Complete `docs/reviews/phase-12-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 12 AND START PHASE 13`

## Completed implementation plan: Phase 11

**Objective:** connect the LangGraph application, Google ADK specialist, and OpenAI
Agents specialist through versioned, discoverable, policy-controlled A2A capabilities and
a complete local task lifecycle using the official Python SDK.

### Scope and acceptance mapping

- Publish official A2A Agent Cards for all three runtimes with versioned skills, security
  declarations, input/output modes, capabilities, and local URLs.
- Implement a tenant-safe capability registry, discovery/compatibility checks, bounded
  remote-agent port, authentication/authorization, correlation, idempotent task creation,
  status, cancellation, timeout, and stable remote error mapping.
- Exercise cross-service delegation through deterministic in-process transports; no model
  call, provider fallback, or network service is required by default tests.
- Use official `a2a-sdk` card/task types at the application boundary; do not recreate
  protocol schemas manually. The production HTTP JSON-RPC server surface remains deferred
  with independently deployed services.

### Deliverables and expected files

- An SDK-backed interoperability adapter and application routes in the API layer, with
  cards identifying the existing bounded LangGraph, ADK, and OpenAI services.
- Unit/contract/e2e tests for cards, discovery, version compatibility, capability policy,
  task lifecycle, duplicate IDs, timeout, cancellation, unavailable agents, and tenancy.
- ADR, agent registry/capability documentation, annotated source, tutorial, exercises,
  security/privacy/traceability/state/roadmap updates, and mandatory phase review.
- Add official `a2a-sdk>=0.3.22,<0.4` after lock, license, compatibility, and audit review.

### Architecture, security, privacy, migration, deployment, and cost

- Agent Cards advertise capabilities and authentication requirements; they confer no
  authorization. Every operation rechecks server-derived caller identity and capability.
- The registry stores descriptors/adapters, not secrets or customer content. Task IDs are
  scoped by tenant/caller; duplicate payload conflicts fail closed and foreign tasks are
  non-enumerating.
- Correlation metadata excludes payload content. Remote inputs/outputs are strict,
  minimized, bounded, and treated as untrusted at both ends.
- Default transport is in-process fake; production HTTP/OAuth/workload identity, remote
  discovery trust/signatures, durable task storage, deployment, and retention are deferred.
- No migration, cloud resource, deployment, billing, live model, or external transfer.

### Risks and mitigations

- Malicious/stale cards: trusted registry allowlist, protocol/skill version checks, strict
  official SDK validation, and incompatible-card tests.
- Cross-tenant/privilege delegation: caller context, deny-default capability grants,
  tenant/task binding, non-enumerating access, and hostile tests.
- Duplicate/cancelled tasks: idempotency fingerprint, deterministic state machine,
  terminal-state rules, cooperative cancellation, and lifecycle tests.
- Remote outage/timeout/error leakage: bounded timeout, stable taxonomy, no fallback, and
  explicit degraded/unavailable results.
- Data leakage: minimized typed payloads, no hidden reasoning, metadata-only correlation,
  synthetic fixtures, and documented retention/legal gaps.

### Automated verification

- Agent Card schema/contract and capability compatibility tests; cross-runtime lifecycle,
  auth, duplicate, timeout, cancellation, unavailable-agent, and tenant-isolation tests.
- Complete Ruff, MyPy, Pytest, frontend/build, dependency audits, SAST, secrets,
  docs/links/Mermaid, pre-commit, governance, and diff review.

### Manual verification

- Discover all three cards and inspect skills/security/protocol versions.
- Delegate synthetic analysis to LangGraph, research to ADK, and interview to OpenAI.
- Observe correlated task transitions; cancel a submitted task and deny an unauthorized one.
- Disable a remote adapter and confirm explicit degradation without provider fallback.

### Explicit exclusions

- Public internet registry, dynamic untrusted card enrollment, real OAuth/mTLS, signed
  cards, remote deployment, streaming/push notification, durable tasks, customer data,
  model calls, Temporal, Pub/Sub, and Phase 12 work.

### Stop condition

Complete `docs/reviews/phase-11-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 11 AND START PHASE 12`

## Completed implementation plan: Phase 10

**Objective:** deliver an isolated OpenAI Agents SDK interview-simulation service and
learning laboratory that compares manager delegation, agent-as-tool, and direct handoff
using equivalent synthetic fixtures and fake execution by default.

### Scope and acceptance mapping

- Define interview manager, interviewer, and feedback specialist agents with structured
  outputs; demonstrate direct handoff and agent-as-tool using the real SDK definitions.
- Provide a deterministic fake runtime for default tests, scoped sessions, input/output/
  tool guardrails, approval pause/serialize/resume, and metadata-only local tracing.
- Expose a narrow authenticated service API and explicit disabled/unavailable behavior.
- Keep OpenAI imports inside `services/openai-agents`; no provider fallback or live call.
- Add an opt-in live test with an explicit per-run budget ceiling and cost approval gate.

### Deliverables and expected files

- New uv workspace package under `services/openai-agents/` with SDK agent definitions,
  contracts, fake/live ports, orchestration comparison, guardrails, sessions, approvals,
  traces, configuration, and API.
- Unit/contract/live tests for handoff paths, agent-as-tool comparison, session isolation,
  guardrails, approval serialization/resume/stale decisions, trace redaction, disabled
  service, and budget gating.
- ADR, annotated source, tutorial, exercises/answers, security/privacy/traceability,
  decision/learning/state/roadmap updates, and mandatory phase review.

### Architecture, security, privacy, migration, deployment, and cost

- The manager pattern retains final-response ownership; direct handoff transfers active
  conversation ownership. Equivalent fixtures make this difference observable.
- Only a bounded feedback-publication demonstration requires approval; it performs no
  external publication, email, submission, or profile mutation after approval.
- SDK tracing export is disabled by default and sensitive trace data is excluded. Local
  trace evidence contains IDs, route, outcome, turns, and provider only.
- Fake runtime is default. Live OpenAI requires explicit provider selection, credentials,
  consent/transfer authority, cost approval, and a positive CHF ceiling; no fallback.
- No schema migration, cloud resource, deployment, paid call, or external transfer.

### Risks and mitigations

- Wrong specialist/control transfer: explicit route enum, equivalent scenario tests, SDK
  shape assertions, and stable route trace metadata.
- Guardrail gaps: deterministic blocking input/output/tool gates outside model authority.
- Approval replay/race: exact session/run/action hash and revision binding plus serialized
  pending state and terminal transition tests.
- PII/hidden reasoning leakage: synthetic fixtures, minimized contracts, redacted traces,
  no prompts/tool payloads in telemetry, and concise decision summaries only.
- Unbounded spend: fake default, max turns, live marker, explicit CHF budget gate, no
  retries/fallback, and zero live execution under current approval.

### Automated verification

- Focused service tests, then complete Ruff, MyPy, Pytest, frontend/build, dependency
  audits, SAST, secrets, docs/links/Mermaid, pre-commit, governance, and diff review.
- Live OpenAI test must skip unless explicit cost/data authorization and budget exist.

### Manual verification

- Start the synthetic interview through direct handoff and inspect active specialist.
- Run the same fixture through agent-as-tool and inspect manager-owned final output.
- Trigger an input/tool/output guardrail and inspect the safe error.
- Pause a feedback action, serialize, approve/reject, resume, and inspect redacted traces.

### Explicit exclusions

- Real candidate data, automatic communications/submissions/profile mutations, voice or
  realtime interview, hosted tools, web search, A2A, deployment, cloud tracing, durable
  production sessions, Temporal, and Phase 11 work.

### Stop condition

Complete `docs/reviews/phase-10-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 10 AND START PHASE 11`

## Completed implementation plan: Phase 9

**Objective:** deliver an isolated, bounded Google ADK specialist service for
company/job research over explicitly supplied sources, with fake-first execution and an
explicitly authorized Gemini path.

### Scope and acceptance mapping

- Implement one ADK research specialist with structured cited output, per-session state,
  allowlisted source tools, safety callbacks, and metadata-only telemetry.
- Expose a narrow authenticated service API plus an in-process fake adapter used by the
  main application and all default tests; disabling the specialist degrades explicitly.
- Keep Google ADK/Gemini imports inside the specialist boundary. No unrestricted web
  scraping, silent provider fallback, profile mutation, or external side effect.
- Classify timeout, quota, malformed output, and provider outage into stable safe errors.
- Provide an opt-in live Gemini evaluation that is skipped unless explicit configuration
  and cost authorization are present.

### Deliverables and expected files

- A prototype-first ADK service workspace under `services/google-adk/`, including an
  agents-cli manifest/spec, agent, tools, callbacks, session boundary, schemas, API,
  telemetry, fake/live provider composition, and evaluation fixture.
- Unit, service-contract, failure-injection, session-isolation, safety, structured-output,
  citation, disabled-service, and opt-in live-evaluation tests.
- An ADR, ADK-versus-LangGraph tutorial, annotated source, exercises/answers, threat/privacy
  updates, requirements traceability, learning/state/roadmap updates, and phase review.
- Pin official `google-adk>=2.5,<2.6` only after lock, license, compatibility, and audit
  checks. Use Python 3.13 and no deployment dependencies.

### Architecture, security, privacy, migration, deployment, and cost

- The service receives minimized user-supplied company/job source excerpts with stable
  source IDs. Its only tool retrieves from that request-local allowlist; citations must
  bind every factual finding to one supplied source.
- A deterministic fake provider is the default. Gemini requires an explicit enable flag,
  consent/authorization metadata, configured model, timeout, and credentials; failures
  never trigger fallback.
- Session IDs are tenant/actor scoped and request content is not recorded in telemetry.
  Structured schemas reject extra fields and safety callbacks reject prompt-injection,
  unsupported-source, and sensitive-transfer violations before model execution.
- Phase 9 creates no cloud resources, database migration, paid call, billing, deployment,
  unrestricted browsing, or real-person data transfer. Live evaluation remains opt-in.

### Risks and mitigations

- Hallucinated research: closed source set, required citations, post-validation, and
  fail-closed malformed/unsupported citation tests.
- Cross-session or tenant leakage: scoped session keys, request-local tools, no global
  source cache, authorization contract, and isolation tests.
- Prompt injection and PII transfer: untrusted-data framing, deterministic inspection,
  minimization/consent checks, and synthetic fixtures.
- Provider instability/cost: bounded timeout, stable quota/outage errors, no retry or
  fallback by default, fake tests, explicit live/cost gates, and metadata-only telemetry.
- Framework coupling: service-only ADK imports and a typed HTTP/client contract keep the
  core and FastAPI application independent.

### Automated verification

- Run focused fake/provider/service tests followed by complete Ruff, strict MyPy, Pytest,
  web checks, build, dependency/security audits, secrets, docs/links/Mermaid, pre-commit,
  governance validation, and complete diff review.
- Keep live Gemini evaluation marked and skipped by default; record the exact opt-in
  command without executing it in the CHF 0 workflow.

### Manual verification

- Run one synthetic fixture through fake configuration and inspect structured findings,
  source citations, session metadata, and telemetry.
- Disable the service and confirm explicit `specialist_unavailable` degradation.
- With separate explicit cost/data approval, run the same fixture through Gemini and
  compare its schema/citations; this is not authorized by the phase-start command.
- Read and exercise the ADK-versus-LangGraph tutorial.

### Explicit exclusions

- Unrestricted web search/scraping, managed Google Search/RAG, real customer data, live or
  paid model calls, cloud resources, deployment/IaC, durable production sessions, A2A,
  OpenAI Agents SDK, Temporal, Pub/Sub, and Phase 10 work.

### Stop condition

Complete `docs/reviews/phase-09-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 9 AND START PHASE 10`

## Completed implementation plan: Phase 8

**Objective:** generate versioned resume and cover-letter drafts whose material claims
are evidence-linked, then pause behind a durable, exact-version human approval gate.

### Scope and acceptance mapping

- Implement Resume Tailoring, Cover Letter, Privacy/PII, Bias/Compliance, and Approval
  Coordinator roles with explicit non-responsibilities and state ownership.
- Build a claim-to-evidence graph; unsupported skills, dates, employers, qualifications,
  and metrics are blocked or returned only as suggestions requiring confirmation.
- Store immutable draft versions and editable structured sections; every material claim
  carries citations and validation status.
- Implement pending, approved, edited-and-approved, rejected, more-information,
  expired, and cancelled approval states with exact draft-version/hash binding.
- Pause and resume human review using LangGraph interrupt/Command semantics and a
  checkpointer; use PostgreSQL for restart-safe production records and local fakes in
  default tests.
- Emit allowlisted A2UI-compatible draft/approval messages that contain presentation
  data only and never authorize an action.

### Deliverables and expected files

- Draft, claim, citation, approval, transition, and repository protocols in core.
- PostgreSQL tables/Alembic `0003`, tenant-safe repository, generation/policy service,
  approval graph, strict API contracts/routes, and application composition.
- Unit/API/contract/e2e/PostgreSQL tests for state machine, restart/resume, stale and
  concurrent approval, edit/versioning, PII, bias, invented claims/dates, and A2UI.
- ADR, role dossiers, annotated source, tutorial, exercises/answers, security/privacy,
  traceability, learning log, and `docs/reviews/phase-08-review.md`.
- Add official `langgraph-checkpoint-postgres>=3.1,<3.2` (MIT, Python 3.10+) if its
  lock/audit remains compatible; no live model dependency or call is needed.

### Architecture, security, privacy, migration, deployment, and cost

- Generation is deterministic/fake-first and may only transform authorized profile and
  cited evidence. Verification, privacy, and bias policy are deterministic gates after
  generation; no reviewer can convert unsupported content into fact.
- Approval is a deterministic state machine. Every decision includes expected draft
  version and content hash under optimistic concurrency and tenant authorization.
- LangGraph interrupt is the interaction checkpoint; PostgreSQL draft/approval records
  are authoritative durable business evidence. Temporal remains future owner of timers,
  schedules, and cross-service recovery.
- Drafts contain high-risk personal data. Store minimized structured content, exclude
  it from logs/audit, and document encryption/retention/deletion/legal review gaps.
- Migration is forward versioned and tested on disposable PostgreSQL. No cloud resource,
  deployment, billing, external transfer, or paid/model call is authorized.

### Risks and mitigations

- Fabricated career claims: claim graph, citation requirements, invented-value corpus,
  fail-closed verification, and confirmation-only suggestions.
- Stale/raced approval: exact version/hash binding, atomic compare-and-update, terminal
  state rules, and concurrency tests.
- Approval bypass: separate generate/review/use permissions, pending by default, no
  external side effect, server-derived context, and audit transitions.
- PII leakage: deterministic detection, user-visible flags, minimized response/A2UI,
  metadata-only telemetry, tenant-filtered persistence, and synthetic fixtures.
- Checkpoint mismatch: scoped thread IDs, interrupt payload version/hash, durable record
  reconciliation, restart/resume tests, and explicit recovery failure.
- UI/schema injection: A2UI message types/components/actions are allowlisted and content
  is data, not executable markup or authority.

### Automated verification

- State-transition matrix, terminal/expiry/cancel, edit/version/hash, stale/concurrent
  decisions, restart/resume, graph interrupt, and repository transaction tests.
- Unsupported/invented claim/date/metric corpus, citation integrity, PII/bias policy,
  A2UI allowlist, cross-tenant/IDOR, OpenAPI, and audit/correlation tests.
- Existing Python/web/PostgreSQL suites plus format, lint, type, build, migration drift,
  SAST/SCA, secrets, docs/links/Mermaid, pre-commit, and complete diff review.

### Manual verification

- Generate synthetic resume/letter drafts; open every claim citation and inspect blocked
  suggestions. Edit one draft and observe a new version/hash.
- Approve exact version, reject another with feedback, request more information, cancel,
  and verify stale approval is refused.
- Restart while pending using PostgreSQL, reload the record/checkpoint, resume safely,
  and inspect correlated audit plus A2UI-compatible review payload.

### Explicit exclusions

- Automatic email/submission/sharing, profile mutation, real resume export/PDF styling,
  provider/model calls, company research, ADK, OpenAI Agents SDK, A2A, Temporal timers,
  Pub/Sub, cloud deployment, production key management, and final legal certification.

### Stop condition

Complete `docs/reviews/phase-08-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 8 AND START PHASE 9`

## Completed implementation plan: Phase 7

**Objective:** build a typed, checkpointed LangGraph job-analysis workflow that
coordinates bounded specialist roles and returns cited match, gap, evidence, and
explanation results using fake providers by default and no paid calls.

### Scope and acceptance mapping

- Define explicit graph, node, model, retrieval, and audit state with ownership rules.
- Implement Manager, Intake, Job Analysis, Retrieval, Match, Skill Gap, Evidence
  Verification, and Explanation nodes; use deterministic routing for known paths and
  expose an evaluated model router only for ambiguous fixture cases.
- Produce validated structured job requirements, cited supported matches, missing and
  uncertain gaps, explicit insufficient-evidence state, and concise explanations.
- Add bounded node timeouts/retries, a terminal error node, cooperative cancellation,
  in-memory checkpoints/resume for local/test, and metadata-only trace events.
- Add a fake provider as the default and a fail-closed Gemini adapter requiring
  explicit live configuration, authorization/consent metadata, and no fallback.
- Add authenticated API start/status/resume/cancel routes and workflow progress that
  remains tenant-scoped and does not expose hidden reasoning.

### Deliverables and expected files

- Graph state, contracts, provider port, role dossiers, and orchestration service in
  `packages/core/` and `apps/api/` without provider imports in the domain package.
- LangGraph graph builder/checkpointer and Google Gen AI adapter in the API adapter
  layer; HTTP schemas/routes and versioned OpenAPI updates.
- Unit, API, contract, end-to-end, failure-injection, transition, routing, checkpoint,
  cancellation, grounding, and hallucination evaluation tests with synthetic fixtures.
- ADR, agent-role dossiers, annotated source, tutorial, exercises/answers, security,
  privacy, traceability, learning log, and `docs/reviews/phase-07-review.md`.
- Add `langgraph>=1.2.9,<1.3` (MIT, Python 3.10+) and
  `google-genai>=2.13,<2.14` (Apache-2.0, Python 3.10+) after lock/audit review.

### Architecture, security, privacy, migration, deployment, and cost

- LangGraph owns only the bounded in-process analysis run. Temporal remains the owner
  of durable business waits, schedules, compensation, and cross-service recovery.
- Nodes return partial state updates and cannot mutate fields owned by other roles.
  Deterministic routes are the default; no model decides authorization or truth.
- Retrieved text stays labeled untrusted. Evidence verification is deterministic and
  every supported result carries source/chunk citations; missing evidence stays
  uncertain or unsupported rather than being fabricated.
- The provider port accepts minimized, redacted structured prompts. The Gemini adapter
  has no credentials by default, never silently falls back, and live tests remain
  opt-in behind explicit cost and data-policy confirmation.
- Local/test checkpoints are process-local and synthetic. No migration, cloud
  deployment, paid resource, billing, or recurring service is authorized in Phase 7.

### Risks and mitigations

- State corruption or accidental overwrite: typed state, narrow node-update models,
  ownership tests, and checkpoint transition assertions.
- Hallucinated requirements or qualifications: structured validation, citations,
  deterministic verification, insufficient-evidence branches, and evaluation corpus.
- Prompt injection: source/job text is data, never instructions; fixed system policy,
  minimized prompts, injection labels, and adversarial fixtures.
- Retry duplication: only retry side-effect-free nodes; make trace identifiers stable
  and distinguish attempt, replay, resume, and fallback explicitly.
- Provider/API churn and cost: pin supported minor lines, fake-first tests, lazy/live
  client configuration, explicit provider identity, no fallback, and zero default cost.
- Checkpoint tenant leakage: thread identity is scoped by tenant/actor/run and every
  status/resume/cancel operation reauthorizes server-derived context.

### Automated verification

- Graph path/state ownership, deterministic/model router fixtures, structured output,
  delegation/handoff, timeout/retry/error, cancellation, checkpoint/resume tests.
- Grounding/hallucination evaluation for citations, supported/missing/uncertain gaps,
  prompt injection, and insufficient evidence; live Gemini marker remains skipped.
- Authenticated cross-tenant API and OpenAPI contract tests plus all existing suites.
- Python/web/PostgreSQL format, lint, type, test, build, SAST/SCA, secret, docs/link,
  Mermaid, pre-commit, governance validation, and complete diff review.

### Manual verification

- Submit a synthetic job-analysis run and inspect ordered node progress, cited evidence,
  match, gaps, concise explanation, provider name, and correlation ID.
- Submit a role with no supporting evidence and confirm explicit uncertainty.
- Inject a transient node failure, observe bounded retry/error state, then resume from
  the checkpoint; cancel a separate run and confirm no later node executes.
- Compare deterministic and fake model routing on documented fixtures without a live
  provider or paid call.

### Explicit exclusions

- Resume/cover-letter generation, human approval lifecycle, editable drafts, and
  LangGraph human interrupts (Phase 8).
- Temporal workflows, durable database checkpointing, schedules, email, application
  submission/tracking, company scraping/research, remote agents, ADK, OpenAI Agents
  SDK, A2A, cloud deployment, and production Gemini calls.

### Stop condition

Complete `docs/reviews/phase-07-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 7 AND START PHASE 8`

## Completed implementation plan: Phase 6

**Objective:** create a secure, typed capability layer for future agents and expose
only an approved read-only subset through MCP, with no model or cloud dependency.

### Scope and acceptance mapping

- Add nine narrow capabilities: profile lookup, evidence retrieval, job ingestion,
  skill taxonomy, deterministic matching, evidence verification, approval request,
  tenant audit lookup, and cost estimation.
- Give every tool strict Pydantic input/output contracts and generated JSON Schema;
  reject unknown fields and sanitize bounded outputs.
- Centralize capability metadata: version, description, risk, permissions, side
  effects, approval requirement, timeout, retry, idempotency, rate limit, audit
  policy, and MCP exposure.
- Enforce authenticated tenant context, deny-by-default tool permissions, per-tool
  authorization, in-memory local rate limits, bounded timeout/retry, idempotency
  replay, stable error taxonomy, correlation IDs, and audit outcomes.
- Add versioned OpenAPI discovery/invocation endpoints and an official MCP Python
  SDK server exposing only approved read-only capabilities.
- Keep approval requests as deterministic pending records only; Phase 8 owns the
  durable approval lifecycle and no consequential action executes here.

### Expected files and dependencies

- Tool domain contracts/metadata under `packages/core/`.
- Pydantic schemas, registry, executor, adapters, API routes, and MCP server under
  `apps/api/`.
- Unit/API/contract/MCP tests covering every capability plus invalid schema,
  authorization, timeout, retry, duplicate, rate limit, and sanitization cases.
- ADR, annotated source, tutorial, exercises/answers, security/privacy updates,
  traceability, learning log, and `docs/reviews/phase-06-review.md`.
- Add official `mcp>=1.28.1,<1.29` (MIT, Python 3.10+) to include the upstream
  security fixes. Resolve pinned Semgrep separately with `uvx` because its CLI
  dependency graph still requires vulnerable `mcp==1.23.3`; that version must not
  enter the application lock or runtime. A handwritten JSON-RPC implementation is
  rejected due to protocol/security maintenance risk. No MCP CLI extra is needed.

### Architecture, security, privacy, and cost decisions

- One registry is the authority for both HTTP and MCP discovery; adapters cannot
  bypass the executor or publish unregistered handlers.
- Tool identity never implies user authority. Server-derived authorization context
  enters every invocation, and underlying services/repositories retain their checks.
- MCP exposure is an explicit allowlist limited initially to read-only profile,
  retrieval, taxonomy, and cost capabilities. Audit data, job mutation, matching,
  verification, and approval creation remain HTTP/internal only.
- Idempotency keys are required for state-changing tools and scoped to tenant,
  actor, tool, and validated input hash. Reuse with different input fails closed.
- Rate limits are local deterministic safeguards for Phase 6, not distributed
  production enforcement. They contain no billing and reset on restart.
- Tools do not call models or external APIs. Cost estimates are deterministic CHF
  zero for current local implementations and never authorize spending.
- Inputs/outputs and retrieved content are not written to logs or audit records.
  Development fixtures remain synthetic.

### Risks and mitigations

- Tool privilege escalation: deny-default registry, permission metadata, context
  validation, MCP allowlist, underlying service checks, and hostile-tenant tests.
- Schema or adapter drift: derive JSON Schema from Pydantic and compare registry,
  OpenAPI, and MCP discovery in contract tests.
- Replay/duplicate mutation: scoped idempotency cache and input fingerprint conflict.
- Denial of service/wallet: payload limits, timeout, bounded retries, and per-actor/
  tenant/tool rate counters; distributed quotas remain Phase 15/16 work.
- Sensitive output leakage: response-model validation, recursive control-character
  removal/size bounds, retrieval `UNTRUSTED` labels, and sanitization tests.
- MCP ecosystem churn: pin the current stable v1 line below v2 and record a review
  trigger before migration.

### Automated verification

- Unit and contract tests for all nine tools and every capability schema.
- Invalid schema, foreign tenant, permission denial, timeout, retry, duplicate,
  idempotency conflict, rate-limit, sanitization, and audit/correlation tests.
- Official MCP in-memory protocol smoke test for list and read-only call plus proof
  that non-approved tools are absent.
- Existing Python/web/PostgreSQL suites, OpenAPI, format/lint/type/build, dependency,
  secret/SAST, documentation/link/Mermaid, pre-commit, and complete diff review.

### Manual verification

- Sign in locally, list capabilities and inspect schemas/metadata, successfully call
  one read-only tool, attempt one unauthorized call, repeat an idempotent mutation,
  trigger a rate limit, and inspect correlated audit facts.
- Start the local MCP server, list its allowlisted tools, call one read-only tool with
  synthetic context, and verify privileged/internal tools are not discoverable.

### Explicit exclusions

- LangGraph, LLM agents, model calls, provider fallback, live taxonomy/API sources,
  automatic browsing, scraping, email, submission, or external side effects.
- Durable approvals and restart recovery (Phase 8/12), distributed rate limiting,
  production OAuth for MCP, remote MCP deployment, and production credentials.
- Cloud resources, paid calls, billing, or recurring services.

### Stop condition

Complete `docs/reviews/phase-06-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 6 AND START PHASE 7`

## Completed implementation plan: Phase 5

**Status:** Complete on 2026-08-11; awaiting owner acceptance. Phase 6 has not
started.

**Objective:** ingest synthetic user documents safely and provide evaluated,
cited, tenant-isolated hybrid retrieval without a live model or paid service.

### Scope and acceptance mapping

- Accept bounded text/PDF bytes through authenticated multipart upload; validate
  name, declared type, magic bytes, size, hash, and a local scanner policy before
  moving content out of quarantine.
- Store raw bytes behind a `DocumentStorage` port using a local adapter; production
  object storage remains an explicit adapter boundary.
- Parse UTF-8 text and bounded PDF text, normalize deterministically, preserve page
  provenance, chunk with overlap, label every chunk untrusted, and detect a versioned
  indirect prompt-injection pattern set.
- Generate deterministic local hash embeddings for default/free behavior and store
  them in PostgreSQL `vector` columns beside a full-text index.
- Combine tenant/document-authorized lexical and vector candidates with reciprocal
  rank fusion, deterministic token-overlap reranking, bounded context assembly, and
  document/chunk/page citations.
- Add index-version metadata and an explicit re-index operation.
- Propagate an explicitly confirmed document deletion to raw local bytes, chunks,
  vectors, and retrieval results; keep the limitation of synchronous Phase 5
  approval visible until the durable Phase 8 approval workflow exists.
- Add a versioned synthetic retrieval dataset and thresholds for recall@k,
  precision@k, MRR, grounding, and citation correctness.

### Expected files and migrations

- Document/retrieval domain values and ports under `packages/core/`.
- Local storage/scanner/parser, deterministic embedder, RAG service, and PostgreSQL
  repository under `apps/api/`.
- Alembic revision `0002` enabling pgvector and adding documents/chunks/index fields.
- Authenticated upload, search, re-index, and confirmed-deletion API/UI flows.
- Unit/API/PostgreSQL/evaluation/injection/deletion/tenant-leakage test suites.
- ADR, annotated source, tutorial, exercises, security/privacy updates, traceability,
  and `docs/reviews/phase-05-review.md`.

### Architecture, dependency, security, privacy, and cost decisions

- PostgreSQL owns metadata, lexical search, and vectors; raw bytes stay behind an
  object-storage port. Local development uses `.data/documents`, which is ignored.
- `pgvector` (BSD-3-Clause) supplies SQLAlchemy/Psycopg vector types; `pypdf`
  (BSD-3-Clause) supplies bounded text extraction; `python-multipart` (Apache-2.0)
  enables FastAPI streaming multipart parsing. Direct custom vector encoding, a
  custom multipart parser, and PDF subprocess tooling are rejected as less mature.
- `UploadFile` is read with a 10 MiB plus one-byte bound; oversized inputs fail closed.
  PDF page/content-stream limits reduce, but cannot eliminate, parser/decompression
  risk. Scanner and parser isolation remain production hardening work.
- Deterministic embeddings are a tested local adapter, not a quality-equivalent
  production embedding model. No provider fallback or external disclosure occurs.
- Retrieved text is always untrusted data and never instruction. Injection matches
  label and constrain results rather than attempting to interpret them.
- Every retrieval SQL query includes tenant, owner/delegation, active document,
  and index-version predicates before ranking.
- Development uses synthetic fixtures. No cloud resource, paid API, model call, or
  recurring service is authorized or required.

### Risks and mitigations

- Parser bombs/exploits: strict byte/page/content-stream/output limits, quarantine,
  safe errors, pinned/scanned dependency, and no OCR/script execution.
- Tenant leakage: authorization before storage/retrieval plus predicates inside both
  lexical and vector candidate queries and hostile-ID integration tests.
- Retrieval quality illusion: versioned fixtures and numeric thresholds; disclose
  deterministic embedding limitations and empty results.
- Stale indexes: explicit component/index versions and transactional replacement.
- Deletion/object-store inconsistency: remove local bytes first, then transactionally
  delete derivatives; a metadata retry may be required if the DB step fails.
- Prompt injection: versioned detection corpus, untrusted labels, quoted context,
  and no agent/tool execution in this phase.

### Automated verification

- Ruff, strict MyPy, Pytest, OpenAPI, frontend format/lint/type/test/build.
- Alembic upgrade/downgrade/drift and real PostgreSQL/pgvector integration tests.
- Chunk/provenance, parser-limit, tenant leakage, hybrid retrieval, injection,
  re-index, deletion-propagation, empty-result, and evaluation-threshold tests.
- Dependency/secret/SAST scans, documentation/link/Mermaid checks, pre-commit,
  and complete diff review.

### Manual verification

- Start PostgreSQL, migrate, upload a synthetic text/PDF resume, inspect processing
  and citations, search known/unknown facts, upload injection text, re-index, confirm
  deletion, and verify the document disappears after API restart.

### Explicit exclusions

- OCR and searchable image content; image-to-text/model processing.
- Live/local neural embedding model downloads or external model calls.
- Generated answers, match/gap reasoning, LangGraph, agents, or tools.
- Cloud object storage, malware-engine service, sandbox/container isolation, RLS,
  unrestricted URL fetch, scraping, or external sources.
- Durable multi-state approval workflow, which remains Phase 8.

### Stop condition

Complete `docs/reviews/phase-05-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 5 AND START PHASE 6`

## Active implementation plan: Phase 4

**Objective:** replace process-local profile persistence with a versioned,
tenant-safe PostgreSQL profile and evidence-metadata foundation while keeping
development local, synthetic, and free.

### Scope and acceptance mapping

- Add versioned PostgreSQL migrations for profiles, skills, experience,
  education, evidence metadata, and deletion lifecycle fields.
- Define explicit repository transaction boundaries and tenant predicates.
- Support create/read/update profile operations with optimistic concurrency.
- Add evidence metadata intake with filename, media-type, and size validation;
  new evidence starts quarantined behind a malware-scanner port.
- Preserve the in-memory adapter for default unit/API tests and add opt-in real
  PostgreSQL migration, constraint, transaction, concurrency, and isolation tests.
- Extend the authenticated UI for profile editing and evidence registration.
- Map FR-001, FR-002, SEC-001, SEC-002, SEC-008, and NFR-019 to evidence.

### Expected files and migrations

- Richer domain models/services/ports under `packages/core/`.
- PostgreSQL tables, adapter, unit of work, and Alembic configuration under
  `apps/api/` and `migrations/`.
- Versioned profile/evidence HTTP contracts and authenticated web controls.
- Unit, API, contract, migration, PostgreSQL integration, upload-security,
  concurrency, transaction, and tenant-isolation tests.
- ADR, annotated source, tutorial, exercises, project records, and Phase 4 review.

### Architecture, dependency, security, and privacy decisions

- PostgreSQL is authoritative in configured environments; SQLite is not used as
  evidence for PostgreSQL behavior.
- SQLAlchemy 2 provides explicit transaction and mapping primitives, Psycopg 3
  is the PostgreSQL driver, and Alembic owns schema versions. All use permissive
  licenses. Direct SQL/custom migration runners were rejected because they add
  maintenance and recovery risk; an ORM does not replace authorization checks.
- The binary Psycopg distribution is convenient locally but bundles native
  libraries that must remain dependency-scanned and be reviewed for hardened
  production images.
- Every query includes tenant scope. IDs never authorize access by themselves.
- Stale profile versions fail atomically. Evidence metadata is minimized, and
  filenames are normalized before persistence. No raw bytes are retained in this
  phase; real object storage and scanner adapters remain later work.
- Soft-deletion timestamps and a default 30-day purge target establish lifecycle
  semantics; final retention periods and exceptions require legal review.

### Risks and mitigations

- The Docker daemon is unavailable: keep PostgreSQL tests opt-in, report them as
  blocked until a real server runs, and never substitute SQLite results.
- Schema/application drift: test Alembic head and metadata agreement plus a
  forward-recovery rehearsal.
- IDOR or tenant leaks: enforce policy in service/repository and test hostile IDs.
- Malicious uploads: accept bounded metadata only, use an allowlist, normalize
  names, quarantine by default, and expose a scanner interface with fail-closed
  behavior.
- Accidental overwrite: use integer versions in the update predicate and return a
  safe conflict response.
- Cost/cloud impact: none; no resource creation, billing, paid API, or model call.

### Automated verification

- Lock freshness; Ruff format/lint; strict MyPy; Pytest; API/OpenAPI contracts.
- Alembic upgrade/downgrade/forward-recovery and PostgreSQL repository tests when
  `CAREERPILOT_TEST_DATABASE_URL` points to an explicitly disposable database.
- Frontend format/lint/type/test/build; dependency, secret, and Semgrep scans.
- Documentation, Mermaid, pre-commit, migration review, and complete diff review.

### Manual verification

- Start PostgreSQL, apply migrations, start the app, create/edit a profile, add
  evidence metadata, reject an unsupported type, trigger a stale update, restart,
  and confirm persistence and tenant isolation.

### Explicit exclusions

- Parsing, object storage, embeddings, pgvector retrieval, and RAG (Phase 5).
- A real malware engine, cloud database, backups, deployment, or paid service.
- Destructive deletion UI without the later durable approval workflow.
- Model, agent, scraping, email, or automatic application behavior.

### Stop condition

Complete `docs/reviews/phase-04-review.md`, report all passed and blocked evidence,
and wait for:

`APPROVE PHASE 4 AND START PHASE 5`

## Completed plan: Phase 0

**Objective:** establish the complete product-discovery and architecture baseline
without production application code or cloud resources.

### Scope

- Product vision, personas, jobs-to-be-done, journeys, scope, metrics.
- Stable functional and non-functional requirements.
- Domain glossary and conceptual domain model.
- Architecture views, responsibility boundaries, and technology decisions.
- Agent-role classification and production-versus-lab separation.
- Initial STRIDE threat model, privacy assessment, risks, and cost assumptions.
- Durable repository governance, traceability, learning material, and review.

### Verification

- Run the Phase 0 document and requirement-ID validator.
- Run available Markdown and Mermaid checks without installing dependencies.
- Inspect links and the complete Git diff.
- Confirm no production application code or cloud resource exists.

### Exclusions

- Application or agent implementation.
- Dependency installation or workspace scaffolding.
- Database schemas or migrations.
- Cloud projects, APIs, billing, resources, deployments, or live-model calls.
- Phase 1 developer-environment remediation, including Docker Compose.

### Stop condition

Complete `docs/reviews/phase-00-review.md`, summarize the acceptance checklist,
and wait for:

`APPROVE PHASE 0 AND START PHASE 1`

## Completed implementation plan: Phase 1

**Objective:** create a reproducible, quality-gated repository foundation without
implementing product behavior.

### Scope and expected files

- Enforce Python 3.13 and Node.js 24 LTS through repository configuration.
- Create a `uv` workspace with an API shell and dependency-free core package.
- Create a Next.js/React/TypeScript web shell without a product journey.
- Add backend, frontend, services, packages, infrastructure, tests, labs, and
  documentation ownership structure.
- Pin runtime and development dependencies with committed lockfiles.
- Configure Ruff, strict MyPy, Pytest, pytest-asyncio, ESLint, Prettier, Vitest,
  pre-commit, detect-secrets, pip-audit, Semgrep, and repository secret scanning.
- Add Docker Compose syntax for local PostgreSQL/pgvector and document the missing
  local Compose plugin as a prerequisite issue.
- Add GitHub Actions quality gates and an architecture-boundary test.
- Add editor settings, tasks, `.env.example`, Makefile commands, setup tutorial,
  annotated source, exercises, answers, traceability, and the Phase 1 review.

### Architecture and security decisions

- The core package contains domain-safe primitives and cannot import frameworks,
  infrastructure, provider SDKs, or service code.
- The API depends inward on the core package; provider/service packages cannot be
  imported by core.
- Configuration examples contain names and safe local defaults only, never secrets.
- Default tests are offline and make no model or cloud calls.
- Dependency versions are exact in lockfiles; upgrades are intentional reviews.

### Risks and mitigations

- Installed runtimes differ from targets: use `uv`-managed Python 3.13 and enforce
  Node engines/version files; disclose any Node 26-only verification limitation.
- Docker Compose is missing: commit valid Compose configuration and a diagnostic,
  but do not mutate the owner's global Docker installation.
- Dependency downloads need public network access: use only official package
  registries and record licenses/security considerations.
- Tooling breadth can create noisy gates: pin configurations and distinguish
  mandatory failures from unavailable environmental integrations.

### Automated verification

- Python lock freshness, format, lint, strict typing, unit tests, architecture
  tests, dependency audit, Semgrep, and pre-commit.
- Frontend lockfile install, format, lint, type check, tests, and production build.
- Docker Compose config validation when the plugin is available; otherwise record
  the exact prerequisite failure.
- Secret scan, documentation validator, CI YAML parse/sanity checks, and Git diff
  review.

### Manual verification

- Follow macOS/VS Code setup from a clean-shell simulation.
- Confirm VS Code discovers Python, tests, formatting, and tasks.
- Run one aggregate quality command.
- Inspect directory ownership and local-service instructions.

### Exclusions

- Profile, job analysis, persistence adapters, API endpoints, or user journeys.
- Real authentication, model, agent, retrieval, or external service calls.
- Cloud resources, billing, deployment, or paid services.
- ADK/OpenAI agent scaffolding, deferred to their approved phases.

### Stop condition

Complete `docs/reviews/phase-01-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 1 AND START PHASE 2`

## Completed implementation plan: Phase 2

**Objective:** prove one deterministic, visible journey across the web, HTTP,
application, and temporary persistence boundaries without agents or live models.

### Scope and acceptance mapping

- Create a local professional profile from a display name and short summary.
- Submit a bounded, user-supplied job description.
- Return a deterministic placeholder match analysis and show it in the UI.
- Add versioned FastAPI contracts, application service, repository protocol,
  in-memory adapter, health/readiness, safe errors, and correlation IDs.
- Establish structured privacy-safe logs and OpenTelemetry propagation APIs.
- Add unit, API, contract, frontend accessibility-smoke, and end-to-end tests.
- Map FR-001, FR-003, NFR-002, NFR-010, NFR-011, and relevant security/privacy
  foundations to source and test evidence without claiming later-phase completion.

### Expected files

- Core domain/application modules under `packages/core/src/careerpilot_core/`.
- API contracts, adapters, telemetry, middleware, and app factory under
  `apps/api/src/careerpilot_api/`.
- UI form, API client, and tests under `apps/web/src/`.
- Phase 2 test suites under `tests/` plus updated CI and local commands.
- ADR/update notes, annotated source, tutorial, exercises, traceability, learning
  log, and `docs/reviews/phase-02-review.md`.

### Architecture, security, and privacy decisions

- Core stays framework-independent; adapters depend inward through a protocol.
- Analysis is a pure deterministic function with no provider fallback.
- Inputs have explicit length/content validation and synthetic examples.
- Logs and traces carry opaque correlation IDs and operation metadata, not profile
  or job-description content.
- API errors use a stable safe envelope and do not expose stack traces.
- The in-memory repository is process-local and its restart data loss is visible,
  tested, and documented; PostgreSQL remains Phase 4 work.

### Risks and mitigations

- Browser/API origin mismatch: configure one explicit local public API URL and
  narrowly scoped local CORS behavior.
- Contract drift: validate OpenAPI plus shared fixtures at API/client boundaries.
- False product claims: label output deterministic placeholder analysis and avoid
  inferred skills, rankings, or evidence claims.
- Personal-data leakage: use minimized fields, bounded inputs, synthetic tests,
  and metadata-only telemetry.
- Scope creep into identity/database/agents: keep those adapters absent and record
  the phase ownership in docs and tests.

### Automated verification

- Lock freshness; Python and frontend format, lint, and strict typing.
- Unit, API, contract, frontend, accessibility-smoke, and end-to-end tests.
- OpenAPI schema and structured error/correlation assertions.
- Production frontend build, security scans, dependency audits, docs/link/Mermaid
  checks, pre-commit, and full diff review.

### Manual verification

- Start API and web through one documented command.
- Enter synthetic profile and job data and observe the deterministic analysis.
- Confirm the correlation ID is visible.
- Trigger invalid input and inspect the understandable safe error.
- Restart the API and confirm the documented in-memory persistence limitation.

### Exclusions

- Real identity, tenants, authorization, audit ledger, or organization features.
- PostgreSQL application persistence, schemas, or migrations.
- LLMs, agents, retrieval, uploads, scraping, or external provider calls.
- Cloud resources, deployment, paid APIs, or non-synthetic customer data.

### Stop condition

Complete `docs/reviews/phase-02-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 2 AND START PHASE 3`

## Completed implementation plan: Phase 3

**Objective:** establish a multi-tenant, deny-by-default security foundation with
provider-neutral identity, layered authorization, and auditable access.

### Scope and acceptance mapping

- Model actors, personal/future organization tenants, memberships, roles,
  permissions, policy inputs/decisions, delegations, and audit events.
- Define an OIDC-compatible identity-verifier port and a local-only development
  session adapter using synthetic users and opaque process-local tokens.
- Derive tenant context from authenticated memberships and reject forged tenant
  selection.
- Enforce RBAC plus contextual ABAC at API, application, and repository layers.
- Add document/tool permission decisions now, with features remaining inactive.
- Add hash-chained append-only audit evidence and an authorized audit viewer.
- Cover SEC-001–SEC-005 and relevant NFR/API/audit requirements with source and
  test evidence while flagging production identity and legal retention review.

### Expected files

- Identity/access/audit domain modules and policy tests under `packages/core/`.
- Local identity/session, tenant-safe repository, audit adapter, request context,
  versioned contracts, and routes under `apps/api/`.
- Local user/tenant controls and audit viewer under `apps/web/`.
- Permission, cross-tenant, IDOR, deny-default, audit, and error-contract tests.
- ADR, threat/privacy updates, annotated source, tutorial, exercises, traceability,
  learning log, and `docs/reviews/phase-03-review.md`.

### Architecture, security, and privacy decisions

- Authentication proves an external subject; internal membership determines
  tenant context and authority.
- The client may request an active tenant ID but cannot assert membership, role,
  actor ID, or permissions.
- RBAC grants a candidate action; ABAC must also allow tenant, ownership,
  delegation, purpose, sensitivity, and resource state. Any missing rule denies.
- Personal tenants are active initially. Organization and coach types exist in
  the model but their product workflows remain disabled.
- Local sessions are random, process-local, non-cookie bearer tokens and are
  refused outside the `local` environment. They are not production credentials.
- Audit payloads exclude career content and use stable IDs/action/outcome/reason;
  events are append-only and SHA-256 hash-chained in this temporary adapter.
- Cross-tenant identifiers return a non-enumerating response while recording a
  security denial.

### Risks and mitigations

- Header spoofing: resolve every actor/tenant/role server-side from the session.
- IDOR: scope repositories by authorized context and test foreign identifiers.
- Role confusion: centralize permission mappings and exhaustively matrix-test.
- Policy bypass: require context at service/repository methods and retain API
  guards; architecture tests reject insecure signatures/import directions.
- Audit PII/tampering: allow-list metadata, pseudonymous IDs, hash chaining, and
  completeness/integrity tests; final retention needs professional legal review.
- Development auth misuse: local-only environment gate, loopback services,
  prominent UI/docs warning, and no password/OIDC-provider imitation.

### Automated verification

- Permission matrix and unrecognized-action deny tests.
- Authentication, membership, tenant-forgery, role-change, and error-contract tests.
- Cross-tenant read/write and IDOR tests at API, service, and repository layers.
- Audit success/denial/completeness/hash-integrity/viewer-authorization tests.
- Existing deterministic journey, OpenAPI, frontend, accessibility, build,
  security, dependency, documentation, and architecture gates.

### Manual verification

- Log in as synthetic users belonging to different personal tenants.
- Create data in each tenant and verify the other user cannot access it.
- Change a synthetic membership role and observe permission changes.
- Inspect correlated success and denial events in the audit viewer.
- Restart and confirm local sessions, data, and audit events are intentionally lost.

### Exclusions

- Google Identity Platform resource creation, live OIDC calls, passwords, MFA,
  email verification, account recovery, or production key management.
- Activated organization administration or coach delegation workflows.
- PostgreSQL schemas/migrations, durable sessions/audit, or production retention.
- Documents, retrieval, tools, models, agents, cloud resources, or paid services.

### Stop condition

Complete `docs/reviews/phase-03-review.md`, report exact evidence, and wait for:

`APPROVE PHASE 3 AND START PHASE 4`
