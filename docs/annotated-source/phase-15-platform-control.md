# Annotated source: Phase 15 platform control

## Core platform policy

`platform_control.py` defines the content-free telemetry event and all allowed operation kinds.
Its post-initialization checks reject whitespace-rich content, negative/non-finite measurements,
unknown schema versions, naive timestamps and excessive attributes before any sink receives data.

`LocalTelemetryCollector` bounds memory and filters by tenant before percentile/count/cost
aggregation. `ModelRegistry.decide` looks up exactly one route and checks capability, provider
availability, privacy, quality, latency, approval and budget in order. It never iterates to a
fallback. `BudgetLedger`, `QuotaLedger` and `CachePolicy` demonstrate pre-execution controls;
all need distributed durable adapters for production. `EvaluationGate` pairs every measured
value with one versioned threshold and exposes failures rather than lowering the bar.

## API and exporters

`observability.py` retains structured safe request logging and adds content-free JSON export plus
a disabled exporter that raises visibly. `main.py` emits one request event after authenticated
requests and exposes owner-only tenant metrics. The current request is recorded after its response,
so the dashboard response summarizes previously completed requests.

The ADK and OpenAI config modules reject trace/content/analytics export flags. In ADK, span
content and prompt-response uploads are independent; both remain disabled. Tests ensure a config
change cannot silently activate an external data transfer.

## Evaluation and UI

`platform-evaluation-v1.json` names retrieval, routing, tool, handoff, grounding, safety, latency,
cost-estimate and workflow-completion metrics. The deterministic gate is code correctness plus
offline product evidence; it is not a live-model quality claim. The web client loads only the
aggregated owner-authorized dashboard and shows export/content-capture state.
