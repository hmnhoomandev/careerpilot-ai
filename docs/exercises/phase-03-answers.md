# Phase 3 Exercise Answers

1. Authentication establishes actor identity; membership and policy authorize a
   tenant/action/resource. A token alone carries no trusted local role.
2. Middleware resolves the random token to an actor, looks up active membership
   for the requested tenant, reads its current role, selects a server-known
   purpose, and creates the context with the correlation ID.
3. RBAC asks whether the role has `analysis.run`. ABAC then requires an active
   same-tenant resource owned by or explicitly delegated to the actor.
4. Grace receives `profile_not_found` with 404. This avoids confirming a foreign
   object's existence while audit evidence records `profile_unavailable`.
5. Owner is a baseline capability, not ownership of every candidate's personal
   data. The resource owner or a future explicit delegation must match.
6. `test_document_and_tool_permissions_fail_closed_without_resource` checks both
   permissions and expects `resource_context_required`.
7. Chaining detects changed/reordered events when verifying the retained chain. It
   cannot stop an operator who can replace the entire in-memory log and recompute
   every hash; signing/external anchoring is absent.
8. The request returns `role_change_conflict` with 409 and records
   `last_owner_required`, preventing an ownerless personal tenant.
9. Signature, issuer, audience, token time bounds, and nonce/state where applicable;
   then map stable issuer/subject, not provider roles, into the application.
10. Live provider integration, keys, MFA, refresh/revocation, recovery, durable
    sessions/audit, retention, incident access, monitoring, and penetration tests.
