# Domain and Architecture Glossary

| Term | Meaning in CareerPilot AI |
|---|---|
| Application | A user's tracked attempt to pursue one job, including approved artifacts and status. |
| Application state | Current product entity values stored by the application. |
| Approval | Durable, auditable human decision governing a proposed action or artifact version. |
| Audit history | Append-oriented security and business events explaining who did what, when, and why. It is not agent memory. |
| Candidate | The job seeker represented by a professional profile. |
| Claim | A material statement about the candidate in generated or stored content. |
| Coach delegation | Explicit, scoped, revocable authorization from a candidate to a coach. |
| Compensation | A deliberate action that semantically reverses a completed workflow effect. It is not database rollback. |
| Deterministic workflow | Control flow whose next step follows explicit code and durable recorded inputs. |
| Evidence item | A user-authorized source that can support one or more claims. |
| Optimistic concurrency | A stale-write guard that updates only when the client's last observed version still matches. |
| Quarantine | A fail-closed evidence state in which metadata or bytes cannot be treated as trusted before an approved scanner result. |
| Transaction | A database boundary that commits all related changes together or rolls all of them back. |
| Fallback | A visible, policy-approved alternative behavior; model-provider fallback is never silent. |
| Graph state | Typed intermediate values owned by a single agent-graph execution. |
| Handoff | Transfer of conversational control and responsibility to another agent. |
| Agent as tool | A manager invokes a specialist for a bounded result while retaining control. |
| Manager delegation | A coordinator assigns bounded work and combines results without necessarily transferring user interaction. |
| Memory | Curated information retained across sessions for an explicit purpose and retention policy. |
| MCP | Protocol boundary exposing narrow tools/resources to compatible clients. |
| Tool capability | A versioned, schema-validated operation with explicit permission, risk, operational limits, errors, and audit policy. |
| Idempotency key | A caller-supplied token scoped to one actor/tool/input so successful mutation replay returns the original result. |
| MCP allowlist | The explicit subset of registered capabilities discoverable through the MCP server. |
| A2A | Protocol boundary for discovery and task interaction between independently deployed agents. |
| Profile | Structured candidate facts supplied or confirmed by the user. |
| Recovery | Continuation or restoration after interruption using persisted state. |
| Replay | Re-execution of deterministic workflow history to rebuild state. |
| Retry | Reattempt of a failed operation under a bounded policy. |
| Session state | Context for one conversational interaction thread. |
| Suggestion | An unverified proposal clearly requiring user confirmation; never rendered as fact. |
| Tenant | Authorization and data-isolation boundary; initially one personal workspace, later an organization. |
| Workflow state | Durable Temporal-managed progress for a long-running business process. |

## Security distinctions

- **Authentication** establishes an actor's identity; **authorization** decides
  whether that actor may perform a specific action on a specific resource.
- **RBAC** grants baseline capability through roles; **ABAC** evaluates context
  such as tenant, ownership, delegation, purpose, sensitivity, and action.
- **SAST** examines source; **SCA** examines dependencies; **DAST** probes a
  running system; **runtime protection** detects or blocks behavior in operation.
- **Graph state** is the typed, checkpointed value for one bounded in-process
  analysis run; it is not application, workflow, session, memory, or audit state.
- **Delegation** means a manager retains run ownership while invoking a bounded
  specialist node or tool.
- **Claim-to-evidence graph** links each material draft statement to its authorized
  source citations and verification status.
- **Exact-version approval** binds a human decision to draft ID, version, content hash,
  and optimistic revision; it is invalid after content changes.
