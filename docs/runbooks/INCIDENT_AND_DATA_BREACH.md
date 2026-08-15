# Incident and Personal-Data Breach Runbook

## Trigger and safety

Treat suspected cross-tenant access, credential/key exposure, unsafe model transfer, malicious
upload execution, deletion failure or personal-data disclosure as an incident. Do not copy career
content into tickets or chat. Use pseudonymous IDs and preserve authorized evidence.

## Procedure

1. Declare an incident ID, severity, commander and privacy/security owners.
2. Contain safely: disable the affected route/provider/tool, revoke sessions/credentials, preserve
   tenant isolation and stop external transfers. Do not destroy evidence.
3. Establish scope from minimized audit/telemetry: tenants, categories, systems, time window,
   recipients and whether encryption/key material was affected.
4. Eradicate and recover using reviewed changes, isolated restore and security regression tests.
5. Verify deletion/consent tombstones and prevent restored data from reactivation.
6. Record decisions, residual risk, user remediation and post-incident actions.

Notification authority, thresholds, recipients and timelines under GDPR/Swiss FADP are
`LEGAL REVIEW` (LEG-008). Only authorized legal/privacy leadership decides notification. Never
claim an incident is legally non-reportable from this engineering runbook alone.
