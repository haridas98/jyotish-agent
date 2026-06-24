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

Technical chart launch visibility and launch diagnostics.

Evidence:

- `/charts/demo-d1` exposes E149/E150/E151/E152 technical markers.
- `/launch-status` exposes E153 live health/deploy-commit panel.
- Production read-only smoke passed on IP and HTTPS for `8c23a784`.
- Local checks passed for the launch batch: `test:launch-readiness`, `test:d1-workbench`, `test:chart-workbench-ux`, `test:chart-detail-smoke`, `test:dasha-workbench`, `typecheck`, `production-check`, `build`.

## Latest Non-Deployed Commit

`e2b7bded` adds `smoke:launch-status-browser`.

Reason not deployed: test-safety only; production runtime is unchanged from `8c23a784`.

Verified:

- `npm.cmd run test:launch-readiness`
- `npm.cmd run typecheck`
- `npm.cmd run smoke:launch-status-browser`
- `npm.cmd run production-check`

## Active Milestone

None in this thread.

Next work must start from a fresh session with a single ExecPlan under `docs/exec/`.

UX/UI work must start from a separate design session using `docs/design/` as the source of truth. Do not redesign in this technical supervisor thread.

## Exact Next Action

Run Stage 1 Technical Core Audit in a fresh session:

- ExecPlan: `docs/exec/2026-06-24-01-technical-core-audit.md`
- Prompt: `docs/exec/2026-06-24-session-prompts.md`

Do not implement formulas before this audit proves the actual gap.

Recommended next candidates:

- AI review quality: connect real saved-chart facts to gated review output without public quality claims.
- Calculation accuracy witness: add one reviewed JH/PL witness packet without parity claims.
- OCR artifact pipeline: validator for reviewed OCR chart/table artifacts.
- UX/UI design: audit `/charts/:id`, write a design brief, produce three visual directions, and stop for selection before code.

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
