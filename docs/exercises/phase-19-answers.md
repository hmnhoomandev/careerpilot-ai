# Phase 19 exercise answers

1. The stable idempotency key lets the ledger return the committed result on the second attempt.
2. Temporal history, DBOS checkpoints or the Restate journal own execution progress; the ledger owns the externally visible artifact record.
3. The new workflow invocation still supplies the old effect key, so the ledger replays the existing effect rather than creating another.
4. It would install comparison runtimes with production code, weaken isolation and allow accidental imports/routing.
5. At minimum: security/threat, privacy and retention, license/legal, residency/vendor, and operational cost/recovery reviews.
