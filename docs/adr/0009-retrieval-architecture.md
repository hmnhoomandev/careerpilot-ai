# ADR-0009: Hybrid, Cited, Evaluated Retrieval

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

Use parsing, normalized chunks, lexical and pgvector retrieval, mandatory tenant
and document authorization, optional reranking, bounded context assembly, and
citations. Index versions and provenance are first-class. Retrieved content is
always labeled untrusted.

## Consequences

Quality is gated by versioned datasets and recall, precision, MRR, grounding, and
citation metrics. Deletion and correction propagate to every derivative.
