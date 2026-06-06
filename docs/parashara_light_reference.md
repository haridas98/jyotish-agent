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
  --output-dir ..\.tmp\pl7\haridas-verification-packet
```

Current local packet smoke:

- `.tmp/pl7/haridas-verification-packet/packet.json`;
- `.tmp/pl7/haridas-verification-packet/fixture.json`;
- `.tmp/pl7/haridas-verification-packet/jyotish-agent-chart.json`;
- `.tmp/pl7/haridas-verification-packet/pl-capture-checklist.md`.

This is a `draft` black-box witness packet. It does not mark PL values as verified and does not parse proprietary internals.

## Next Capture Targets

- Birth data/settings screen: date, time, timezone, coordinates, ayanamsa, nodes, house system.
- Main rashi/navamsa chart screen.
- Planet table with signs, houses, nakshatras and degrees.
- Shadbala/strengths tables if PL exposes copyable text.
- Dasha table and current period.
