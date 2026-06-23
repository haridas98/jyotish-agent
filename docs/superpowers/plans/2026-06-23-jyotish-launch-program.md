# Jyotish Launch Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` for implementation tasks. Keep commits focused. Do not invent numbered micro-stages. Do not mix technical calculation, OCR, AI review, and UI redesign in one commit.

**Goal:** Launch a private technical jyotish chart service first, then improve calculation parity, OCR evidence, AI interpretation, and UX in parallel.

**Architecture:** The current codebase already has a Django calculation backend, Next.js frontend, saved chart profiles, varga/dasha/classical payloads, JH/PL witness tooling, and OCR/source policy work. The first launch must expose existing technical calculation output clearly; full AI analysis quality is a later gated track.

**Tech Stack:** Django/DRF, Python 3.12+, optional Swiss Ephemeris/JPL, Next.js 16, React 19, TypeScript, local CSS, pytest, npm checks, Playwright/screenshot smoke where UI changes are made.

---

## Current State

- Active technical worktree: `C:\w\jt-a`.
- Active branch: `codex/technical-launch-b`.
- Latest technical checkpoints:
  - `5e96d8d` saved chart auto-calculate flow and workbench recalculate.
  - `99b1228` calculator-only production AI-worker gate.
  - `7c4bb33` technical graha details and internal JSON snapshot.
  - `47a7187` repeatable calculator launch smoke.
- Current dirty state includes unrelated/in-progress files:
  - `frontend/scripts/check-ai-review-benchmark-parity.mjs`
  - `frontend/src/lib/ai-review-benchmark-parity.ts`
  - `frontend/src/lib/ai-review-quality.ts`
  - `docs/source_policy.md`
  - `docs/jyotish_ocr_chart_policy.md`
  - `tools/`
- Do not mix those dirty files into the technical launch commit unless the task explicitly owns them.
- Existing runnable commands:
  - `.\start-dev.ps1 -Install`
  - `.\start-dev.ps1 -Restart`
  - frontend: `http://127.0.0.1:3130`
  - backend: `http://127.0.0.1:8100`
- Existing calculation APIs:
  - `POST /api/calculations/birth-chart`
  - `POST /api/calculations/dual`
  - `POST /api/charts/profiles/<id>/calculate`
  - `GET /api/charts/<id>/workbench`
  - `GET /api/calculations/witness-summary`
- New launch smoke command:
  - `cd frontend; npm.cmd run smoke:calculator-launch`
  - Requires running backend/frontend and env `JYOTISH_API_BASE_URL`, optionally `JYOTISH_FRONTEND_BASE_URL`.

## Non-Negotiable Decisions

- JH and PL are black-box witnesses, not formula authority.
- Do not decompile/copy proprietary JH/PL code/data.
- Product launch must not wait for full JH/PL parity.
- Telegram export is only a weak competitor-style reference, not calculation truth and not quality authority.
- MP3 consultations are the real quality benchmark for AI review structure, but raw audio/full transcripts stay out of git.
- OCR literature feeds AI as evidence with provenance, not as unverified prose.
- Swiss Ephemeris production use remains licensing-gated.

---

## Track A: Technical Chart Launch

**Objective:** Ship a usable private technical chart viewer before full AI analysis.

**Launch Slice A1: Saved Chart Calculate Flow**

**Files:**
- Modify: `frontend/src/app/charts/new/page.tsx`
- Modify: `frontend/src/app/charts/[id]/page.tsx`
- Modify: `frontend/src/lib/api.ts` only if existing types are insufficient
- Test: `frontend/scripts/check-chart-detail-smoke.mjs`
- Test: `frontend/scripts/check-d1-workbench.mjs`

**Steps:**
- [ ] Add/adjust test so creating a chart is expected to trigger calculation or redirect to a calculable detail page.
- [ ] Verify RED with `cd frontend; npm.cmd run test:chart-detail-smoke`.
- [ ] In `/charts/new`, after `createChartProfile`, call `calculateSavedProfile(profile.id)` before redirect when credentials/session allow it.
- [ ] In `/charts/[id]`, if no latest calculation exists, show a calculate button and auto-safe fallback for fresh profiles.
- [ ] Add a recalculate action that calls `calculateSavedProfile`.
- [ ] Run `npm.cmd run test:chart-detail-smoke`, `npm.cmd run test:d1-workbench`, `npm.cmd run typecheck`.
- [ ] Commit only Track A files.

**Launch Slice A2: Technical Payload Panels**

**Files:**
- Modify: `frontend/src/astrology/d1-workbench.ts`
- Modify: `frontend/src/ui/d1-workbench/D1ChartWorkbench.tsx`
- Modify: `frontend/src/lib/api.ts` if needed
- Test: `frontend/scripts/check-d1-workbench.mjs`
- Test: `frontend/scripts/check-dasha-workbench.mjs`

