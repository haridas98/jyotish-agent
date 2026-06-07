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

After manual review confirms UI-state, screenshots, settings evidence and copied/manual values, mark the packet reviewed:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py mark_parashara_light_witness_reviewed `
  ..\.tmp\pl7\haridas-verification-packet `
  --reviewer Haridas `
  --reviewed-at 2026-06-07T12:30:00+05:00
```

The command refuses incomplete packets unless `--force` is passed.

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
- Birth timezone audit: `1998-04-30 13:45:00 Asia/Yekaterinburg` resolves to `+06:00` with DST observed and UTC `1998-04-30T07:45:00+00:00`.
- Result: 50 checked fields, 44 passed, 6 failed, 100% manual completion.
- Failed PL fields: Surya longitude, Mangala longitude, Budha pada/longitude, Guru longitude, Shukra longitude.
- Swiss forensic dump: `.tmp/pl7/swiss-raw-vs-engine-vs-pl7-screenshot.json`.
- Current finding: jyotish-agent graha longitudes match direct Swiss Lahiri sidereal output exactly for this input. The repeatable forensic command reports `engine_swiss_diff_count=0`, `pl_diff_count=5` for longitudes, and `conclusion=engine_matches_swiss_pl_profile_diff_open`; the sixth manual diff is Mercury pada caused by the longitude crossing the Revati pada boundary. The next audit target is PL7 calculation/profile settings rather than the local Swiss wrapper.
- The same forensic dump now rejects simple global offset and time-shift hypotheses: `uniform_offset.status=rejected`, `time_shift.status=rejected`, `next_action=capture_parashara_light_profile_settings`.
- The Accuracy tab now includes the timezone audit and forensic dump through `GET /api/calculations/witness-summary`. It exposes only aggregate audit signals: DST/UTC offset, conclusion, PL diff count, max deviation, rejected hypotheses and next action.

Build a safe PL7 settings evidence manifest without parsing proprietary option/session formats:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_settings_evidence `
  --chart-xml C:\GeoVision\GeoVisionCharts\Haridas.xml `
  --options-dir C:\GeoVision\GeoVisionOptions `
  --pl7-dir C:\GeoVision\PL7 `
  --session-token-limit 40 `
  --output ..\.tmp\pl7\haridas-pl-settings-evidence.json
```

Current local settings evidence:

- Report: `.tmp/pl7/haridas-pl-settings-evidence.json`.
- Captured 238 option-file hashes, 40 opaque `.e31` session-token hashes and 4 safe text runtime artifacts.
- Policy: `hash_only_do_not_parse` for proprietary `.dat`, `.bin`, `.wsl` and `.e31` artifacts.
- The Accuracy tab exposes only aggregate counts and PL runtime build under `parashara_light.settings_evidence`; raw manifests remain private.

Build a visible PL7 settings capture packet from UI-state JSON and screenshots:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_visible_settings_capture `
  --id pl7-haridas-visible-settings-20260606 `
  --ui-state ..\.tmp\pl7\visible-settings-attempt-ui-state.json `
  --ui-state ..\.tmp\pl7\options-coordinate-menu-ui-state.json `
  --ui-state ..\.tmp\pl7\calculation-options-keyboard-ui-state.json `
  --screenshot ..\.tmp\pl7\visible-settings-attempt.png `
  --screenshot ..\.tmp\pl7\options-coordinate-menu.png `
  --screenshot ..\.tmp\pl7\calculation-options-keyboard.png `
  --output ..\.tmp\pl7\haridas-pl-visible-settings-capture.json
```

Current visible settings capture:

- Report: `.tmp/pl7/haridas-pl-visible-settings-capture.json`.
- Status: `menu_path_captured_settings_dialog_pending`.
- Captured 3 screenshots and 3 UI-state files, including the visible `Options` menu path.
- The `Calculation options` dialog still needs either reliable UI capture or a native PL export; the packet keeps that as `next_action=capture_calculation_options_dialog_or_native_export`.

Build a PL7 birth XML profile report from the installed chart file:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_profile_report `
  --birth-xml C:\GeoVision\GeoVisionCharts\Haridas.xml `
  --packet ..\.tmp\pl7\haridas-verification-packet\packet.json `
  --output ..\.tmp\pl7\haridas-pl-profile-report.json
```

Current local profile report:

- Report: `.tmp/pl7/haridas-pl-profile-report.json`.
- PL raw XML stores `Longitude=-55.9666667`, `Latitude=53.6166667`, `TimeZone=-5`, `DST=1`.
- Candidate normalization records `longitude_east_candidate=55.9666667` and `timezone_offset_hours_candidate=6.0`; these are convention candidates, not silent corrections.
- Compared with the app packet, timezone delta is `0.0h`; coordinate deltas are `+0.016467°` longitude and `-0.013733°` latitude.
- Finding: the PL chart XML explains PL's east-negative storage convention and a small coordinate variance, but it does not explain the observed graha longitude differences. Detailed PL7 calculation/profile settings remain the next audit target.
- The Accuracy tab now includes this profile through `GET /api/calculations/witness-summary` under `parashara_light.profile`. It is marked `authoritative=false`; `candidate_normalization` is shown only as audit context.

Build the consolidated PL7 internal settings audit from the visible settings, preferences, hidden option-store and option-store diff reports:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_parashara_light_internal_settings_audit `
  --settings-aware-forensic ..\.tmp\pl7\haridas-pl-settings-aware-forensic.json `
  --preferences-inventory ..\.tmp\pl7\haridas-pl-preferences-inventory.json `
  --hidden-option-store ..\.tmp\pl7\haridas-pl-hidden-option-store.json `
  --option-store-diff ..\.tmp\pl7\haridas-pl-option-store-diff.json `
  --output ..\.tmp\pl7\haridas-pl-internal-settings-audit.json
```

Current internal settings audit:

- Report: `.tmp/pl7/haridas-pl-internal-settings-audit.json`.
- Policy: private audit only; proprietary PL option bytes stay hash-only and are not parsed.
- The Accuracy tab exposes this as `parashara_light.internal_settings_audit` with status, evidence gates, ruled-out count and next action.
- If visible settings do not explain the PL diff and the option-store probe is inconclusive, the next action is `capture_pl_native_export_or_internal_ephemeris_mode`.

## Next Capture Targets

- Birth data/settings screen: date, time, timezone, coordinates, ayanamsa, nodes, house system.
- Main rashi/navamsa chart screen.
- Planet table with signs, houses, nakshatras and degrees.
- Shadbala/strengths tables if PL exposes copyable text.
- Dasha table and current period.
