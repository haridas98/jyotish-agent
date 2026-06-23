# AI Review Quality Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current offline AI-review guard work into a real, testable path toward useful jyotish reviews: grounded calculations, Telegram-benchmark accents, strong follow-up questions, and production only after a checkpoint.

**Architecture:** Keep raw Telegram exports and OCR/private material out of runtime and git. Extract sanitized benchmark facts into explicit fixtures, compare calculations against those fixtures, then connect the existing AI-review contract/evaluator/composer/generation-boundary to a real review composer. The supervisor assigns one batch task at a time and independently verifies before sending the next task.

**Tech Stack:** Next.js 16, TypeScript, Node checker scripts, Django/DRF backend, pytest, local-only smoke checks, no production deploy until Task 5.

---

## Operating Rules

- No infinite P/E micro-stages. Use the task names below: `R1` through `R5`.
- Each task must finish with one commit and `READY_FOR_REVIEW`.
- Normal tasks are local-only: no deploy, report `deployCommit: 508df50 (unchanged, deploy skipped per user batching policy)`.
- Deploy only in `R5 Deploy Checkpoint`, after Tasks R1-R4 pass.
- Do not stage or revert unrelated files:
  - `docs/source_policy.md`
  - `docs/jyotish_ocr_chart_policy.md`
- Raw Telegram export path is external input only:
  - `E:\Downloads\Telegram Desktop\ChatExport_2026-06-23`
- Raw export strings must not appear in runtime UI, committed fixture prose, or public report text:
  - `ChatExport`
  - `message default clearfix`
  - `tgme_widget_message`
  - `from_name`
  - raw Telegram HTML
  - balance/payment/menu noise
- Allowed deviation: fix a newly discovered blocker only if it would make later tasks unreliable. The worker final must explain the deviation and why it was necessary.
- Supervisor accepts a task only after independent diff, source scan, tests, local smoke when relevant, and git status.

## File Structure

### New Files

- `frontend/scripts/extract-ai-review-telegram-benchmark.mjs`
  - Reads local Telegram `messages.html`.
  - Extracts chart tables and question candidates.
  - Writes sanitized JSON only.
  - Must be deterministic and safe to run without network.

- `frontend/scripts/check-ai-review-telegram-benchmark.mjs`
  - Verifies sanitized benchmark structure and privacy rules.
  - Fails if raw HTML/noise/private export classes leak.
  - Fails if benchmark lacks chart facts, calculation accents, and follow-up questions.

- `frontend/src/data/ai-review-telegram-benchmark.json`
  - Sanitized benchmark data derived from Telegram export.
  - Contains no raw bot prose.
  - Uses anonymized case ids, not display names.

- `frontend/src/lib/ai-review-benchmark.ts`
  - Typed loader and normalizer for sanitized benchmark data.
  - Exports helpers used by `ai-review-quality.ts`.

- `docs/ai_review_quality_reset.md`
  - Short product policy: what the benchmark is, what it is not, and why style copying is forbidden.

### Existing Files To Modify

- `frontend/src/lib/ai-review-quality.ts`
  - Stop growing Telegram benchmark logic inline.
  - Keep existing public exports stable.
  - Import benchmark helper from `ai-review-benchmark.ts`.

- `frontend/scripts/check-ai-review-quality.mjs`
  - Keep existing P119-P133 gates.
  - Add cross-check that benchmark helper is used.

- `frontend/package.json`
  - Add `test:ai-review-telegram-benchmark`.

- `frontend/src/app/reports/page.tsx`
  - Later tasks only: display benchmark status and real composer status.

- `frontend/src/app/report-mock-review/page.tsx`
  - Later tasks only: display case-level review composer evidence.

---

## Task R1: Sanitized Telegram Benchmark Ingestion

**Purpose:** Convert the Telegram export into a safe benchmark fixture for calculations, accents, and follow-up questions. This task does not build final AI reviews.

**Files:**
- Create: `frontend/scripts/extract-ai-review-telegram-benchmark.mjs`
- Create: `frontend/scripts/check-ai-review-telegram-benchmark.mjs`
- Create: `frontend/src/data/ai-review-telegram-benchmark.json`
- Create: `frontend/src/lib/ai-review-benchmark.ts`
- Create: `docs/ai_review_quality_reset.md`
- Modify: `frontend/src/lib/ai-review-quality.ts`
- Modify: `frontend/scripts/check-ai-review-quality.mjs`
- Modify: `frontend/package.json`

