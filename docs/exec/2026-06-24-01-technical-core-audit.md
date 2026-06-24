# Technical Core Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove which calculation/technical-core features already work, where tests exist, and which single gap should be implemented next.

**Architecture:** This is an audit milestone, not a formula rewrite. The worker must compare backend calculations, saved-chart workbench APIs, frontend visibility, and smoke checks, then write a coverage report. Any discovered implementation gap becomes a future ExecPlan, not an opportunistic patch in this session.

**Tech Stack:** Django/DRF, Next.js, Node checker scripts, pytest, git, repo docs.

---

## Baseline

- Branch: `codex/technical-launch-b`
- Production runtime baseline: `8c23a784`
- Current branch tip: run `git log -1 --oneline`
- Expected working tree: clean

## In Scope

- Audit D-scope coverage for `D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60`.
- Distinguish four confidence levels:
  - backend calculation exists;
  - API/workbench exposes it;
  - frontend displays or can switch to it;
  - tests/smoke verify it.
- Audit grahas, houses, panchanga, dashas, and classical payload status coverage.
- Run existing focused backend/frontend checks.
- Produce one coverage report and one recommended next ExecPlan name.

## Out Of Scope

- Do not implement or change formulas.
- Do not change UX/UI.
- Do not deploy.
- Do not claim JH/PL parity.
- Do not inspect proprietary JH/PL internals.
- Do not touch raw audio, ASR, Telegram, or OCR artifacts.

## Files To Read

- `docs/status/CURRENT.md`
- `docs/roadmap/MASTER_PLAN.md`
- `docs/handoffs/2026-06-24-technical-launch.md`
- `frontend/scripts/smoke-calculator-launch.mjs`
- `frontend/scripts/check-d1-workbench.mjs`
- `frontend/scripts/check-chart-workbench-ux.mjs`
- `frontend/scripts/check-dasha-workbench.mjs`
- `frontend/src/astrology/d1-workbench.ts`
- `frontend/src/ui/d1-workbench/D1ChartWorkbench.tsx`
- `backend/apps/calculations/`
- `backend/apps/charts/`

## Files To Create

- `docs/handoffs/2026-06-24-technical-core-audit.md`

## Files To Modify

- `docs/status/CURRENT.md`

## Read-Only Helper Tasks

Use helpers only if available. They must not edit files.

1. Backend coverage helper:
   - inspect calculation modules and backend tests;
   - report which D scopes and payloads have deterministic backend coverage.
2. Frontend/API helper:
   - inspect workbench adapters, scripts, and UI markers;
   - report whether each scope is exposed and switchable.
3. Test/regression helper:
   - inspect package scripts and smoke coverage;
   - identify missing or duplicate checks.

## Tasks

### Task 1: Baseline Verification

- [ ] Run `git status --short --branch`.
  Expected: clean branch.
- [ ] Run `git log -1 --oneline`.
  Expected: a branch tip on `codex/technical-launch-b`.
- [ ] Run `curl.exe -s --max-time 10 https://jyotish-agent.duckdns.org/api/health`.
  Expected: JSON with `deploy_commit=8c23a784`.

### Task 2: Existing Coverage Inventory

- [ ] Read `frontend/scripts/smoke-calculator-launch.mjs`.
- [ ] Extract the `requiredScopes` list.
- [ ] Search backend/frontend for each D scope:
  - `D1`
  - `D2`
  - `D3`
  - `D4`
  - `D7`
  - `D9`
  - `D10`
  - `D12`
  - `D16`
  - `D20`
  - `D24`
  - `D27`
  - `D30`
  - `D40`
  - `D45`
  - `D60`
- [ ] Build a matrix with columns:
  - scope;
  - backend calculation;
  - saved workbench API;
  - frontend selector/display;
  - automated test/smoke;
  - confidence;
  - evidence file.

### Task 3: Payload Coverage Inventory

- [ ] Audit these payload groups:
  - grahas;
  - houses;
  - house cusps;
  - panchanga;
  - Vimshottari dashas;
  - avasthas;
  - vimshopaka;
  - ashtakavarga;
  - shadbala;
  - yogas;
  - argala;
  - special points.
- [ ] For each group, record:
  - backend source;
  - API exposure;
  - UI/status visibility;
  - test/smoke evidence.

### Task 4: Run Validation

Run these commands and record pass/fail exactly:

```powershell
cd C:\w\jt-a\backend
.\.venv\Scripts\python -m pytest apps/calculations/test_vargas.py apps/charts/test_api.py apps/charts/test_services.py
```

```powershell
cd C:\w\jt-a\frontend
npm.cmd run test:launch-readiness
npm.cmd run test:d1-workbench
npm.cmd run test:chart-workbench-ux
npm.cmd run test:chart-detail-smoke
npm.cmd run test:dasha-workbench
npm.cmd run typecheck
npm.cmd run production-check
```

If a command fails:

- do not fix production code;
- capture the failing command and first meaningful error;
- classify it as blocker or follow-up.

### Task 5: Write Handoff

Create `docs/handoffs/2026-06-24-technical-core-audit.md` with:

- baseline commit;
- production commit;
- validation results;
- D-scope coverage matrix;
- payload coverage matrix;
- confirmed already-done items;
- gaps;
- recommended next single milestone;
- out-of-scope items preserved.

### Task 6: Update Current State

Modify `docs/status/CURRENT.md`:

- set Active milestone to none after audit;
- add latest audit handoff path;
- add exact next action from the audit result;
- keep production baseline `8c23a784` unless a runtime deploy actually happened.

### Task 7: Commit And Stop

- [ ] Run `git diff --check`.
- [ ] Run `git status --short`.
- [ ] Commit only docs changed by this audit.
- [ ] Push branch.
- [ ] Do not start the next milestone.

## Definition Of Done

- Audit report exists.
- `CURRENT.md` points to the report.
- Validation results are recorded.
- No runtime code changes were made.
- One next milestone is named.
- Git status is clean after commit.
