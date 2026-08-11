# Tutorial: PostgreSQL Profiles, Transactions, and Quarantine

## Mental model

A profile is an aggregate: its main row, skills, experience, and education should
change as one unit. A PostgreSQL transaction gives the all-or-nothing guarantee.
Optimistic concurrency adds a second guarantee: a browser holding version 1 cannot
overwrite a profile already saved as version 2.

Evidence has a trust lifecycle. A filename and browser media type are untrusted
hints. Phase 4 validates and stores only metadata, strips path components, and
uses `quarantined`. Phase 5 may store and parse bytes only after scanner and
document-security boundaries are connected.

## Local walkthrough

1. Put a synthetic local password and database URLs in ignored `.env`.
2. Export that file into the current shell, run `make db-up`, then
   `make db-migrate`.
3. Run `make db-integration-test`; the URL must point to a disposable local DB.
4. Start `make dev`, sign in as Ada, and run the synthetic comparison.
5. Edit skills and save. The visible profile version increments.
6. Choose a small synthetic PDF. Only its name/type/size are sent; the UI shows
   `quarantined`.
7. Try an executable or renamed PNG-as-PDF fixture and observe safe rejection.

Do not use a real resume or certificate in development. The current local password,
session adapter, audit log, and database topology are not production-ready.
