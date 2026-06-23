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
  "E122-A",
  "P123-A",
  "E124-A",
  "P125-A",
  "E126-A",
  "P127-A",
  "E128-A",
  "ai_review_quality_eval_stage=P119-A",
  "ai_review_quality_preview_stage=E120-A",
  "ai_review_composer_stage=P121-A",
  "ai_review_prompt_contract_stage=E122-A",
  "ai_review_multi_fixture_stage=P123-A",
  "ai_review_telegram_benchmark_stage=E124-A",
  "ai_review_question_contract_stage=P125-A",
  "ai_review_assertion_ledger_stage=E126-A",
  "ai_review_narrative_rubric_stage=P127-A",
  "ai_review_response_contract_stage=E128-A",
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
  "ai_review_prompt_payload_present=true",
  "ai_review_prompt_uses_evidence_packet=true",
  "ai_review_prompt_requires_three_evidence_citations=true",
  "ai_review_prompt_sections_present=true",
  "ai_review_anti_generic_guardrails_present=true",
  "ai_review_quality_gate_before_final_answer=true",
  "ai_review_quality_fixture_matrix_present=true",
  "ai_review_multiple_intents_covered=true",
  "ai_review_scenario_count=4",
  "ai_review_each_scenario_has_four_evidence_items=true",
  "ai_review_each_scenario_requires_three_citations=true",
  "ai_review_strong_outputs_pass_all_scenarios=true",
  "ai_review_generic_outputs_blocked_all_scenarios=true",
  "ai_review_prompt_contract_applied_all_scenarios=true",
  "ai_review_telegram_benchmark_present=true",
  "ai_review_benchmark_charts_count=2",
  "ai_review_benchmark_uses_chart_facts=true",
  "ai_review_benchmark_extracts_accents_not_style=true",
  "ai_review_benchmark_followup_questions_present=true",
  "ai_review_benchmark_advanced_claims_gated=true",
  "ai_review_blueprint_sections_present=true",
  "ai_review_followup_question_contract_present=true",
  "ai_review_followup_questions_total>=8",
  "ai_review_followup_questions_ready>=5",
  "ai_review_followup_questions_gated>=2",
  "ai_review_followup_questions_rejected_generic>=1",
  "ai_review_followup_questions_grounded_in_chart_facts=true",
  "ai_review_followup_questions_use_benchmark_blueprint=true",
  "ai_review_followup_questions_avoid_generic_prompts=true",
  "ai_review_advanced_claims_blocked_without_calculation=true",
  "ai_review_question_contract_visible=true",
  "ai_review_assertion_ledger_present=true",
  "ai_review_assertions_total>=12",
  "ai_review_assertions_computed_chart_facts>=5",
  "ai_review_assertions_jyotish_rules>=3",
  "ai_review_assertions_derived_synthesis>=2",
  "ai_review_assertions_practical_guidance>=2",
  "ai_review_assertions_blocked_advanced>=2",
  "ai_review_composed_review_sections_present=true",
  "ai_review_composed_review_uses_only_usable_assertions=true",
  "ai_review_composed_review_cites_ledger_anchors=true",
  "ai_review_advanced_claims_visible_as_blocked=true",
  "ai_review_local_quality_harness_not_final_output=true",
  "ai_review_narrative_rubric_present=true",
  "ai_review_narrative_dimensions=chart_specificity,rule_to_interpretation_chain,life_domain_tension,practical_next_question,caveat_and_gating",
  "ai_review_narrative_sample_count>=3",
  "ai_review_strong_grounded_sample_passes=true",
  "ai_review_generic_pretty_sample_blocked=true",
  "ai_review_overclaimed_advanced_sample_blocked=true",
  "ai_review_passing_samples_have_four_anchors=true",
  "ai_review_rubric_failure_reasons_visible=true",
  "ai_review_narrative_quality_matrix_visible=true",
  "ai_review_response_contract_present=true",
  "ai_review_response_contract_sections=5",
  "ai_review_response_contract_sections_exact=true",
  "ai_review_response_contract_every_section_requires_anchor=true",
  "ai_review_response_contract_every_section_has_repair=true",
  "ai_review_repair_guidance_present=true",
  "ai_review_repair_generic_without_anchors_present=true",
  "ai_review_repair_advanced_overclaim_present=true",
  "ai_review_repair_missing_practical_question_present=true",
  "ai_review_response_contract_uses_assertion_ledger=true",
  "ai_review_response_contract_uses_narrative_rubric=true",
  "ai_review_response_contract_visible=true",
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
  "Prompt contract dry run",
  "System quality rules",
  "Chart evidence packet",
  "Required review structure",
  "Anti-generic guardrails",
  "Quality gate before final answer",
  "local-only and no LLM call was executed",
  "Require at least 3 evidence citations",
  "Block or revise generic text that lacks chart evidence and synthesis",
  "AI review regression matrix",
  "Natal personality",
  "Career dharma",
  "Relationship compatibility",
  "Transit timing guidance",
  "Evidence items",
  "Required citations",
  "Strong status",
  "Weak generic status",
  "Improvement reason",
  "Telegram benchmark accents",
  "Haridev D1/D9 benchmark",
  "Seva D1/career benchmark",
  "Chart fact",
  "Jyotish rule",
  "Interpretive accent",
  "Risk or caveat",
  "Practical next step",
  "Next question",
  "source style is intentionally not copied",
  "advanced claims gated unless calculated table exists",
  "10th-house Aries cluster",
  "Sookshma-dasha Mars timing",
  "D9 relationship layer",
  "Grounded follow-up question contract",
  "Ready chart-grounded questions",
  "Gated advanced claims",
  "Rejected generic prompts",
  "Anchor fact",
  "Rule/accent",
  "Question status",
  "Assertion ledger",
  "computed_chart_fact",
  "jyotish_rule",
  "derived_synthesis",
  "practical_guidance",
  "gated_advanced_claim",
  "Grounded chart facts",
  "Jyotish interpretation",
  "Practical focus",
  "Caveats and blocked claims",
  "local deterministic quality harness, not final AI output",
  "Narrative quality rubric",
  "chart_specificity",
  "rule_to_interpretation_chain",
  "life_domain_tension",
  "practical_next_question",
  "caveat_and_gating",
  "strong_grounded_review",
  "generic_pretty_review",
  "overclaimed_advanced_review",
  "Passed dimensions",
  "Failed dimensions",
  "Anchor count",
  "Key failure reason",
  "not final generated AI output",
  "AI review response contract",
  "Chart anchors",
  "Rule chain",
  "Interpretive tension",
  "Practical next question",
  "Caveats and gated claims",
  "Required anchors",
  "Required rubric dimensions",
  "Repair instruction",
  "Failing draft coverage",
  "generic without anchors",
  "advanced overclaim without computed tables",
  "advice without practical next question",
  "Shadbala",
  "Ashtakavarga",
  "Avastha",
  "Mrityu-bhaga",
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
assert(typeof helper.buildAiReviewPromptPayload === "function", "buildAiReviewPromptPayload must be exported.");
assert(typeof helper.buildAiReviewScenarioMatrix === "function", "buildAiReviewScenarioMatrix must be exported.");
assert(typeof helper.buildTelegramBenchmarkReviewBlueprint === "function", "buildTelegramBenchmarkReviewBlueprint must be exported.");
assert(typeof helper.buildAiReviewFollowupQuestionContract === "function", "buildAiReviewFollowupQuestionContract must be exported.");
assert(typeof helper.buildAiReviewAssertionLedger === "function", "buildAiReviewAssertionLedger must be exported.");
assert(typeof helper.buildAiReviewNarrativeQualityRubric === "function", "buildAiReviewNarrativeQualityRubric must be exported.");
assert(typeof helper.buildAiReviewResponseContract === "function", "buildAiReviewResponseContract must be exported.");

