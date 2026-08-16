# Phase 19 tutorial: compare durable execution safely

Durable execution records enough progress to continue work after retry or process
failure. It does not turn an arbitrary external call into an exactly-once effect.
The safest small experiment therefore fails immediately after a pretend commit.

Start with the fixture in `labs/fixtures/`. Its idempotency key names one logical
effect. Run the DBOS tests and observe that a temporary SQLite database stores
framework checkpoints while the fake ledger stores the business effect. The
recovery test enters the ledger twice but stores one key.

Next run the Restate tests with Docker available. The official harness starts a
local Restate server, registers the SDK endpoint, and invokes a keyed workflow.
The durable run retries the failed action and receives the ledger's existing
result. The container is stopped after each test; no cloud service is contacted.

Finally run the architecture isolation test. It demonstrates a different kind of
correctness: the labs have independent locks, the production root cannot install
their SDKs, and production Python cannot import either package. Compare the
frameworks using `DURABLE_EXECUTION_COMPARISON.md`, but do not infer that a tiny
test measures production latency, availability, operational effort or migration
risk.
