# ADR-0005: Bounded Model and Agent Providers

- **Status:** Accepted
- **Date:** 2026-08-09

## Decision

Use fake providers by default. Gemini is the initial learning-path model for the
LangGraph adapter and Google ADK service. OpenAI is used only in the bounded
Agents SDK service. Every call requires authorization, purpose, consent where
applicable, minimization, redaction, structured validation, telemetry policy, and
cost control. Never silently switch providers.

## Consequences

Provider outages yield explicit failure or an approved non-model degradation.
Live tests are opt-in. Sensitive data cannot use a tier that permits training or
product improvement without an approved contractual basis.

## Sources

- [Google ADK](https://adk.dev/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
