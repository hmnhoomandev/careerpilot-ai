# Phase 19 review — complete

## 1. Phase objective

Compare DBOS and Restate practically against CareerPilot's existing Temporal
durable workflow without changing production architecture, routing or cost.

## 2. Delivered features

- Separately locked DBOS 2.22.0 and Restate SDK 1.0.3 projects outside the root workspace.
- One shared synthetic preparation-effect contract with happy and failure-after-commit cases.
- Real DBOS SQLite and official Restate 1.7.0 harness tests proving two recovery attempts create one effect.
- Root architecture tests proving lab dependencies and imports cannot enter production.
- ADR-0031, a nine-dimension comparison, primary references, annotated source, tutorial and exercises.
- Synchronized dependency/license, risk, cost, traceability, decision, learning, roadmap and state records.

## 3. Explicitly not delivered

No production adoption, API route, schema/migration, cloud resource, deployment,
hosted console, real personal data, model call, external communication, billing or
paid service exists. Phase 20 has not started.

## 4. Files created/changed

Primary additions are `labs/dbos`, `labs/restate`, the shared fixture,
`test_durable_lab_isolation.py`, ADR-0031 and
`DURABLE_EXECUTION_COMPARISON.md`, with phase learning and governance records.

## 5. Architecture decisions

Temporal remains the only production durable-workflow engine. Both alternatives
remain comparison-only, independently locked, non-routed and removable. A future
adoption needs a replacement ADR and measured requirements, migration/recovery,
security/privacy/residency/license, operations, load and cost evidence.

## 6. Security/privacy review

Inputs are opaque synthetic IDs and no document/model/customer data enters either
runtime. Stable effect idempotency is enforced separately from framework retry.
DBOS and Restate SDKs are MIT licensed; Testcontainers is Apache-2.0. Restate's
server uses BSL 1.1 with an additional-use grant, requiring professional license
review before adoption. No compliance or legal approval is claimed.

## 7. Data/schema/migration impact

No CareerPilot data model or migration changed. DBOS creates a temporary test-only
SQLite system database. The Restate harness creates ephemeral container state and
stops it after the test. Production persistence remains PostgreSQL/pgvector and
Temporal owns durable history.

## 8. Automated commands and exact results

- DBOS Ruff and strict MyPy passed; Pytest: 2 passed.
- Restate Ruff and strict MyPy passed; official harness Pytest: 2 passed in 38.00s.
- Root Ruff passed; strict MyPy passed 144 source files.
- Full Pytest: 237 passed, 6 intentional skips, 4 upstream ADK deprecation warnings.
- Frontend format/lint/typecheck/build and 10 Vitest tests passed.
- Semgrep scanned 156 Python targets with zero findings; secrets, the existing
  148-distribution license policy and all pre-commit hooks passed.
- Root, DBOS and Restate environment advisory checks found no known vulnerabilities;
  the three unpublished CareerPilot distributions were expected audit skips.
- Markdown lint passed 180 files; links passed; 13 Mermaid diagrams rendered;
  governance passed 191 Markdown files and 74 requirement IDs.

An initial sandboxed full Pytest run could not launch the local Temporal server and
reported five failures. The unchanged suite was rerun with the required local
process permission and all five Temporal tests passed. The first link and Mermaid
runs were likewise sandbox/network blocked; authorized reruns passed.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| DBOS happy/recovery | 1/2 attempts and one effect | Pass |
| Restate happy/recovery | 1/2 attempts and one effect | Pass |
| Temporal recovery regression | Retry completes without duplicate effect | Pass |
| Root workspace/lock/import inspection | No DBOS or Restate production path | Pass |
| Runtime/data/cost inspection | Local synthetic lab only | Pass |

## 10. Requirements traceability

NFR-003/012/013/019 map ADR-0031 and both independent labs to framework
happy/recovery tests plus the root isolation test. Production adoption, SLO,
residency and migration evidence remains explicitly unverified.

## 11. Example request/response

The recovery command uses key
`application_synthetic_001:record_preparation:v1`. Both lab results return
`artifact:application_synthetic_001:record_preparation`, `completed`, and
`replayed_effect: true`; each ledger reports two attempts and one unique effect.

## 12. Known limitations, debt, and risks

The ledgers are process-local fakes, DBOS SQLite is test-only, and the Restate
harness is a single ephemeral server. The labs do not measure crash across host
loss, concurrency, throughput, long retention, backup/restore, upgrades, regional
deployment, on-call effort or cost. Restate licensing and both platforms' personal-
data controls require review before any proposal.

## 13. Rollback/recovery instructions

Delete the two lab directories, shared fixture, phase documents and isolation test;
no production code, root lock, schema or external state depends on them. Local test
containers/databases are ephemeral. Temporal behavior is unchanged.

## 14. Learning summary

Durable execution remembers progress, while idempotency protects effects. A small
framework experiment becomes architecturally safe only when dependency, import,
data, routing, license and adoption boundaries are tested as carefully as recovery.

## 15. Owner acceptance checklist

- [x] Equivalent happy and recovery scenarios execute in Temporal, DBOS and Restate.
- [x] Programming, state, recovery, observability, deployment, testing, lock-in, maturity and cost are compared.
- [x] Lab dependencies and routes remain isolated from production.
- [x] No paid/cloud/model/personal-data operation occurred.
- [ ] Complete diff is accepted by the owner.

## 16. Proposed next phase

Phase 20 is the production-readiness release candidate and curriculum phase. It
has not started.

## 17. Exact approval command

`APPROVE PHASE 19 AND START PHASE 20`
