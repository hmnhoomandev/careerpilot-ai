# Dependency Policy and Phase 1 Review

## Rules

- Runtime manifests declare compatible ranges; lockfiles commit exact resolutions.
- New production dependencies require purpose, license, alternatives, security,
  privacy, cost, and ADR-impact review.
- Upgrades are explicit and reviewed; CI uses locked installs.
- Default dependencies must not require paid services or live-model calls.
- SCA findings are reported; critical/high findings block unless explicitly
  accepted with a documented expiration and mitigation.

## Phase 1 production dependencies

| Dependency | Purpose | License | Alternative considered | Security/ADR impact |
|---|---|---|---|---|
| FastAPI | Future HTTP adapter shell | MIT | Starlette directly | Selected architecture; input validation still required |
| Pydantic Settings | Typed environment configuration boundary | MIT | Manual environment parsing | Prevents unvalidated config; secrets remain external |
| Uvicorn | Local ASGI runtime foundation | BSD-3-Clause | Hypercorn | Development/runtime adapter only |
| Next.js | Web application framework | MIT | Vite SPA | Matches ADR-0006; server/client boundary needs review |
| React/React DOM | Accessible component UI | MIT | Vue/Svelte | Matches ADR-0006; rendering must sanitize untrusted data |
| careerpilot-core | Internal framework-independent package | Repository license | Monolithic API package | Enforces ADR-0001 dependency direction |
| OpenTelemetry API | Vendor-neutral trace/correlation API | Apache-2.0 | Custom trace context | No exporter/content capture; 1.42.x satisfies Google ADK 2.5 runtime constraints |
| pgvector | SQLAlchemy vector mapping | BSD-3-Clause | Handwritten vector SQL | Keeps pgvector typed; no service/data transfer |
| pypdf | Local text-based PDF extraction | BSD-3-Clause | PDFium or cloud parser | Untrusted parser requires bounds now and production isolation later |
| python-multipart | FastAPI multipart upload parsing | Apache-2.0 | Custom multipart parser | Smaller risk than custom parsing; upload limits remain mandatory |
| mcp >=1.28.1,<1.29 | Official MCP server/client protocol SDK | MIT | Handwritten JSON-RPC | Minimum includes fixes for PYSEC-2026-3481/3482/3483; explicit allowlist in ADR-0018 |
| langgraph >=1.2.9,<1.3 | Typed graph, retry, and checkpoint runtime | MIT | Custom state machine | Bounded in-process ownership in ADR-0019; no LangSmith service configured |
| google-genai >=2.13,<2.14 | Official future Gemini adapter SDK | Apache-2.0 | Handwritten HTTP | No client/default call; explicit transfer authorization and no fallback |
| google-adk >=2.5,<2.6 | Isolated Google agent/session/tool runtime | Apache-2.0 | Custom specialist loop | Service-only import, fake default, no deployment or model call by default; ADR-0021 |
| openai-agents >=0.8,<0.9 | Isolated handoff/tool/session/approval learning runtime | MIT | Custom orchestration loop | Service-only import, trace export off, fake default, opt-in live path; ADR-0022 |

## Development dependencies

Ruff, MyPy, Pytest, pytest-asyncio, pre-commit, ESLint, Prettier, TypeScript,
Vitest, jsdom, and Testing Library are permissively licensed developer tools.
detect-secrets and pip-audit provide secret/SCA checks. Semgrep Community Edition
adds SAST and has stronger copyleft licensing considerations than runtime tools;
it is development-only and not distributed with production artifacts. Exact
licenses must be rechecked from locked package metadata during release review.

Phase 2 adds BSD-3-Clause `httpx2` for Starlette's supported test client and
MPL-2.0 `axe-core` as a development-only accessibility test engine. Neither is
part of the browser production dependency graph. The previous `httpx` fallback
was removed after Starlette reported it as deprecated.

Phase 4 adds MIT-licensed SQLAlchemy Core for mappings/transactions and Alembic
for migrations. Psycopg 3 uses LGPL-3.0 with exceptions and is the PostgreSQL
driver; its local binary distribution bundles native `libpq`/TLS components, so
locked SCA and later container/SBOM scans are required. Direct SQL plus a custom
migration runner was rejected as higher-maintenance recovery machinery. These
dependencies make no external service call by themselves and add no paid cost.

Current Semgrep 1.172.0 hard-pins vulnerable `mcp==1.23.3`. Semgrep therefore runs
through pinned `uvx` resolution only for a local, metrics-disabled source scan; its
environment is absent from the application lock and runtime, and its MCP server is
never started or exposed. The application uses MCP 1.28.1 or newer and must pass its
dependency audit. Revisit the isolation when Semgrep adopts patched MCP 1.28.1 or
newer. Pytest is constrained to 9.0.3 or newer to remediate PYSEC-2026-1845.

## Residual risk

Locking improves reproducibility but does not prove safety. Dependency confusion,
malicious releases, compromised actions, transitive vulnerabilities, and license
changes require SCA, SBOM, provenance, and later supply-chain controls.

## Phase 11 A2A dependency

`a2a-sdk` is locked to the compatible `>=0.3.22,<0.4` line and supplies official Agent
Card/Task validation. It is Apache-2.0 licensed. Phase 11 does not activate its network
server/client or cloud integrations. Lock changes and transitive protobuf/Google API
packages are dependency-audited; a minor `uv` normalization warning for an upstream
`>=3.6.*` specifier is recorded as non-blocking.

## Phase 12 Temporal dependency

`temporalio>=1.30,<1.31` is locked at 1.30.0. The official SDK is MIT licensed, supports
Python 3.13, and brings `nexus-rpc` plus protobuf typing metadata. The minor line is bounded
because workflow replay compatibility requires deliberate upgrades. Default integration
tests use the SDK's downloaded local time-skipping server; Temporal Cloud and production
server images are not dependencies or authorized services. Upgrade review must run history
replay, security/license audit, Python compatibility, and test-server checksum/provenance
checks before changing the bound.
