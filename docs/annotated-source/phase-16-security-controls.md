# Annotated Source: Phase 16 Security Controls

## `privacy_control.py`

Enums make rights and states closed/versionable. Frozen records prevent accidental mutation.
`PrivacyControlService` keys consent and requests by server-derived tenant/actor, requires step-up
plus an exact approval reference, calculates the 30-day UTC window and permits cancellation only
for the same subject before expiry. `due_for_purge` produces work; it deliberately does not pretend
to erase PostgreSQL, vector, event or backup stores.

## `security_hardening.py`

The fixed header map prevents caching/framing/type sniffing and gives API responses a closed CSP.
`validate_outbound_destination` parses once, forbids embedded credentials/non-HTTPS/fragments,
matches a closed host allowlist and rejects every resolved non-global IP before a socket exists.
Redirects must repeat this validation. `LocalRateLimiter` is locked and bounded per identity; a
distributed edge/store replaces it in production. Production configuration fails closed without
TLS, managed configuration/KMS and edge limiting.

## `backup_control.py` and `key_management.py`

Backup records are opaque metadata. Canonical JSON makes integrity deterministic; restore verifies
schema/hash, scopes the tenant and removes tombstones. This demonstrates ordering, not encryption.
The KMS protocol keeps provider SDKs outside core and rotation state explicit.

## Failure and tests

Invalid lifecycle transitions, foreign IDs, unsafe destinations, modified backups and missing
production controls fail with stable reasons. Unit/API/e2e tests plus the local DAST and versioned
red-team corpus cover the activated behaviors. Provider KMS, real scanner, WAF, durable deletion,
container and IaC behavior remain intentionally unclaimed.
