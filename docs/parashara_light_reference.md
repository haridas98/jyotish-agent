# Parashara Light Reference

Purpose: use Parashara's Light as an additional black-box witness beside JHora. Do not copy proprietary tables or reverse engineer internals; keep captured artifacts private and tied to reviewer notes.

## Local PL7 Session

- Executable: `C:\GeoVision\PL7\PL7.exe`.
- Current observed window: `Parashara's Light 7.0.1 - [Haridas ,  [C:/GeoVision/GeoVisionCharts/Haridas.xml]]`.
- PL7 is a Qt app. Win32/UIA automation exposes most chart panes as generic `QWidget`, so reliable capture starts with window metadata, visible control texts/rectangles, screenshots, and manual/exported calculation text when available.
- Screenshot capture uses Windows `PrintWindow` through pywin32 plus Pillow. This captures the PL window itself even when another app is in front.

## Capture Command

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py capture_parashara_light_ui_state `
  --output ..\.tmp\pl7\haridas-ui-state.json `
  --screenshot ..\.tmp\pl7\haridas-ui-state.png `
  --max-controls 200
```

The JSON includes:

- `window_title`;
- `captured_at`;
- backend/process used for capture;
- control class/type summary;
- visible control text and rectangles;
- `artifact_policy=private_audit_only_do_not_commit`;
- screenshot path or `screenshot_error`;
- `screenshot_blank` so black/empty PrintWindow captures are visible in review.
- SHA256/byte fingerprints in the verification packet so UI JSON and screenshots cannot be mixed silently.

If Pillow is not installed, metadata capture still succeeds and records `screenshot_error`. Keep `.tmp/pl7/` out of git.

Current local smoke artifact:

- `.tmp/pl7/haridas-ui-state.json`;
- `.tmp/pl7/haridas-ui-state.png` - verified nonblank PL7 birth chart screenshot.

## Verification Packet

Build a PL witness packet from the UI-state JSON, screenshots and the same birth input used by the app:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_verification_packet `
  --id pl7-haridas-1998 `
  --birth-date 1998-04-30 `
  --birth-time 13:45:00 `
  --place-name Sterlitamak `
  --timezone Asia/Yekaterinburg `
  --timezone-offset +06:00 `
  --latitude 53.6304 `
  --longitude 55.9502 `
  --pl-ui-state ..\.tmp\pl7\haridas-ui-state.json `
  --screenshot ..\.tmp\pl7\haridas-ui-state.png `
  --manual-witness-values ..\.tmp\pl7\haridas-manual-values.json `
  --output-dir ..\.tmp\pl7\haridas-verification-packet
```

Current local packet smoke:

- `.tmp/pl7/haridas-verification-packet/packet.json`;
- `.tmp/pl7/haridas-verification-packet/fixture.json`;
- `.tmp/pl7/haridas-verification-packet/jyotish-agent-chart.json`;
- `.tmp/pl7/haridas-verification-packet/pl-capture-checklist.md`.

This is a `draft` black-box witness packet. It does not mark PL values as verified and does not parse proprietary internals.

## Manual Witness Values

When PL exposes values through clickable text, copy/export or manual transcription, keep them in a private JSON array and pass it with `--manual-witness-values`.

Create an editable template from the current packet:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_manual_witness_template `
  --packet ..\.tmp\pl7\haridas-verification-packet\packet.json `
  --source pl7 `
  --output ..\.tmp\pl7\haridas-manual-values-template.json
```

Minimal format:

```json
[
  {
    "source": "pl7",
    "body": "Lagna",
    "witness": {
      "status": "pending",
      "rashi": null,
      "nakshatra": null,
      "pada": null,
      "house": null,
      "longitude_dms": null,
      "notes": ""
    },
    "calculated_reference": {
      "rashi": "Karka",
      "nakshatra": "Ashlesha",
      "pada": 3,
      "house": 1,
      "longitude": 115.414369,
      "longitude_dms": "25:24:51.73"
    }
  }
]
```

Supported witness fields for comparison: `rashi`, `nakshatra`, `pada`, `house`, `longitude` or `longitude_dms`. Null or empty witness fields are skipped, so a fresh template does not create false diffs. If `longitude_dms` is supplied with a `rashi`, it is treated as degrees inside that sign. The Accuracy tab shows `matched`, `diff_open`, `no_manual_values` or missing fields.

Compare the filled file without rebuilding the packet:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py compare_manual_witness_values `
  --packet ..\.tmp\pl7\haridas-verification-packet\packet.json `
  --manual-witness-values ..\.tmp\pl7\haridas-manual-values-template.json `
  --output ..\.tmp\pl7\haridas-manual-witness-report.json
```

The Accuracy tab reads this file through `PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH`. If the file is absent, the backend falls back to `fixture.manual_witness_values` inside the packet.
The same panel shows manual completion percent, filled/empty field counts and a short sample of still-empty fields.

Build a repeatable Swiss forensic dump for the same PL witness:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_forensic_dump `
  --packet ..\.tmp\pl7\haridas-verification-packet\packet.json `
  --manual-witness-values ..\.tmp\pl7\haridas-manual-values-from-screenshot.json `
  --output ..\.tmp\pl7\haridas-pl-swiss-forensic-dump.json
```

Current Haridas PL witness status:

- Filled screenshot transcription: `.tmp/pl7/haridas-manual-values-from-screenshot.json`.
- Compare report: `.tmp/pl7/haridas-manual-witness-from-screenshot-report.json`.
- Repeatable forensic report: `.tmp/pl7/haridas-pl-swiss-forensic-dump.json`.
- Result: 50 checked fields, 44 passed, 6 failed, 100% manual completion.
- Failed PL fields: Surya longitude, Mangala longitude, Budha pada/longitude, Guru longitude, Shukra longitude.
- Swiss forensic dump: `.tmp/pl7/swiss-raw-vs-engine-vs-pl7-screenshot.json`.
- Current finding: jyotish-agent graha longitudes match direct Swiss Lahiri sidereal output exactly for this input. The repeatable forensic command reports `engine_swiss_diff_count=0`, `pl_diff_count=5` for longitudes, and `conclusion=engine_matches_swiss_pl_profile_diff_open`; the sixth manual diff is Mercury pada caused by the longitude crossing the Revati pada boundary. The next audit target is PL7 calculation/profile settings rather than the local Swiss wrapper.
- The same forensic dump now rejects simple global offset and time-shift hypotheses: `uniform_offset.status=rejected`, `time_shift.status=rejected`, `next_action=capture_parashara_light_profile_settings`.

## Next Capture Targets

- Birth data/settings screen: date, time, timezone, coordinates, ayanamsa, nodes, house system.
- Main rashi/navamsa chart screen.
- Planet table with signs, houses, nakshatras and degrees.
- Shadbala/strengths tables if PL exposes copyable text.
- Dasha table and current period.
