# Transit Workbench Calculation Inventory

## Current calculation entry points

- Legacy public calculation endpoint: `POST /api/calculations/transits` in `backend/apps/calculations/views.py`.
- Legacy workflow: `build_transit_report` in `backend/apps/calculations/workflows.py`.
- Accepted scope for 9A: no predictions, no aspects, no natal overlay, no dasha synthesis. The new workbench API is chart-scoped and read-only: `GET /api/charts/:id/transit-workbench`.

## Existing position data

The saved chart calculation already stores D1 facts used by the common chart workbench:

- 9 grahas in `result.grahas` when calculation is complete;
- Lagna / Ascendant in `result.ascendant`;
- 12 whole-sign houses in `result.houses`;
- rashi name and rashi index on placements;
- longitude and degree data when available;
- nakshatra and pada when the existing calculation produced them.

9A normalizes these existing fields into a transit workbench contract. It does not introduce new transit formulas.

## Calculation settings used by current chart engine

Existing saved/profile settings include:

- `ayanamsa`;
- `node_type` (`true` / `mean` source setting);
- `timezone` / IANA timezone handling;
- latitude and longitude from the saved place or explicit query;
- calculation preset / model;
- ephemeris setting.

The 9A endpoint returns the selected defaults explicitly in the payload.

## Reused UI components

The Transit Workbench reuses:

- shared `ProductShell` and `AppNavigation`;
- existing `D1ChartWorkbench` adapter/renderer;
- existing North/South renderer inside `D1ChartWorkbench`;
- existing `EntityInspector` through the chart workbench;
- existing graha, house and nakshatra data tabs.

No `TransitNorthChart`, `TransitSouthChart` or second inspector should be introduced.

## Missing data / postponed work

Not in 9A:

- natal-transit overlay;
- transit aspects;
- ingress/event boundaries;
- Sade Sati;
- Ashtakavarga;
- dasha + transit synthesis;
- transit interpretations or daily predictions;
- AI generation;
- raw calculation traces in normal UI.

These belong to later stages: 9B calculation contract, 9C overlay, 9D aspects/events.

## Legacy components

- `/transits` previously reused `PrivateHistoryPage` for current-day AI/report history. That is legacy for the transit workbench goal.
- `POST /api/calculations/transits` remains a legacy calculation/report endpoint and is not expanded in 9A.

## Do not rewrite

Do not rewrite formulas in:

- `backend/apps/calculations/chart.py`;
- `backend/apps/calculations/workflows.py`;
- existing varga/dasha engines.

9A is only shell, normalized contract and adapter work.