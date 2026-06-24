# Chart Workflow Hardening ExecPlan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` or `superpowers:executing-plans` in a fresh implementation session. Track steps with checkbox (`- [ ]`) syntax.

**Goal:** Make saved chart create, edit, calculate, view, and recalculate states explicit, reliable, and covered by local smoke.

**Architecture:** This is workflow contract hardening around existing saved `BirthProfile` and `ChartCalculation` APIs. The worker may add state metadata, tests, and smoke markers, but must not change astrology formulas, add AI review behavior, redesign UI, or start witness/OCR work.

**Tech Stack:** Django/DRF chart APIs, existing chart service functions, Next.js chart pages, TypeScript API types, Node smoke/check scripts, pytest.

---

## Baseline

- Branch: `codex/technical-launch-b`
- Required start point: `8e8410b2` or newer
- Stage 2 status: Live Workbench Contract Gate accepted by verifier thread `019ef8a6-be81-7753-b3aa-47f1249aa8c4`
- Production runtime baseline in `docs/status/CURRENT.md`: `8c23a784`
- Expected initial working tree: clean
- Deploy expected: no, unless the worker changes runtime behavior and a manager explicitly schedules a deployment checkpoint

## Goals

- Saved profile creation has a visible and API-level state before calculation.
- Saved-but-not-calculated profiles do not look like broken charts.
- Calculation request/running state is visible where supported by the current synchronous API and frontend in-flight behavior.
- Complete calculations are rendered from saved `ChartCalculation` rows.
- Failed calculations return and display a useful message.
- Editing birth data, place, or calculation assumptions after a calculation marks the saved result stale and requiring recalculation.
- Recalculation after stale edits creates or reuses the correct current calculation.
- Detail page renders saved calculations without silently hiding stale/failed/no-calculation states.
- Edit page preserves birth data and calculation assumptions.
- Local smoke covers create/edit/calculate/view/recalculate end to end.

## In Scope

- Backend state contracts for:
  - `not_calculated`;
  - `calculation_requested` or frontend `calculating` when no async backend state exists;
  - `complete`;
  - `failed`;
  - `stale`;
  - `recalculated`.
- API payload additions on profile/detail/list/workbench responses, preferably under one stable object such as `calculation_state`.
- Saved profile creation through `/api/charts` and `/api/charts/profiles`.
- Calculate/recalculate through `/api/charts/profiles/{id}/calculate`.
- Current input snapshot comparison against latest calculation `input_snapshot`.
- Frontend data handling in:
  - `/charts/new`;
  - `/charts/{id}`;
  - `/charts/{id}/edit`;
  - `/charts`.
- Focused contract tests and local smoke/check scripts.
- Docs updates only where needed for status/handoff.

## Out Of Scope

- Formula changes.
- AI review or report-generation changes.
- OCR, raw audio, ASR, Telegram, or private corpus work.
- UX/UI redesign, cosmetic restyling, Tailwind/shadcn migration, or new visual direction.
- JH/PL parity claims, proprietary internals, or witness packet work.
- Splitting work by one helper per D-chart.
- Production write smoke unless a manager explicitly schedules a deploy checkpoint.

## Files And Areas To Inspect

- `backend/apps/charts/models.py`
  - `BirthProfile`
  - `ChartCalculation.Status`
  - `ChartCalculation.input_snapshot`
- `backend/apps/charts/services.py`
  - `create_birth_profile`
  - `update_birth_profile_flags`
  - `calculate_profile_chart`
  - `profile_payload`
  - `profiles_payload`
  - `latest_calculation_summary`
  - `calculation_payload`
  - `_profile_input`
  - `_profile_calculation_settings`
- `backend/apps/charts/views.py`
  - `BirthProfileListView`
  - `BirthProfileDetailView`
  - `BirthProfileWorkbenchView`
  - `BirthProfileCalculateView`