- [ ] **Step 1: Write the failing benchmark checker**

Create `frontend/scripts/check-ai-review-telegram-benchmark.mjs` with checks for:

```js
const requiredTopLevel = [
  "schemaVersion",
  "sourceKind",
  "privacy",
  "cases",
  "qualityTargets"
];

const forbiddenFragments = [
  "ChatExport",
  "message default clearfix",
  "tgme_widget_message",
  "from_name",
  "Ваш баланс",
  "Энергия Света",
  "Выберите действие",
  "<div class=\"message",
  "<html",
];
```

The checker must fail if:
- fewer than 2 benchmark cases;
- any case has fewer than 8 D1 chart facts;
- no case has D9 facts;
- fewer than 3 calculation accents per case;
- fewer than 3 follow-up questions per case;
- raw HTML/noise strings appear anywhere in committed benchmark JSON;
- case ids expose raw names instead of anonymized ids;
- no status label `ai_review_telegram_sanitized_benchmark_stage=R1`.

Run:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run test:ai-review-telegram-benchmark
```

Expected before implementation: command missing or checker fails.

- [ ] **Step 2: Add package script**

Modify `frontend/package.json`:

```json
"test:ai-review-telegram-benchmark": "node scripts/check-ai-review-telegram-benchmark.mjs"
```

Run again. Expected: checker fails because fixture/helper does not exist yet.

- [ ] **Step 3: Implement extractor**

Create `frontend/scripts/extract-ai-review-telegram-benchmark.mjs`.

Required behavior:
- Default input: `process.env.AI_REVIEW_TELEGRAM_EXPORT_DIR || "E:\\Downloads\\Telegram Desktop\\ChatExport_2026-06-23"`.
- Read only `messages.html`.
- Parse `<pre>` chart tables.
- Extract D1 and D9/D10 labels when present.
- Store anonymized case ids such as:
  - `case_cancer_lagna_1998`
  - `case_cancer_lagna_career`
- Store sanitized rows:

```json
{
  "planet": "Lagna",
  "sign": "Cancer",
  "degree": 25.42,
  "house": 1,
  "retrograde": false,
  "nakshatra": "Ashlesha"
}
```

- Store derived benchmark expectations, not copied style:

```json
{
  "calculationAccents": [
    "Career interpretation must anchor the Aries 10th-house cluster before advice.",
    "Moon placement must be tied to house, sign, and nakshatra before emotional framing.",
    "Advanced strength claims require computed shadbala/ashtakavarga/avastha evidence."
  ],
  "followUpQuestions": [
    "Which 10th-house factor is most visible in current work decisions?",
    "Which dasha layer should be checked before timing claims?",
    "Which divisional chart is needed before making a career or relationship conclusion?"
  ]
}
```

Run:

```powershell
cd C:\Projects\jyotish-agent\frontend
$env:AI_REVIEW_TELEGRAM_EXPORT_DIR='E:\Downloads\Telegram Desktop\ChatExport_2026-06-23'
node scripts/extract-ai-review-telegram-benchmark.mjs
```

Expected: writes `frontend/src/data/ai-review-telegram-benchmark.json`.

- [ ] **Step 4: Add typed benchmark helper**

Create `frontend/src/lib/ai-review-benchmark.ts` exporting:

```ts
export type AiReviewTelegramBenchmarkCase = {
  id: string;
  chartFacts: string[];
  d1Rows: Array<{
    planet: string;
    sign: string;
    degree: number;
    house: number | null;
    retrograde: boolean;
    nakshatra: string | null;
  }>;
  divisionalFacts: string[];
  calculationAccents: string[];
  followUpQuestions: string[];
  advancedClaimCautions: string[];
};

export type AiReviewTelegramSanitizedBenchmark = {
  schemaVersion: 1;
  stage: "R1";
  sourceKind: "sanitized_telegram_export_benchmark";
  privacy: {
    rawExportCommitted: false;
    rawStyleCopied: false;
    anonymizedCaseIds: true;
  };
  cases: AiReviewTelegramBenchmarkCase[];
  qualityTargets: string[];
  statusLabels: string[];
};

