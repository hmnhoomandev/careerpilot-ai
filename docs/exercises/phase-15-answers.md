# Phase 15 exercise answers

1. The version is a bounded registry reference; prompt text may contain career data or secrets.
2. The request selected one route. Choosing another after failure changes provider/behavior
   silently; CareerPilot instead returns the explicit blocking reason.
3. Estimate predicts cost, reservation prevents knowingly exceeding the limit before work, and
   reconciliation replaces the estimate with authoritative billed usage later.
4. ADK content-in-span capture and completion upload are independent controls; remove/disable the
   upload hook and bucket configuration as well as keeping spans at `NO_CONTENT`.
5. Add the same metric name to `values` and `thresholds`; a lower value makes report `passed`
   false. Fix implementation/fixture evidence rather than weakening the threshold.
