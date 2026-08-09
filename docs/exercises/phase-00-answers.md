# Phase 0 Exercise Answers

1. The upload crosses the untrusted input boundary. Threats include tampering,
   information disclosure, elevation of privilege, and denial of service. Controls
   include quarantine/scanning, untrusted-content labeling, injection detection,
   narrow tool allowlists, authorization, approval, output validation, and no
   email tool in the initial workflow.
2. LangGraph interprets a job section and routes match/gap nodes. Temporal owns a
   seven-day timer, retrying an external activity, and the month-long durable
   approval wait. Temporal can invoke a bounded LangGraph run through an activity.
3. A role grants baseline capabilities, not candidate consent. ABAC must also
   require an active candidate-specific delegation, purpose, tenant, scope, and
   resource/action match, with revocation and audit.
4. It is primarily a deterministic tool/service. A model may choose to call it,
   but the lookup itself does not need an LLM identity.
5. Block the unsupported leadership claim. The system may offer a clearly labeled
   suggestion asking the user for evidence or confirmation; it cannot insert it
   as fact. Existing evidence supports only the narrower statement.
6. Retry repeats a failed send; replay reconstructs deterministic workflow state;
   recovery resumes after a worker outage; compensation retracts or records a
   correction for an already completed effect; fallback uses an explicitly
   approved alternative and reports it.
7. Record the unavailable service, proposed region, data-residency implications,
   security/privacy implications, latency implications, and cost implications,
   then obtain approval before creation.
8. Compare the requested/authorized provider and model identifiers with the
   executed provider/model telemetry for every call; fail if they differ without
   a recorded, visible policy decision. The target is zero silent switches.
