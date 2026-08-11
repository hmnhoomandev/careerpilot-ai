# Initial Privacy Impact Assessment

This is an engineering assessment, not legal advice or certification. Items
marked `LEGAL REVIEW` require qualified Swiss/EU counsel before production.

## Processing purposes

- Maintain a user-controlled professional profile and evidence library.
- Analyze user-supplied job information.
- Produce cited match/gap results and truthful application drafts.
- Record approvals and track applications.
- Secure, evaluate, operate, recover, and improve the product using minimized data.

Secondary use, employer ranking, advertising profiles, model training, or sale of
personal data is outside the accepted purpose.

## Data categories and sensitivity

| Category | Examples | Risk | Default treatment |
|---|---|---|---|
| Identity/contact | Name, email, location, links | High | Minimize, encrypt, restrict, redact telemetry |
| Employment/education | Employers, dates, roles, certificates | High | Evidence source, purpose-limited access |
| Uploaded documents | Resumes, portfolios, certificates | Very high | Quarantine, scan, encrypt, short raw retention |
| Inferred data | Skills, matches, gaps, confidence | High | Label inference, cite sources, user correction |
| Potential special-category data | Disability, health, union, ethnicity, religion | Very high | Avoid collection; detect/minimize; explicit policy and legal review |
| Authentication/security | Subject IDs, IP/device/security events | High | Separate access and retention, pseudonymize where practical |
| Agent/model telemetry | Prompts, tool inputs, traces, outputs | Very high | Content off by default, opaque IDs, redaction before export |

## Data-subject controls

- Access and understandable source/provenance views.
- Correction of source facts and propagation to derivatives.
- Portable export through step-up authentication and approval.
- Deletion with a default 30-day recoverable window and documented exceptions.
- Consent withdrawal and delegated-access revocation.
- Human review of consequential inference and generation.

## Retention baseline

- Raw uploads: retain only for defined processing/recovery needs; final period is
  `LEGAL REVIEW` and must be configured, not hard-coded.
- Active profile/evidence/application data: while the account and purpose remain.
- Recoverable deletion: 30 days by default, unless immediate deletion or a valid
  legal hold applies (`LEGAL REVIEW`).
- Chunks, embeddings, caches, replicas, and indexes: same lifecycle as source.
- Audit/security events: separate minimized schedule, access controls, and
  pseudonymization; final duration is `LEGAL REVIEW`.
- Backups: bounded rotation with tested expiry and restoration-time deletion
  handling; final duration is `LEGAL REVIEW`.

## External disclosure gate

Before an external model or source call: authenticate; authorize; confirm purpose
and consent basis; minimize; redact unnecessary PII; select an approved provider,
region, tier, and retention policy; estimate cost; record safe metadata; validate
the response. Do not use a free tier for sensitive customer data when its terms
permit training or product improvement.

## Residency

Prefer Zurich (`europe-west6`). Any EU fallback needs a recorded service-specific
analysis. Pub/Sub needs an explicit message storage policy because default global
routing is not sufficient residency evidence. Provider processing locations and
subprocessors remain `LEGAL REVIEW`.

## High-risk privacy scenarios

- Cross-tenant retrieval or coach overreach.
- Protected traits inferred from career history or language.
- Resume content entering provider traces or evaluation datasets.
- Deleted documents remaining in embeddings, backups, or caches.
- Incorrect match/gap inference affecting user opportunity.
- Third-party personal information contained in evidence.
- International provider processing not understood by the user.

## Phase 4 privacy implementation note

Development uses synthetic profiles. Evidence registration minimizes collection to
title, normalized basename, declared media type, size, ownership, and lifecycle
state; the browser does not transmit selected bytes. PostgreSQL fields establish
soft-deletion and purge-target foundations. The 30-day default, exceptions, legal
holds, backup propagation, and final Swiss/EU schedule require professional legal
review before production.

## Phase 3 identity and audit note

The local adapter uses only fictional identities and pseudonymous stable IDs.
Tokens and submitted career content are excluded from audit events. Tenant audit
views require owner permission and show only their derived tenant. Organization
and coach data processing is not activated. Production identity verification,
staff access, audit/security retention, lawful basis, data-subject verification,
and delegation confidentiality remain `LEGAL REVIEW` under LEG-001, LEG-002,
LEG-004, and LEG-006.

## Required legal reviews

See `LEG-001` through `LEG-008` in `docs/product/REQUIREMENTS.md`.
