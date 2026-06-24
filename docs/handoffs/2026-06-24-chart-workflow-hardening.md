# Handoff: Chart Workflow Hardening

Date: 2026-06-24

## Outcome

Stage 3 Chart Workflow Hardening is implemented and ready for independent verifier review.

Baseline:

- Branch target: `codex/technical-launch-b`
- Start commit: `e3ca8837` (`docs: plan chart workflow hardening`)
- Production runtime commit: `8c23a784`
- Runtime code changed: yes, branch only
- Deploy performed: no

## State Contract

Profile payloads now expose `calculation_state`:

- `not_calculated`: saved profile exists, no calculation row.
- `calculation_requested`: pending calculation row exists.
- `complete`: latest calculation matches current birth data/settings.
- `failed`: latest current calculation failed and carries `error`/`message`.
- `stale`: latest calculation input differs from current birth data/settings and `requires_recalculation=true`.

Historical `ChartCalculation` rows are not mutated for stale state. Stale is derived by comparing current profile input with saved `input_snapshot`.

## Changed Files

- Backend workflow state/API: `backend/apps/charts/services.py`, `backend/apps/charts/views.py`
- Backend tests: `backend/apps/charts/test_api.py`
- Frontend API/types/pages: `frontend/src/lib/api.ts`, `frontend/src/app/charts/**`, `frontend/src/astrology/d1-workbench-smoke-fixture.ts`
- Smoke/contracts: `frontend/scripts/smoke-chart-workflow.mjs`, `frontend/scripts/check-chart-detail-smoke.mjs`, `frontend/package.json`
- Docs: `docs/status/CURRENT.md`, this handoff

## Validation

Commands run from `C:\Users\Admin\.codex\worktrees\38a8\jyotish-agent` unless noted.

| Command | Result |
|---|---|
| `git status --short --branch` | clean at start, detached at `e3ca8837` |
| `git merge-base --is-ancestor e3ca883731c1099bd67ee77b009c32161b7ec786 HEAD` | PASS |
| `.\.venv\Scripts\python -m pytest backend\apps\charts\test_api.py -q` | PASS: 52 passed, 52 warnings |
| `npm.cmd run test:chart-detail-smoke` from `frontend` | PASS |
| `npm.cmd run test:launch-readiness` from `frontend` | PASS |
| `npm.cmd run typecheck` from `frontend` | PASS |
| `npm.cmd run build` from `frontend` | PASS; Next.js workspace-root warning only |
| `npm.cmd run production-check` from `frontend` | PASS |
| `npm.cmd run smoke:calculator-launch` from `frontend` with local API/frontend URLs | PASS |
| `npm.cmd run smoke:chart-workflow` from `frontend` with local API/frontend URLs | PASS |

Local smoke services:

- Backend: `http://127.0.0.1:18110`
- Frontend: `http://127.0.0.1:3131`
- Both were stopped after smoke.

## Local Smoke Evidence

`smoke:chart-workflow` created local-only users/profiles and verified:

- save profile without calculating;
- API `not_calculated` state;
- calculate and API/workbench `complete` state;
- edit birth time plus calculation assumption;
- API/list/workbench `stale` and `requires_recalculation`;
- recalculate back to `complete`;
- failed calculation state using an invalid local-only exact-time profile;
- `/charts/new`, `/charts/{id}`, `/charts/{id}/edit`, and `/charts` static workflow markers.

`smoke:calculator-launch` still passed D1-D60 saved workbench coverage.

## Production Status

- Production deploy: not performed.
- Production runtime remains `8c23a784`.
- No production write smoke was run.

## Known Limitations

- Backend calculation is still synchronous; `calculation_requested` is represented by pending rows and frontend in-flight markers, not a new async queue.
- Local venvs and local sqlite DB were created for validation only and are ignored.
- `npm install` reported 2 moderate audit findings; dependency upgrades were left out of scope.
