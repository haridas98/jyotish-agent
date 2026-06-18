# Report Constructor Inventory

## Current report types

1. `personal_overview`
   - User label: `Личный обзор`.
   - Current UI source before this stage: `/reports` page selected the old `core` recipe.
   - Subject: one saved chart.
   - Saved relationship context: optional.
   - Status: active as a structure, not as generated interpretation.

No other report types are currently part of the accepted `/reports` UI. Earlier `family`, `career`, and `karma` entries were scaffold recipes, not accepted user-facing report types.

## Hardcoded factors found in `/reports`

The current personal report structure contains:

- primary entity factors: `house.1`, `graha.MO`, `graha.SU`;
- secondary entity factors: `house.5`, `house.9`, `house.10`;
- calculation factors: `calc.varga.D1`, `calc.varga.D9`, `calc.vimshottari`;
- optional relationship context: selected saved relationship projected through the Relationship Recipe Registry.

## Page responsibilities

- Chart selection: `/reports/page.tsx` loads saved chart profiles and stores the selected chart id in workspace state.
- Report type selection: `/reports/page.tsx` stores selected `ReportTypeId`; definitions come from the Report Type Registry.
- Saved relationship selection: `/reports/page.tsx` filters saved relationships by selected chart and stores selected relationship id.
- Preview: the page calls the Report Recipe Resolver and passes the resolved recipe to `ReportRecipeRenderer`.
- Entity explanation: one `EntityInspector` is rendered by the page.

## Former arrays to remove from the page

- house ids;
- graha ids;
- varga ids;
- calculation ids;
- relationship recipe factor extraction for report preview.

These now belong to the Report Recipe Registry and Report Recipe Resolver.

## User-facing availability

- Available now: `personal_overview`.
- Not available as report types yet: family, career, karma, period overview, relationship overview.

Those can be added later only as separate content tasks.
