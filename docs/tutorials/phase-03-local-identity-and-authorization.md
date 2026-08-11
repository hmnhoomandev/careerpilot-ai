# Tutorial: Local Identity, Tenant Isolation, and Audit

## Safety boundary

Use synthetic data only. Ada, Grace, and Sam are fixed fictional users. The local
session adapter is not a password system or production OIDC implementation and
will refuse to initialize outside `CAREERPILOT_ENVIRONMENT=local`.

## Start

```sh
make dev
```

Open `http://127.0.0.1:3000`.

## Observe roles and tenants

- Ada owns Ada's personal workspace.
- Grace owns Grace's separate personal workspace.
- Sam is initially a member of Ada's workspace.

Choose Ada and start a local session. The session bar displays the actor, tenant,
and server-derived role. Run the comparison, then select **View tenant audit
events**. Authentication, context, profile, analysis, and audit-view events are
visible without submitted career text.

Clear the session and enter as Sam. Audit viewing returns a safe denial because a
member lacks `audit.view`. Enter as Ada, select **Promote Sam to owner**, then
start a fresh Sam session and view the audit. The permission now succeeds and the
denial, role change, and success are all visible.

## Verify isolation

The automated test creates a profile as Ada and submits its identifier as Grace.
Grace receives the same safe 404 used for an unavailable profile, so the API does
not confirm that a foreign identifier exists. A tenant-scoped denial event is
recorded. Another test proves Ada cannot access Sam's owned profile merely because
Ada is an owner; ownership or explicit future delegation is still required.

## Inspect contracts

Open `http://127.0.0.1:8000/docs`. Protected endpoints require:

```text
Authorization: Bearer <opaque local token>
X-CareerPilot-Tenant-ID: <selected membership tenant>
```

Never treat the tenant header as proof. The server validates it against the
token's actor and current membership.

## Restart behavior

Control-C stops both processes. Restarting clears sessions, profiles, role changes,
and audit events. Phase 4 adds durable application data; later security phases own
production session and audit retention.
