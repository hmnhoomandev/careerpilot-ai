# ADR-0008: OpenTelemetry with Privacy-Safe Export

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

OpenTelemetry provides trace context, metrics, and structured-log correlation.
Telemetry uses opaque identifiers and redacts prompts, resumes, evidence,
personal data, secrets, and generated documents before export. Provider-native
traces are adapters, not the sole telemetry system.

## Consequences

Every service propagates correlation, tenant-safe request, workflow, graph,
agent, tool, approval, retrieval, prompt-version, and model identifiers. Raw
content logging is off by default. OpenAI SDK tracing requires explicit sensitive-
data configuration because its tracing is enabled by default.

## Source

- [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/)