**Required UI sections:**
- Birth/settings summary.
- Graha table: body, longitude, speed, sign, nakshatra, pada, navamsa, retrograde marker if available.
- Houses and house cusps.
- Varga selector: D1, D9, D10, D12, D30, D60 visible; all supported vargas accessible.
- Panchanga: tithi, vara, yoga, karana, Moon nakshatra.
- Dashas: Vimshottari at least.
- Classical technical payload summary: avastha, vimshopaka, ashtakavarga, shadbala, yogas, argala, special points, with status labels.
- Raw JSON/debug drawer for internal review only.

**Steps:**
- [ ] Add failing checker assertions for the required section markers.
- [ ] Verify RED with `cd frontend; npm.cmd run test:d1-workbench`.
- [ ] Render the sections using existing `BirthChart` payload; do not invent new calculations.
- [ ] Keep mobile readable; no forced wide table as the main mobile path.
- [ ] Run `npm.cmd run test:d1-workbench`, `npm.cmd run test:dasha-workbench`, `npm.cmd run typecheck`, `npm.cmd run build`.
- [ ] Commit only Track A files.

**Launch Slice A3: Calculator-Only Production Gate**

**Files:**
- Modify: `docker-compose.prod.yml` only if calculator launch still starts unnecessary AI workers.
- Modify: `deploy/prod.env.example` only if public calculator mode needs explicit disabled AI flags.
- Test: `frontend/scripts/production-check.mjs`

**Steps:**
- [ ] Check whether production compose can run frontend/backend/db without AI worker.
- [ ] Add a production-check assertion for health, charts page, chart detail/demo, and calculation API availability.
- [ ] Run backend focused tests:
  `cd backend; .\.venv\Scripts\python -m pytest apps/calculations/test_birth_chart.py apps/calculations/test_vargas.py apps/calculations/test_panchanga.py apps/calculations/test_dasha_systems.py apps/calculations/test_classical.py apps/charts/test_api.py apps/charts/test_services.py apps/health/test_health_api.py`
- [ ] Run frontend checks:
  `cd frontend; npm.cmd run typecheck; npm.cmd run test:d1-workbench; npm.cmd run test:chart-detail-smoke; npm.cmd run production-check`
- [ ] Deploy only after explicit deploy checkpoint.

**Current Track A status:**

- [x] A1 saved chart calculate flow implemented and verified locally.
- [x] A2 technical payload panel implemented and verified locally.
- [x] A3 calculator-only AI worker gate implemented.
- [x] Calculator launch smoke added and verified locally against real backend/frontend.
- [ ] Production deploy checkpoint remains pending; do not deploy on every small batch.

---

## Track B: JH/PL Calculation Witness

**Objective:** Make technical calculation differences reviewable and reproducible without treating JH/PL as authority.

**What exists:**
- JH/PL tooling, fixtures, packet reports, witness summary.
- Local JH: `C:\Program Files (x86)\Jagannatha Hora\...`
- Local PL7: `C:\GeoVision\PL7\PL7.exe`
- Current parity is not complete enough to claim full parity.

**Plan:**
- [ ] Freeze comparison settings per case: datetime seconds, timezone/DST evidence, lat/lon, ayanamsha, true/mean node, house/bhava, sunrise source, varga scheme, dasha options, software version.
- [ ] Verify our engine against direct Swiss/JPL before blaming JH/PL differences.
- [ ] Generate/open JH `.jhd`; capture settings screenshots; use “Copy complete calculations”; parse packet.
- [ ] For PL, prefer native export if found; otherwise use manual witness JSON from screenshots.
- [ ] Promote only reviewed packets with reviewer/date/version/settings/artifacts.
- [ ] Target 20 reviewed witness charts before public “parity” claims.

**Acceptance criteria:**
- Core: Lagna + 9 grahas longitude, sign, nakshatra, pada.
- JH tolerance: planets <= 1 arcsec, Lagna <= 5 arcsec.
- PL manual tolerance: <= 60 arcsec unless native export allows tighter.
- Vargas: exact placement for D1/D2/D3/D7/D9/D10/D12/D20/D27/D30/D60.
- Panchanga: exact after normalization.
- Dashas: Vimshottari sequence and dates within 1 day initially.

---

## Track C: OCR Literature Evidence

**Objective:** Turn OCR literature into auditable evidence for AI review, not unverified copied prose.

**Artifact standard:**
- `original/` with source PDF/scan/text copy.
- `pdf_crops/` for chart/table/figure crops.
- `charts/` or `figures/` for generated visual redraws.
- `book.reviewed.md`
- `book.reviewed.html`
- `book.reviewed.json`

**Immediate tasks:**
- [ ] Add OCR artifact validator command/test.
- [ ] Validate required dirs/files, `original_files`, rights/status, chart rows, crop/page refs, QA status.
- [ ] Sync chart layout enum between docs and `tools/jyotish_chart_renderer.py`.
- [ ] Add renderer contract tests for south/north HTML/SVG/agent table.
- [ ] Extend private corpus import to accept reviewed OCR JSON and preserve page/crop/witness metadata.
- [ ] Add tests proving research-only OCR appears in `research_context/source_traces`, not public citations.
- [ ] Add approval path test: approved passage becomes public citation; unapproved OCR never does.

