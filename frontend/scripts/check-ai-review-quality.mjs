import { existsSync, readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function read(path) {
  assert(existsSync(path), `Missing file: ${path}`);
  return readFileSync(path, "utf8");
}

function loadTsModule(path) {
  const source = read(path);
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(output, { exports: module.exports, module }, { filename: path });
  return module.exports;
}

const helperPath = "src/lib/ai-review-quality.ts";
const pagePath = "src/app/reports/page.tsx";
const packageJson = read("package.json");
const helperSource = read(helperPath);
const page = read(pagePath);
const combinedSource = `${helperSource}\n${page}`;
const combinedSourceLower = combinedSource.toLowerCase();
const helper = loadTsModule(helperPath);

assert(packageJson.includes("\"test:ai-review-quality\""), "package.json must expose test:ai-review-quality.");

for (const marker of [
  "P119-A",
  "ai_review_quality_eval_stage=P119-A",
  "ai_review_quality_gate_present=true",
  "ai_review_fixture_strong_passes=true",
  "ai_review_fixture_weak_fails=true",
  "ai_review_generic_filler_guard=true",
  "ai_review_quality_dimensions=interpretation_depth,specific_chart_evidence,practical_synthesis,caveats_confidence",
  "ai_review_llm_network_call_executed=false",
  "backend_calculation_changed=false",
  "production_deploy_skipped_per_user_batching_policy=true",
  "last_verified_deploy_commit=508df50",
]) {
  assert(helperSource.includes(marker) || page.includes(marker), `Missing P119 marker: ${marker}`);
}

for (const label of [
  "Interpretation depth",
  "Specific chart evidence",
  "Practical synthesis",
  "Caveats and confidence",
  "chart-specific evidence, not generic advice",
  "synthesis across multiple placements/factors",
  "practical next-step framing",
  "caveats/confidence",
  "local quality gate/harness",
  "not a generated final review",
]) {
  assert(combinedSourceLower.includes(label.toLowerCase()), `/reports missing quality-lab label: ${label}`);
}

assert(Array.isArray(helper.AI_REVIEW_QUALITY_DIMENSIONS), "AI_REVIEW_QUALITY_DIMENSIONS must be exported.");
assert(helper.AI_REVIEW_QUALITY_DIMENSIONS.join(",") === "interpretation_depth,specific_chart_evidence,practical_synthesis,caveats_confidence", "Quality dimensions order changed.");
assert(helper.aiReviewQualityFixtures?.strong?.draft, "Strong fixture missing.");
assert(helper.aiReviewQualityFixtures?.weak?.draft, "Weak fixture missing.");
assert(typeof helper.evaluateAiReviewDraft === "function", "evaluateAiReviewDraft must be exported.");

const strong = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.strong.draft, helper.aiReviewQualityFixtures.strong.fixtureEvidence);
const weak = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.weak.draft, helper.aiReviewQualityFixtures.weak.fixtureEvidence);

assert(strong.passed === true, "Strong fixture must pass the quality gate.");
assert(weak.passed === false, "Weak fixture must fail the quality gate.");
assert(weak.genericFillerGuard.passed === false, "Weak fixture must fail the generic filler guard.");
assert(strong.dimensions.every((item) => item.passed), "Strong fixture must pass every quality dimension.");
assert(weak.dimensions.some((item) => !item.passed), "Weak fixture must fail at least one quality dimension.");
assert(strong.matchedEvidence.length >= 3, "Strong fixture must cite at least three chart-evidence terms.");

for (const forbidden of [
  "fetch(",
  "XMLHttpRequest",
  "navigator.sendBeacon",
  "OpenAI",
  "OPENAI_API_KEY",
  "sk-proj",
  "release ready",
  "parity success",
  "formula accuracy improved",
  "final generated AI output",
]) {
  assert(!helperSource.includes(forbidden), `Helper contains forbidden marker: ${forbidden}`);
  assert(!page.includes(forbidden), `/reports contains forbidden marker: ${forbidden}`);
}

console.log("AI review quality gate check passed.");
