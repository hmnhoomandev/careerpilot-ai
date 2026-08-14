# Phase 12 exercise answers

1. Models involve I/O, nondeterminism, cost and provider policy; activities isolate those
   concerns while workflow history records only their result reference.
2. An activity may commit externally and fail before acknowledging completion. A stable
   idempotency key makes the retry reuse the committed effect.
3. A stopped worker is recoverable infrastructure loss; cancellation requests termination;
   compensation is a new semantic effect that reverses prior effects where possible.
4. It rejects stale or cross-actor decisions. The gateway must additionally authenticate,
   authorize and verify the authoritative approval record before signalling.
5. Put a patch marker around the command-shape change and replay a captured pre-change
   history against the new worker before deployment.
6. History proves process commands and state. PostgreSQL business records and cited
   evidence remain authoritative for qualifications, drafts, approvals and applications.
