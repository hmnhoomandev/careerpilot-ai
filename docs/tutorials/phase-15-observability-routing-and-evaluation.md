# Phase 15 tutorial: measure, route, and spend explicitly

Observability answers what happened; evaluation asks whether it was good; routing decides which
approved capability may run; budget policy decides whether it may spend. Combining them into an
opaque “AI platform” function makes failures hard to explain, so CareerPilot keeps four explicit
boundaries linked by versioned identifiers.

Run the focused zero-cost checks:

```bash
UV_CACHE_DIR=/tmp/careerpilot-uv-cache uv run pytest \
  tests/unit/test_platform_control.py \
  tests/api/test_platform_metrics_api.py \
  tests/e2e/test_platform_evaluation.py -q
```

Change `routing_correctness` in the fixture below its threshold and observe the evaluation gate
fail. Request the paid route without approval and observe `budget_approval_required`; approve it
under a zero remaining budget and observe `budget_exceeded`, not a fake-provider fallback.

ADK's `agents-cli eval` generate/grade quality loop is documented but not run in the CHF 0 path:
generation and built-in judging may call models or managed services. Local code metrics are the
safe default until the owner separately approves provider, data transfer, region and budget.
