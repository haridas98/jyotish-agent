# AI Review Quality Saved Chart Gate ExecPlan

**Goal:** Create the first AI Review Quality implementation milestone: a deterministic local gate that proves AI review drafts are grounded in stable saved-chart facts and blocks unsupported generic analysis.

**Architecture:** This milestone is a local contract/gate around existing saved chart calculation output and existing AI review quality helpers. The worker must use one real saved-chart fixture path, require calculation anchors for key claims, and keep sanitized audio/Telegram material witness-only. It must not implement the whole AI Review Quality program.

**Tech Stack:** Next.js/TypeScript, existing frontend Node checker scripts, Django/DRF saved chart APIs, existing backend chart fixtures/tests when needed, repo docs.

---

## Starting State

- Branch target: `codex/technical-launch-b`.
- Required baseline: start at or after `f70cc55c9f3b1e48c6443161fe296eb083bd1168`.
- Accepted upstream state:
  - Calculation / Technical Core is accepted through Stage 2.
  - Chart Workflow Hardening is accepted through commit `f70cc55c9f3b1e48c6443161fe296eb083bd1168`.
  - Big Accuracy Witness / JH-PL parity work is skipped for now due limited Codex budget.
  - JH/PL remain witness-only; make no parity claims.
  - OCR Evidence is separate and must not block AI Review Quality.
- Historical input only:
  - `docs/ai_review_quality_reset.md`
  - `docs/superpowers/plans/2026-06-23-ai-review-quality-reset.md`
- Current truth comes from:
  - `docs/status/CURRENT.md`
  - `docs/exec/2026-06-24-stage-outcomes-and-manager-program.md`
  - `docs/exec/2026-06-24-manager-prompts.md`
  - `docs/exec/2026-06-24-functional-stage-program.md`
  - `docs/handoffs/2026-06-24-chart-workflow-hardening.md`
  - `docs/handoffs/2026-06-24-live-workbench-contract-gate.md`

## Desired Product Shape

AI review uses stable saved-chart facts, not generic prose.

Required behavior for this first milestone:

- Review input is derived from a real saved chart fixture path or fixture builder.
- Key claims require calculation anchors.
- Unsupported or generic analysis is blocked or marked draft-only.
- Draft shape includes caveats, practical questions, and concrete emphasis points.
- The gate makes no public quality claim.
- Literature/OCR evidence is treated as unavailable unless already approved by existing source contracts.

## Non-Goals

- No raw audio, ASR, Telegram, OCR, private corpus, or extracted source artifacts in commits.
- No JH/PL implementation, proprietary internals, or parity claims; witness-only policy remains.
- No Big Accuracy Witness/JH-PL parity milestone.
- No OCR evidence dependency.
- No UX/UI redesign, Tailwind/shadcn migration, or visual polish work.
- No formula rewrites or calculation behavior changes unless a blocker is proven and separately planned.
- No production deploy unless a later meaningful runtime batch explicitly requires it.
- No new public copy claiming final AI quality, accuracy, parity, or launch readiness.

---

## First Implementation Milestone Only

### Milestone: Saved Chart Grounding Gate

Create a deterministic local gate that reads one real saved-chart fixture path and proves the AI review draft contract:

1. The fixture contains or builds stable saved-chart facts from the saved chart workflow.
2. The gate extracts a bounded fact packet with calculation anchors such as:
   - calculation settings/passport;
   - Lagna and graha placements;
   - panchanga;
   - Vimshottari dasha status;
   - D1 plus at least one divisional chart marker if available;
   - classical payload statuses such as shadbala/ashtakavarga/yogas.
3. The gate evaluates draft fixtures:
   - grounded draft: passes as draft-eligible;
   - generic draft: blocked;
   - overclaim draft: blocked or draft-only with repair instructions.
4. The gate requires:
   - calculation anchors for key claims;
   - caveat for unsupported advanced claims;
   - at least one practical question;
   - concrete emphasis points tied to chart facts;
   - no raw witness artifacts;
   - no public quality/parity claim.

This milestone ends after one worker commit and one handoff. Do not continue into live LLM generation, UI redesign, OCR, or witness parity.

## Worker Scope

The worker may inspect and modify only the areas needed for this first gate:

