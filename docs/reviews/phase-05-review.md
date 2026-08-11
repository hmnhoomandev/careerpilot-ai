# Phase 05 Review: Secure Document Ingestion and RAG

## Objective and delivered outcome

Phase 5 delivers a free, local, evaluated RAG foundation: bounded text/PDF ingestion,
opaque local storage, deterministic chunking/embeddings, PostgreSQL full-text plus
pgvector retrieval, in-query tenant/owner filtering, deterministic reranking, citations,
injection labels, reindexing, and explicit deletion propagation. It returns evidence
passages, not generated answers.

## Security and privacy review

- Documents remain untrusted from upload through context assembly.
- Size, filename, extension, declared type, magic, UTF-8, page, stream, and extracted
  output limits fail closed; EICAR test content is rejected.
- Both retrieval SQL branches authorize tenant, owner, active state, and index version.
- Deletion requires explicit confirmation and removes bytes, chunks, and vectors.
- Tests and fixtures use synthetic data. No external model, cloud resource, paid call,
  secret, or unrestricted scraping was used.
- Production scanner/parser isolation, encryption/KMS, backup lifecycle, legal holds,
  recoverable deletion, and final GDPR/FADP retention interpretations remain open and
  require security/privacy work plus qualified legal review.

## Data and architecture impact

Alembic `0002` enables `vector`, adds tenant-scoped `documents` and
`document_chunks`, a generated English `tsvector`, GIN lexical index, HNSW cosine index,
and a composite evidence key. Downgrade is for disposable local/test databases only.
PostgreSQL remains authoritative; the process-local repository is a test/dev fake.

ADR-0017 records the local baseline and three dependencies. Important implementation
is explained in the Phase 5 annotated-source note. The API is version `0.5.0` and the
web page exposes upload, cited search, injection state, and confirmed deletion.

## Evaluation and verification

The versioned retrieval fixture gates recall@3, precision@3, MRR, grounding, and
citation correctness. A separate versioned corpus gates five suspected and three benign
injection examples. PostgreSQL integration proves migration, pgvector/full-text search,
cross-tenant non-disclosure, reindexing, and zero remaining chunks after deletion.

Final evidence: Python format/lint and strict MyPy passed; 101 Pytest tests passed
against real PostgreSQL/pgvector with zero skips; Alembic reported no drift; web
format/lint/type, 5 tests, and production build passed; Markdown lint/link checks,
8-diagram rendering, and governance validation passed; Python/npm vulnerability
audits found no known vulnerabilities; Semgrep, detect-secrets, and all five
pre-commit hooks passed. Owner browser walkthrough remains an acceptance action.

## Known limitations

- Deterministic hash vectors are an educational offline baseline, not neural semantic
  embeddings. There is no model-generated synthesis in Phase 5.
- OCR, JPEG/PNG content processing, Office/archive formats, crawling, and production
  antivirus are absent.
- PDF processing is in-process and bounded but not OS-sandboxed.
- Identity and audit storage remain local/process-bound; raw file storage is local disk.
- English full-text configuration is intentional for launch; per-locale configuration
  must accompany later internationalization.

## Owner acceptance checklist

- [ ] Upload a synthetic text/PDF resume and inspect its index status.
- [ ] Search for a known fact and inspect the cited passage/document/page/offsets.
- [ ] Search for a nonexistent fact and confirm no answer is fabricated.
- [ ] Upload a synthetic malicious instruction and observe `suspected`/`UNTRUSTED`.
- [ ] Confirm deletion and verify the passage no longer appears.
- [ ] Confirm no legal compliance certification or production scanner claim is made.

## Next phase gate

Stop here. Phase 6 may start only after:

`APPROVE PHASE 5 AND START PHASE 6`
