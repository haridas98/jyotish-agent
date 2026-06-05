# JHora UI Reference

Purpose: use JHora as a functional and density reference, not as a source of copied UI assets or proprietary data.

## Local Screenshots

- `.tmp/jhora-reference/jhora-main-printwindow-20260603-195219.png` - correct main JHora window captured via PrintWindow.
- `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/` - verified Sterlitamak reference session, `1998-04-30 13:45:00 +06:00`.
- `.tmp-jhora-front.png` - earlier front-window reference.
- `.tmp-jhora-window.png` - earlier window reference.
- `.tmp-jhora-file-menu.png` - file-menu reference.

The Sterlitamak `1345` series is the current reliable JHora parity reference. Older files remain useful only as secondary visual context.

## Sterlitamak 1998 Capture

Birth input used for this session:

- date/time: `1998-04-30 13:45:00`;
- timezone: `+06:00`, shown in JHora as `6:00:00 (East of GMT)`;
- place: Sterlitamak, Russia;
- coordinates shown by JHora: `55 E 57' 01", 53 N 37' 49"`;
- local packet: `.tmp/jhora/sterlitamak-1998/packet.json`;
- complete calculations export: `.tmp/jhora/sterlitamak-1998/complete-calculations.txt`;
- comparison report for API: `.tmp/jhora/sterlitamak-1998/accuracy-report.json`;
- full fixture-run envelope: `.tmp/jhora/sterlitamak-1998/accuracy-run.json`.
- API/UI summary: `GET /api/calculations/jhora-accuracy`, shown in the web app `Accuracy` tab.
- Django default report path now points to this local report unless `JHORA_ACCURACY_REPORT_PATH` overrides it.

## JHora Screenshot/Export Inventory

Use this checklist when preparing visual references and calculation fixtures. For every captured screen, keep the screenshot path, JHora profile/settings, and any exported/copied table text together.

### 1. Tabs

- [x] Main workspace / Chakras: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-04-chakras-main.png`.
- [x] Basics: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-05-basics.png`.
- [x] Strengths: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-06-strengths.png`.
- [x] Strengths / Other strengths: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-06-strengths-other-2.png`.
- [x] Dasas: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-07-dasas.png`.
- [x] Transits: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-10-transits.png`.
- [x] Tajaka and Tithi Pravesha: `jhora-sterlitamak-1345-11-tajaka.png`, `jhora-sterlitamak-1345-12-tithi-pravesha.png`.
- [x] Mundane and Miscellany: `jhora-sterlitamak-1345-13-mundane.png`, `jhora-sterlitamak-1345-09-miscellany.png`.

### 2. Settings

- [x] Ayanamsa offset from export: `23-49-04.82`.
- [ ] Node mode: true/mean Rahu and Ketu.
- [ ] House/bhava system and chart style.
- [x] Siddhanta menu captured: `.tmp/jhora-reference/session-20260604/sterlitamak-tabs/jhora-sterlitamak-03-siddhanta-dialog-keyboard.png`.
- [x] Preferences calculation submenu captured: `.tmp/jhora-reference/session-20260604/sterlitamak-tabs/jhora-sterlitamak-02-preferences-related-calculations-menu.png`.
- [x] Current `jhora.ini` copied locally: `.tmp/jhora/sterlitamak-1998/jhora.ini`.
- [x] Calculation dialogs captured as Win32 JSON: `.tmp/jhora/sterlitamak-1998/dialogs/`.
- [x] Birth timezone, DST handling, longitude/latitude and place source captured through export and screenshots.
- [x] Non-default divisional chart options: `HoraPreference=6` / JHora `D-2 (US)` Uma-Shambhu profile.
- [x] Display/export format used for copied table: `Edit -> Copy complete calculations`.

### 3. Numerical Fixture Data

- [x] Lagna, graha longitudes, signs, nakshatras, padas and retrograde flags.
- [x] Varga placements for D2, D3, D7, D9, D12, D30 and D60 checked from JHora ASCII charts; implemented D2 Uma-Shambhu profile matches the JHora `D-2 (US)` chart.
- [x] Tithi, vara, nakshatra, yoga, karana and sunrise/sunset values.
- [x] Vimshottari mahadasha names with start dates.
- [x] Shadbala and vimshopaka totals where visible/exported.
- [x] Ashtakavarga bindu counts by graha/sign and sarvashtakavarga totals.
- [x] Upagrahas, special lagnas and right-side table values shown on the main screen.

### 4. Main Screenshot Status

