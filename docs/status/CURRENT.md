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

Stage 3 Chart Workflow Hardening.

Evidence:

- Audit handoff: `docs/handoffs/2026-06-24-technical-core-audit.md`
- Stage 2 handoff: `docs/handoffs/2026-06-24-live-workbench-contract-gate.md`
- Stage 3 handoff: `docs/handoffs/2026-06-24-chart-workflow-hardening.md`
- Baseline commit audited: `3669f619`
- Production runtime remains `8c23a784`; `/api/health` returns `deploy_commit=8c23a784`.
- D1/D2/D3/D4/D7/D9/D10/D12/D16/D20/D24/D27/D30/D40/D45/D60 have backend calculation, saved workbench API, frontend switch/display, and automated evidence.
- Chart workflow state contract is explicit for saved/not calculated, calculation requested, complete, failed, stale, and recalculated states.
- Focused validation passed: backend chart API pytest, real local `smoke:calculator-launch`, real local `smoke:chart-workflow`, `test:launch-readiness`, `test:chart-detail-smoke`, `typecheck`, `build`, `production-check`.
- `test:launch-readiness` now requires `smoke:calculator-launch` as release evidence for D1-D60 saved workbench scopes and core payload/status markers.
- Runtime code changed on branch only; production was not deployed.

## Latest Non-Deployed Branch Work

Branch commits after the deployed runtime are docs/test-safety/planning work unless a later handoff explicitly says runtime changed.

Known non-deployed branch work:

- `e2b7bded` adds `smoke:launch-status-browser`.
- `d8c40a9e` documents the Stage 1 Technical Core Audit.
- Stage 2 Live Workbench Contract Gate adds test/smoke/docs evidence requiring `smoke:calculator-launch`.
- Current branch tip: run `git log -1 --oneline`.
- Reason not deployed: no production runtime change requiring deploy.

## Active Milestone

AI Review Quality Saved Chart Grounding Gate is implemented and ready for independent verifier review.

Evidence:

- ExecPlan: `docs/exec/2026-06-24-ai-review-quality-saved-chart-gate.md`
- Handoff: `docs/handoffs/2026-06-24-ai-review-saved-chart-grounding-gate.md`
- Fixture: `frontend/src/data/ai-review-saved-chart-fixture.json`
- Gate script: `frontend/scripts/check-ai-review-saved-chart-gate.mjs`
- Named package script: `test:ai-review-saved-chart-gate`
- `test:ai-review-quality` runs the existing harness plus the saved-chart gate.

Production was not deployed.

Next work must start from a fresh session with a single ExecPlan under `docs/exec/`.

UX/UI work must start from a separate design session using `docs/design/` as the source of truth. Do not redesign in this technical supervisor thread.

## Exact Next Action

Independent verifier should review AI Review Saved Chart Grounding Gate output:

- ExecPlan: `docs/exec/2026-06-24-ai-review-quality-saved-chart-gate.md`
- Handoff: `docs/handoffs/2026-06-24-ai-review-saved-chart-grounding-gate.md`
- Base milestone: `48e4b896fea184a53e748672cf85a0e682a9c124`

After this gate is accepted, choose the next single milestone through the manager tree.

Do not implement formulas, AI review, OCR, JH/PL witness work, or UX redesign in this verification step.

Recommended next candidates:

- Accuracy Witness or another manager-selected single ExecPlan after gate verifier acceptance.

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