- `frontend/src/lib/ai-review-quality.ts`
- `frontend/src/lib/ai-review-benchmark.ts`
- `frontend/src/lib/ai-review-benchmark-parity.ts`
- `frontend/scripts/check-ai-review-quality.mjs`
- a new or existing focused checker script under `frontend/scripts/`
- a new or existing saved-chart fixture under `frontend/src/astrology/`, `frontend/src/data/`, or `backend/apps/charts/fixtures/`
- `frontend/package.json` only if a script needs to be added or narrowed
- docs handoff/status files for this milestone only

Read-only inspection areas:

- `backend/apps/charts/models.py`
- `backend/apps/charts/services.py`
- `backend/apps/charts/views.py`
- `backend/apps/charts/test_api.py`
- `frontend/scripts/smoke-calculator-launch.mjs`
- `frontend/scripts/smoke-chart-workflow.mjs`
- `frontend/src/astrology/d1-workbench-smoke-fixture.ts`
- `frontend/src/app/charts/[id]/page.tsx`
- `frontend/src/lib/api.ts`
- `docs/ai_review_quality_reset.md`

## Test And Smoke Expectations

Minimum local validation for the worker:

```powershell
git status --short --branch
git merge-base --is-ancestor f70cc55c9f3b1e48c6443161fe296eb083bd1168 HEAD
cd frontend
npm.cmd run test:ai-review-quality
npm.cmd run test:launch-readiness
npm.cmd run typecheck
git diff --check
```

If the worker adds a new script, also run that exact script through `npm.cmd run <script>`.

If the gate depends on a real locally created saved chart instead of a static saved-chart fixture, also run:

```powershell
cd frontend
npm.cmd run smoke:calculator-launch
```

Do not require OCR tests, production smoke, full build, or deployment for this docs/test-contract-sized milestone unless runtime code changes make them meaningful.

## Acceptance Criteria

- Exactly one first AI Review Quality milestone is implemented.
- A deterministic local gate exists and is wired to a named test script.
- The gate uses one real saved-chart fixture path or fixture builder, not only generic hardcoded prose.
- Key draft claims are traceable to calculation anchors.
- Generic unsupported draft text is blocked.
- Unsupported advanced claims are blocked or marked draft-only with repair instructions.
- Caveats, practical questions, and concrete emphasis points are required.
- Audio/Telegram benchmarks remain sanitized witness-only.
- JH/PL remain witness-only and no parity claim appears.
- OCR evidence is not required.
- No raw audio/ASR/Telegram/OCR artifacts are committed.
- No public quality, parity, or production-readiness claim is added.
- Worker final includes `READY_FOR_REVIEW`, commit, tests, deploy status, git status, and short notes.

## Verifier Checklist

- Confirm branch/commit starts at or after `f70cc55c9f3b1e48c6443161fe296eb083bd1168`.
- Review `git diff --name-status` for tight scope.
- Review the saved-chart fixture path and confirm it is not generic prose only.
- Confirm the gate checks calculation anchors, caveats, practical questions, concrete emphasis points, and blocked generic output.
- Run the worker's listed tests.
- Run `git diff --check`.
- Scan for forbidden material:

```powershell
rg "ChatExport|message default clearfix|tgme_widget_message|from_name|raw transcript|source audio|OPENAI_API_KEY|sk-proj|parity achieved|JH/PL compatible|release accuracy guaranteed|public quality claim" .
```

- Confirm any matches are either existing policy/checker forbidden-string lists or unrelated historical docs, not runtime claims or committed raw artifacts.
- Confirm deploy was not performed.

## Rollback And Risks

Rollback:

- Revert the worker commit if the gate is too broad, unstable, or leaks witness/private material.
- Keep this ExecPlan and write a rejected verifier note with exact fix instructions.

Risks:

- Existing AI review helpers contain old staged labels and historical benchmark language; worker must preserve only what fits the current saved-chart gate.
- A static fixture can drift from real saved-chart workflow; prefer fixture builder or explicit provenance from saved chart smoke data.
- Over-tight gate may block useful draft-only work; repair instructions should explain missing anchors instead of silently failing.
- Over-broad edits can mix in UX, OCR, witness parity, or live LLM behavior; reject if that happens.

## Stop Rule

Stop after the first Saved Chart Grounding Gate worker commit and handoff. Do not implement runtime/test code in the planning thread. Do not start the next AI Review Quality milestone in the same worker session.
