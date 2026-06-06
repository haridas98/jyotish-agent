# Parashara Light Reference

Purpose: use Parashara's Light as an additional black-box witness beside JHora. Do not copy proprietary tables or reverse engineer internals; keep captured artifacts private and tied to reviewer notes.

## Local PL7 Session

- Executable: `C:\GeoVision\PL7\PL7.exe`.
- Current observed window: `Parashara's Light 7.0.1 - [Haridas ,  [C:/GeoVision/GeoVisionCharts/Haridas.xml]]`.
- PL7 is a Qt app. Win32/UIA automation exposes most chart panes as generic `QWidget`, so reliable capture starts with window metadata, visible control texts/rectangles, screenshots, and manual/exported calculation text when available.

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
- screenshot path or `screenshot_error`.

If Pillow is not installed, metadata capture still succeeds and records `screenshot_error`. Keep `.tmp/pl7/` out of git.

## Next Capture Targets

- Birth data/settings screen: date, time, timezone, coordinates, ayanamsa, nodes, house system.
- Main rashi/navamsa chart screen.
- Planet table with signs, houses, nakshatras and degrees.
- Shadbala/strengths tables if PL exposes copyable text.
- Dasha table and current period.
