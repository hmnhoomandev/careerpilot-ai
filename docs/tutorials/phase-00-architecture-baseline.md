# Tutorial: Turning a Product Idea into an Architecture Baseline

## 1. Start with outcomes, not frameworks

CareerPilot AI's core outcome is not “use many agents.” It is a truthful,
evidence-grounded application journey controlled by the job seeker. Frameworks
are selected only after the product invariants are clear.

## 2. Give every state one owner

Application state stores business truth. LangGraph graph state stores intermediate
agent progress. Temporal workflow state stores durable process progress. Session
state supports one interaction, memory is curated across interactions, and audit
history explains actions. Combining these creates unclear retention, recovery,
and authorization behavior.

## 3. Prefer deterministic controls

Authorization, approval transitions, retention, claim verification, arithmetic,
and external effects must be deterministic. A model may interpret a vacancy or
draft text, but schemas and policies validate the result. The safest agent action
is often a narrow tool call behind a policy engine.

## 4. Bound agent collaboration

Manager delegation keeps control with a coordinator. Agent-as-tool requests one
bounded specialist result. A handoff transfers conversational control. MCP exposes
tools; A2A communicates with remote agents. These patterns solve different
problems and should not be interchangeable labels.

## 5. Model trust boundaries and data lifecycle

Authenticated input is still untrusted content. A resume can contain malware or
prompt injection. Every flow crosses validation, authorization, purpose,
minimization, and output-validation gates. Derived chunks and embeddings inherit
the source's access and deletion lifecycle.

## 6. Make reliability measurable

“Reliable” is not testable. CareerPilot records initial targets for availability,
latency, workflow recovery, retrieval quality, grounding, restore, errors, and
cost. These are design targets until later phases measure them.

## 7. Record decisions and uncertainty

ADRs preserve decisions and consequences. Requirements have stable IDs.
Traceability later links each ID to code and tests. Legal questions are labeled
for professional review rather than converted into unsupported compliance claims.

## 8. Respect phase gates

Phase 0 intentionally contains no application code. A complete architecture
baseline reduces rework, while the phase gate lets the owner review scope and
trade-offs before scaffolding begins.
