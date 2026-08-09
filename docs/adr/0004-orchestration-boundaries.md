# ADR-0004: LangGraph and Temporal Have Separate Ownership

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

LangGraph owns typed in-process agent graphs, model routing, checkpoints, and
human interrupts within a bounded run. Temporal owns long-running business
processes, durable timers/waits, activity retries, signals, recovery, versioning,
and compensation. Temporal invokes agent work through activities; model calls do
not run inside deterministic Temporal workflow code.

## Consequences

Graph state and workflow state require explicit mapping and identifiers. DBOS and
Restate remain isolated Phase 19 labs.

## Source

- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
