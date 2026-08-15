# Phase 16 Security Control Matrix

This is an engineering control map, not legal advice or certification. `LEGAL REVIEW` means a
qualified Swiss/EU professional must decide the production requirement.

| Boundary/threat | STRIDE | Prevent | Detect/test | Respond/recover | Residual risk |
|---|---|---|---|---|---|
| Browser/API spoofing | S | OIDC boundary, local-only dev auth, step-up contract | auth/forged-header DAST | revoke session, inspect audit | Production MFA/IdP policy |
| Tenant/object tampering | T/E | deny-default RBAC+ABAC, tenant predicates | IDOR/cross-tenant corpus | deny, audit, incident triage | DB RLS is not active |
| Action repudiation | R | exact approval and metadata audit | audit-chain tests | preserve scoped evidence | Durable/WORM audit later |
| API/content disclosure | I | no-store, CSP, redaction, safe errors | header/secret/hostile-path tests | revoke access, breach runbook | Browser extensions/endpoints |
| API/agent exhaustion | D | bounded input, local quota/rate/budget | rate and denial-of-wallet tests | 429/cancel/provider block | Distributed edge abuse |
| Prompt/tool elevation | E | untrusted labels, schemas, authorization, approval | red-team injection/tool corpus | block and audit | Novel semantic attacks |
| Upload/parser compromise | T/D/E | quarantine, signature/type/active-PDF/size limits | EICAR, active PDF, parser bomb tests | reject, retain safe reason | Real scanner/sandbox later |
| Outbound SSRF | S/I/E | no generic fetch; HTTPS/host/DNS/IP policy | loopback/link-local/credential tests | block before socket | DNS pinning/egress later |
| Export disclosure | I | subject/tenant scope, step-up, exact approval, minimized manifest | member/cross-tenant tests | expire/revoke export | Identity proofing `LEGAL REVIEW` |
| Incomplete deletion | I/T | recovery tombstone, derivative plan, purge-due state | lifecycle/restore tests | retry purge, tombstone restore | Durable multi-store ledger later |
| Backup reactivation | I/T | integrity hash, isolated tenant restore, tombstones | tamper/tenant/deleted record tests | abort restore | Cloud encryption/rotation later |
| Secret/key compromise | S/I/E | external config, KMS port, versioned rotation | config/rotation policy tests | rotate/revoke/re-encrypt | Cloud IAM/HSM later |
| Dependency compromise | T/E | lockfiles, pinned actions/tools | SCA/SAST/secrets/license gates | block release, upgrade/revert | Registry compromise |
| Bias/protected trait use | I/E | truthful evidence, bias flags, human review | draft/adversarial fixtures | block/edit/review | Employment AI law `LEGAL REVIEW` |
| Incident mishandling | R/I | roles, minimized evidence, runbooks | tabletop checklist | contain/investigate/notify | Notification duties `LEGAL REVIEW` |

## Severity and release policy

- Critical/high exploitable findings block release until resolved or the release is explicitly
  stopped; risk acceptance cannot silently downgrade severity.
- Medium findings need an owner, deadline and tested mitigation. Low findings remain tracked.
- Secret findings block immediately. Unknown dependency licenses require explicit review.
- SAST, SCA, DAST, secrets, licenses and red-team gates run in CI. Phase 17 container/SBOM/IaC
  scans are **not applicable** until those artifacts exist; absence is not a passing scan.
