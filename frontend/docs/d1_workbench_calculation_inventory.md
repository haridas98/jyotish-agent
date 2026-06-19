# D1 Workbench Calculation Inventory

Scope: stage 7A uses only the saved D1 birth chart result. It does not add new formulas.

## Existing data used

- `BirthProfile`: display name, birth date, birth time, time accuracy, place, timezone, calculation settings.
- `ChartCalculation.result`: existing `BirthChart` JSON.
- `BirthChart.ascendant`: Lagna placement.
- `BirthChart.grahas`: graha longitudes, rashis, nakshatras, pada, dignity, retrograde flag, navamsa.
- `BirthChart.houses`: whole-sign house to rashi mapping.

## Adapter responsibility

`buildD1WorkbenchModel(profile, settings, calculationResult)` only converts saved values into a UI read model:

- stable schema version: `d1-workbench.v1`;
- deterministic graha and house ordering;
- entity IDs for grahas, houses, rashis, nakshatras and graha-in-house placements;
- warnings for missing or uncertain data.

## Explicit non-goals

- no AI request, provider, prompt or response;
- no D-chart switching;
- no dasha/transit/yoga workspace;
- no new astrology formulas;
- no raw debug markers in normal UI.