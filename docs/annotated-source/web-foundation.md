# Annotated Source: Web Foundation

Sources: `apps/web/src/app/layout.tsx`, `page.tsx`, `styles.css`, and
`page.test.tsx`.

## Architectural role

The App Router shell proves React, TypeScript, CSS, testing, accessibility-oriented
queries, and the production build connect without implementing a product feature.

## Logical walkthrough

- `layout.tsx` imports global styles, publishes safe static metadata, declares the
  initial English document language, and types children as immutable `ReactNode`.
- `page.tsx` renders one semantic `main` landmark, label, H1, and honest phase
  boundary. There is no network, state, authentication, or model behavior.
- `styles.css` uses system fonts, responsive width, and light/dark color-scheme
  support without a UI dependency.
- `page.test.tsx` renders the component in jsdom and queries its semantic heading
  and explanatory text. Semantic queries provide an early accessibility signal.

## Failure and alternatives

Build/type errors fail CI. The unit test does not replace browser accessibility or
end-to-end tests, which arrive with real screens. A component library and Tailwind
were rejected in Phase 1 because no product design requires them yet.
