# Support and on-call process

## Ownership model

No production support rota exists yet. Go-live requires named primary and secondary
on-call owners, a privacy/security escalation contact, database/workflow owners and an
owner empowered to stop spending or traffic. Personal names belong in an access-
controlled operational system, not this public repository.

## Severity

| Severity | Example | Initial response objective |
|---|---|---:|
| SEV-1 | Cross-tenant disclosure, destructive corruption, active credential compromise | 15 minutes, 24×7 only after staffing approval |
| SEV-2 | Main journey unavailable, sustained SLO burn, provider outage without safe service | 30 minutes |
| SEV-3 | Degraded non-critical workflow or bounded customer issue | 4 business hours |
| SEV-4 | Question, documentation defect or low-impact bug | 2 business days |

Objectives are operating targets, not contractual guarantees. Security/privacy events
follow the incident and data-breach runbook; notification duties require legal review.

## Incident flow

1. Acknowledge and assign incident ID, severity and commander.
2. Protect people/data first: block traffic/action, revoke identity, disable provider or
   stop promotion without copying sensitive payloads into chat/tickets.
3. Preserve metadata-only evidence and correlation/workflow identifiers.
4. Communicate verified impact and uncertainty on a fixed cadence.
5. Recover through documented rollback/restore; validate tenant isolation and deletion.
6. Close only after monitoring is stable; produce a blameless review and tracked actions.

Release changes freeze during SEV-1/2 and during error-budget exhaustion unless the
change is an approved remediation. Access to logs, backups, secrets and customer support
data is least-privilege, audited and retained only under reviewed policy.
