import { existsSync, readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function read(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return readFileSync(path, "utf8");
}

const fixturePath = "src/data/ai-review-telegram-benchmark.json";
const helperPath = "src/lib/ai-review-benchmark.ts";
const qualityPath = "src/lib/ai-review-quality.ts";
const docsPath = "../docs/ai_review_quality_reset.md";
const packageJson = read("package.json");

assert(packageJson.includes('"test:ai-review-telegram-benchmark"'), "package.json must expose test:ai-review-telegram-benchmark.");

const fixtureSource = read(fixturePath);
const helperSource = read(helperPath);
const qualitySource = read(qualityPath);
const docsSource = read(docsPath);
const fixture = JSON.parse(fixtureSource);

const forbiddenFragments = [
  "ChatExport",
  "message default clearfix",
  "tgme_widget_message",
  "from_name",
  "Ваш баланс",
  "Энергия Света",
  "Выберите действие",
  '<div class="message',
  "<html",
];

const runtimeSources = [
  { path: fixturePath, source: fixtureSource },
  { path: helperPath, source: helperSource },
  { path: qualityPath, source: qualitySource },
  { path: docsPath, source: docsSource },
];

for (const { path, source } of runtimeSources) {
  for (const fragment of forbiddenFragments) {
    assert(!source.includes(fragment), `${path} leaked forbidden Telegram/raw fragment: ${fragment}`);
  }
}

assert(fixture.schemaVersion === 1, "Benchmark schemaVersion must be 1.");
assert(fixture.stage === "R1", "Benchmark stage must be R1.");
assert(fixture.sourceKind === "sanitized_telegram_export_benchmark", "Benchmark sourceKind mismatch.");
assert(fixture.privacy?.rawExportCommitted === false, "Raw export must not be committed.");
assert(fixture.privacy?.rawStyleCopied === false, "Raw Telegram style must not be copied.");
assert(fixture.privacy?.anonymizedCaseIds === true, "Case ids must be anonymized.");
assert(Array.isArray(fixture.cases) && fixture.cases.length >= 2, "Benchmark must include at least two cases.");
assert(Array.isArray(fixture.qualityTargets) && fixture.qualityTargets.length >= 3, "Benchmark must include quality targets.");

const requiredPlanets = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
let divisionalFactCount = 0;
for (const item of fixture.cases) {
  assert(/^case_[a-z0-9_]+$/.test(item.id), `Case id must be anonymized: ${item.id}`);
  assert(!/haridev|seva/i.test(item.id), `Case id exposes raw name: ${item.id}`);
  assert(Array.isArray(item.chartFacts) && item.chartFacts.length >= 8, `${item.id} must have at least eight D1 chart facts.`);
  assert(Array.isArray(item.d1Rows), `${item.id} must include d1Rows.`);
  for (const planet of requiredPlanets) {
    assert(item.d1Rows.some((row) => row.planet === planet), `${item.id} missing D1 row for ${planet}.`);
  }
  assert(
    item.d1Rows.every(
      (row) =>
        typeof row.planet === "string" &&
        typeof row.sign === "string" &&
        typeof row.degree === "number" &&
        (typeof row.house === "number" || row.house === null) &&
        typeof row.retrograde === "boolean" &&
        (typeof row.nakshatra === "string" || row.nakshatra === null),
    ),
    `${item.id} has invalid D1 row shape.`,
  );
  divisionalFactCount += item.divisionalFacts?.length ?? 0;
  assert(Array.isArray(item.calculationAccents) && item.calculationAccents.length >= 3, `${item.id} needs three calculation accents.`);
  assert(Array.isArray(item.followUpQuestions) && item.followUpQuestions.length >= 3, `${item.id} needs three follow-up questions.`);
  assert(
    item.advancedClaimCautions?.some((caution) => /shadbala/i.test(caution)) &&
      item.advancedClaimCautions?.some((caution) => /ashtakavarga/i.test(caution)) &&
      item.advancedClaimCautions?.some((caution) => /avastha/i.test(caution)),
    `${item.id} must gate unsupported shadbala/ashtakavarga/avastha claims.`,
  );
}
assert(divisionalFactCount >= 1, "Benchmark must include at least one D9/divisional fact.");

for (const marker of [
  "ai_review_telegram_sanitized_benchmark_stage=R1",
  "ai_review_telegram_sanitized_benchmark_present=true",
  "ai_review_telegram_raw_export_committed=false",
  "ai_review_telegram_style_copied=false",
  "ai_review_telegram_case_count>=2",
  "ai_review_telegram_followup_questions_present=true",
]) {
  assert(fixture.statusLabels?.includes(marker) || helperSource.includes(marker) || qualitySource.includes(marker), `Missing R1 marker: ${marker}`);
}

assert(helperSource.includes("buildAiReviewTelegramSanitizedBenchmark"), "Typed benchmark helper must export buildAiReviewTelegramSanitizedBenchmark.");
assert(qualitySource.includes("buildAiReviewTelegramSanitizedBenchmark"), "ai-review-quality must use the sanitized benchmark helper.");
assert(docsSource.includes("sanitized Telegram benchmark"), "Docs must explain sanitized Telegram benchmark purpose.");
assert(docsSource.includes("No raw export text"), "Docs must document raw export privacy rule.");
assert(docsSource.includes("No source style copying"), "Docs must document no-style-copy rule.");

console.log("AI review Telegram benchmark check passed.");