**Acceptance criteria:**
- Bad artifact rejected before import.
- Sample artifact imports as `research_only`.
- AI packet includes provenance chain.
- Public mode cannot quote/cite unapproved OCR.

---

## Track D: AI Review Quality

**Objective:** Produce serious chart reviews grounded in chart facts and literature, using MP3 consultations as quality benchmark.

**Benchmark inputs:**
- `E:\Downloads\Астрологическая_консультация_Харидас_род_1345,_30_апреля_1998,_Стерлитамак.mp3` (~2h41m)
- `E:\Downloads\Говардхан_9_10_утра_10_марта_2000_в_Стерлитамаке_Астрологическая.mp3` (~2h05m)

**Rules:**
- Do not commit raw audio or full transcript.
- Store transient chunks/transcripts under `.tmp/audio-benchmark/` or private corpus only.
- Commit only distilled rubric/schema/checkers if privacy-safe.
- Telegram examples may inform “interesting accents/questions” only.

**Plan:**
- [x] Confirm ASR path: local Whisper/faster-whisper if installed, or API transcription if credentials are available.
- [x] Chunk audio with ffmpeg into 10-15 minute segments.
- [x] Transcribe first 3-5 minutes from each MP3 as proof.
- [x] Full transcription in background.
- [x] Distill non-verbatim benchmark rubric:
  - opening framing;
  - calculation fact chain;
  - major life themes;
  - timing/dasha reasoning;
  - spiritual/devotional framing;
  - question prompts;
  - uncertainty language;
  - what makes the review feel expert.
- [x] Add a deterministic consultation-method contract around `ChartFacts -> Evidence -> ReviewSections -> QualityGate` (`P135-A`) using the sanitized `E134-A` witness.
- [x] Offline quality gate fixtures fail unsupported claims, generic text, copied style, and missing calculation anchors before display.
- [x] Add a deterministic live-composer contract (`E136-A`) that accepts saved-chart `ChartFacts` plus approved source/evidence links and blocks display when source evidence, anchors, caveats, or practical next questions are missing.
- [x] Build the live AI composer path that consumes real saved-chart `ChartFacts` and literature evidence instead of fixture data.
- [x] Add live composer gate tests proving generated reviews cannot display without calculation anchors, source/evidence links, caveats, and practical next questions.

---

## Track E: UX/UI

**Objective:** Make one attractive, usable technical jyotish desk, not many competing demo pages.

**Current frontend facts:**
- Next.js + React + TypeScript.
- No Tailwind/shadcn/lucide currently.
- Heavy CSS debt in global files.
- Better base is `/charts/:id` + `D1ChartWorkbench`, not monolithic `/`.

**Process:**
- [ ] Before redesign, use `product-design:get-context` to create a brief: “technical jyotish consultation desk, not landing page.”
- [ ] Use existing refs:
  - `docs/design/jyotish-main-page-wireframe.html`
  - `docs/design/jyotish-ux-concepts.html`
  - local screenshots in `.tmp-*`
  - JH/PL screenshots for density and workflow, not visual copying.
- [ ] Do not add shadcn/Tailwind immediately.
- [ ] First extract local primitives:
  - `Button`
  - `IconButton`
  - `Tabs`
  - `Panel`
  - `DataTable`
  - `ChartCell`
  - `Inspector`
- [ ] Add `lucide-react` later only if it reduces hand-written SVG/nav debt.

**Minimal UI milestone:**
- `/charts/:id` is canonical chart viewer.
- [x] Add an `E137-A` technical context strip above the chart so scope, coverage, calculation status, and accuracy gate are visible without opening the technical tab.
- First viewport: birth meta, D1 chart, graha table, selected object inspector.
- D chart rail grouped by use: main, family/relationship, profession, expert, all.
- Mobile: chart first, compact graha rows, bottom nav; no giant horizontal table as primary path.
- Visual QA after each UI milestone with desktop/mobile screenshots.

---

## Parallel Execution Model

Run these in parallel because they touch mostly different files:

1. Technical launch worker: Track A only.
2. Audio worker: Track D transcription under `.tmp/audio-benchmark/` only.
3. JH/PL witness worker: Track B artifacts/reports only.
4. OCR worker: Track C validator/renderer/import only.
5. UX worker: Track E design brief/primitives only after Track A has a stable canonical route.

Do not run multiple workers on the same files.

## First Work To Start Now

1. Preserve or isolate the current dirty R2 state.
2. Start Track A Launch Slice A1 in a clean branch/worktree.
3. Continue Track D audio transcription proof in background.
4. Do not deploy until Track A1+A2 checks pass locally.

## Stop Conditions

- Missing ASR/API credentials blocks only audio transcription, not technical launch.
- Swiss Ephemeris licensing blocks public production claims, not private local launch.
- JH/PL mismatch blocks parity claims, not technical viewer launch.
- Dirty unrelated files block in-place commits; use clean worktree or explicitly clean only owned R2 files.
