# ADR-0017: Secure Local Hybrid Retrieval Baseline

- **Status:** Accepted for Phase 5
- **Date:** 2026-08-11

## Context

Phase 5 must teach and prove production retrieval semantics without external model
calls or paid infrastructure. Resumes are high-sensitivity, attacker-controlled
documents. Authorization applied after vector search would permit cross-tenant
candidate leakage.

## Decision

Accept UTF-8 text and text-based PDF only, capped at 10 MiB. Apply signature checks,
a deterministic local scanner, bounded parsing, normalized overlapping chunks, and
a versioned 64-dimensional deterministic hash embedding. The hash embedding is an
offline baseline, not a claim of neural semantic quality.

PostgreSQL stores lexical `tsvector` and pgvector indexes. Both candidate SQL queries
include tenant, owner, active-document, and index-version predicates before ranking.
Reciprocal-rank fusion plus lexical overlap reranks candidates. Returned passages
always carry document/chunk/page/offset citations and an `UNTRUSTED` context label.
No answer is generated and no provider fallback exists.

Raw bytes use a local object-storage adapter with server-derived paths and mode 0600.
Explicitly confirmed deletion removes bytes and chunk/vector derivatives while
soft-deleting provenance metadata. Revision `0002` owns schema changes.

## Dependencies

- `pgvector` (BSD-3-Clause) maps vector values in SQLAlchemy. Alternative: handwritten
  SQL; rejected because it increases type/adapter risk.
- `pypdf` (BSD-3-Clause) extracts text locally. Alternatives include PDFium and
  external parsing services; rejected for added native/cloud complexity and cost.
- `python-multipart` (Apache-2.0) supports FastAPI multipart upload parsing. The
  alternative is a custom multipart parser, which would increase security risk.

All stay within the CHF 0 local budget. Dependency and vulnerability checks remain
mandatory. No ADR changes the production PostgreSQL/pgvector decision.

## Consequences and limits

- Image OCR, archive/Office parsing, active-content sanitization, production malware
  scanning, parser process isolation, cloud object storage, encryption/KMS, backups,
  and recoverable deletion are not implemented.
- The local signature scanner is demonstrative and must not be described as an
  antivirus product.
- PDF extraction can be memory-intensive; current page, stream, byte, and output
  limits reduce but do not eliminate decompression risk. Production parsing needs a
  sandboxed worker with CPU/memory/time limits.
- Final retention and deletion rules require qualified legal review. No guaranteed
  GDPR or Swiss FADP compliance is claimed.
