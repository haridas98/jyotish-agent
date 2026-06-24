# Handoff: Live Workbench Contract Gate

Date: 2026-06-24

## Outcome

Stage 2 Live Workbench Contract Gate is complete.

Baseline:

- Branch target: `codex/technical-launch-b`
- Start commit: `f290ddbf` (`Plan live workbench contract gate`)
- Production runtime commit: `8c23a784`
- Production health: `https://jyotish-agent.duckdns.org/api/health` returned `deploy_commit=8c23a784`
- Runtime code changed: no
- Deploy performed: no

## Contract Change

- `frontend/scripts/check-launch-readiness-contract.mjs` now requires `package.json` to keep `smoke:calculator-launch` wired to `node scripts/smoke-calculator-launch.mjs`.
- The same contract now requires the calculator smoke to keep the exact D1-D60 scope list and the saved-chart create/calculate/detail/workbench workflow markers.
- `frontend/scripts/smoke-calculator-launch.mjs` now checks the full technical payload/status marker set on `/charts/demo-d1`: E145/E146/E149/E150/E151/E152 and launch status E153, including technical payload index, classical status rows, and dasha period-window status.

## Validation

Commands run from `C:\Users\Admin\.codex\worktrees\d1e2\jyotish-agent\frontend` unless noted.

| Command | Result |
|---|---|
| `git status --short --branch` | clean at start, detached HEAD at `f290ddbf` |
| `git log -1 --oneline` | `f290ddbf Plan live workbench contract gate` |
| `curl.exe -s --max-time 10 https://jyotish-agent.duckdns.org/api/health` | PASS: `deploy_commit=8c23a784` |
| `npm.cmd run test:launch-readiness` after adding RED contract only | expected FAIL: missing `E146-A` in calculator smoke |
| `npm.cmd run test:launch-readiness` after smoke hardening | PASS |
| `cd C:\w\jt-a; .\start-dev.ps1 -CheckOnly -BackendPort 18110 -FrontendPort 3131` | PASS: dependencies present |
| `JYOTISH_API_BASE_URL=http://127.0.0.1:18110; JYOTISH_FRONTEND_BASE_URL=http://127.0.0.1:3131; npm.cmd run smoke:calculator-launch` | PASS |
| `npm.cmd run typecheck` | PASS |
| `npm.cmd run build` | PASS; Next.js warned about workspace root inference because `C:\Users\Admin\package-lock.json` also exists |
| `npm.cmd run production-check` after build | PASS: production browser bundle check passed |

Notes:

- `production-check` was first run before a local build in this worktree and failed with `No browser bundle directories found`; it passed after `npm.cmd run build`.
- `C:\w\jt-a\start-dev.ps1 -Restart` could not be used in this shell because `netstat` was unavailable in PATH. Backend and frontend were started directly from `C:\w\jt-a` for local smoke, then stopped after validation.
- `npm.cmd ci` was run in this worktree to install frontend dependencies for `typecheck` and `build`. `node_modules` and `.next` remain ignored.

## Local Smoke Evidence

The real calculator smoke created a local-only user/profile and checked:

- API workflow: CSRF, register, create chart profile, calculate saved chart, list charts, chart detail, D1 workbench, and all required varga workbench scopes.
- D scopes: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60.
- Frontend pages: `/charts/new`, real `/charts/27`, real `/charts/27/edit`, `/charts/demo-d1`, `/launch-status`.
- Core payloads/status: grahas, houses, ascendant, panchanga, Vimshottari dashas, all vargas, shadbala, ashtakavarga, yogas, technical payload index, calculation passport, classical payload status, dasha status, launch live health markers.

The local smoke wrote only to the local development backend. No production users or charts were created.

## Production Status

- Production health is OK.
- Production runtime remains `8c23a784`.
- No deploy was performed because this milestone changed only test/contract/docs evidence.

## Next Recommended Milestone

Stage 3 Chart Workflow Hardening: make create/edit/calculate/view/recalculate states reliable and testable without UI redesign or formula changes.
