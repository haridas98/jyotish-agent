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

## Implemented Harness

The backend now has a first fixture comparison layer in `apps.calculations.accuracy`:

- `compare_longitude` for shortest angular delta in arcseconds;
- `compare_chart_to_fixture` for graha longitude, Lagna longitude, rashi, nakshatra, pada, and panchanga exact matches.
- `run_accuracy_fixtures` management command for local and CI fixture runs.

This is a harness only. A case is not authoritative until the expected values come from a recorded JHora export or another reviewed source.

JHora `.jhd` sample inputs can be converted into draft fixtures:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_jhora_jhd_inputs `
  "C:\Program Files (x86)\Jagannatha Hora\data" `
  --output-dir .tmp\jhora-input-fixtures
```

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

Minimal expected data shape:

```json
{
  "id": "jhora-case-id",
  "tolerances": {
    "planet_longitude_arcseconds": 1.0,
    "lagna_arcseconds": 5.0
  },
  "expected": {
    "grahas": {
      "Surya": {
        "longitude": 118.3909,
        "rashi": "Karka",
        "nakshatra": "Ashlesha",
        "pada": 4
      }
    },
    "ascendant": {
      "longitude": 154.0,
      "rashi": "Kanya"
    },
    "panchanga": {
      "tithi": "Dashami",
      "vara": "Budhavara",
      "yoga": "Vyaghata",
      "karana": "Vanija"
    }
  }
}
```
