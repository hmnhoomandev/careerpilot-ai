# Annotated Source: Phase 8 Truthful Drafts and Approval

`drafting.py` defines immutable claim/draft/approval values. `hash_content` canonicalizes
reviewed content; `decide` and `expire` reject stale revisions, mismatched versions or
hashes, terminal-state reuse, and missing feedback.

`draft_service.py` retrieves only authorized profile/evidence, converts cited passages
to supported claims, runs PII/bias policy, stores version 1 plus pending approval, and
creates a fresh approval for each edit. An edit must be contained in existing supported
claim text; invented dates, employers, qualifications, or metrics fail closed.

`draft_repository.py` provides the default fake and PostgreSQL adapter. PostgreSQL
queries include tenant/owner predicates; immutable versions insert once; approval
updates compare the expected revision atomically.

`approval_graph.py` calls LangGraph `interrupt` with JSON-serializable ID/version/hash
and an allowlisted decision set. Resume uses `Command`; approval authorization still
belongs to the deterministic service and durable repository.

`draft_contracts.py` rejects unknown input. A2UI messages allow only two components and
five actions, contain presentation data, and grant no authority. `main.py` maps safe
404/409/422 errors and excludes draft content from logs/audit.
