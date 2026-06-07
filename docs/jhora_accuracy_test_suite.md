# JHora Accuracy Test Suite

## Fixture Groups

- 20 modern charts with exact timezone.
- 20 historical charts before 1900.
- 20 charts near DST transitions.
- 20 charts near rashi, nakshatra, or varga boundaries.
- 20 public teaching examples.
- 20 manually verified JHora comparison charts.

Current authoritative JHora fixture count: 0. Existing fixtures are smoke/audit material until a recorded JHora export or screenshot packet is attached and reviewed.

Current batch audit command:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py audit_jhora_witness_batch
```

The audit scans `.tmp\jhora` and `.tmp\pl7`, matches packet/fixture artifacts to the 20-chart target queue, and reports:

- candidate suite size;
- authoritative-ready count;
- capture-started count;
- Parashara Light witness count;
- next case ids still needing reviewed evidence.

As of 2026-06-07 local artifacts, the queue has 21 candidate cases, target reviewed count is 20, Sterlitamak capture has started, one PL witness is attached by birth data, and authoritative-ready count is still 0.

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

JHora verification packets can be created before the real export is attached. These packets keep the case in
`capture_pending`/`draft` status and include our chart, dual-calculation witness, tolerances and a screenshot/export checklist:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py capture_jhora_complete_export `
  --launch-jhd ..\.tmp\jhora\sterlitamak-1998\sterlitamak-1998.jhd `
  --output ..\.tmp\jhora\sterlitamak-1998\complete-calculations.txt `
  --expected-timezone-offset +06:00
```

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_jhora_verification_packet `
  --id sterlitamak-1998-04-30-1345 `
  --birth-date 1998-04-30 `
  --birth-time 13:45:00 `
  --place-name Sterlitamak `
  --timezone Asia/Yekaterinburg `
  --timezone-offset +06:00 `
  --latitude 53.6304 `
  --longitude 55.9502 `
  --calculation-model drik_siddhanta `
  --ayanamsa lahiri `
  --node-type mean `
  --output-dir ..\.tmp\jhora\sterlitamak-1998
```

For copied/clicked JHora values that are not part of a full export yet, use the shared manual witness flow:

```powershell
.\.venv\Scripts\python manage.py build_manual_witness_template `
  --packet .tmp\jhora\sterlitamak-1998\verification-packet\packet.json `
  --source jhora `
  --output .tmp\jhora\sterlitamak-1998\manual-values-template.json

.\.venv\Scripts\python manage.py compare_manual_witness_values `
  --packet .tmp\jhora\sterlitamak-1998\verification-packet\packet.json `
  --manual-witness-values .tmp\jhora\sterlitamak-1998\manual-values-template.json `
  --output .tmp\jhora\sterlitamak-1998\manual-witness-report.json
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

For JHora parity, also record:

- JHora calculation model: Drik Siddhanta or SSS;
- true or mean nodes;
- timezone/DST source used by JHora;
- export/screenshot paths for each captured tab.

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
