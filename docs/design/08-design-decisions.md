# Design Decisions

## 2026-06-24 - Separate UX/UI From Technical Launch

Decision:

UX/UI design work must run in a separate design session and must not be mixed into technical launch milestones.

Reason:

The technical service is now usable, but visual quality requires a different workflow: audit, brief, visual options, chosen source, implementation, visual QA.

Rejected:

- Continuing to make small visual tweaks in the long technical supervisor thread.
- Letting Codex invent design while implementing.
- Rebuilding the whole frontend in one commit.

## 2026-06-24 - First Design Target

Decision:

Start with `/charts/:id`, not login, landing page, or dashboard.

Reason:

It is the most complex and characteristic screen. It defines density, navigation, tables, panels, and mobile behavior for the product.
