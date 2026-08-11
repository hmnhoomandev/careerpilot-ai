# Annotated Source: Phase 3 Security Foundation

## Authentication is not authorization

`IdentityVerifier` is the production-facing port: a future adapter verifies an
OIDC assertion and returns only stable issuer/subject identity. The core has no
Google or other provider import. `InMemoryIdentityAccess` is a separate local
adapter. It accepts only the `local` environment, uses synthetic named users, and
issues random tokens held until process restart.

Authentication middleware protects all `/api/v1/` paths except explicit local
session discovery/creation. It validates the bearer session and asks the adapter
for membership. The tenant header is a selection request, not authority: a forged
tenant fails because no membership can be resolved.

## RBAC plus ABAC

`ROLE_PERMISSIONS` is the auditable permission matrix. `AccessPolicy.decide`
first checks that matrix, then approved purpose. Resource operations must also
supply tenant, owner, delegation, sensitivity, and state. Any absent resource
context, foreign tenant, missing ownership/delegation, inactive state, restricted
delegated access, unknown role, or unknown permission denies.

Document and tool permissions already require an owned/delegated resource. Their
features are inactive, but tests prove they cannot default to allow later.

## Defense in depth

- API middleware authenticates and derives context before body validation.
- API routes select a server-known purpose and never accept actor/role permission.
- `CareerJourneyService` asks policy before behavior and audits outcomes.
- Profiles carry tenant and owner IDs.
- `InMemoryProfileRepository` requires context and rejects mismatched writes while
  returning no object for foreign reads.

The repeated checks address different bypass classes. They are not redundant.

## Audit evidence

`AuditEvent` is frozen and contains IDs, action, outcome, reason, correlation, and
optional resource reference—never profile/job content or token. The adapter
canonicalizes each draft, includes the previous event hash, and computes SHA-256.
Tests check event order, tenant filtering, success/denial completeness, and full
chain integrity.

The audit endpoint applies `audit.view` before filtering by the derived tenant.
Role changes require `membership.manage`, record the change, and cannot demote the
last owner of a personal workspace.

## Safe limitations

Tokens have no production expiry/refresh/revocation protocol and disappear only
on restart. Hash chaining is tamper-evident design evidence, not externally
anchored non-repudiation. Final audit/security retention and staff access require
professional legal and security review.
