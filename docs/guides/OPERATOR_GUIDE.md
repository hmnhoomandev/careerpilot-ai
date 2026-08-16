# Operator guide

## Operating boundary

CareerPilot 0.20.0-rc.1 is local-only and production `NO-GO`. This guide describes the
intended operating model and safe local rehearsals; it does not authorize cloud mutation.

## Local start and health

Use `docker compose config`, then `docker compose --profile specialists --profile durable
up --build` when Docker is available. Apply migrations before application rollout. Check
`/health/live` for process liveness and `/health/ready` for readiness. Use metadata-only
logs/correlation IDs and never paste career content into incident systems.

Run `make release-readiness` to write ignored `.artifacts/release-readiness.json`. A zero
exit means local gates passed; inspect `decision`, which remains `no_go_production` while
production measurements are absent. Then follow `release/RELEASE_CHECKLIST.md`.

## Routine operations

- Watch availability, p50/p95/p99 latency, completion/recovery, errors, explicit provider
  failures, retrieval quality, cost/workflow, queues, database connections and backup age.
- Stop promotion on security/privacy/integrity failure or error-budget exhaustion.
- Migrate once with the dedicated identity before workload rollout; use forward recovery.
- Roll back compute only to a verified digest. Never roll application code behind an
  incompatible schema without an approved recovery path.
- Reconcile deletion tombstones during restore and reauthorize every replay or recovery.

## Incidents and recovery

Use `SUPPORT_AND_ON_CALL.md`, `INCIDENT_AND_DATA_BREACH.md`,
`DEPLOYMENT_ROLLBACK_AND_MIGRATION.md`, and `BACKUP_RESTORE_AND_DELETION.md`. Disable
affected traffic/action/provider, preserve minimal evidence, revoke access where required,
communicate verified facts, recover in isolation and validate tenant boundaries before reopen.

Production setup must replace local identity/fakes, activate trusted workload identity,
managed secrets/KMS, private database access, monitored backups, alerts and approved support.
