# Phase 10 Exercise Answers

1. Handoff transfers the active conversation and final response; agent-as-tool returns a
   specialist result to the manager, which retains control.
2. Input blocks injection/sensitive content, tool blocks non-allowlisted actions, and
   output blocks sensitive feedback before delivery.
3. Resume fails with `approval_conflict`; revision and exact action hash must both match.
4. Only scoped IDs, provider, orchestration mode, and outcome exist—no prompts, answers,
   tool payloads, tokens, secrets, or hidden reasoning.
5. A live call also requires explicit cost/data approval, positive CHF limit, credentials,
   consent, transfer authority, and synthetic minimized input.
