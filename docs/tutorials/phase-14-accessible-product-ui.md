# Phase 14 tutorial: accessible product UI and safe A2UI

An accessible interface is not a layer added after visual design. Start with the reading and
keyboard order: landmarks, headings, labels, native buttons, live status and a skip link.
Then use CSS to arrange the same semantic document for desktop and mobile.

A2UI is also a trust boundary. CareerPilot receives structured presentation messages, but it
does not let the server name arbitrary React components or inject HTML. The renderer accepts a
known schema, component and action list. React displays strings as text. An action still goes
through the authenticated API and exact-version business policy.

Run the focused checks:

```bash
cd apps/web
npm test
npm run typecheck
npm run build
```

In the A2UI test, an image-shaped HTML string appears literally and creates no image element.
An unknown schema becomes a visible blocked-content alert. In page tests, axe inspects both
login and authenticated workspace structures, and the offline fixture produces recovery copy
without navigating away or writing browser storage.
