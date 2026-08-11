# Phase 4 Exercise Answers

1. An opaque ID identifies a row; it grants no authority. Tenant scope must be an
   enforced query attribute even when an attacker cannot easily guess IDs.
2. Client B receives `409 profile_version_conflict`, refreshes version 5, reconciles
   changes, and retries intentionally.
3. Extensions and browser media types are attacker-controlled. Content scanning,
   parser isolation, and strict post-scan handling are still required.
4. Both statements run inside one transaction. The constraint exception exits the
   transaction context, which rolls back every statement including the version bump.
5. SQLite has different concurrency/locking, type, constraint, SQL, and migration
   semantics; passing SQLite tests would not prove PostgreSQL production behavior.
