# Phase 16 Review: Security Hardening and Adversarial Verification

## 1. Phase objective

Harden the local/API security and privacy posture and verify it with deterministic adversarial,
DAST, restore and supply-chain controls at CHF 0, without claiming legal compliance.

## 2. Delivered features

- Subject inventory, consent/withdrawal and access/correction/export/deletion request lifecycles.
- Minimized tenant-safe JSON profile/evidence export after step-up and exact approval reference.
- Thirty-day recoverable deletion, cancellation and purge-due tombstone semantics.
- Security headers, closed CSP, no-store, local identity rate limit and hashed request-path logs.
- Pre-connect HTTPS/host/DNS/IP SSRF policy and active-PDF upload rejection.
- Production TLS/managed-config/KMS/edge-limit gate plus provider-neutral KMS/rotation boundary.
- Integrity-checked isolated backup restore with tenant scope and deletion tombstones.
- Nine-case agent red-team corpus, local DAST, license gate and CI security steps.
- STRIDE control matrix and incident, key rotation and backup/restore runbooks.

## 3. Explicitly not delivered

No legal certification, production identity proofing, physical account purge, durable privacy
ledger, database RLS, cloud KMS/Secret Manager/WAF/scanner/backup, real fetch, customer data,
container/SBOM/IaC artifact, deployment, live/paid model, paid scanner or cloud resource.

## 4. Files created/changed

Core privacy/backup/key controls and exports; API privacy contracts/routes/security middleware and
scanner; OpenAPI, unit/API/e2e fixtures/tests; DAST/license scripts; CI/Makefile; ADR-0028, matrix,
runbooks, annotated source, tutorial/exercises and synchronized governance/security documents.

## 5. Architecture decisions

Rights are domain states while FastAPI reauthorizes identity/tenant. Consequential export/deletion
require step-up plus exact approval reference. Deletion is recoverable before purge. SSRF policy
runs before a socket. KMS is a port, not a core provider dependency. Scanners remain distinct.

## 6. Security/privacy review

Owner-only permissions and tenant/subject keys deny members/foreign IDs. Export is no-store and
excludes raw bytes, derivatives, audit and provider/workflow records. Logs hash paths. Final identity
verification, lawful basis, portability scope, legal holds, retention and breach notification are
`LEGAL REVIEW`. The local approval fields are interface demonstrations, not cryptographic proof.

## 7. Data/schema/migration impact

API version is 0.16.0 with five privacy paths. No database migration/dependency/lock change exists.
Privacy/rate state is process-local. Production durability/purge requires reviewed migrations.

## 8. Automated commands and exact results

- Ruff passed; strict MyPy passed 117 files.
- Full Pytest passed 227, skipped six and emitted four upstream ADK deprecation warnings. Four
  skips need configured PostgreSQL; two live-model tests lack explicit data/cost approval.
- Frontend Prettier/ESLint/TypeScript, ten Vitest tests and Next build passed.
- Local DAST passed three probes. License policy scanned 148 installed distributions.
- Detect-secrets passed. Semgrep ran three rules on 144 Python files with zero findings.
- Markdown lint passed 159 files; governance passed 24 required files, 74 IDs and 167 Markdown
  files; 13 Mermaid diagrams rendered.
- Pip/npm advisory audits were inconclusive because registry DNS failed. No dependency changed.
- Container/SBOM/IaC scans are not applicable until Phase 17 creates artifacts.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Inventory/export | Owner sees minimized no-store JSON | Automated pass; owner pending |
| Correction | Existing profile PATCH changes subject data | Regression pass; owner pending |
| Deletion/cancel | Thirty-day state then cancel | Automated pass; owner pending |
| Member/foreign request | Non-enumerating denial | Automated pass; owner pending |
| Headers/rate/SSRF | Secure headers, 429 and unsafe URL block | Automated pass; owner pending |
| Backup restore | Tampering fails; tombstone not restored | Automated pass; owner pending |
| Red-team corpus | All malicious cases block; benign allows | Automated pass; owner pending |

## 10. Requirements traceability

FR-016/017 and SEC-006/008–010/012/015–020 map to core controls, privacy API, scanner, CI,
red-team/DAST/restore tests and runbooks. Physical deletion and managed controls remain open.

## 11. Example requests/responses

`POST /api/v1/privacy/exports` accepts profile ID, step-up flag and `approval-*` reference. It
returns `careerpilot.portable-export.v1`, subject/tenant IDs, minimized profile/evidence metadata,
excluded categories and `legal_review_required: true`, with `Cache-Control: no-store`.

## 12. Known limitations, debt, and risks

- Client fields simulate step-up/approval; production must bind real IdP and durable approval.
- Privacy, consent, budget and rate state is process-local and not distributed or restart-safe.
- Recoverable deletion schedules purge work but does not physically purge all stores.
- Export omits several categories pending portable format, identity and legal review.
- Backup hash gives integrity detection, not authenticated encryption/provenance.
- No fetcher means SSRF connection pinning/redirect handling remains a production implementation.
- Scanner is deterministic, not a managed malware engine/sandbox.
- Advisory data was unavailable; registry checks must pass before release/dependency change.

## 13. Rollback/recovery instructions

Before Phase 17, revert the eventual Phase 16 commit. No migration/cloud rollback exists. Restart
clears privacy/rate state. Reapply the prior API 0.15 OpenAPI contract when reverting.

## 14. Learning summary

Security layers answer different questions. Deletion and restore must share tombstones. SSRF is
prevented before connection. Scanner classes are complementary. Engineering is not legal advice.

## 15. Owner acceptance checklist

- Create/edit a synthetic profile and perform the minimized export.
- Withdraw a consent, request deletion and cancel it within the recovery window.
- Try the privacy routes as Sam/Grace and inspect safe denial/audit entries.
- Run DAST, red-team, license and backup restore checks.
- Review residual risks, `LEGAL REVIEW` items and all three runbooks.

## 16. Proposed next phase

Phase 17 will create hardened containers, SBOM/provenance and reviewed IaC/deployment plans only
after the exact gate. It is not started; no infrastructure apply or paid resource is authorized.

## 17. Exact approval command

`APPROVE PHASE 16 AND START PHASE 17`
