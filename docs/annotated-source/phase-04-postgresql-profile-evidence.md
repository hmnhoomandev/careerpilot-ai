# Annotated Source: Phase 4 Persistence Boundary

## `careerpilot_api/database.py`

- The metadata block defines tenant-owned profile, child, and evidence tables.
  Composite tenant/profile foreign keys prevent a child row from attaching across
  tenant boundaries; repository predicates remain necessary because constraints
  do not decide actor authorization.
- `Transaction` wraps `Engine.begin()`: normal exit commits, and any exception
  rolls back the profile row plus every child-table change.
- `save` writes an aggregate once. `get` combines profile ID, tenant ID, and active
  state, so a hostile foreign ID produces absence rather than disclosure.
- `update` includes `version = expected_version` in the SQL predicate. A zero-row
  result becomes a domain-neutral stale-version error; child constraint failures
  roll back the already-issued version update.
- `_replace_children` is simple and correct for bounded profile collections. A
  differential update was rejected for now because it adds identity/order rules
  without product value.
- Evidence methods store metadata only and filter deleted rows. Raw bytes cannot
  accidentally be parsed or treated as clean because they never enter this path.

Failures include unavailable PostgreSQL, migration drift, constraint violations,
stale writes, and tenant mismatch. Offline tests cover policy and validation; the
marked PostgreSQL test covers migrations, reconnect persistence, rollback,
concurrency, and isolation against the actual production database family.

## `careerpilot_core/services.py`

The application service loads an authorized resource before update/evidence work.
It transforms validated input into immutable domain values, converts adapter-level
stale-write evidence to `ProfileConflictError`, and emits allowed/denied audit facts.
Filename normalization uses `PurePath` only to extract a safe basename; media type,
extension, and size are separately allowlisted because no one signal proves safety.