- `backend/apps/charts/urls.py`
- `backend/apps/charts/test_api.py`
- `frontend/src/lib/api.ts`
  - `ChartProfile`
  - `ChartCalculationRecord`
  - `D1WorkbenchApiResponse`
  - `createChartProfile`
  - `updateChartProfile`
  - `fetchChartProfile`
  - `fetchD1ChartWorkbench`
  - `calculateSavedProfile`
- `frontend/src/app/charts/new/page.tsx`
- `frontend/src/app/charts/[id]/page.tsx`
- `frontend/src/app/charts/[id]/edit/page.tsx`
- `frontend/src/app/charts/page.tsx`
- `frontend/src/app/charts/chart-profile-form.tsx`
- `frontend/scripts/smoke-calculator-launch.mjs`
- `frontend/scripts/check-chart-detail-smoke.mjs`
- `frontend/scripts/check-launch-readiness-contract.mjs`
- `frontend/package.json`

## Implementation Approach

### Task 1: Baseline And Contract Inventory

- [ ] Run:

```powershell
git status --short --branch
git log -1 --oneline
```

- [ ] Confirm the commit is `8e8410b2` or newer on `codex/technical-launch-b`.
- [ ] Read the files listed above.
- [ ] Document the current behavior:
  - create currently saves `BirthProfile`;
  - `/charts/new` currently attempts auto-calculate;
  - `/charts/{id}` currently attempts auto-calculate when workbench has no calculation;
  - `calculate_profile_chart(..., reuse_existing=True)` reuses only matching complete `input_snapshot`;
  - failed calculations can exist as `ChartCalculation.Status.FAILED`;
  - explicit stale state is not yet exposed in profile payloads.

### Task 2: Add Backend Workflow State Contract

- [ ] Add a small service helper in `backend/apps/charts/services.py` that compares the latest calculation with current `_profile_input(profile)`.
- [ ] Prefer one payload object named `calculation_state` with this shape:

```json
{
  "status": "not_calculated|calculation_requested|complete|failed|stale",
  "has_calculation": false,
  "has_complete_calculation": false,
  "latest_calculation_id": null,
  "latest_calculation_status": null,
  "requires_recalculation": false,
  "is_stale": false,
  "message": "Saved profile has not been calculated yet.",
  "calculated_at": null,
  "updated_at": null
}
```

- [ ] For a complete current calculation:
  - `status="complete"`;
  - `has_calculation=true`;
  - `has_complete_calculation=true`;
  - `requires_recalculation=false`;
  - `is_stale=false`.
- [ ] For no calculation:
  - `status="not_calculated"`;
  - message tells the user to calculate the saved profile.
- [ ] For failed calculation:
  - `status="failed"`;
  - `message` includes the saved `ChartCalculation.error` or a useful fallback.
- [ ] For changed profile input after a calculation:
  - `status="stale"`;
  - `requires_recalculation=true`;
  - `is_stale=true`;
  - keep the latest calculation summary available, but mark that it was calculated for previous birth data/settings.
- [ ] Do not add async queue semantics unless the current app already has them. If calculation remains synchronous, `calculation_requested` may be represented only in frontend in-flight state and smoke markers.

### Task 3: Add Backend Tests First

- [ ] Add focused tests to `backend/apps/charts/test_api.py`.
- [ ] Cover saved profile without calculation:

```python
def test_chart_profile_detail_marks_saved_not_calculated(...):
    ...
    assert response.data["profile"]["calculation_state"]["status"] == "not_calculated"
    assert response.data["profile"]["calculation_state"]["requires_recalculation"] is False
```

- [ ] Cover complete calculation:

```python
def test_chart_profile_detail_marks_current_calculation_complete(...):
    ...
    assert response.data["profile"]["latest_calculation"]["status"] == "complete"
    assert response.data["profile"]["calculation_state"]["status"] == "complete"
```

- [ ] Cover failed calculation using `monkeypatch` against `apps.charts.services.build_birth_chart`:

```python
def fake_build_birth_chart(data, provider=None):
    raise ChartInputError("birth_time must be HH:MM")
```