export function buildAiReviewTelegramSanitizedBenchmark(): AiReviewTelegramSanitizedBenchmark;
```

The helper must return labels:

```ts
"ai_review_telegram_sanitized_benchmark_stage=R1"
"ai_review_telegram_sanitized_benchmark_present=true"
"ai_review_telegram_raw_export_committed=false"
"ai_review_telegram_style_copied=false"
"ai_review_telegram_case_count>=2"
"ai_review_telegram_followup_questions_present=true"
```

- [ ] **Step 5: Wire existing quality summary**

Modify `frontend/src/lib/ai-review-quality.ts` so:
- existing `buildTelegramBenchmarkReviewBlueprint()` still exists;
- it uses `buildAiReviewTelegramSanitizedBenchmark()`;
- it no longer hardcodes raw names or copied benchmark prose.

Run:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run test:ai-review-telegram-benchmark
npm.cmd run test:ai-review-quality
npm.cmd run typecheck
```

Expected: all pass.

- [ ] **Step 6: Source scan**

Run:

```powershell
cd C:\Projects\jyotish-agent
rg "ChatExport|message default clearfix|tgme_widget_message|from_name|Ваш баланс|Энергия Света|<div class=\"message|<html" frontend/src frontend/scripts docs/ai_review_quality_reset.md
```

Expected: no matches except the forbidden-list arrays inside checker/extractor scripts.

- [ ] **Step 7: Commit**

Stage only R1 files:

```powershell
git add frontend/scripts/extract-ai-review-telegram-benchmark.mjs frontend/scripts/check-ai-review-telegram-benchmark.mjs frontend/src/data/ai-review-telegram-benchmark.json frontend/src/lib/ai-review-benchmark.ts frontend/src/lib/ai-review-quality.ts frontend/scripts/check-ai-review-quality.mjs frontend/package.json docs/ai_review_quality_reset.md
git commit -m "Add sanitized AI review Telegram benchmark"
git push
```

Worker final must include:
- `READY_FOR_REVIEW: R1`
- commit
- deploy status unchanged
- files changed
- extraction summary
- privacy/source scan summary
- tests run
- git status including unrelated docs files

---

## Task R2: Benchmark Calculation Parity Audit

**Purpose:** Compare sanitized Telegram benchmark chart facts against our calculation/fixture layer and make mismatches visible before using the benchmark for reviews.

**Files:**
- Create: `frontend/scripts/check-ai-review-benchmark-parity.mjs`
- Create: `frontend/src/lib/ai-review-benchmark-parity.ts`
- Modify: `frontend/src/lib/ai-review-benchmark.ts`
- Modify: `frontend/src/lib/ai-review-quality.ts`
- Modify: `frontend/package.json`
- Optional backend read-only reference: `backend/apps/charts/views.py`, `backend/apps/calculations/*`

- [ ] Add `test:ai-review-benchmark-parity`.
- [ ] Build deterministic parity report from sanitized rows.
- [ ] Require at least:
  - Lagna sign/house present;
  - Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn/Rahu/Ketu present;
  - nakshatra present for D1 rows;
  - explicit unsupported/missing markers for shadbala, ashtakavarga, avastha if not calculated.
- [ ] Expose status labels:
  - `ai_review_benchmark_parity_stage=R2`
  - `ai_review_benchmark_parity_present=true`
  - `ai_review_benchmark_d1_rows_checked>=18`
  - `ai_review_benchmark_unsupported_advanced_claims_gated=true`
- [ ] Run:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run test:ai-review-telegram-benchmark
npm.cmd run test:ai-review-benchmark-parity
npm.cmd run test:ai-review-quality
npm.cmd run typecheck
npm.cmd run build
npm.cmd run production-check
```

Worker final: `READY_FOR_REVIEW: R2`, commit, no deploy.

---

## Task R3: Real Review Composer V1

**Purpose:** Build a deterministic review composer that produces useful review sections from benchmark/calculation facts, not generic prose.

**Files:**
- Create: `frontend/src/lib/ai-review-composer.ts`
- Create: `frontend/scripts/check-ai-review-composer.mjs`
- Modify: `frontend/src/lib/ai-review-quality.ts`
- Modify: `frontend/src/app/reports/page.tsx`
- Modify: `frontend/src/app/report-mock-review/page.tsx`
- Modify: `frontend/package.json`

- [ ] Add `test:ai-review-composer`.
- [ ] Composer output must use this structure:

```ts
type ReviewSection = {
  heading: "Calculation facts" | "Jyotish rule" | "Interpretive accent" | "Risk or caveat" | "Practical next step" | "Follow-up questions";
  bullets: string[];
  evidenceRefs: string[];
};
```

- [ ] Require each review:
  - at least 5 sections;
  - at least 8 calculation facts;
  - at least 3 interpretive accents;
  - at least 3 follow-up questions;
  - caveat for every unsupported advanced claim class;
  - no generic filler.
- [ ] Expose labels:
  - `ai_review_real_composer_stage=R3`
  - `ai_review_real_composer_present=true`
  - `ai_review_real_composer_sections>=5`
  - `ai_review_real_composer_followup_questions>=3`
  - `ai_review_real_composer_generic_filler_blocked=true`
- [ ] Run:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run test:ai-review-composer
npm.cmd run test:ai-review-quality
npm.cmd run test:ai-report-workspace
npm.cmd run typecheck
npm.cmd run build
npm.cmd run production-check
```

