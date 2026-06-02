# JHora Black-Box Audit

## Installed App

- Version: Jagannatha Hora 8.0.
- Executable: `C:\Program Files (x86)\Jagannatha Hora\bin\jhora.exe`.
- Help index: `C:\Program Files (x86)\Jagannatha Hora\bin\jhora.cnt`.
- Ephemeris: `C:\Program Files (x86)\Jagannatha Hora\jhcore\ephe`.
- Atlas: `C:\Program Files (x86)\Jagannatha Hora\jhcore\atlas\jhworld.adb`.
- Sample inputs: `C:\Program Files (x86)\Jagannatha Hora\data\*.jhd`.

## Audit Boundary

JHora is used as a black-box functional and numeric reference only.

Allowed:

- record UI settings;
- enter or import charts;
- export visible outputs;
- compare our calculations against recorded outputs.

Not allowed:

- decompile binaries;
- copy proprietary UI/report text;
- copy proprietary data tables into this repository.

## Found Surface

Help topics show the major parity areas:

- rashi, graha, bhava, varga, karaka, arudha;
- drishti, argala, yogas;
- ashtakavarga, strengths, upagrahas, sahamas;
- Vimsottari, Ashtottari, Kalachakra, Narayana and other dasas;
- transits, Tajaka, Tithi Pravesha, mundane, prasna.

## Input Fixture Import

The backend can now convert JHora `.jhd` inputs into draft fixture JSON.

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_jhora_jhd_inputs `
  "C:\Program Files (x86)\Jagannatha Hora\data" `
  --output-dir .tmp\jhora-input-fixtures
```

These fixtures contain input data only. They are not authoritative until expected results are manually exported from JHora and reviewed.

## First Captured Expected Fixture

`India.jhd` was opened in JHora 8.0 and `Edit -> Copy complete calculations` was captured through the application menu.

Created fixture:

- `backend/apps/calculations/fixtures/accuracy/jhora-india-1947.json`
- source: `jhora_complete_calculations_clipboard`
- review status: `draft`
- captured layers: graha longitudes, Lagna, panchanga, Navamsa column, ashtakavarga, shadbala, Vimshottari raw block.

First parity run:

- rashi, nakshatra and pada matched for grahas and Lagna;
- panchanga yoga and karana matched;
- planet longitudes differ by about 55-99 arcseconds;
- Lagna differs by about 58 arcseconds;
- Rahu/Ketu differ much more, so true/mean node settings must be audited first;
- JHora weekday/tithi naming and sunrise-day handling need a separate normalization check.

## Next Manual Pass

For each priority fixture:

- open the `.jhd` in JHora 8.0;
- record calculation preferences: ayanamsa, node type, sunrise, house/bhava settings, varga options, dasa options;
- export or manually record D1, D9, D60, panchanga, Vimshottari, shadbala, ashtakavarga, yogas and special points;
- add expected values to a fixture JSON;
- run `manage.py run_accuracy_fixtures`;
- keep the fixture `draft` until the diff is reviewed.