- [ ] Assert the calculate endpoint returns a failed calculation with useful `error`/`message`.
- [ ] Cover stale after edit:
  - create profile;
  - calculate or insert complete calculation with `input_snapshot=_profile_input(profile)`;
  - patch `birth_time`, `birth_date`, `place_name`, or a calculation setting;
  - assert detail/list/workbench response has `status="stale"` and `requires_recalculation=true`.
- [ ] Cover recalculation after stale edit:
  - post calculate again;
  - assert a new or current matching complete calculation is used;
  - assert `calculation_state.status == "complete"`;
  - assert the old stale calculation is not treated as current.
- [ ] Cover edit preservation:
  - patch birth data and calculation assumptions such as `node_type`, `ayanamsa`, `house_system`, `varga_scheme`;
  - assert `fetch detail` payload returns the patched fields and `calculation_settings`.

### Task 4: Apply Minimal Backend Implementation

- [ ] Implement only the code needed to pass the tests.
- [ ] Update `profile_payload`, `profiles_payload`, and `calculation_payload` only as needed.
- [ ] Keep query-count behavior in `test_birth_profile_list_batches_latest_calculation_queries`; if the new payload needs `input_snapshot`, select/defer deliberately instead of creating N+1 queries.
- [ ] Do not mutate historical `ChartCalculation` rows when marking stale; stale is derived from current profile input versus saved `input_snapshot`.
- [ ] Preserve `reuse_existing=True` semantics: reuse only matching complete calculations.

### Task 5: Frontend Contract Updates

- [ ] Update `frontend/src/lib/api.ts` types for `calculation_state`.
- [ ] Update `/charts/new` so create/calculate flow exposes:
  - saved profile creation;
  - calculation requested/running via existing local `calculating` state or equivalent;
  - failed calculation message when API returns failed/error.
- [ ] Update `/charts/{id}` so it:
  - renders saved calculations;
  - shows no-calculation state without relying on hidden auto-calculate only;
  - shows stale state and offers recalculate;
  - shows failed state and useful message;
  - refreshes after recalculate.
- [ ] Update `/charts/{id}/edit` and `ChartProfileForm` only enough to preserve calculation assumptions already present on the profile.
- [ ] Update `/charts` list only if needed to make saved/not-calculated/stale/failed states visible in a compact way.
- [ ] Add stable smoke markers, not cosmetic redesign:
  - `chart-workflow-state-not-calculated`;
  - `chart-workflow-state-calculation-requested`;
  - `chart-workflow-state-complete`;
  - `chart-workflow-state-failed`;
  - `chart-workflow-state-stale`;
  - `chart-workflow-recalculate-complete`;
  - `chart-workflow-edit-preserves-assumptions`.

### Task 6: Local Smoke Coverage

- [ ] Extend `frontend/scripts/smoke-calculator-launch.mjs` or create a focused script such as `frontend/scripts/smoke-chart-workflow.mjs`.
- [ ] If a new script is added, wire it in `frontend/package.json`, for example:

```json
"smoke:chart-workflow": "node scripts/smoke-chart-workflow.mjs"
```

- [ ] Smoke must create a local-only user/profile and cover:
  - save profile without calculating;
  - verify no-calculation state through API;
  - calculate;
  - verify complete state through API and detail/workbench;
  - edit profile birth data and one calculation assumption;
  - verify stale/requires-recalculation state;
  - recalculate;
  - verify complete state again;
  - simulate or verify failed calculation state if supported without formula changes;
  - check `/charts/{id}`, `/charts/{id}/edit`, and `/charts` when `JYOTISH_FRONTEND_BASE_URL` is provided.
- [ ] Keep production smoke read-only. Do not create production charts/users.

### Task 7: Contract Checker Updates

- [ ] Update `frontend/scripts/check-chart-detail-smoke.mjs` or add a new checker so future edits cannot remove workflow state markers.
- [ ] Update `frontend/scripts/check-launch-readiness-contract.mjs` only if launch readiness should require the new workflow smoke.
- [ ] Keep forbidden scans for:
  - `JHora`;
  - `Parashara Light`;
  - `verified parity`;
  - `parity success`;
  - raw evidence markers;
  - secrets such as `OPENAI_API_KEY` and `sk-`.

