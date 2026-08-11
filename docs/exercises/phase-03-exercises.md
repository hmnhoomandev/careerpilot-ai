# Phase 3 Exercises

1. Explain why a valid session token does not authorize every tenant.
2. Trace how a tenant ID becomes an `AuthorizationContext` without trusting the
   browser's role or actor claims.
3. Compare the RBAC and ABAC decisions for `analysis.run`.
4. Predict the response when Grace submits Ada's profile ID and explain why 404 is
   preferable to a detailed authorization error there.
5. Explain why Ada cannot analyze Sam's same-tenant profile by role alone.
6. Find the tests proving documents and tools deny without resource context.
7. Explain what the audit hash chain can and cannot prove.
8. Try to demote Ada before another owner exists. Explain the 409 response.
9. Identify what a production OIDC adapter must verify before returning an
   `ExternalIdentity`.
10. List the security work intentionally deferred from the local adapter.
