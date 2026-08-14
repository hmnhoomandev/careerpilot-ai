# Success Metrics and Initial Targets

Targets are design objectives until measured in the relevant implementation
phase. They are not current service claims.

| ID | Metric | Initial target | Measurement phase |
|---|---|---:|---:|
| MET-001 | Monthly production availability | 99.5% | 20 |
| MET-002 | API read latency | p95 ≤ 500 ms, excluding model work | 15 |
| MET-003 | API mutation latency | p95 ≤ 1 s, excluding asynchronous work | 15 |
| MET-004 | Agent workflow completion | ≥ 95% on supported evaluation cases | 15 |
| MET-005 | Recoverable interrupted workflows | 100% of recovery fixtures | 12 |
| MET-006 | Unauthorized cross-tenant reads/writes | 0 in security suites | 3+ |
| MET-007 | Material generated claims with valid evidence links | 100% | 8 |
| MET-008 | Unsupported material claims admitted as facts | 0 | 8 |
| MET-009 | Retrieval recall@5 on versioned fixture set | ≥ 0.85 | 5 |
| MET-010 | Citation correctness on fixture set | ≥ 0.95 | 5 |
| MET-011 | Restorable production backups | 100% of scheduled restore exercises | 16+ |
| MET-012 | Recovery point objective | ≤ 24 hours initially | 17 |
| MET-013 | Recovery time objective | ≤ 8 hours initially | 17 |
| MET-014 | Server error rate | < 1% of valid requests monthly | 15 |
| MET-015 | Explicit provider-outage behavior | 100% block/degrade visibly; 0 silent switches | 7+ |
| MET-016 | Default test/model cost | CHF 0 | Every phase |
| MET-017 | Cost estimate coverage | 100% of model workflows before live enablement | 15 |
| MET-018 | Keyboard completion of core journey | 100% of core steps | 14 |

Thresholds must be reassessed with real, consented production telemetry and may
change only through a recorded decision.

Phase 15 implements local measurement contracts for MET-002–004, MET-014–017. The synthetic
offline fixture meets its versioned thresholds, but this is not production traffic evidence and
does not establish the production availability, latency or error-rate claims.
