# Phase 2 Exercise Answers

1. UI client → HTTP adapter → application service → repository protocol; the
   in-memory adapter points inward. Core owns the protocol because it states the
   application's need without coupling business behavior to storage technology.
2. The sorted shared terms are `accessibility`, `engineer`, and `python`. `and` is
   a stop word; `go` is shorter than the three-character token rule.
3. Display name 100, summary 1,000, job description 5,000 characters. Browser
   controls improve feedback but can be bypassed by any HTTP client.
4. Middleware creates or validates the ID, writes the response header, the
   analysis contract includes it, and the logger emits it as allow-listed metadata.
5. A new app instance owns a new empty dictionary. The service raises
   `ProfileNotFoundError`, which the HTTP adapter maps to the safe 404 envelope.
6. Display name, professional summary, job description, result text, and request/
   response bodies are excluded. Logs contain operation metadata only.
7. OpenAPI may still generate, but the typed browser client or rendering assertion
   fails when it cannot find the expected field. This demonstrates why both sides
   need contract evidence.
8. Exact word overlap has no evidence reasoning, context, weighting, confidence,
   or evaluation. Calling it fit would be misleading and potentially harmful.
