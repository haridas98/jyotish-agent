# Jyotish Agent Design Workflow

This folder is the source of truth for UX/UI work. Chat history is not.

## Rule

Do not redesign or implement UI inside a technical launch session.

UX/UI work must use a separate design session:

1. Audit existing product and routes.
2. Write/confirm a design brief.
3. Produce three substantially different visual directions.
4. Wait for one direction to be chosen.
5. Save decisions and screen specs here.
6. Implement in a separate Codex session from the approved visual source.
7. Run visual QA against screenshots/mock/Figma before acceptance.

## Current Status

The technical chart service is usable. Visual design is not considered final.

Existing exploratory references:

- `docs/design/jyotish-main-page-wireframe.html`
- `docs/design/jyotish-ux-concepts.html`

These are references only, not approved final UI.

## Hard Boundaries

- Do not start Tailwind/shadcn migration without its own ExecPlan.
- Do not add decorative cards, badges, gradients, or hero sections to fill space.
- Do not change backend, calculations, auth, permissions, or API contracts for visual work unless the design ExecPlan explicitly requires it.
- Do not treat a prose description as a visual source. Use Figma, screenshot, generated visual option, or approved mock.
