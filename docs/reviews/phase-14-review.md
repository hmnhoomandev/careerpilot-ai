# Phase 14 Review: Accessible Product UI and A2UI

## 1. Phase objective

Turn the API-oriented preview into a coherent, responsive, accessible job-seeker workspace
and safely render versioned A2UI-compatible presentation messages.

## 2. Delivered features

- Responsive dashboard shell, workspace navigation, skip link, visible focus and live status.
- Profile/evidence, job comparison, supported match/gap, citation and agent timeline views.
- Truthful resume/letter controls and exact-version approval presentation.
- Interview-lab and application-tracker states with honest local-only limitations.
- Notification preferences/inbox, audit/access controls and loading, empty, denied, offline,
  partial, stale-oriented and cancellation/confirmation presentation patterns.
- Closed, text-escaped A2UI draft/review renderer and adversarial tests.

## 3. Explicitly not delivered

No new backend workflow, real Temporal web gateway, live interview/model, automatic submission,
email/SMS/push, PDF/export, organization/coach UI, production auth, analytics, browser persistence,
cloud resource, deployment, paid visual testing or Phase 15 behavior.

## 4. Files created/changed

The web page, responsive stylesheet, API client/contracts and tests changed. A2UI renderer and
tests, Phase 14 plan, ADR-0026, web architecture, annotated source, tutorial, exercises/answers,
security/privacy/risk, decisions/learning/traceability/state/roadmap and this review were added
or synchronized. No dependency manifest or lockfile changed.

## 5. Architecture decisions

Next.js owns presentation and tab-local interaction state; FastAPI remains authoritative for
identity, tenant, policy and business transitions. A2UI is a closed presentation protocol, not
dynamic code loading or authorization. Existing React/CSS/test tools were sufficient.

## 6. Security/privacy review

Unknown A2UI schemas/components/actions fail closed; HTML-shaped text remains inert, arbitrary
URLs do not exist and no `dangerouslySetInnerHTML` is used. Consequential visible actions retain
confirmation and exact server validation. Career content is not put in browser storage, URLs or
frontend telemetry. Production sessions, headers/CSP, device risks, retention/export/deletion
copy and legal review remain open. No compliance certification is claimed.

## 7. Data/schema/migration impact

No database, API or migration changed. New TypeScript types mirror existing draft, notification
and A2UI HTTP contracts. Browser state is process/tab-local and disappears on reload/sign-out.

## 8. Automated commands and exact results

- Frontend Prettier, ESLint, TypeScript and Next.js production build passed.
- Vitest passed 9 tests in 2 files, including login/workspace axe scans, landmark/skip navigation,
  offline/denied recovery, existing profile/evidence/citation flows and hostile A2UI messages.
- Lock check and Ruff passed; strict MyPy passed 123 source files.
- Full Pytest passed 182 with 6 expected skips and 4 upstream ADK deprecation warnings. Four
  skips require local PostgreSQL and two live-model tests lack explicit cost/data approval.
- Markdown lint passed 141 files; governance passed 24 required files, 74 requirement IDs and
  149 Markdown files; 12 Mermaid diagrams rendered; detect-secrets passed.
- All applicable pre-commit hooks passed for every modified and untracked Phase 14 file; the
  Python-only Ruff hooks correctly reported no matching staged-file input in that invocation.
- Semgrep scanned 129 tracked Python targets with three rules and zero findings; its macOS signal
  handler warning did not prevent exit 0. Pip-audit found no known vulnerabilities and skipped
  five unpublished internal packages. Production/full npm audits found zero vulnerabilities.
- External link validation remained inconclusive (`Status: 0`) for pre-existing external links.

## 9. Manual test checklist

| Check | Expected | Actual |
|---|---|---|
| Keyboard journey | Skip/navigation/forms/actions work with visible focus | Automated baseline passed; owner pending |
| Mobile 375px/desktop/200% zoom | Layout collapses without losing content | Responsive CSS inspected; owner pending |
| Citation and draft review | Sources visible; exact human decision required | Automated API/render tests passed; owner pending |
| Offline/denied/partial states | Safe, actionable state; page remains usable | Automated pass; owner pending |
| Hostile A2UI | Literal text or blocked alert; no executable node/action | Automated pass; owner pending |

## 10. Requirements traceability

FR-001–020 are represented as one user workspace where their activated APIs exist and future
labs are labelled. NFR-017 maps to responsive semantic UI, keyboard/focus, axe and reduced-motion
controls. SEC-003/006/011 map to server authority, safe A2UI and bounded actions.

## 11. Example requests/responses

After local sign-in, the overview leads to a job workspace and an evidence-grounded result.
The draft API's `careerpilot.a2ui.v1` messages become an escaped editable-draft card and approval
card. An unknown schema becomes “Unsupported presentation content was safely blocked.”

## 12. Known limitations, debt, and risks

- Page sections use in-document navigation rather than URL routes/deep links.
- Interview and tracker content are synthetic labelled fixtures, not durable backend views.
- Draft editing UI is represented but only server-supported decision actions are connected.
- Notification read receipts and live workflow cancellation are not wired into this dashboard.
- Axe/jsdom cannot replace VoiceOver/NVDA, real-browser zoom/mobile and visual review.
- Visual regression was not added because no stable local screenshot runner exists.

## 13. Rollback/recovery instructions

Before Phase 15, revert the eventual Phase 14 commit. No migration, cloud or persistent-data
rollback exists. The prior single-page preview is recoverable from Git history.

## 14. Learning summary

Accessible structure precedes visual layout; state needs both semantic and visual expression.
The browser cannot authorize itself. Structured generative UI must be treated like any untrusted
protocol: validate a closed schema, render text, constrain actions and reauthorize server-side.

## 15. Owner acceptance checklist

- Complete the keyboard-only journey and inspect focus/status announcements.
- Inspect at mobile/desktop widths and 200% zoom.
- Open citations and exercise draft approval/rejection/cancellation with synthetic data.
- Trigger offline and denied states and inspect recovery/correlation information.
- Review ADR-0026 and the labelled non-production interview/tracker limitations.

## 16. Proposed next phase

Phase 15 will add observability, evaluation, explicit model routing and cost controls only after
the exact phase gate. It is not started.

## 17. Exact approval command

`APPROVE PHASE 14 AND START PHASE 15`
