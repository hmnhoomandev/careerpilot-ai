# Phase 3 Review

## 1. Objective

Add provider-neutral identity, personal-tenant isolation, deny-by-default RBAC/
ABAC, layered enforcement, and auditable access around the deterministic journey
without cloud identity, real credentials, paid services, or non-synthetic data.

## 2. Delivered behavior

- Synthetic local login for Ada, Grace, and Sam using random process-local tokens.
- Two isolated personal tenants; future organization/coach types remain modeled
  but inactive.
- Server-derived actor, membership, role, tenant, purpose, and correlation context.
- Owner/member/coach/organization-admin role and permission model.
- Resource ABAC for tenant, ownership, delegation, purpose, sensitivity, and state.
- Protected profile/analysis APIs, role-management API, current-context API, and
  owner-authorized tenant audit viewer.
- Hash-chained append-only audit events for authentication, context, business
  success/denial, policy decisions, role changes, and audit access.
- UI for local identity selection, authorized comparison, Sam promotion, safe
  denial display, and tenant audit events.

## 3. Architecture decisions

ADR-0015 implements ADR-0010's provider boundary. Core owns `IdentityVerifier`,
`ExternalIdentity`, actor/tenant/membership/value types, the role matrix, policy,
resource attributes, and audit contracts. No provider SDK enters core.

The browser requests a tenant but never supplies trusted actor, role, or
permission. Authentication middleware resolves the token and current membership
before request-body validation. API routes select purpose; services run policy;
repositories require context and scope by tenant. Document and tool permissions
fail closed now although those features remain inactive.

## 4. Authentication review

The local adapter constructs only when the environment is exactly `local`. It has
no password, email, provider emulation, cookie, persistence, refresh, or recovery.
Tokens use cryptographic randomness, receive `Cache-Control: no-store`, remain in
browser component memory, and disappear at API restart.

This is not production authentication. The production port documents required
OIDC signature, issuer, audience, time, and nonce/state verification; Google
Identity Platform remains only the approved future reference.

## 5. Authorization and tenant-isolation review

RBAC must grant the permission before ABAC evaluates resource context. Resource
operations deny missing context, foreign tenants, inactive state, missing owner/
delegation, and restricted delegated access. Unknown combinations deny.

Observed protections include:

- Missing authentication returns safe 401 before body validation.
- Forged tenant selection returns safe 403.
- Grace using Ada's profile ID receives non-enumerating 404.
- Ada cannot use owner role to access Sam's same-tenant owned profile.
- Members cannot view audit or manage roles.
- Document/tool access denies without owned/delegated resource context.
- A personal tenant's final owner cannot demote themselves; safe 409 is audited.

## 6. Audit, privacy, and legal review

Events contain pseudonymous IDs, action, outcome, reason, correlation, resource
reference, time, and hashes. They exclude token, display name, summary, job text,
result content, and error internals. Tenant views are policy-protected and filtered.

SHA-256 chaining detects retained-chain modification/reordering but is not a
signature or external immutable ledger. A privileged process could replace and
recompute all in-memory events. Durable storage, restricted operator access,
signing/anchoring, retention, deletion exceptions, legal holds, and data-subject
verification remain later work and professional legal review under LEG-001,
LEG-002, LEG-004, and LEG-006. No compliance certification is claimed.

## 7. Data, migration, recovery, deployment, and cost

Tenant/owner fields were added to in-memory Phase 2 values and contracts only.
There is no database schema or migration. Restart clears sessions, role changes,
profiles, and audit events; this limitation is tested and documented. No cloud
resource, identity provider, deployment, model call, or paid service was used.
Cost remains CHF 0.

## 8. Automated verification

| Gate | Exact result |
|---|---|
| uv lock | 116 packages resolved; unchanged and current |
| Ruff | 112 files format-clean; lint passed |
| strict MyPy | No issues in 37 source files |
| Pytest | 61 passed |
| Permission matrix | 32 role/permission combinations plus ABAC cases passed |
| Tenant/IDOR | Forgery, foreign tenant, same-tenant ownership, service and repository tests passed |
| Authentication/error contracts | 401, 403, non-enumerating 404, and last-owner 409 passed |
| Audit | Success/denial completeness, filtering, viewer roles, and chain integrity passed |
| Vitest/axe | 1 file, 3 tests passed; initial login view had no automatic violations (color contrast excluded in jsdom) |
| Next build | Passed; static `/` and `/_not-found` generated |
| pip-audit | No known vulnerabilities; two internal non-PyPI packages skipped |
| npm audits | Web and documentation tools: 0 vulnerabilities |
| Semgrep | 3 rules on 37 Python targets; 0 findings |
| detect-secrets | Passed for tracked and untracked non-ignored files |

