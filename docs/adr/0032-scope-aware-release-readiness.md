# ADR-0032: Require scope-aware evidence for release promotion

- **Status:** Accepted for Phase 20 release-candidate scope
- **Date:** 2026-08-16

## Context

CareerPilot has broad deterministic local verification, container and infrastructure
plans, but no approved staging or production resources. Treating in-process latency,
local containers or synthetic restore as proof of a production SLO would be unsafe.
Conversely, refusing to assemble a release candidate until cloud spending is approved
would hide useful integration and operational gaps.

## Decision

Version `0.20.0-rc.1` is a local source release candidate. Every quantitative gate
declares whether local or production evidence is required. Local evidence can pass
local regression gates but cannot satisfy a production gate. Missing or insufficient-
scope measurements fail closed. The current production decision is `NO-GO`.

No artifact is described as signed or published. Promotion requires immutable images,
a trusted CI identity, protected approval, registry attestation, Zurich staging,
representative load and recovery evidence, production identity, monitoring/error-
budget observation, legal/security/privacy review and current cost approval.

## Consequences

The repository can ship a coherent, reproducible candidate for evaluation without a
false go-live claim. Production release remains blocked by deliberate external-state
and professional-review gates. A later decision must reference concrete evidence,
update the manifest, and receive explicit owner authorization; passing CI alone is
never promotion authority.
