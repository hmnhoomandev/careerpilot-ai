# Phase 10 Tutorial: Handoff versus Agent as Tool

The same synthetic interview fixture is intentionally routed three ways.

| Pattern | Who selects specialist | Who owns final response | Best fit |
|---|---|---|---|
| Direct handoff | Manager/SDK route | Interview specialist | Specialist continues conversation |
| Agent as tool | Manager calls nested agent | Interview manager | Manager combines and governs output |
| Manager delegation | Manager policy | Interview manager | Deterministic application-owned delegation |

An SDK handoff is represented as a tool to the model but changes the active agent. An
agent-as-tool call returns the nested specialist's result to the manager. Neither grants
authorization or permission to publish feedback.

Run the free comparison:

```bash
uv run pytest -q tests/unit/test_openai_agents_lab.py \
  tests/contract/test_openai_agents_api.py
```

The feedback preparation tool declares SDK approval, while the deterministic laboratory
also serializes a pending state with tenant, actor, session, exact action hash, status,
and revision. Approving or rejecting resumes only that bound action. It does not publish.

SDK tracing is disabled in the CHF 0 configuration and sensitive trace inclusion is
false. Local trace evidence contains only identity scope, provider, route, and outcome;
prompts, candidate answers, tool payloads, and hidden reasoning are excluded.

The live test stays skipped unless explicit cost approval and a positive budget ceiling
are configured. Phase approval alone does not authorize that model call.
