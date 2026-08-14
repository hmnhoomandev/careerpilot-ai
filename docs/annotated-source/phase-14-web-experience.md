# Annotated source: Phase 14 web experience

## `app/page.tsx`

The page composes a session-scoped workspace. React state holds only tab-local view data;
there is deliberately no browser storage. The `run` helper gives all operations one loading,
safe-error and recovery path. Forms reuse typed API functions, while confirmation remains
mandatory for exact approval, cancellation and deletion. Static interview/tracker examples
are visibly synthetic and never pretend to execute unavailable backend behavior.

Semantic `aside`, `nav`, `header`, `main`, `section`, `article`, tables, fieldsets and native
buttons/inputs create the accessibility tree before CSS. The skip link and focus target let
keyboard users bypass repeated navigation. Live status regions announce asynchronous changes.

## `components/a2ui-renderer.tsx`

The renderer accepts `unknown[]`, validates schema/component/action values and rejects any
message outside the allowlist. It extracts bounded strings and renders them through React,
which escapes markup. No dynamic imports, HTML injection or arbitrary links exist. Action
callbacks emit an intent; the API still validates identity, authorization and exact version.

## `lib/careerpilot-api.ts`

Typed draft, notification and A2UI contracts document the browser boundary. Every protected
request receives the local bearer token and selected tenant header, but the server derives
actual membership and permission. Safe response parsing keeps correlation IDs available
without exposing internal exceptions.

## `app/styles.css`

CSS defines a desktop sidebar, sticky header, cards, state variants and responsive collapse.
Focus is never removed. Reduced-motion preference disables animation, and mobile breakpoints
change layout rather than hide product content.
