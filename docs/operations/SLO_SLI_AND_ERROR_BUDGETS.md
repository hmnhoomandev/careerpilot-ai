# SLOs, SLIs, and error budgets

## Status and measurement boundary

These are initial production design targets, not achieved production SLOs. Phase 20
has no staging or production traffic. Local measurements are regression evidence only.

## Service targets

| Capability | SLI | Initial target | Window | Production evidence needed |
|---|---|---:|---|---|
| API availability | Valid non-user-error requests returning an acceptable response / valid requests | 99.5% | Calendar month | Edge and application metrics with maintenance policy |
| API latency | Server duration for accepted API requests | p50 ≤ 250 ms, p95 ≤ 500 ms, p99 ≤ 1,000 ms | Rolling 28 days | Representative endpoint mix excluding client/network timing only when labelled |
| Agent workflow completion | Eligible workflows reaching expected terminal outcome / started workflows | ≥ 99% | Rolling 28 days | Durable workflow and graph terminal events |
| Workflow recovery | Recoverable injected/real interruptions successfully resumed without duplicate effect | 100% | Quarterly exercise and rolling incidents | Temporal history, effect ledger and recovery drill |
| Error rate | Unexpected 5xx or stable internal failure / valid requests | ≤ 0.5% | Rolling 28 days | Route-weighted API metrics |
| Provider failure | Authorized provider operations ending unavailable/timeout/quota/malformed | ≤ 1% | Rolling 28 days | Explicit provider/model/version events; no fallback masking |
| Retrieval quality | Versioned offline retrieval composite gate | ≥ 0.85 | Each release and monthly | Representative, consented, versioned evaluation set |
| Cost per workflow | Reconciled provider/cloud variable cost / completed workflow | Owner-approved budget | Daily/monthly | Provider invoices/usage and durable reservations |
| Restore success | Scheduled isolated restores meeting integrity/scope/RPO/RTO | 100% | Quarterly | Managed backup/PITR restore drill |
| Data durability | Provider-backed durability design target | ≥ 99.999999999% | Annual architecture review | Contract/configuration plus restore evidence; not an application measurement |

User-caused validation, authorization denial and deliberate budget/privacy blocks are
tracked separately and never reclassified to make availability look better. Model or
provider fallback is prohibited; a provider outage remains visible.

## Error budget

A 99.5% monthly availability target allows 0.5% unsuccessful eligible requests. In a
30-day month that is approximately 216 minutes only when a time-based approximation is
appropriate; request-based burn remains authoritative for API availability. Alert at:

- 2% budget consumed in one hour: investigate during support hours.
- 10% consumed in six hours: page the primary on-call and freeze risky promotion.
- 50% consumed before the window midpoint: reliability work takes priority.
- 100% consumed: stop feature promotion until the owner accepts a remediation plan.

Alerts use metadata and bounded labels only. Candidate content, prompts and documents
must not enter metrics. Final support coverage, exclusions and contractual SLO language
require business and legal approval.