const strong = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.strong.draft, helper.aiReviewQualityFixtures.strong.fixtureEvidence);
const weak = helper.evaluateAiReviewDraft(helper.aiReviewQualityFixtures.weak.draft, helper.aiReviewQualityFixtures.weak.fixtureEvidence);
const packet = helper.buildAiReviewEvidencePacket();
const preview = helper.buildAiReviewMockPreview();
const composed = helper.composeEvidenceDrivenMockReview(packet);
const promptPayload = helper.buildAiReviewPromptPayload(packet, composed);
const scenarioMatrix = helper.buildAiReviewScenarioMatrix();
const telegramBenchmark = helper.buildTelegramBenchmarkReviewBlueprint();
const questionContract = helper.buildAiReviewFollowupQuestionContract();
const assertionLedger = helper.buildAiReviewAssertionLedger();
const narrativeRubric = helper.buildAiReviewNarrativeQualityRubric();
const responseContract = helper.buildAiReviewResponseContract();

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
assert(promptPayload.stage === "E122-A", "Prompt payload stage must be E122-A.");
assert(promptPayload.statusLabels.includes("ai_review_prompt_contract_stage=E122-A"), "Prompt payload status labels missing E122 stage.");
assert(promptPayload.sections.map((section) => section.heading).join("|") === "System quality rules|Chart evidence packet|Required review structure|Anti-generic guardrails|Quality gate before final answer", "Prompt payload sections changed.");
assert(promptPayload.evidenceItems.length >= 4, "Prompt payload must include at least four chart evidence items.");
assert(promptPayload.requiredEvidenceCitationCount >= 3, "Prompt payload must require at least three evidence citations.");
assert(promptPayload.localOnly === true, "Prompt payload must be local-only.");
assert(promptPayload.llmNetworkCallExecuted === false, "Prompt payload must not execute an LLM/network call.");
assert(promptPayload.antiGenericGuardrails.some((item) => item.includes("Block or revise generic text")), "Prompt payload must block/revise generic text.");
assert(promptPayload.qualityGateBeforeFinalAnswer.join(",") === "interpretation_depth,specific_chart_evidence,practical_synthesis,caveats_confidence", "Prompt payload quality gate dimensions changed.");
assert(scenarioMatrix.stage === "P123-A", "Scenario matrix stage must be P123-A.");
assert(scenarioMatrix.statusLabels.includes("ai_review_multi_fixture_stage=P123-A"), "Scenario matrix status labels missing P123 stage.");
assert(scenarioMatrix.scenarios.length >= 4, "Scenario matrix must cover at least four review scenarios.");
assert(scenarioMatrix.aggregate.scenarioCount >= 4, "Scenario aggregate must report at least four scenarios.");
assert(scenarioMatrix.aggregate.strongPassCount === scenarioMatrix.scenarios.length, "Every strong scenario must pass.");
assert(scenarioMatrix.aggregate.weakBlockedCount === scenarioMatrix.scenarios.length, "Every weak scenario must be blocked.");
assert(scenarioMatrix.aggregate.minimumEvidenceItemCount >= 4, "Every scenario must carry at least four evidence items.");
assert(scenarioMatrix.aggregate.promptContractAppliedAllScenarios === true, "Prompt contract must apply to all scenarios.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.evidenceItems.length >= 4), "Each scenario must include at least four evidence items.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.requiredEvidenceCitationCount >= 3), "Each scenario must require at least three citations.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.strong.status === "passes_quality_gate"), "Every strong scenario must pass the gate.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.weak.status === "blocked_by_quality_gate"), "Every weak scenario must be blocked.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.promptPayload.requiredEvidenceCitationCount >= 3), "Every scenario prompt payload must require at least three citations.");
assert(scenarioMatrix.scenarios.every((scenario) => scenario.promptPayload.evidenceItems.length >= 4), "Every scenario prompt payload must include at least four evidence items.");
assert(telegramBenchmark.stage === "E124-A", "Telegram benchmark stage must be E124-A.");
assert(telegramBenchmark.statusLabels.includes("ai_review_telegram_benchmark_stage=E124-A"), "Telegram benchmark labels missing E124 stage.");
assert(telegramBenchmark.benchmarks.length >= 2, "Telegram benchmark must include at least two named charts.");
assert(telegramBenchmark.benchmarks.every((benchmark) => benchmark.chartFacts.length >= 4), "Each Telegram benchmark must include at least four chart facts.");
assert(telegramBenchmark.benchmarks.every((benchmark) => benchmark.calculationAccents.length >= 3), "Each Telegram benchmark must include at least three accents/rules.");
assert(telegramBenchmark.benchmarks.every((benchmark) => benchmark.followUpQuestions.length >= 3), "Each Telegram benchmark must include at least three follow-up questions.");
assert(telegramBenchmark.benchmarks.every((benchmark) => benchmark.advancedClaimCautions.length >= 3), "Advanced claims must be gated with cautions.");
assert(telegramBenchmark.blueprintSections.join("|") === "Chart fact|Jyotish rule|Interpretive accent|Risk or caveat|Practical next step|Next question", "Benchmark blueprint sections changed.");
assert(telegramBenchmark.benchmarks.some((benchmark) => benchmark.name === "Haridev D1/D9 benchmark"), "Haridev benchmark missing.");
assert(telegramBenchmark.benchmarks.some((benchmark) => benchmark.name === "Seva D1/career benchmark"), "Seva benchmark missing.");
assert(telegramBenchmark.styleCopied === false, "Telegram benchmark must not copy source prose style.");
assert(questionContract.stage === "P125-A", "Question contract stage must be P125-A.");
assert(questionContract.statusLabels.includes("ai_review_question_contract_stage=P125-A"), "Question contract labels missing P125 stage.");
assert(questionContract.candidates.length >= 8, "Question contract must include at least eight candidates.");
assert(questionContract.aggregate.readyCount >= 5, "Question contract must include at least five ready questions.");
assert(questionContract.aggregate.gatedCount >= 2, "Question contract must include at least two gated questions.");
assert(questionContract.aggregate.rejectedGenericCount >= 1, "Question contract must include at least one rejected generic question.");
assert(questionContract.aggregate.groundedInChartFacts === true, "Ready questions must be grounded in chart facts.");
assert(questionContract.aggregate.advancedClaimsBlockedWithoutCalculation === true, "Advanced claims must be blocked without calculated tables.");
assert(questionContract.candidates.filter((candidate) => candidate.status === "ready").every((candidate) => candidate.anchorChartFact && candidate.jyotishRuleAccent), "Ready questions must include anchor facts and rules.");
assert(questionContract.candidates.filter((candidate) => candidate.status === "rejected").every((candidate) => candidate.reason.includes("generic")), "Rejected questions must explain generic prompt failure.");
assert(questionContract.candidates.some((candidate) => candidate.status === "rejected" && candidate.question.includes("What should I do next?")), "Generic rejected question fixture missing.");
const advancedTerms = ["Shadbala", "Ashtakavarga", "Avastha", "Mrityu-bhaga"];
assert(
  questionContract.candidates
    .filter((candidate) => advancedTerms.some((term) => candidate.question.includes(term) || candidate.jyotishRuleAccent.includes(term)))
    .every((candidate) => candidate.status === "gated" && candidate.reason.includes("calculated table")),
  "Advanced claim questions must be gated unless computed-table support exists.",
);
assert(assertionLedger.stage === "E126-A", "Assertion ledger stage must be E126-A.");
assert(assertionLedger.statusLabels.includes("ai_review_assertion_ledger_stage=E126-A"), "Assertion ledger labels missing E126 stage.");
assert(assertionLedger.assertions.length >= 12, "Assertion ledger must include at least twelve assertions.");
assert(assertionLedger.aggregate.computedChartFactCount >= 5, "Assertion ledger must include at least five computed chart facts.");
assert(assertionLedger.aggregate.jyotishRuleCount >= 3, "Assertion ledger must include at least three jyotish rules.");
assert(assertionLedger.aggregate.derivedSynthesisCount >= 2, "Assertion ledger must include at least two derived synthesis assertions.");
assert(assertionLedger.aggregate.practicalGuidanceCount >= 2, "Assertion ledger must include at least two practical guidance assertions.");
assert(assertionLedger.aggregate.blockedAdvancedCount >= 2, "Assertion ledger must include at least two blocked advanced claims.");
assert(assertionLedger.aggregate.usableCount > assertionLedger.aggregate.blockedCount, "Assertion ledger should have usable assertions plus blocked claims.");
assert(assertionLedger.composedReview.sections.map((section) => section.heading).join("|") === "Grounded chart facts|Jyotish interpretation|Practical focus|Caveats and blocked claims", "Assertion-ledger composed sections changed.");
assert(assertionLedger.composedReview.sections.every((section) => section.anchorIds.length >= 1), "Every composed-review section must cite ledger anchors.");
assert(assertionLedger.composedReview.sections.every((section) => section.anchorIds.every((id) => assertionLedger.assertions.some((assertion) => assertion.id === id))), "Composed-review anchors must resolve to ledger assertions.");
const usableAssertionIds = new Set(assertionLedger.assertions.filter((assertion) => assertion.status === "usable").map((assertion) => assertion.id));
const blockedAssertionIds = new Set(assertionLedger.assertions.filter((assertion) => assertion.status === "blocked").map((assertion) => assertion.id));
assert(
  assertionLedger.composedReview.sections
    .filter((section) => section.heading !== "Caveats and blocked claims")
    .every((section) => section.anchorIds.every((id) => usableAssertionIds.has(id))),
  "Usable composed-review sections must not include blocked assertions.",
);
assert(
  assertionLedger.composedReview.sections
    .find((section) => section.heading === "Caveats and blocked claims")
    ?.anchorIds.some((id) => blockedAssertionIds.has(id)),
  "Caveats section must cite blocked advanced claims.",
);
assert(
  assertionLedger.assertions
    .filter((assertion) => advancedTerms.some((term) => assertion.assertion.includes(term)))
    .every((assertion) => assertion.status === "blocked" && assertion.sourceType === "gated_advanced_claim"),
  "Advanced terms must appear only as blocked gated advanced claims.",
);
assert(narrativeRubric.stage === "P127-A", "Narrative rubric stage must be P127-A.");
assert(narrativeRubric.statusLabels.includes("ai_review_narrative_rubric_stage=P127-A"), "Narrative rubric labels missing P127 stage.");
assert(narrativeRubric.dimensions.join(",") === "chart_specificity,rule_to_interpretation_chain,life_domain_tension,practical_next_question,caveat_and_gating", "Narrative dimensions changed.");
assert(narrativeRubric.samples.length >= 3, "Narrative rubric must include at least three samples.");
assert(narrativeRubric.aggregate.strongPassCount >= 1, "Narrative rubric must include a passing strong sample.");
assert(narrativeRubric.aggregate.blockedGenericCount >= 1, "Narrative rubric must block a generic pretty sample.");
assert(narrativeRubric.aggregate.blockedOverclaimCount >= 1, "Narrative rubric must block an overclaimed advanced sample.");
assert(narrativeRubric.aggregate.passingSamplesHaveFourAnchors === true, "Every passing narrative sample must have at least four anchors.");
const strongNarrative = narrativeRubric.samples.find((sample) => sample.id === "strong_grounded_review");
const genericNarrative = narrativeRubric.samples.find((sample) => sample.id === "generic_pretty_review");
const overclaimNarrative = narrativeRubric.samples.find((sample) => sample.id === "overclaimed_advanced_review");
assert(strongNarrative?.status === "passes_quality_rubric", "Strong grounded narrative sample must pass.");
assert(genericNarrative?.status === "blocked_by_quality_rubric", "Generic pretty narrative sample must be blocked.");
assert(overclaimNarrative?.status === "blocked_by_quality_rubric", "Overclaimed advanced narrative sample must be blocked.");
assert(strongNarrative.anchorCount >= 4, "Strong narrative sample must cite at least four ledger anchors.");
assert(strongNarrative.hasLifeDomainTension === true, "Strong narrative sample must include concrete life-domain tension.");
assert(strongNarrative.hasPracticalNextQuestion === true, "Strong narrative sample must include a practical next question.");
assert(genericNarrative.failedDimensions.includes("chart_specificity"), "Generic pretty sample must fail chart specificity.");
assert(genericNarrative.failedDimensions.includes("rule_to_interpretation_chain"), "Generic pretty sample must fail rule-to-interpretation chain.");
assert(overclaimNarrative.failedDimensions.includes("caveat_and_gating"), "Overclaimed advanced sample must fail caveat/gating.");
assert(
  overclaimNarrative.text.includes("Shadbala") &&
    overclaimNarrative.text.includes("Ashtakavarga") &&
    overclaimNarrative.text.includes("Avastha") &&
    overclaimNarrative.text.includes("Mrityu-bhaga"),
  "Overclaim sample must cover gated advanced terms.",
);
assert(responseContract.stage === "E128-A", "Response contract stage must be E128-A.");
assert(responseContract.statusLabels.includes("ai_review_response_contract_stage=E128-A"), "Response contract labels missing E128 stage.");
assert(responseContract.sections.length === 5, "Response contract must define exactly five sections.");
assert(responseContract.sections.map((section) => section.name).join("|") === "Chart anchors|Rule chain|Interpretive tension|Practical next question|Caveats and gated claims", "Response contract section names changed.");
assert(responseContract.sections.every((section) => section.requiredSourceAnchorCount >= 1), "Every response section must require at least one anchor.");
assert(responseContract.sections.every((section) => section.repairInstruction.length > 0), "Every response section must include repair instruction.");
assert(responseContract.sections.every((section) => section.requiredRubricDimensions.length >= 1), "Every response section must require rubric dimensions.");
assert(responseContract.sections.every((section) => section.blockedFailureExamples.length >= 1), "Every response section must include blocked failure examples.");
assert(responseContract.aggregate.sectionCount === 5, "Response contract aggregate section count must be five.");
assert(responseContract.aggregate.sectionsExact === true, "Response contract must mark sections exact.");
assert(responseContract.aggregate.everySectionRequiresAnchor === true, "Response contract must require anchors in every section.");
assert(responseContract.aggregate.everySectionHasRepair === true, "Response contract must include repair guidance in every section.");
assert(responseContract.aggregate.genericRepairPresent === true, "Generic-without-anchors repair guidance missing.");
assert(responseContract.aggregate.advancedOverclaimRepairPresent === true, "Advanced-overclaim repair guidance missing.");
assert(responseContract.aggregate.missingPracticalQuestionRepairPresent === true, "Missing-practical-question repair guidance missing.");
assert(responseContract.usesAssertionLedger === true, "Response contract must use assertion ledger.");
assert(responseContract.usesNarrativeRubric === true, "Response contract must use narrative rubric.");
for (const repairType of ["generic_without_anchors", "advanced_overclaim_without_computed_tables", "advice_without_practical_next_question"]) {
  assert(responseContract.repairGuidance.some((repair) => repair.type === repairType), `Missing repair guidance: ${repairType}`);
}

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
  "final generated AI output is solved",
]) {
  assert(!helperSource.includes(forbidden), `Helper contains forbidden marker: ${forbidden}`);
  assert(!page.includes(forbidden), `/reports contains forbidden marker: ${forbidden}`);
}

console.log("AI review quality gate check passed.");
