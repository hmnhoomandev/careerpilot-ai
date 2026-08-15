# ADR-0028: Defense in Depth and Recoverable Data Rights

- **Status:** Accepted for the Phase 16 local reference path
- **Date:** 2026-08-14

## Context

Career data is personal and sometimes highly sensitive. A prompt detector, WAF, encryption or
approval alone cannot protect the complete journey. Data-subject actions also cross mutable stores,
derived indexes, workflow/event history and backups; a single synchronous delete is misleading.

## Decision

Use layered deterministic controls: authenticated tenant context, centralized authorization,
step-up and exact approval for export/deletion, a 30-day recoverable deletion tombstone, source-
linked derivative lifecycle, restore-time tombstone application, strict HTTP headers, local and
future-edge rate controls, pre-connect SSRF validation, fail-closed uploads and a versioned red-team
corpus. KMS and secret management remain provider-neutral ports. Production configuration must
prove HTTPS, managed configuration, KMS and edge rate limiting before startup.

## Consequences

Phase 16 can verify policy locally at CHF 0. Physical account purge, durable lifecycle ledgers,
production identity proofing, cloud encryption/WAF/backups and legal-hold decisions remain future
production work. Final lawful bases, retention schedules and notification duties are `LEGAL REVIEW`;
this ADR is not a certification or compliance guarantee.

## Rejected alternatives

- Immediate cascade deletion: conflicts with the approved recovery window and backups.
- Client-asserted step-up/approval as final production proof: the local boolean/reference is only a
  contract demonstration; production must bind cryptographic identity and durable approval.
- Allowing outbound fetch and blocking known metadata URLs: incomplete against IPv6, redirects,
  DNS rebinding and internal ranges. Phase 16 exposes policy without a network fetcher.
- One security scanner: SAST, SCA, DAST, secrets, licenses and adversarial behavior find different
  defect classes and cannot substitute for one another.
