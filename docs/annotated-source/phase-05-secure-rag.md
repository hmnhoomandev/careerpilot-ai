# Annotated Source: Phase 5 Secure RAG

## Trust flow

`RagService.ingest` is the policy coordinator. It first loads an authorized profile,
then validates size/type/name, scans bytes, parses bounded content, labels suspected
indirect injection, stores bytes under an opaque key, and atomically persists evidence,
document, chunks, and vectors. If database persistence fails, stored bytes are removed.

`BoundedDocumentParser` never executes content. Text must be UTF-8. PDF extraction
preserves page numbers and has explicit page, content-stream, and total-output limits.
The local scanner checks declared type/magic, binary text, and the EICAR test marker;
it is a safe development adapter rather than production malware protection.

## Retrieval invariant

`PostgresDocumentRepository.hybrid_candidates` applies tenant, owner, active status,
and index version directly in both full-text and vector SQL. Filtering after retrieval
would be too late because foreign passages would already have crossed a data boundary.

`RagService.search` performs deterministic fusion/reranking and emits passages, never
a career claim or generated answer. Each passage includes a stable citation. Context
assembly marks every block `UNTRUSTED`, so later agents must treat document commands as
data. Suspected injection is visible rather than silently discarded.

## Lifecycle invariant

Parser, chunker, embedding, and index versions are stored with documents. Reindexing
replaces every derived chunk in one transaction. Confirmed deletion removes local raw
bytes first, then removes chunks/vectors and marks document/evidence provenance deleted.
Backup and 30-day recoverable deletion semantics remain a later production concern.
