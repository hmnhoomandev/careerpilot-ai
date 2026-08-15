# Phase 16 Tutorial: Defense in Depth and Privacy Lifecycles

Security controls answer different questions. Authentication asks who, authorization asks whether,
validation asks what shape, approval asks whether a human accepted a consequence, and audit asks
what decision occurred. A WAF cannot replace tenant predicates; encryption cannot stop an authorized
but excessive export; a prompt detector cannot authorize a tool.

Deletion is a workflow. First create a subject/tenant-bound tombstone. During the approved 30-day
window the user may cancel. After expiry a durable worker must purge source and derivatives, caches,
indexes and replicas. Backups cannot be edited casually, so restore must replay tombstones before
service. Temporal/event history may require retention or crypto-erasure design and legal review.

SSRF protection belongs before connection. Validate scheme and authority, resolve all addresses,
reject internal/reserved/link-local networks, apply an allowlist, connect only to validated addresses
and repeat the whole decision after redirects. CareerPilot still has no general URL fetcher.

Run the local evidence:

```bash
uv run python scripts/dast_baseline.py
uv run python scripts/audit_licenses.py
uv run pytest tests/e2e/test_security_red_team.py tests/api/test_privacy_security_api.py
```

These tests prove the local engineering baseline. They do not certify GDPR/FADP compliance, cloud
IAM, production WAF/KMS, breach notification or recovery objectives.
