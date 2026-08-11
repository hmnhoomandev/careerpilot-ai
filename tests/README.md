# Tests

- `unit/` verifies deterministic units and package discovery.
- `architecture/` enforces dependency direction.
- `api/`, `contract/`, and `e2e/` cover authenticated HTTP and full local slices.
- `integration/` uses real PostgreSQL only when
  `CAREERPILOT_TEST_DATABASE_URL` names an explicitly disposable database.
- Later phases add retrieval, agent, security, evaluation, and performance suites.

Default tests are offline and use synthetic data and fake providers.
CI supplies a PostgreSQL 17/pgvector service so production semantics cannot be
silently skipped there.
