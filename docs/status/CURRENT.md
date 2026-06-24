# Current Project State

Updated: 2026-06-24

## Stable Production Baseline

- Production commit: `8c23a784`
- Branch: `codex/technical-launch-b`
- Latest pushed branch commit: branch tip; run `git log -1 --oneline`
- Production URL: `https://jyotish-agent.duckdns.org/`
- Health: `/api/health` returns `deploy_commit=8c23a784`
- Working tree expected: clean

## Last Completed Milestone

Stage 2 Live Workbench Contract Gate.

Evidence:

- Audit handoff: `docs/handoffs/2026-06-24-technical-core-audit.md`
- Stage 2 handoff: `docs/handoffs/2026-06-24-live-workbench-contract-gate.md`
- Baseline commit audited: `3669f619`
- Production runtime remains `8c23a784`; `/api/health` returns `deploy_commit=8c23a784`.
- D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60 have backend calculation, saved workbench API, frontend switch/display, and automated evidence.
- Focused validation passed: backend varga/chart API/services pytest, real local `smoke:calculator-launch`, `test:launch-readiness`, `test:d1-workbench`, `test:chart-workbench-ux`, `test:chart-detail-smoke`, `test:dasha-workbench`, `typecheck`, `build`, `production-check`.
- `test:launch-readiness` now requires `smoke:calculator-launch` as release evidence for D1-D60 saved workbench scopes and core payload/status markers.
- Runtime code was not changed.

## Latest Non-Deployed Branch Work

Branch commits after the deployed runtime are docs/test-safety/planning work unless a later handoff explicitly says runtime changed.

Known non-deployed branch work:

- `e2b7bded` adds `smoke:launch-status-browser`.
- `d8c40a9e` documents the Stage 1 Technical Core Audit.
- Stage 2 Live Workbench Contract Gate adds test/smoke/docs evidence requiring `smoke:calculator-launch`.
- Current branch tip: run `git log -1 --oneline`.
- Reason not deployed: no production runtime change requiring deploy.

## Active Milestone

Stage 3 planned, not implemented in this supervisor thread.

Next work must start from a fresh session with a single ExecPlan under `docs/exec/`.

UX/UI work must start from a separate design session using `docs/design/` as the source of truth. Do not redesign in this technical supervisor thread.

## Exact Next Action

Run Stage 3 Chart Workflow Hardening in a fresh session after adding a dedicated ExecPlan:

- ExecPlan: create `docs/exec/2026-06-24-03-chart-workflow-hardening.md`
- Prompt: `docs/exec/2026-06-24-session-prompts.md`

Do not implement formulas, AI review, OCR, JH/PL witness work, or UX redesign in the chart workflow hardening milestone.

Recommended next candidates:

- Chart workflow hardening: create/edit/calculate/view/recalculate state contracts and smoke checks.

## Do Not Touch Without New ExecPlan

- Production authentication.
- Raw ASR/audio files.
- Raw Telegram export.
- OCR literature import/runtime citation behavior.
- JH/PL proprietary internals or parity claims.
- Cosmetic redesign or Tailwind/shadcn migration.
- UI implementation without approved visual source and design ExecPlan.

## Session Policy

This long supervisor session should not start another milestone.

New session rule:

1. Read this file.
2. Read the chosen `docs/exec/*.md`.
3. Check git status and current commit.
4. Run baseline checks named in the ExecPlan.
5. Implement only that milestone.
