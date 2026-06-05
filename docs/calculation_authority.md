# Calculation Authority Policy

## Authority Order

1. Primary shastra rules and reviewed parampara instruction.
2. Astronomical ephemeris audit: Swiss/JPL, timezone, coordinates, ayanamsa and node settings.
3. JHora and other services as black-box comparison witnesses.
4. Internal regression fixtures.

No formula is changed only because one service disagrees. A change needs either a primary textual source, a documented tradition decision, or a verified settings/profile mismatch.

The machine-readable gate for public interpretation is `shastra_audit` in the birth-chart payload. See `docs/shastra_calculation_audit.md`.

## Cross-Service Audit

Use `external_expected` in accuracy fixtures for service captures:

```json
{
  "external_expected": [
    {
      "id": "vedaansh",
      "name": "Vedaansh",
      "authority_tier": "black_box_service",
      "url": "https://vedaansh.com/",
      "settings": {
        "ayanamsa": "lahiri",
        "node_type": "mean",
        "ephemeris": "swiss"
      },
      "expected": {
        "ashtakavarga": {
          "Su": {
            "Mesha": 6
          }
        },
        "shadbala": {
          "Sun": {
            "shadbala": 343.31
          }
        }
      }
    }
  ]
}
```

The fixture runner stores these under `diagnostics.external_layers`. They do not override shastra-backed formulas.

## Current Ashtakavarga Decision

The implemented BAV/SAV table follows Brihat Jataka chapter IX and the standard 337-bindu total. The Sterlitamak JHora 8.0 fixture now matches 84 of 84 checked Sun-through-Saturn BAV cells. Lagna/Ascendant Ashtakavarga is still skipped until the app implements that row explicitly.

## Sources To Cross-Check

- Brihat Jataka, chapter IX: primary source for Ashtakavarga benefic places.
- Vedaansh (`https://vedaansh.com/`): service witness; claims Swiss Ephemeris and exposes Shadbala/Ashtakavarga.
- Vedic-Horo (`https://vedic-horo.ru/`): service witness; exposes coordinates, timezone, Shadbala, Ashtakavarga and vargas. First raw capture is stored in `vedic-horo-haridev-1998`, but comparison is disabled until the rendered cell order is confirmed.
- AstroSK (`https://astrosk.com/`): service witness candidate; claims Swiss Ephemeris and Lahiri defaults.
- OurNakshatra (`https://ournakshatra.com/`): service witness candidate; claims Swiss Ephemeris and Lahiri/Chitrapaksha.
- SUTRA Jyotish (`https://jyotish-calculator.ru/`): service witness candidate; claims Swiss Ephemeris v2.10 and NASA JPL DE431.
- JHora 8.0: local black-box reference with fixed settings capture.