- [x] Main screenshot captured: `.tmp/jhora-reference/session-20260604/sterlitamak-1345-tabs/jhora-sterlitamak-1345-04-chakras-main.png`.
- [x] Export/copy text recorded: `.tmp/jhora/sterlitamak-1998/complete-calculations.txt`.

## Observed Layout

- Left workspace shows several charts at once: Rasi, Navamsa D9, Trimsamsa D30, Drekkana D3, Dasamsa D10, Shashtyamsa D60.
- Right side keeps dense tabular data: planets, special lagna/points, upagrahas and panchanga-like values.
- Bottom area combines key birth information, panchanga and ashtakavarga/bala-style summaries.
- Top navigation is tab-like and compact: Chakras, Basics, Strengths, Dasas, Transits, Tajaka, Tithi Pravesha, Mundane, Miscellany.
- Overall density is high: small rows, small headings, many simultaneous panels.

## Product Direction

The web UI should not become one long page. It should use a compact analytical workspace:

- primary chart + quick varga snapshot;
- tabbed calculation areas;
- dense tables for grahas, vargas, dashas, strengths and classical factors;
- separate report view for human-readable interpretation;
- separate source/review view for shastra evidence.

## Missing Screens To Capture

- Ashtakavarga views.
- Muhurta/prashna related screens.
- Settings dialogs: ayanamsa, node type, DST/timezone, chart style.
- Detailed shadbala component table, if JHora exposes a deeper table beyond bar charts/export. The captured `Other strengths` and `Bar graphs` subtabs show totals, vimshopaka totals, active yogas and summary graphs, not full Sthana/Dig/Kala/Chesta/Drik components.

## Dual Calculation Mode

First pass implemented in the app as a trust/audit feature:

1. `primary_calculation` - Jyotish Agent calculation with explicit settings.
2. `jhora_profile_calculation` - reproduction attempt with the captured JHora profile settings.
3. `delta` - exact differences by graha, lagna, nakshatra, dasha, varga and bala component.
4. `settings_diff` - ayanamsa, nodes, timezone, house/bhava, siddhanta, sunrise method.
5. `authority_decision` - why the service accepts the primary value, follows JHora, or marks the item for review.

Current limitation: `jhora_profile_calculation` is still our engine with a JHora-like settings profile, not a copied JHora export. The `Accuracy` tab shows the real captured JHora export diff from `.tmp/jhora/sterlitamak-1998/accuracy-report.json`.

For the Sterlitamak packet, the current primary reason for longitude mismatch is visible in diagnostics: JHora export uses ayanamsa `23-49-04.82`, while the Swiss Lahiri value in the backend is about `23-50-01.78`, a delta of about `56.57"`; after that correction, the maximum longitude delta drops to about `37.49"`.

The rebuilt chart now records `ephemeris_engine` per graha. In the current local setup it is `swiss`, using local `.tmp/swisseph/ephe/*.se1` files configured through `.env`.

For this JHora packet, `sunrise_source=swiss_center_no_refraction` is required. It reproduces JHora's sunrise/sunset profile closely enough for Gulika, Maandi, Indu Lagna and the solar upagrahas. Bhava/Hora/Ghati Lagna are now matched by one recorded time-lagna profile correction: `surya_at_sunrise_plus_elapsed_ghati`.

Current layer decisions from the real export:

- Panchanga: 4 checked, 4 matched, 0 failed after name alias normalization (`Sukla/Shukla`, `Sukarman/Sukarma`, weekday names).
- Ashtakavarga: 84 checked, 84 matched, 0 failed; Lagna row skipped because the app does not implement that row yet.
- Special points: 11 checked, 11 matched, 0 failed; 35 broader JHora points skipped because they are not implemented yet.
- Active yogas from JHora `Other strengths`: 13 checked, 13 matched, 0 failed. The captured rows are stored in `.tmp/jhora/sterlitamak-1998/ui-tables-strengths-bargraphs.json`.
- Vargas D2-D60: 300 checked, 300 matched, 0 failed across captured JHora ASCII charts.
- Shadbala: 7 checked, 0 matched, 7 failed; max delta 61.46 virupas. Component formulas are more source-backed now, but component-level audit remains open because JHora totals are captured while full internal components are not exposed in the current screenshots/export.
- Vimshopaka: 36 checked, 36 matched, 0 failed; max delta 0.01. BPHS Varga Viswa weights and the JHora-matched Rahu/Ketu dignity profile are now in the engine.

This is required because astrologers may distrust a new service even when the astronomy is more precise than JHora.