### Task 8: Required Validation

Run backend checks from repo root:

```powershell
.\.venv\Scripts\python -m pytest backend\apps\charts\test_api.py -q
```

Run frontend checks from `frontend`:

```powershell
npm.cmd run test:chart-detail-smoke
npm.cmd run test:launch-readiness
npm.cmd run typecheck
npm.cmd run build
npm.cmd run production-check
```

Run local smoke against local services. If services are not already running:

```powershell
cd C:\w\jt-a
.\start-dev.ps1 -CheckOnly -BackendPort 18110 -FrontendPort 3131
```

Then:

```powershell
cd C:\w\jt-a\frontend
$env:JYOTISH_API_BASE_URL="http://127.0.0.1:18110"
$env:JYOTISH_FRONTEND_BASE_URL="http://127.0.0.1:3131"
npm.cmd run smoke:calculator-launch
npm.cmd run smoke:chart-workflow
```

If `smoke:chart-workflow` is folded into `smoke:calculator-launch`, record that explicitly in the handoff and do not add a duplicate script.

### Task 9: Docs And Handoff

- [ ] Create a handoff such as `docs/handoffs/2026-06-24-chart-workflow-hardening.md`.
- [ ] Include:
  - baseline commit;
  - changed files;
  - exact state contract;
  - exact validation commands/results;
  - local smoke evidence;
  - production deploy status;
  - known limitations.
- [ ] Update `docs/status/CURRENT.md` only after implementation is complete and verified by the worker's own required checks.

### Task 10: Commit And Stop

- [ ] Run:

```powershell
git diff --check
git status --short
```

- [ ] Commit one focused Stage 3 implementation commit.
- [ ] Push `codex/technical-launch-b`.
- [ ] Stop. Do not begin Accuracy Witness, AI Review, OCR, UX/UI, or production deploy work in the same session.

## Acceptance Criteria

- API responses expose an explicit chart workflow state for saved profile, complete, failed, stale, and recalculated conditions.
- A saved profile with no calculation is not treated as a broken chart.
- Calculation failure returns a useful message and is visible to the user.
- Editing birth data or calculation assumptions after a complete calculation marks the prior saved result stale/requires recalculation.
- Recalculate after stale edit results in a current complete calculation matching the edited profile input.
- Detail page can render saved complete calculations and stale saved calculations with an explicit stale warning.
- Edit page preserves birth data and calculation assumptions.
- Local smoke covers create/edit/calculate/view/recalculate.
- No formulas, AI review, OCR, raw audio/ASR/Telegram, JH/PL parity claims, or cosmetic redesign are included.

## Verifier Checklist

- [ ] Confirm diff scope is limited to chart workflow contracts, tests/smokes, and docs.
- [ ] Confirm no formula files were changed except incidental imports needed by tests; reject formula behavior changes.
- [ ] Confirm no AI review, OCR, raw audio/ASR/Telegram, JH/PL witness/parity, or UI redesign work is included.
- [ ] Run or inspect evidence for:

```powershell
.\.venv\Scripts\python -m pytest backend\apps\charts\test_api.py -q
cd frontend
npm.cmd run test:chart-detail-smoke
npm.cmd run test:launch-readiness
npm.cmd run typecheck
npm.cmd run build
npm.cmd run production-check
npm.cmd run smoke:calculator-launch
npm.cmd run smoke:chart-workflow
```

- [ ] If `smoke:chart-workflow` was not added, verify equivalent workflow assertions exist in `smoke:calculator-launch`.
- [ ] Verify `git status --short --branch` is clean after commit.
- [ ] Verify production deploy status is honestly documented.

## Stop Rule

Stop after the Stage 3 worker commit is pushed and ready for independent verifier review. Do not implement witness accuracy, AI review, OCR evidence, UX/UI redesign, or deployment follow-up in the same worker session.
