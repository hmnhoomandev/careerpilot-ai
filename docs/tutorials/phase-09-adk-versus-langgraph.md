# Phase 9 Tutorial: Google ADK Specialist versus LangGraph Core

## What now exists

LangGraph remains the application's primary in-process coordinator: it owns the known job
analysis sequence, deterministic branches, checkpoints, and application-facing state.
Google ADK lives in a separate service and owns one bounded task: synthesize interview
research from source excerpts that the caller already supplied and was permitted to use.

| Concern | LangGraph core | Google ADK specialist |
|---|---|---|
| Responsibility | Candidate/job analysis graph | Supplied-source research synthesis |
| State | Typed graph/checkpoint state | Request-scoped ADK session |
| Tools | Central policy registry | One request-local source reader |
| Provider | Fake or bounded model port | Fake or explicit Gemini through ADK |
| Truth control | Retrieval and evidence nodes | Citation post-validation |
| Failure | Graph error state | Stable service error contract |

Neither framework grants authorization. The server derives identity and policy before a
workflow starts. Model output is untrusted until its schema and citations pass validation.

## Run the free fixture

```bash
uv run pytest -q tests/unit/test_google_adk_service.py \
  tests/contract/test_google_adk_api.py
```

The HTTP service requires `X-CareerPilot-Service: careerpilot-main-api`. Its default
configuration uses `FakeResearchProvider`; it makes no network request. Setting
`CAREERPILOT_ADK_ENABLED=false` produces `specialist_unavailable`, which lets the main
journey degrade visibly instead of silently substituting another provider.

## Live evaluation gate

The live test is skipped unless `CAREERPILOT_ADK_LIVE_EVAL_COST_APPROVED=true`, a model is
configured, credentials exist, and the owner separately approved cost and data transfer.
The Phase 9 approval alone does not authorize it. Use synthetic data even when approved.

## Production gaps

Replace the development header with authenticated workload identity, choose a reviewed
Zurich/EU deployment, add durable encrypted sessions only if needed, define retention,
and complete professional privacy/legal review before customer-data use.