Worker final: `READY_FOR_REVIEW: R3`, commit, no deploy.

---

## Task R4: End-to-End Local Review Smoke

**Purpose:** Verify the review composer through UI routes and backend packet assumptions before deploy.

**Files:**
- Modify: `frontend/src/app/reports/page.tsx`
- Modify: `frontend/src/app/report-mock-review/page.tsx`
- Modify: existing checker scripts only if needed
- Do not modify production deploy files.

- [ ] `/reports` must show:
  - benchmark case count;
  - parity status;
  - composer status;
  - blocked unsupported advanced claims.
- [ ] `/report-mock-review` must show:
  - one full composed review preview;
  - evidence refs per section;
  - follow-up questions;
  - gate result.
- [ ] Run built local smoke:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run build
$env:ENABLE_DEBUG_ROUTES='true'
npm.cmd run start -- --hostname 127.0.0.1 --port 13056
```

Then check:

```powershell
$pages=@('/reports','/report-mock-review')
foreach($page in $pages){
  $res=Invoke-WebRequest "http://127.0.0.1:13056$page" -UseBasicParsing
  if($res.StatusCode -ne 200){ exit 1 }
  if($res.Content -notmatch 'ai_review_real_composer_stage=R3'){ exit 1 }
  if($res.Content -match 'ChatExport|message default clearfix|tgme_widget_message|Ваш баланс|Энергия Света'){ exit 1 }
}
```

Worker final: `READY_FOR_REVIEW: R4`, commit, no deploy.

---

## Task R5: Deploy Checkpoint

**Purpose:** Deploy only after R1-R4 are accepted and production smoke is meaningful.

**Files:**
- No feature files unless a deploy-only fix is required.
- Use existing deploy docs/scripts.

- [ ] Verify HEAD has R1-R4 accepted commits.
- [ ] Run full local frontend suite relevant to reports/AI:

```powershell
cd C:\Projects\jyotish-agent\frontend
npm.cmd run test:ai-review-telegram-benchmark
npm.cmd run test:ai-review-benchmark-parity
npm.cmd run test:ai-review-composer
npm.cmd run test:ai-review-quality
npm.cmd run test:ai-report-workspace
npm.cmd run test:reports
npm.cmd run test:report-recipes
npm.cmd run test:report-evidence
npm.cmd run test:report-evidence-snapshot
npm.cmd run typecheck
npm.cmd run build
npm.cmd run production-check
```

- [ ] Run backend smoke if backend changed:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python -m pytest apps\reports apps\charts apps\calculations -q
```

- [ ] Deploy using existing project deploy instructions only.
- [ ] Production browser smoke:
  - `/reports`
  - `/report-mock-review` if debug route is enabled in that environment;
  - main public chart/report page.
- [ ] Worker final: `READY_FOR_REVIEW: R5`, commit if any, fresh `deployCommit`, production URLs/status.

---

## Supervisor Verification Contract

For every task:

```powershell
git status --short --branch
git rev-parse --short HEAD
git diff --name-status <previous_accepted_commit>..HEAD
git diff --check <previous_accepted_commit>..HEAD
```

Supervisor must independently run the task's required tests and source scans.

Reject the task if:
- worker stages unrelated docs;
- raw Telegram export leaks into runtime/source fixture;
- tests are skipped without a concrete reason;
- worker deploys outside R5;
- final says quality is solved/final/public-ready before R5.

Accept the task if:
- diff is scoped;
- tests pass;
- source scan passes;
- git status contains only known unrelated docs;
- final contains `READY_FOR_REVIEW`, commit, deploy status, tests, and git status.

After accepting R5, stop. Do not invent R6.
