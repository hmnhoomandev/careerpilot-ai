# ADR-0015: Local Identity, Policy, and Audit Foundation

- **Status:** Accepted for Phase 3
- **Date:** 2026-08-10

## Context

The deterministic journey needs identity and tenant isolation before durable or
broader user data is added. The CHF 0 development policy forbids creating a paid
identity service, and provider-specific identity must remain outside the domain.

## Decision

- Core defines an `IdentityVerifier` protocol returning issuer/subject only. A
  production OIDC adapter must validate signature, issuer, audience, time, and
  nonce where applicable before returning that value.
- Local development uses three synthetic actors and random process-local bearer
  sessions. Construction fails unless the environment is exactly `local`.
- Active tenant and role derive from server-side membership. Client actor, role,
  and permission claims are ignored.
- RBAC grants candidate permissions. ABAC additionally checks purpose, tenant,
  ownership/delegation, sensitivity, and resource state. Missing context denies.
- Personal workspaces are active. Organization and coach types exist in the
  domain but are not activated as product workflows.
- Security events are append-only values linked by SHA-256 hashes. Tenant audit
  views are permission-checked and filtered.
- Profile repository operations require authorization context and enforce tenant
  matching independently from API and service checks.

## Consequences

Two local users cannot cross tenant boundaries, same-tenant members cannot access
one another's owned profile without delegation, and document/tool permissions
fail closed before those features exist. Audit hashing detects accidental or
unsophisticated mutation but is not a signature or external immutable ledger; an
operator controlling memory could rewrite the full chain. PostgreSQL durability,
retention, cryptographic anchoring, production sessions, MFA, and incident access
belong to later phases.

## Rejected alternatives

- Trusting tenant/role headers would permit spoofing.
- Implementing passwords would create credential storage and recovery scope while
  teaching the wrong production boundary.
- Connecting Google Identity Platform now would create cloud/cost/configuration
  state before deployment approval.
- Role-only policy would allow coach/admin overreach and weak resource ownership.
