# Handoff: Technical Core Audit

Date: 2026-06-24

## Outcome

Stage 1 Technical Core Audit is complete.

Baseline:

- Branch baseline expected by ExecPlan: `codex/technical-launch-b`
- Audit start commit: `3669f619` (`Plan functional technical stages`)
- Production runtime commit: `8c23a784`
- Production health: `https://jyotish-agent.duckdns.org/api/health` returned `deploy_commit=8c23a784`
- Runtime code changed: no
- Deploy performed: no

## Validation

Commands run from the canonical repo path `C:\w\jt-a`:

| Command | Result |
|---|---|
| `cd C:\w\jt-a\backend; .\.venv\Scripts\python -m pytest apps/calculations/test_vargas.py apps/charts/test_api.py apps/charts/test_services.py` | PASS: 86 passed, 46 warnings |
| `cd C:\w\jt-a\frontend; npm.cmd run test:launch-readiness` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run test:d1-workbench` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run test:chart-workbench-ux` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run test:chart-detail-smoke` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run test:dasha-workbench` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run typecheck` | PASS |
| `cd C:\w\jt-a\frontend; npm.cmd run production-check` | PASS |

Note: the same backend pytest command failed in this detached Codex worktree because `backend\.venv` is absent here. It passed in the ExecPlan canonical path `C:\w\jt-a`.

## D-Scope Coverage Matrix

Confidence legend:

- High: backend calculation, saved workbench API, frontend switch/display, and automated test/smoke evidence all exist.
- Medium: capability exists, but formula-specific golden coverage is thinner than primary scopes.

| Scope | Backend calculation | Saved workbench API | Frontend selector/display | Automated test/smoke | Confidence | Evidence |
|---|---|---|---|---|---|---|
| D1 | yes | yes | yes | yes | High | `backend/apps/calculations/vargas.py`; `frontend/scripts/smoke-calculator-launch.mjs`; `frontend/scripts/check-d1-workbench.mjs` |
| D2 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `backend/apps/charts/test_api.py` |
| D3 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `frontend/src/astrology/d1-workbench.ts` |
| D4 | yes | yes | yes | yes | Medium | `backend/apps/calculations/test_vargas.py`; `frontend/scripts/check-d1-workbench.mjs` |
| D7 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `backend/apps/charts/test_api.py` |
| D9 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `frontend/scripts/check-chart-workbench-ux.mjs` |
| D10 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `frontend/scripts/check-chart-workbench-ux.mjs` |
| D12 | yes | yes | yes | yes | High | `backend/apps/calculations/test_vargas.py`; `backend/apps/charts/test_api.py` |
| D16 | yes | yes | yes | yes | Medium | `backend/apps/calculations/test_vargas.py`; `frontend/scripts/check-d1-workbench.mjs` |
| D20 | yes | yes | yes | yes | Medium | `backend/apps/calculations/test_vargas.py`; source review pending in registry |
| D24 | yes | yes | yes | yes | Medium | `backend/apps/calculations/test_vargas.py`; `frontend/scripts/check-d1-workbench.mjs` |
| D27 | yes | yes | yes | yes | Medium | `backend/apps/calculations/test_vargas.py`; source review pending in registry |
| D30 | yes | yes | yes, expert gated | yes | High | `backend/apps/calculations/test_vargas.py`; `varga.d30.parashara_unequal.v1` |
| D40 | yes | yes | yes | yes | Medium | all-codes registry/API tests; fewer formula-specific golden cases |
| D45 | yes | yes | yes | yes | Medium | all-codes registry/API tests; fewer formula-specific golden cases |
| D60 | yes, exact birth time only | yes, exact birth time only | yes, expert gated | yes | High | `backend/apps/calculations/test_vargas.py`; D60 accuracy gate |

Confirmed:

- `frontend/scripts/smoke-calculator-launch.mjs` has `requiredScopes = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]`.
- `backend/apps/calculations/vargas.py` implements all requested scopes in `VARGA_METHOD_REGISTRY` and `divisional_placement`.
- `backend/apps/charts/views.py` exposes supported scopes, expert scopes, varga metadata, and accuracy gates through `/api/charts/:id/workbench`.
- `frontend/src/astrology/d1-workbench.ts` and `frontend/src/ui/d1-workbench/D1ChartWorkbench.tsx` normalize and switch/display the same scope registry.

## Payload Coverage Matrix

| Payload group | Backend source | API exposure | UI/status visibility | Test/smoke evidence | Confidence |
|---|---|---|---|---|---|
| grahas | `backend/apps/calculations/chart.py` | saved calculation result + workbench | chart cells + graha table | backend service/API tests; calculator smoke asserts count | High |
| houses | `backend/apps/calculations/chart.py` | saved calculation result + workbench | chart cells + house table | backend service/API tests; calculator smoke asserts 12 houses | High |
| house cusps | provider-backed in `chart.py` | saved calculation result | technical tab table | backend birth-chart tests outside focused command | Medium |
| panchanga | `backend/apps/calculations/panchanga.py`, wired in `chart.py` | saved calculation result | calculation passport + technical tab | panchanga tests; calculator smoke asserts tithi/vara/yoga/karana | High |
| Vimshottari dashas | `backend/apps/calculations/vimshottari.py` | saved calculation result + dasha workbench | status strip, technical tab, `/dashas` page | dasha tests; `test:dasha-workbench` | High |
| avasthas | `backend/apps/calculations/classical.py` | `classical.avasthas` | status/count only | `test_classical.py` outside focused command | Medium |
| vimshopaka | `backend/apps/calculations/classical.py` | `classical.vimshopaka_bala` | status/count only | `test_classical.py` outside focused command | Medium |
| ashtakavarga | `backend/apps/calculations/classical.py` | `classical.ashtakavarga` | status/count only | `test_classical.py`; calculator smoke asserts presence | Medium |
| shadbala | `backend/apps/calculations/classical.py` | `classical.shadbala` | status/count only | `test_classical.py`; calculator smoke asserts presence | Medium |
| yogas | `backend/apps/calculations/classical.py` | `classical.yogas` | status/count only | `test_classical.py`; calculator smoke asserts presence | Medium |
| argala | `backend/apps/calculations/classical.py` | `classical.argala` | status/count only | `test_classical.py` outside focused command | Medium |
| special points | `chart.py` Lagna + `classical.py` special points | saved calculation result + classical payload | Lagna displayed separately; classical special points status/count | `test_classical.py`; workbench static checks | Medium |

## Already Working

- Saved chart calculation produces grahas, Lagna, houses, house cusps when provider supports them, panchanga, Vimshottari, all requested vargas, and classical payload status groups.
- Workbench API exposes D1-D60 supported metadata, varga method metadata, expert-only scopes, and D60 birth-time gate.
- Frontend can switch/display all supported D scopes through the same saved-chart workbench flow.
- Production runtime is healthy at deployed commit `8c23a784`.

## Real Gaps

1. ExecPlan validation does not run the real API calculator smoke `npm.cmd run smoke:calculator-launch`; it is inspected and relevant, but not part of the focused command list.
2. D40 and D45 have backend calculation/API/UI coverage, but thinner formula-specific golden tests than D9/D10/D12/D30/D60.
3. Classical groups beyond shadbala/ashtakavarga/yogas are visible mostly as status/count rows, not detailed dedicated UI tables.
4. D20/D27 registry notes still say source review pending; do not promote them as externally witnessed or parity-proven.

## Recommended Next Milestone

Exact next milestone: `Stage 2 - Live Workbench Contract Gate`.

Goal: add one focused validation gate that runs the real saved-chart calculator smoke against the intended environment and records D1-D60 plus payload assertions as required release evidence. Keep it test/contract-only unless the new gate exposes a real runtime failure.

Suggested ExecPlan file name:

- `docs/exec/2026-06-24-02-live-workbench-contract-gate.md`

## Out Of Scope Preserved

- No formula rewrites.
- No UX/UI implementation.
- No deploy.
- No JH/PL parity claim.
- No proprietary JH/PL internals.
- No raw audio, ASR, Telegram, or OCR artifacts.
