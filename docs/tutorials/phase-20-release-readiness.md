# Phase 20 tutorial: evidence-based release decisions

A release gate answers two questions: did a measured value meet its threshold, and was
the measurement taken in the environment the target describes? A 35 ms in-process health
response can catch a regression but says nothing about Cloud Run cold starts, TLS, Cloud
SQL, real retrieval or provider latency. Scope is therefore a first-class field.

Run `make release-readiness`, then inspect `.artifacts/release-readiness.json`. Local gates
cover 400 requests at concurrency 16, a 1,000-request bounded soak, restore isolation,
provider-outage visibility and zero default cost. Production targets have no measurement
and fail closed. The script exits zero because local gates pass, while the report decision
remains `no_go_production`; these statements are compatible.

Read the SLO and capacity documents. An SLI is a measurement; an SLO is the target over a
window; the error budget is tolerated unreliability. A test threshold is not an SLO because
it lacks production population, window and operational response. Similarly, a backup file
is not recovery evidence until a restore validates integrity, authorization, deletion and
actual RPO/RTO.

Finish at the release checklist and go/no-go report. A trustworthy release report includes
failed and missing evidence. The unsigned candidate can move to an explicitly approved
staging validation, but cannot be deployed to customers through implication or CI success.
