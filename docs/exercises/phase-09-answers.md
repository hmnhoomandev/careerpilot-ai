# Phase 9 Exercise Answers

1. The closure contains only that request's allowlist, reducing cross-session leakage.
2. The service returns HTTP 503 with `specialist_unavailable`.
3. Post-validation raises `malformed_provider_output`; unsupported sources fail closed.
4. ADK session holds specialist conversation context; LangGraph checkpoint resumes the
   main analysis graph; durable business records remain authoritative application state.
5. Explicit cost approval, external-transfer authorization, consent/purpose, minimized
   synthetic input, credentials/model configuration, and reviewed provider policy.
