# ADR-0002: Python 3.13 and Node.js 24 LTS

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

The workstation has Python 3.14 and Node.js 26. Some required frameworks and
native dependencies may lag those versions. Current FastAPI release notes record
Python 3.13 support, and current Next.js documentation requires Node.js 20.9 or
newer.

## Decision

Target Python 3.13 and Node.js 24 LTS. Phase 1 will enforce exact versions and
verify every selected dependency before locking.

## Consequences

Developers need version managers or `uv`-managed Python. Installed global versions
are not authoritative. Revisit versions through an ADR, not incidental upgrades.

## Sources

- [FastAPI release notes](https://fastapi.tiangolo.com/release-notes/)
- [Next.js installation requirements](https://nextjs.org/docs/app/getting-started/installation)
