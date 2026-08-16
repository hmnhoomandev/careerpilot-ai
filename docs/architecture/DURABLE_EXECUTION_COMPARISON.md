# Durable execution comparison

## Decision summary

Temporal remains CareerPilot's production durable-process owner. DBOS and Restate
are executable learning labs, not candidates silently routed by configuration.
All three demonstrate the important invariant: framework retries do not make an
external effect exactly once; the effect boundary still needs a stable
idempotency key.

## Equivalent scenario

The versioned fixture contains only synthetic opaque identifiers. A workflow asks
an effect ledger to record one application-preparation artifact. In the recovery
case the ledger commits the artifact and then raises once. The runtime re-enters
the effect, the ledger recognizes the idempotency key and returns the existing
artifact. Observable acceptance is two attempts, one unique effect, completed
status and a replay marker.

This is semantic equivalence, not framework equivalence. The Temporal test uses
an activity retry inside the existing multi-step workflow. DBOS uses a workflow
and retryable step. Restate uses a workflow handler and durable run.

## Practical comparison

| Dimension | Temporal (production choice) | DBOS lab | Restate lab |
|---|---|---|---|
| Programming model | Deterministic workflow plus separately registered activities, signals, queries and timers | Decorated Python workflow and steps in one application process | Service/workflow handlers use a context for durable runs, calls, state and timers |
| Durable state | Event history owned by Temporal; business records remain PostgreSQL-owned | Checkpoints workflow/step outputs in a system database; SQLite is test-only and PostgreSQL is the production recommendation | Restate server journals invocations and owns runtime state; SDK endpoint executes handlers |
| Retry and recovery | Activity retry policy, workflow-task replay and worker restart recovery; effects remain idempotent | Step retries are opt-in/bounded; interrupted workflow recovery reuses checkpoints | Durable runs retry by default and can be bounded; invocation journal replays completed actions |
| Observability | Mature workflow/event history, visibility APIs/UI and OpenTelemetry paths; content controls still required | Local logs and system tables; hosted Conductor is optional and not used here | Server/admin APIs/UI and tracing integration; local harness logs are ephemeral |
| Deployment | Separate server/cloud plus workers and task queues; already bounded in CareerPilot | Application plus reachable system PostgreSQL for a production design | Restate server cluster plus deployed SDK endpoints and registration/connectivity |
| Testing | Official time-skipping server, replay tooling and worker restart tests | Fast SQLite-backed tests in-process | Official Testcontainers harness is realistic but slower and requires Docker/image availability |
| Lock-in | Workflow history and SDK semantics require deliberate migration/versioning | Decorators/checkpoints and system schema bind code to DBOS runtime semantics | Journal/context/service protocols bind handlers to Restate; service registration is platform-specific |
| Maturity fit | Existing CareerPilot implementation and operational decision; broad long-running workflow feature set | Compact Python-centric model worth studying; less project evidence here than Temporal | Strong service-oriented durable execution concepts; less CareerPilot evidence and an additional server license boundary |
| Operational cost | Server/cloud, worker, persistence and on-call cost; no production cost is incurred in this phase | Potentially fewer runtime components but production PostgreSQL, monitoring, backup and ownership still cost money | Server cluster, storage, SDK endpoints, networking, backup and ownership; no hosted/public-service assumption |
| Phase 19 evidence | Existing activity and workflow integration tests | 2 framework tests pass against DBOS 2.22.0 and temporary SQLite | 2 framework tests pass against SDK 1.0.3 and pinned Restate 1.7.0 local server |

## Security, privacy, residency, and licensing

The labs accept no resume text, job text, evidence, model prompt, secret or real
identifier. If either engine were considered later, its history/journal/system
database would become personal-data infrastructure requiring tenant authorization,
retention/deletion mapping, encryption, backup/restore, pseudonymized telemetry,
Swiss/EU residency evidence and processor/subprocessor review.

DBOS and Restate Python SDKs are MIT licensed. The Restate server repository uses
the Business Source License 1.1 with an additional-use grant and an eventual
Apache 2.0 change license. The repository's internal product use may appear to fit
the grant, but that is an engineering reading only; professional license review
is a mandatory adoption gate.

## Primary references

- [DBOS workflow tutorial](https://docs.dbos.dev/python/tutorials/workflow-tutorial)
- [DBOS step retries](https://docs.dbos.dev/python/tutorials/step-tutorial)
- [DBOS local testing and SQLite](https://docs.dbos.dev/python/tutorials/testing)
- [DBOS Python package](https://pypi.org/project/dbos/)
- [Restate Python testing](https://docs.restate.dev/develop/python/testing)
- [Restate durable steps](https://docs.restate.dev/develop/python/durable-steps)
- [Restate error handling](https://docs.restate.dev/develop/python/error-handling)
- [Restate Python SDK](https://github.com/restatedev/sdk-python)
- [Restate server license](https://github.com/restatedev/restate/blob/main/LICENSE)

## Adoption gate

No comparison score automatically selects a runtime. A future proposal must start
from a production requirement Temporal cannot meet adequately, then include data
migration, in-flight workflow handling, failure domains, operations staffing,
security/license review, Zurich or documented EU placement, load/recovery evidence
and explicit cost and owner approval.
