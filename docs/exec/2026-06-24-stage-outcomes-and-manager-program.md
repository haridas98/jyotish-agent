# Stage Outcomes And Manager Program

> **For manager sessions:** This document defines the end state for each work line. Managers create worker and verifier sessions; they do not implement or verify their own work.

**Goal:** Keep Jyotish Agent work split into clean, reviewable lines with explicit end states.

**Architecture:** The top-level coordinator creates one manager per line. Each manager creates focused workers and independent verifiers, then reports only stage status and the next single action. Long, polluted sessions must not do detailed code review.

**Tech Stack:** Codex threads, git worktrees, Django/DRF, Next.js, Node smoke scripts, pytest, repo docs.

---

## Operating Rules

- One manager owns one line of work.
- One worker owns one milestone.
- One verifier checks one worker result.
- A manager must not accept its own implementation.
- A worker final must include `READY_FOR_REVIEW`, commit, tests, deploy status, and git status.
- A verifier final must include `VERIFIED` or `REJECTED`, evidence, and exact fix instructions if rejected.
- Do not create one helper per D-chart. Split by responsibility: backend calculation, API persistence, frontend visibility, smoke/test contract, source/witness policy.
- Deploy only after a meaningful runtime batch. Test-only/docs-only commits usually do not deploy.
- JH/PL are witness-only. Never claim parity.
- Raw audio, ASR, Telegram exports, and OCR private corpus files must not be committed.

## Manager Tree

Top-level coordinator:

- creates managers;
- does not inspect detailed diffs;
- only reads manager summaries;
- archives or stops obsolete long supervisor loops.

Managers:

- Calculation / Technical Core Manager;
- Chart Workflow Manager;
- Accuracy Witness Manager;
- AI Review Quality Manager;
- OCR Evidence Manager;
- UX/UI Manager.

Workers:

- implement exactly one ExecPlan;
- may use helper subagents inside the worker session only when useful;
- stop after commit/push.

Verifiers:

- start from clean context;
- check diff, tests, status, production health when relevant;
- do not continue implementation.

## Stage 1: Calculation / Technical Core

### Desired Product Shape

The service must calculate and expose the technical chart without relying on AI interpretation.

Visible to a user or reviewer:

- D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60 availability.
- Grahas, Lagna, houses, house cusps when available.
- Panchanga: tithi, vara, nakshatra, yoga, karana.
- Dashas: at least Vimshottari status and mahadasha rows.
- Classical payload status: avasthas, vimshopaka, ashtakavarga, shadbala, yogas, argala, special points.
- Calculation passport: birth data, coordinates, timezone, ayanamsa, ephemeris, node type, house system, varga scheme, calculation schema/version.
- Status per item: calculated, missing, expert-only, accuracy-gated, or needs source review.

### Current State

Stage 1 audit and Stage 2 live workbench gate are complete on branch history. Stage 2 must be accepted by an independent verifier before new technical work starts.

### Final Done State

- Every technical payload has a visible status and a test or smoke assertion.
- `smoke:calculator-launch` proves real saved-chart calculation and D1-D60 workbench access locally.
- `/launch-status` states which gates were run.
- No JH/PL parity claim.

## Stage 2: Chart Workflow

### Desired Product Shape

A user can create, calculate, view, edit, and recalculate a chart without entering a broken or ambiguous state.

Required states:

- new profile form;
- profile saved but not calculated;
- calculation running or requested;
- calculation complete;
- calculation failed with useful message;
- profile changed after calculation and requires recalculation;
- recalculation complete;
- detail page can render saved calculations;
- edit page preserves calculation assumptions and birth data.

### Final Done State

- Create/edit/calculate/view/recalculate path is covered by local smoke.
- UI labels clearly distinguish saved profile data from calculated result data.
- Failed or stale calculation states are visible.
- No formula, AI, OCR, or cosmetic redesign work is mixed into this line.

## Stage 3: Accuracy Witness

### Desired Product Shape

The project can compare one reviewed case against external tools as witness evidence without claiming authority or parity.

Required packet fields:

- chart input;
- calculation settings;
- external witness tool/version when known;
- reviewer and date;
- tolerances;
- compared fields;
- matched, different, not comparable, or unresolved status;
- artifacts and screenshots if allowed;
- no proprietary internals.

### Final Done State

- One reviewed witness packet exists.
- Source scan proves no parity/success marketing language leaked.
- Differences produce follow-up tasks, not broad formula rewrites.

## Stage 4: AI Review Quality

### Desired Product Shape

AI review uses stable saved-chart facts and cannot show unsupported generic text as a final analysis.

Required behavior:

- draft review receives structured chart facts;
- every key claim has a calculation anchor;
- unsupported sections are blocked or marked draft-only;
- review includes caveats and practical questions;
- review does not pretend literature/OCR evidence is approved unless it is.

### Final Done State

- A deterministic gate blocks generic or unsupported AI output.
- One real saved-chart fixture path exists.
- Audio/Telegram examples remain sanitized witness-only benchmarks.
- No public quality claim.

## Stage 5: OCR Literature Evidence

### Desired Product Shape

Reviewed literature artifacts can become an evidence layer for agents, with provenance and human-readable charts/tables.

Required artifact shape:

```text
book-artifact/
  original/
  raw/
  pdf_crops/ or rendered-pages/
  charts/ or figures/
  review/
  book.reviewed.md
  book.reviewed.html
  book.reviewed.json
```

Required quality:

- HTML is the primary human review artifact.
- Charts/chakras are redrawn as real charts, not OCR garbage.
- Tables are real HTML tables.
- Each visual has an agent/audit table.
- Research-only artifacts cannot become public citations without approval.

### Final Done State

- Bad artifact validator rejects missing provenance, crude OCR charts, or missing `original/`.
- One accepted reviewed sample proves the pipeline.
- OCR work remains separate from technical launch runtime.

## Stage 6: UX/UI

### Desired Product Shape

The interface is a professional technical astrology workbench, not a decorative landing page.

Required shape:

- first viewport shows identity, calculation status, and technical readiness;
- D-scope matrix is readable;
- graha summary is immediately visible;
- technical tab is reachable from payload/status indicators;
- mobile layout keeps chart, table, and inspector usable;
- visual redesign starts only after functional data contracts are stable.

### Final Done State

- UX/UI manager produces audit, brief, and three visual directions before implementation.
- User or designated reviewer selects a direction.
- UI implementation has its own ExecPlan.
- No Tailwind/shadcn migration starts without explicit design plan.

## Stage 7: Production Launch

### Desired Product Shape

Production can honestly show what is deployed and which gates passed.

Required shape:

- `/api/health` exposes `deploy_commit`.
- `/launch-status` shows live health and deploy commit.
- production smoke is read-only by default.
- production write smoke happens only during explicit deploy checkpoints.
- branch docs explain latest deployed and non-deployed commits.

### Final Done State

- Production commit matches expected deploy checkpoint.
- Read-only production smoke checks health, public pages, and technical markers.
- Runtime deploys happen after meaningful batches, not after every tiny edit.

## Immediate Next Action

The Calculation / Technical Core Manager must accept or reject Stage 2 using an independent verifier. If accepted, the next single milestone is Chart Workflow Hardening ExecPlan creation and worker launch.
