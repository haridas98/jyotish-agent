# Live Workbench Contract Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:subagent-driven-development for helper/review flow or superpowers:executing-plans for a fresh-session implementation. Track tasks with checkbox (`- [ ]`) syntax.

**Goal:** Make the real saved-chart calculator smoke (`npm.cmd run smoke:calculator-launch`) a required launch evidence gate for D1-D60 scopes and core technical payloads.

**Architecture:** This is a test/contract milestone. Do not rewrite formulas, redesign UI, or add broad product features. The worker should harden the release contract so the project cannot claim technical launch readiness without running the API-backed saved-chart workflow.

**Tech Stack:** Next.js frontend scripts, Node checker scripts, Django API, existing local dev startup script, repo docs.

---

## Baseline

- Branch: `codex/technical-launch-b`
- Production runtime baseline: `8c23a784`
- Latest audit commit: `d8c40a9e`
- Expected working tree: clean
- Runtime deploy expected: no, unless this milestone changes runtime behavior and all checks pass

## In Scope

- Require `smoke:calculator-launch` as first-class launch evidence in the local launch-readiness contract.
- Ensure the smoke covers:
  - create chart profile;
  - calculate saved chart;
  - saved chart detail;
  - saved workbench API for D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60;
  - frontend pages `/charts/new`, real `/charts/{id}`, `/charts/{id}/edit`, `/charts/demo-d1`, `/launch-status` when a frontend URL is provided;
  - visible technical markers E145/E146/E149/E150/E151/E152/E153.
- Add or tighten a lightweight contract test so future edits cannot remove the calculator smoke from release evidence.
- Update docs/status handoff with the exact commands and results.

## Out Of Scope

- Formula rewrites.
- UX/UI redesign.
- JH/PL parity claims.
- Raw audio, ASR, Telegram, or OCR artifacts.
- Production user/chart creation outside an explicit deploy checkpoint.
- Deploying a test-only/docs-only change.

## Files To Read

- `docs/status/CURRENT.md`
- `docs/handoffs/2026-06-24-technical-core-audit.md`
- `docs/exec/2026-06-24-functional-stage-program.md`
- `frontend/package.json`
- `frontend/scripts/check-launch-readiness-contract.mjs`
- `frontend/scripts/smoke-calculator-launch.mjs`
- `frontend/scripts/smoke-production-live.mjs`
- `start-dev.ps1`

## Likely Files To Modify

- `frontend/scripts/check-launch-readiness-contract.mjs`
- `frontend/package.json` only if a clearer named script is needed
- `docs/status/CURRENT.md`
- new handoff: `docs/handoffs/2026-06-24-live-workbench-contract-gate.md`

Do not modify runtime source unless the smoke exposes a real runtime failure that blocks the gate.

## Tasks

### Task 1: Baseline Verification

- [ ] Run `git status --short --branch`.
- [ ] Run `git log -1 --oneline`.
- [ ] Run production health:

```powershell
curl.exe -s --max-time 10 https://jyotish-agent.duckdns.org/api/health
```

Expected: JSON with `deploy_commit=8c23a784` unless `docs/status/CURRENT.md` names a newer deployed commit.

### Task 2: Contract Inventory

- [ ] Inspect `frontend/package.json`.
- [ ] Confirm scripts exist:
  - `test:launch-readiness`
  - `smoke:calculator-launch`
  - `smoke:production-live`
  - `production-check`
- [ ] Inspect `frontend/scripts/check-launch-readiness-contract.mjs`.
- [ ] Identify whether `smoke:calculator-launch` is only mentioned or genuinely required as release evidence.
- [ ] Inspect `frontend/scripts/smoke-calculator-launch.mjs` and confirm its required scopes and payload assertions.

### Task 3: Add The Missing Gate

- [ ] Add the smallest possible test/contract change so `test:launch-readiness` fails if:
  - `smoke:calculator-launch` is removed from `package.json`;
  - `smoke-calculator-launch.mjs` stops checking all required D scopes;
  - the smoke stops checking saved-chart creation/calculation/workbench flow;
  - the smoke stops checking core payload status markers.
- [ ] If useful, add a separate named script for the live-workbench contract, but keep `test:launch-readiness` as the umbrella gate.
- [ ] Keep local and production read-only checks separate:
  - local smoke may create a local test user/chart;
  - production read-only smoke must not create production users/charts.

### Task 4: Run Required Validation

Run:

```powershell
cd C:\w\jt-a\frontend
npm.cmd run test:launch-readiness
npm.cmd run production-check
```

Run the real calculator smoke against local services. If services are not running, use the repo script to start or verify them first:

```powershell
cd C:\w\jt-a
.\start-dev.ps1 -CheckOnly -BackendPort 18110 -FrontendPort 3131
```

Then run:

```powershell
cd C:\w\jt-a\frontend
npm.cmd run smoke:calculator-launch
```

If the smoke needs explicit URLs, use the local backend/frontend URLs from the running services.

Also run:

```powershell
cd C:\w\jt-a\frontend
npm.cmd run typecheck
npm.cmd run build
```

If runtime source changed, additionally run the relevant backend pytest command from the audit handoff.

### Task 5: Write Handoff

Create `docs/handoffs/2026-06-24-live-workbench-contract-gate.md` with:

- baseline commit and production commit;
- whether runtime code changed;
- exact contract change;
- exact validation commands and results;
- local smoke evidence:
  - checked D scopes;
  - checked API workflow;
  - checked frontend pages or why frontend URL was not used;
- production read-only health status;
- next recommended milestone.

### Task 6: Update Current State

Update `docs/status/CURRENT.md`:

- set last completed milestone to Stage 2 after completion;
- point to the new handoff;
- keep production baseline unchanged unless a deploy actually happened;
- name one next milestone only.

### Task 7: Commit And Stop

- [ ] Run `git diff --check`.
- [ ] Run `git status --short`.
- [ ] Commit the focused changes.
- [ ] Push `codex/technical-launch-b`.
- [ ] Stop. Do not start formula work, UX/UI work, or deploy follow-up in the same session.

## Definition Of Done

- `test:launch-readiness` protects the real saved-chart calculator smoke as required release evidence.
- `smoke:calculator-launch` has been run locally and the result is recorded.
- No production write smoke was run.
- Handoff and `CURRENT.md` are updated.
- Git status is clean after commit.
