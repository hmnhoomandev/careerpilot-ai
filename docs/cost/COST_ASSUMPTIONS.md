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

## Phase 15 cost-control addendum

The local tenant budget is CHF 0. Model routes include a conservative CHF-per-1,000-token estimate;
positive estimates require explicit approval and remaining budget before reservation. Local/fake
routes cost zero. Estimates are not invoices. Production requires provider price-version records,
currency conversion policy, atomic durable reservations, usage reconciliation, alerts and owner-
approved budgets. No cloud analytics/export resource or model call was created in Phase 15.

## Phase 18 GKE comparison

The render-only reference costs CHF 0. A real GKE choice adds cluster/control-plane,
Pod compute and memory, persistent/network storage, load balancing, NAT/egress,
logging/metrics and operational labor/support to the existing database, messaging,
secrets, KMS and model costs. Unlike Cloud Run's current scale-to-zero design, a
two-replica availability floor consumes capacity continuously.

Prices are time-sensitive and no deployment shape is approved, so Phase 18 does
not assert a numeric monthly estimate. Before any staging cluster, obtain current
Zurich prices, specify cluster mode/zones/replicas/resources/traffic/log volume,
estimate one-time and monthly CHF including tax/currency assumptions, compare the
same load on Cloud Run, configure budgets/quotas/shutdown, and receive explicit
owner approval. Local Kustomize remains the free alternative.

## Phase 19 durable-execution labs

The DBOS SQLite test and Restate Docker harness use local compute and cost CHF 0;
no hosted console, cloud database, deployment, model or paid API is used. A future
DBOS design would at least require production PostgreSQL, backups, telemetry and
operational ownership. A future Restate design would add server capacity/storage,
SDK endpoints, networking, backup and operational ownership. Prices and deployment
shapes are deliberately not estimated because adoption is not approved. Temporal
remains the baseline, and local isolated labs remain the free alternative.
