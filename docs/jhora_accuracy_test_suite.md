# JHora Accuracy Test Suite

## Fixture Groups

- 20 modern charts with exact timezone.
- 20 historical charts before 1900.
- 20 charts near DST transitions.
- 20 charts near rashi, nakshatra, or varga boundaries.
- 20 public teaching examples.
- 20 manually verified JHora comparison charts.

## Metrics

- Planet longitude: arcsecond delta.
- Lagna: arcsecond delta.
- Rashi: exact sign match.
- Nakshatra and pada: exact match.
- Varga placements: exact match.
- Dasha period starts and ends: configured time tolerance.
- Panchanga transitions: configured time tolerance.

## Required Metadata

Each fixture must include:

- source;
- permission status;
- birth date and time;
- birthplace and coordinates;
- timezone source;
- JHora version;
- JHora settings;
- Jyotish Agent calculation version.