Semgrep emitted its previously documented macOS signal-handler warning and still
completed successfully. No new dependency was added in Phase 3.

## 9. Real localhost verification

`make dev` started both loopback services. Exact observed results:

- Web root: HTTP 200.
- Grace submitted Ada's profile ID: HTTP 404, `profile_not_found`.
- Sam audit view before promotion: HTTP 403, `access_denied`.
- Ada promoted Sam: HTTP 200.
- The existing Sam session then viewed 11 tenant events, proving roles are resolved
  from current server membership rather than embedded token claims.
- Logs showed path/status/duration/correlation metadata without tokens or career
  content. Control-C stopped both processes cleanly.

## 10. Failures and corrections

- The first mechanical export patch placed new core exports outside `__all__`; the
  malformed file was detected immediately by inspection and replaced completely.
- A repository type-checking import lost indentation; Ruff parser failure stopped
  the gate before execution and the indentation was corrected.
- Static checks required explicit complexity exceptions for the composition root
  and audit helper; these are limited to named files and documented here rather
  than weakening repository-wide rules.
- Existing Phase 2 tests failed strict typing after authorization context became
  mandatory. Their fakes and calls were upgraded; no compatibility bypass or
  optional context was added.
- One service test expected three success events although only profile creation
  and completed analysis are recorded. The assertion was corrected to two.
- The last-owner 409 was initially attached to the wrong OpenAPI route during a
  broad text patch; inspection moved it to membership role changes.
- Documentation lint found two older high-risk privacy bullets displaced by the
  Phase 3 note; they were restored to their original list.

## 11. Manual owner checklist

| Check | Actual result |
|---|---|
| Log in as users in separate tenants | Pass via localhost API; visual owner check pending |
| Confirm cross-tenant read denial | Pass: 404 non-enumerating response |
| Observe member versus owner permission | Pass: Sam 403 before promotion, 200 after |
| Inspect success and denial audit events | Pass: 11 tenant events returned; visual owner check pending |
| Restart and understand all temporary-state loss | Automated/documented; owner walkthrough pending |

## 12. Traceability and learning

SEC-001 through SEC-005 and relevant NFR contract/operational requirements map to
specific source and tests in the traceability table. The annotated source,
tutorial, exercises, and answers teach identity versus authorization, tenant
derivation, RBAC/ABAC, IDOR, layered checks, audit integrity, and limitations.

## 13. Known limitations and debt

- No live OIDC provider validation, production sessions, MFA, recovery, or revocation.
- Organization administration and coach delegation are inactive.
- All state and audit evidence are in memory and disappear at restart.
- The hash chain has no signature, restricted external store, or anchor.
- No PostgreSQL query-policy integration exists until Phase 4.
- No production rate limiting, security monitoring, DAST, or penetration test yet.
- Browser-network automation remains composite rather than a full real-browser test.

## 14. Rollback

No external state needs rollback. Before acceptance, Phase 3 consists of local
uncommitted repository changes. Preserve any desired review, identify exact paths
with Git, and obtain owner confirmation before destructive removal.

## 15. Owner acceptance checklist

- [ ] Local authentication is clearly distinguished from production OIDC.
- [ ] Tenant context is server-derived and cannot be asserted by the browser.
- [ ] RBAC, ABAC, ownership, delegation, and deny-default behavior are understood.
- [ ] Cross-tenant, IDOR, audit, and last-owner results are adequate.
- [ ] Temporary audit limitations and legal-review requirements are accepted.
- [ ] Phase 4 remains focused on PostgreSQL, migrations, profiles, and evidence.

## 16. Proposed next phase

Phase 4 — PostgreSQL, migrations, profile, and evidence library. It will replace
temporary profile persistence with tenant-safe production semantics and add
versioned schema/migration evidence without weakening Phase 3 authorization.

## 17. Exact approval command

`APPROVE PHASE 3 AND START PHASE 4`
