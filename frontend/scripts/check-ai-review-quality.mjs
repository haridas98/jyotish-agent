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
  "E120-A",
  "P121-A",
  "ai_review_quality_eval_stage=P119-A",
  "ai_review_quality_preview_stage=E120-A",
  "ai_review_composer_stage=P121-A",
  "ai_review_quality_gate_present=true",
  "ai_review_fixture_strong_passes=true",
  "ai_review_fixture_weak_fails=true",
  "ai_review_generic_filler_guard=true",
  "ai_review_evidence_packet_present=true",
  "ai_review_quality_gate_applied_to_mock_preview=true",
  "ai_review_strong_preview_pass_visible=true",
  "ai_review_weak_preview_blocked_visible=true",
  "ai_review_failed_dimension_feedback_present=true",
  "ai_review_matched_evidence_count_visible=true",
  "ai_review_evidence_driven_mock_review_present=true",
  "ai_review_composed_sections_present=true",
  "ai_review_composer_uses_evidence_packet=true",
  "ai_review_composed_strong_passes_gate=true",
  "ai_review_generic_output_blocked_by_gate=true",
  "ai_review_generic_block_reason_visible=true",
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
  "review evidence packet",
  "Strong preview: passes quality gate",
  "Weak preview: blocked by quality gate",
  "Failed dimensions",
  "Matched evidence count",
  "Evidence-driven mock review",
  "Chart evidence cited",
  "Interpretive synthesis",
  "Practical guidance",
  "Caveats and confidence",
  "Strong composed review passes quality gate",
  "Generic output blocked by quality gate",
  "generic text lacks chart evidence and synthesis",
  "lacks chart-specific evidence",
  "lacks practical synthesis",
  "not a generated final review",
]) {
  assert(combinedSourceLower.includes(label.toLowerCase()), `/reports missing quality-lab label: ${label}`);
}

assert(Array.isArray(helper.AI_REVIEW_QUALITY_DIMENSIONS), "AI_REVIEW_QUALITY_DIMENSIONS must be exported.");
assert(helper.AI_REVIEW_QUALITY_DIMENSIONS.join(",") === "interpretation_depth,specific_chart_evidence,practical_synthesis,caveats_confidence", "Quality dimensions order changed.");
assert(helper.aiReviewQualityFixtures?.strong?.draft, "Strong fixture missing.");
assert(helper.aiReviewQualityFixtures?.weak?.draft, "Weak fixture missing.");
assert(typeof helper.evaluateAiReviewDraft === "function", "evaluateAiReviewDraft must be exported.");
assert(typeof helper.buildAiReviewEvidencePacket === "function", "buildAiReviewEvidencePacket must be exported.");
assert(typeof helper.buildAiReviewMockPreview === "function", "buildAiReviewMockPreview must be exported.");
assert(typeof helper.composeEvidenceDrivenMockReview === "function", "composeEvidenceDrivenMockReview must be exported.");

const strong = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.strong.draft, helper.aiReviewQualityFixtures.strong.fixtureEvidence);
const weak = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.weak.draft, helper.aiReviewQualityFixtures.weak.fixtureEvidence);
const packet = helper.buildAiReviewEvidencePacket();
const preview = helper.buildAiReviewMockPreview();
const composed = helper.composeEvidenceDrivenMockReview(packet);

assert(strong.passed === true, "Strong fixture must pass the quality gate.");
assert(weak.passed === false, "Weak fixture must fail the quality gate.");
assert(weak.genericFillerGuard.passed === false, "Weak fixture must fail the generic filler guard.");
assert(strong.dimensions.every((item) => item.passed), "Strong fixture must pass every quality dimension.");
assert(weak.dimensions.some((item) => !item.passed), "Weak fixture must fail at least one quality dimension.");
assert(strong.matchedEvidence.length >= 3, "Strong fixture must cite at least three chart-evidence terms.");
assert(packet.chartEvidenceItems.length >= 4, "Evidence packet must include concrete chart evidence items.");
assert(packet.synthesisLinks.length >= 2, "Evidence packet must include synthesis links.");
assert(packet.practicalNextStepRequirement.includes("practical next-step"), "Evidence packet must include practical next-step requirement.");
assert(packet.caveatConfidenceRequirement.includes("confidence"), "Evidence packet must include caveat/confidence requirement.");
assert(preview.strong.status === "passes_quality_gate", "Strong preview must pass.");
assert(preview.weak.status === "blocked_by_quality_gate", "Weak preview must be blocked.");
assert(preview.strong.matchedEvidenceCount >= 3, "Strong preview must expose matched evidence count.");
assert(preview.weak.failedDimensionFeedback.some((item) => item.includes("lacks chart-specific evidence")), "Weak preview must explain missing chart-specific evidence.");
assert(preview.weak.failedDimensionFeedback.some((item) => item.includes("lacks practical synthesis")), "Weak preview must explain missing practical synthesis.");
assert(preview.weak.passed === false, "Weak generic preview must not pass.");
assert(composed.stage === "P121-A", "Composer stage must be P121-A.");
assert(composed.statusLabels.includes("ai_review_composer_stage=P121-A"), "Composer status labels missing P121 stage.");
assert(composed.sections.map((section) => section.heading).join("|") === "Chart evidence cited|Interpretive synthesis|Practical guidance|Caveats and confidence", "Composer sections changed.");
assert(composed.strong.status === "passes_quality_gate", "Strong composed review must pass.");
assert(composed.strong.matchedEvidenceCount >= 3, "Strong composed review must cite at least three evidence references.");
assert(composed.weak.status === "blocked_by_quality_gate", "Weak generic output must be blocked.");
assert(composed.weak.usableReviewVisible === false, "Weak generic output must not be displayed as usable review.");
assert(composed.weak.blockReason.includes("generic text lacks chart evidence and synthesis"), "Weak block reason must be concrete.");

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
