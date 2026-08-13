# Phase 8 Tutorial: Truth Before Fluency

A polished sentence is unsafe if its factual claim cannot be traced to evidence.
CareerPilot therefore models claims separately from prose. A supported claim links to
the exact document and chunk. Missing evidence does not become a fact.

Approval is version binding, not a generic yes/no flag. If version 1 is approved and
version 2 changes one sentence, version 2 needs a new approval. The content hash makes
the reviewed bytes explicit; the revision prevents two decisions racing successfully.

LangGraph interrupt pauses interaction and exposes a serializable review payload.
PostgreSQL stores the authoritative draft and decision so review survives API restart.
Temporal later adds durable schedules such as automatic expiry.

Run `make dev`, upload synthetic evidence, create a draft through `/api/v1/drafts`,
inspect each citation, edit only evidence-supported content, then decide the matching
approval. Try an invented number/date and observe a safe `422`; reuse an old revision
and observe `409`.
