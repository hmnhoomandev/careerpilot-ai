# API guide

## Contract

The FastAPI OpenAPI document is available locally at `/openapi.json`; interactive docs
are at `/docs`. The candidate API version is `0.20.0-rc.1`, while public paths remain
under `/api/v1`. A correlation ID is returned in `X-Correlation-ID` and stable errors use
an `error` object with code, message and correlation reference.

Local authentication starts with `POST /api/v1/dev/sessions` and a synthetic user ID.
Protected calls require the returned bearer token and `X-CareerPilot-Tenant-ID`. The
server derives actor, memberships, roles and permissions; clients cannot assert them.
Development sessions are refused outside local mode and are not production credentials.

## Capability groups

- Profiles/evidence/documents: tenant-safe CRUD, bounded upload, cited retrieval and deletion.
- Analyses/drafts/approvals: deterministic or fake-first analysis, truthful versioned drafts
  and exact approval transitions.
- Tools/MCP/A2A/specialists: narrow typed capabilities with policy, timeout, idempotency,
  rate, audit and explicit unavailable behavior.
- Notifications/audit/privacy/platform: tenant-scoped operational views and rights controls.
- Health: `/health/live` and `/health/ready` are public and content-free.

Use generated OpenAPI as the field/status authority. Treat all input as untrusted, bound
payload sizes, reuse idempotency keys only for identical requests, and never retry a
consequential action without its documented exact approval/effect key. HTTP 401 means no
valid identity; 403 means known but not authorized; some foreign resources intentionally
return non-enumerating 404; 409 indicates version/idempotency conflict.

No endpoint authorizes automatic job submission, email, scraping, paid model fallback or
cloud provisioning. Production clients require OIDC/workload identity, TLS, CSRF/session
design, rate enforcement and approved deployment evidence.
