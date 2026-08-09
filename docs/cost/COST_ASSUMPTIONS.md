# Cost Assumptions

## Binding budget

Development and learning budget: **CHF 0 per month**.

No paid cloud resource, billing enablement, paid API call, or recurring paid
service is authorized. Phase 0 creates no resources.

## Local strategy

| Capability | CHF 0 approach |
|---|---|
| Python/Node services | Local processes and containers |
| PostgreSQL/pgvector | Local container in Phase 1+ |
| Models | Deterministic fake providers by default |
| Pub/Sub | In-memory adapter or supported emulator |
| Object storage | Local filesystem-compatible fake for development |
| Temporal | Local development server/container |
| Identity | Safe development adapter |
| Telemetry | Local OpenTelemetry collector and local sink |
| Malware boundary | Fake scanner first; safe test fixtures |

## Cost gate

If a future phase cannot meet acceptance without payment, stop before cost and
state:

1. Why payment is required.
2. Provider and service.
3. One-time and estimated monthly CHF cost, assumptions, taxes, and currency date.
4. Free/local alternative and resulting limitation.
5. Quotas, free-tier conversion risk, shutdown method, and budget alerts.
6. Exact owner approval required.

## Future estimates

Staging and production estimates will be separate and usage-based. They must cover
Zurich Tier 2 Cloud Run pricing, Cloud SQL, storage/backups, networking/egress,
Pub/Sub, secrets/KMS, telemetry, security tooling, model tokens, support, and tax.
No numeric estimate is recorded in Phase 0 because no deployment shape or usage
volume is approved and prices are time-sensitive.
