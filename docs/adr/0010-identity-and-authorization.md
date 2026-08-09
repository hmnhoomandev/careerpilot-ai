# ADR-0010: OIDC Boundary with RBAC and ABAC

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

Authenticate through a standards-based OIDC port. Use a safe local development
adapter and Google Identity Platform as the initial production reference. Combine
RBAC baseline permissions with ABAC using tenant, ownership, delegation, purpose,
sensitivity, action, and resource state. Deny by default.

## Consequences

Provider subjects map to internal actors; domain code never imports provider SDKs.
Authorization is enforced at every boundary and tested for cross-tenant access.
