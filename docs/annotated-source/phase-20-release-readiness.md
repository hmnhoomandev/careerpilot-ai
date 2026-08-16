# Annotated source: Phase 20 release readiness

`release_readiness.py` keeps promotion policy in the framework-neutral core. Targets say
whether higher/lower is better and whether local or production evidence is required.
Measurements carry only aggregate value, scope and sample count. Validation rejects empty,
duplicate, non-finite or zero-sample evidence. `evaluate_readiness` fails missing metrics,
checks scope before threshold and never upgrades local evidence to production. Report
properties deliberately expose separate local and production outcomes.

`nearest_rank_percentile` sorts a non-empty sample and selects the deterministic ceiling
rank. It is simple and reproducible for a regression harness; a production metrics backend
must define aggregation, sampling and histogram error separately.

`run_release_readiness.py` loads a versioned policy, warms an in-process FastAPI app,
measures concurrent liveness and sequential readiness traffic, then exercises a synthetic
tombstone-aware restore and unavailable provider route. It writes aggregate JSON under
ignored `.artifacts/`; inputs contain no career content and the provider cannot make a call.
The process exits nonzero only when local gates fail. Production gates remain failed in the
report, so successful local execution cannot authorize deployment.

Architecture tests bind `VERSION`, manifest and CI while proving publishing/deployment and
signature claims remain absent. Alternatives rejected were a benchmark-only Markdown claim
and a paid staging test: the former is not executable; the latter lacks cost/mutation approval.
