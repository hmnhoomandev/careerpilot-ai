# Tutorial: Secure Document Retrieval

## Mental model

A resume is evidence and attacker-controlled input at the same time. Its text can
support a claim, but a sentence such as “ignore previous instructions” must never gain
authority. CareerPilot therefore returns cited passages as untrusted data; Phase 5 does
not ask a model to answer from them.

Hybrid retrieval combines two views: PostgreSQL full-text search finds exact words,
while pgvector compares the local baseline vectors. Reciprocal-rank fusion combines
ranks without assuming their scores share a scale. Authorization lives inside both
queries.

## Local walkthrough

1. Use only synthetic text or text-based PDF evidence.
2. Start the local PostgreSQL container, apply Alembic head, and start API/web.
3. Sign in as Ada, create the synthetic profile, then upload a `.txt` file in the
   “Index and search documents” panel.
4. Search for a fact present in the file. Inspect document, filename, page, offsets,
   chunk ID, and injection label.
5. Search for an unrelated fact. An empty passage list is the correct result; the
   system does not invent an answer.
6. Upload a synthetic file containing “ignore all previous instructions.” The file is
   indexed as evidence but visibly labeled `suspected` and remains untrusted.
7. Press Delete, approve the browser confirmation, and repeat the search. No passage
   from the deleted document should remain.

The deterministic hash embedding is free and reproducible, but it is not production
semantic retrieval. Do not use real personal data in this development environment.
