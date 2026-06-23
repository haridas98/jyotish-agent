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

const moduleCache = new Map();

function loadTsModule(path) {
  if (moduleCache.has(path)) return moduleCache.get(path);
  const source = read(path);
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
  }).outputText;
  const module = { exports: {} };
  moduleCache.set(path, module.exports);
  function localRequire(specifier) {
    if (specifier === "@/lib/ai-review-benchmark") return loadTsModule("src/lib/ai-review-benchmark.ts");
    if (specifier === "@/lib/ai-review-benchmark-parity") return loadTsModule("src/lib/ai-review-benchmark-parity.ts");
    if (specifier === "@/data/ai-review-telegram-benchmark.json") return { default: JSON.parse(read("src/data/ai-review-telegram-benchmark.json")) };
    throw new Error(`Unsupported test loader import: ${specifier}`);
  }
  vm.runInNewContext(output, { exports: module.exports, module, require: localRequire, structuredClone }, { filename: path });
  return module.exports;
}

const helperPath = "src/lib/ai-review-quality.ts";
const benchmarkHelperPath = "src/lib/ai-review-benchmark.ts";
const benchmarkParityPath = "src/lib/ai-review-benchmark-parity.ts";
const benchmarkFixturePath = "src/data/ai-review-telegram-benchmark.json";
const pagePath = "src/app/reports/page.tsx";
const mockReviewPagePath = "src/app/report-mock-review/page.tsx";
const packageJson = read("package.json");
const helperSource = read(helperPath);
const benchmarkHelperSource = read(benchmarkHelperPath);
const benchmarkParitySource = read(benchmarkParityPath);
const benchmarkFixtureSource = read(benchmarkFixturePath);
const page = read(pagePath);
const mockReviewPage = read(mockReviewPagePath);
const combinedSource = `${helperSource}\n${benchmarkHelperSource}\n${benchmarkParitySource}\n${benchmarkFixtureSource}\n${page}\n${mockReviewPage}`;
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
  "R1",
  "R2",
  "P125-A",
  "E126-A",
  "P127-A",
  "E128-A",
  "P129-A",
  "E130-A",
  "P131-A",
  "E132-A",
  "P133-A",
  "E134-A",
  "P135-A",
  "ai_review_quality_eval_stage=P119-A",
  "ai_review_quality_preview_stage=E120-A",
  "ai_review_composer_stage=P121-A",
  "ai_review_prompt_contract_stage=E122-A",
  "ai_review_multi_fixture_stage=P123-A",
  "ai_review_telegram_benchmark_stage=E124-A",
  "ai_review_telegram_sanitized_benchmark_stage=R1",
  "ai_review_benchmark_parity_stage=R2",
  "ai_review_question_contract_stage=P125-A",
  "ai_review_assertion_ledger_stage=E126-A",
  "ai_review_narrative_rubric_stage=P127-A",
  "ai_review_response_contract_stage=E128-A",
  "ai_review_response_contract_shared_stage=P129-A",
  "ai_review_calculation_packet_stage=E130-A",
  "ai_review_grounded_draft_evaluator_stage=P131-A",
  "ai_review_grounded_composer_stage=E132-A",
  "ai_review_generation_boundary_stage=P133-A",
  "ai_review_audio_consultation_benchmark_stage=E134-A",
  "ai_review_consultation_method_stage=P135-A",
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
  "ai_review_telegram_sanitized_benchmark_present=true",
  "ai_review_telegram_raw_export_committed=false",
  "ai_review_telegram_style_copied=false",
  "ai_review_telegram_case_count>=2",
  "ai_review_telegram_followup_questions_present=true",
  "ai_review_benchmark_parity_present=true",
  "ai_review_benchmark_d1_rows_checked>=18",
  "ai_review_benchmark_unsupported_advanced_claims_gated=true",
  "ai_review_benchmark_lagna_present=true",
  "ai_review_benchmark_nakshatra_present=true",
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
  "ai_review_response_contract_shared_source=true",
  "ai_review_response_contract_shared_across_surfaces=true",
  "ai_review_response_contract_reports_surface=true",
  "ai_review_response_contract_mock_review_surface=true",
  "ai_review_response_contract_mock_review_visible=true",
  "ai_review_response_contract_shared_sections=5",
  "ai_review_response_contract_shared_sections_exact=true",
  "ai_review_response_contract_shared_repair_guidance=true",
  "ai_review_response_contract_shared_generic_repair=true",
  "ai_review_response_contract_shared_overclaim_repair=true",
  "ai_review_response_contract_shared_missing_question_repair=true",
  "ai_review_response_contract_product_gate_not_final_output=true",
  "ai_review_calculation_evidence_packet_present=true",
  "ai_review_calculation_evidence_groups=6",
  "ai_review_calculation_evidence_groups_minimum_met=true",
  "ai_review_calculation_group_chart_placements=true",
  "ai_review_calculation_group_lord_relationships=true",
  "ai_review_calculation_group_dignity_strength=true",
  "ai_review_calculation_group_yoga_candidates=true",
  "ai_review_calculation_group_dasha_transit_timing=true",
  "ai_review_calculation_group_tension_flags=true",
  "ai_review_sanitized_benchmark_cases_present=true",
  "ai_review_sanitized_benchmark_cases=3",
  "ai_review_sanitized_benchmark_cases_minimum_met=true",
  "ai_review_benchmark_cases_have_focus_accent_question=true",
  "ai_review_benchmark_raw_export_text_committed=false",
  "ai_review_prompt_packet_uses_shared_response_contract=true",
  "ai_review_prompt_packet_uses_assertion_ledger=true",
  "ai_review_prompt_packet_uses_calculation_evidence=true",
  "ai_review_prompt_packet_uses_sanitized_benchmarks=true",
  "ai_review_prompt_packet_visible=true",
  "ai_review_prompt_packet_not_final_output=true",
  "ai_review_grounded_draft_evaluator_present=true",
  "ai_review_grounded_draft_fixtures=3",
  "ai_review_grounded_draft_fixtures_minimum_met=true",
  "ai_review_grounded_draft_strong_passes=true",
  "ai_review_grounded_draft_generic_fails=true",
  "ai_review_grounded_draft_overclaim_fails=true",
  "ai_review_grounded_draft_strong_groups_hit_minimum_met=true",
  "ai_review_grounded_draft_repairs_present=true",
  "ai_review_grounded_draft_uses_calculation_packet=true",
  "ai_review_grounded_draft_uses_shared_response_contract=true",
  "ai_review_grounded_draft_visible=true",
  "ai_review_grounded_draft_not_final_output=true",
  "ai_review_grounded_composer_present=true",
  "ai_review_grounded_composer_sections=5",
  "ai_review_grounded_composer_sections_exact=true",
  "ai_review_grounded_composer_uses_response_contract=true",
  "ai_review_grounded_composer_uses_calculation_packet=true",
  "ai_review_grounded_composer_uses_grounded_evaluator=true",
  "ai_review_grounded_composer_draft_passes=true",
  "ai_review_grounded_composer_groups_hit=5",
  "ai_review_grounded_composer_groups_hit_minimum_met=true",
  "ai_review_grounded_composer_practical_question_present=true",
  "ai_review_grounded_composer_drift_fixture_fails=true",
  "ai_review_grounded_composer_visible=true",
  "ai_review_grounded_composer_not_final_output=true",
  "ai_review_generation_boundary_present=true",
  "ai_review_generation_boundary_request_present=true",
  "ai_review_generation_boundary_response_gate_present=true",
  "ai_review_generation_boundary_required_sections=5",
  "ai_review_generation_boundary_required_groups=5",
  "ai_review_generation_boundary_practical_question_required=true",
  "ai_review_generation_boundary_forbidden_classes_present=true",
  "ai_review_generation_boundary_fixture_count=3",
  "ai_review_generation_boundary_grounded_fixture_accepted=true",
  "ai_review_generation_boundary_generic_fixture_blocked=true",
  "ai_review_generation_boundary_overclaim_fixture_blocked=true",
  "ai_review_generation_boundary_blocked_not_display_eligible=true",
  "ai_review_generation_boundary_repairs_present=true",
  "ai_review_generation_boundary_uses_grounded_composer=true",
  "ai_review_generation_boundary_uses_grounded_evaluator=true",
  "ai_review_generation_boundary_uses_calculation_packet=true",
  "ai_review_generation_boundary_uses_response_contract=true",
  "ai_review_generation_boundary_visible=true",
  "ai_review_generation_boundary_not_final_output=true",
  "ai_review_audio_consultation_benchmark_present=true",
  "ai_review_audio_consultation_cases=2",
  "ai_review_audio_consultation_house_walkthrough_present=true",
  "ai_review_audio_consultation_yoga_weighting_present=true",
  "ai_review_audio_consultation_review_structure_chain_present=true",
  "ai_review_audio_consultation_raw_transcript_committed=false",
  "ai_review_audio_consultation_source_audio_committed=false",
  "ai_review_audio_consultation_witness_only=true",
  "ai_review_audio_consultation_style_copied=false",
  "ai_review_audio_consultation_not_jh_pl_parity=true",
  "ai_review_audio_consultation_not_final_output=true",
  "ai_review_quality_dimensions=interpretation_depth,specific_chart_evidence,practical_synthesis,caveats_confidence",
  "ai_review_live_composer_from_report_evidence_pack=true",
  "ai_review_live_composer_blocks_unapproved_report_evidence=true",
  "ai_review_llm_network_call_executed=false",
  "backend_calculation_changed=false",
  "production_deploy_skipped_per_user_batching_policy=true",
  "last_verified_deploy_commit=508df50",
]) {
  assert(combinedSource.includes(marker), `Missing P119 marker: ${marker}`);
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
  "case_cancer_lagna_public_work",
  "case_cancer_lagna_career",
  "Chart fact",
  "Jyotish rule",
  "Interpretive accent",
  "Risk or caveat",
  "Practical next step",
  "Next question",
  "source style is intentionally not copied",
  "advanced claims gated unless calculated table exists",
  "10th-house Aries cluster",
  "dasha layer",
  "D9 relationship or dharma claims",
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
  "Shared response contract",
  "pre-generation quality gate, not final AI text",
  "Repair coverage status",
  "Calculation evidence packet",
  "chart placements",
  "house/lord relationships",
  "dignity/strength notes",
  "yoga or combination candidates",
  "dasha/transit timing anchors",
  "contradiction/tension flags",
  "Evidence group",
  "Why it matters",
  "Required anchor type",
  "Benchmark-covered status",
  "sanitized benchmark cases",
  "Grounded draft evaluator",
  "strong_calculation_grounded_draft",
  "generic_inspirational_draft",
  "advanced_overclaim_draft",
  "Expected result",
  "Actual result",
  "Evidence groups hit",
  "Repair summary",
  "Grounded review composer",
  "Composed section",
  "Source evidence groups",
  "Evaluator status",
  "Drift repair summary",
  "Generation boundary",
  "Audio consultation benchmark",
  "Local ASR witness for review structure",
  "audio_haridas_house_walkthrough",
  "audio_govardhan_yoga_weighting",
  "House walkthrough consultation witness",
  "Yoga weighting consultation witness",
  "raw transcripts and source audio are not committed",
  "Source kind",
  "Blocked uses",
  "Do not treat the witness as JH/PL parity evidence",
  "Gate outcome",
  "Display eligibility",
  "Failed gates",
  "Forbidden output classes",
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
assert(typeof helper.buildAiReviewSharedResponseContractSurfaceSummary === "function", "buildAiReviewSharedResponseContractSurfaceSummary must be exported.");
assert(typeof helper.buildAiReviewCalculationPromptPacket === "function", "buildAiReviewCalculationPromptPacket must be exported.");
assert(typeof helper.buildAiReviewGroundedDraftEvaluator === "function", "buildAiReviewGroundedDraftEvaluator must be exported.");
assert(typeof helper.buildAiReviewGroundedComposer === "function", "buildAiReviewGroundedComposer must be exported.");
assert(typeof helper.buildAiReviewAudioConsultationBenchmark === "function", "buildAiReviewAudioConsultationBenchmark must be exported.");
assert(typeof helper.buildAiReviewConsultationMethodContract === "function", "buildAiReviewConsultationMethodContract must be exported.");
assert(typeof helper.buildAiReviewLiveComposerContract === "function", "buildAiReviewLiveComposerContract must be exported.");
assert(typeof helper.buildAiReviewLiveComposerFromReportEvidencePack === "function", "Report evidence-pack live composer adapter must be exported.");
assert(typeof helper.buildAiReviewGenerationBoundary === "function", "buildAiReviewGenerationBoundary must be exported.");
assert(typeof helper.buildAiReviewQualityLabSummary === "function", "buildAiReviewQualityLabSummary must be exported.");

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
const reportsSharedSummary = helper.buildAiReviewSharedResponseContractSurfaceSummary("reports");
const mockSharedSummary = helper.buildAiReviewSharedResponseContractSurfaceSummary("report-mock-review");
const calculationPromptPacket = helper.buildAiReviewCalculationPromptPacket();
const groundedDraftEvaluator = helper.buildAiReviewGroundedDraftEvaluator();
const groundedComposer = helper.buildAiReviewGroundedComposer();
const generationBoundary = helper.buildAiReviewGenerationBoundary();
const audioConsultationBenchmark = helper.buildAiReviewAudioConsultationBenchmark();
const consultationMethodContract = helper.buildAiReviewConsultationMethodContract();
const liveComposerContract = helper.buildAiReviewLiveComposerContract(
  {
    settings: { ayanamsa: "lahiri", house_system: "whole_sign", varga_scheme: "parashara" },
    ascendant: { body: "Lagna", rashi: "Cancer", rashi_index: 4, nakshatra: "Pushya", pada: 2 },
    grahas: [
      { body: "Sun", rashi: "Cancer", rashi_index: 4, nakshatra: "Ashlesha", pada: 1 },
      { body: "Moon", rashi: "Aquarius", rashi_index: 11, nakshatra: "Purva Bhadrapada", pada: 3 },
      { body: "Jupiter", rashi: "Cancer", rashi_index: 4, nakshatra: "Punarvasu", pada: 4, dignity: "exalted" },
      { body: "Saturn", rashi: "Capricorn", rashi_index: 10, nakshatra: "Uttara Ashadha", pada: 3, retrograde: true, dignity: "own" },
    ],
    panchanga: { tithi: { name: "Ekadashi" }, vara: { name: "Wednesday" }, yoga: { name: "Siddha" }, karana: { name: "Bava" }, nakshatra: { name: "Purva Bhadrapada", pada: 3 } },
    dashas: { vimshottari: { mahadashas: [{ lord: "Moon", starts_at: "2026-01-01", ends_at: "2036-01-01" }] } },
    vargas: { D9: { placements: [{ body: "Lagna", rashi: "Virgo" }, { body: "Moon", rashi: "Gemini" }] } },
    classical: {
      shadbala: { status: "calculated", items: [{ body: "Jupiter" }] },
      yogas: { status: "calculated", summary: { detected_count: 2 } },
      ashtakavarga: { status: "calculated", sarva: { scores: [24, 31] } },
    },
  },
  [
    { id: "approved-bphs-house-1", title: "Approved house evidence", status: "approved" },
    { id: "approved-bphs-yoga", title: "Approved yoga evidence", status: "approved" },
  ],
);
const blockedLiveComposerContract = helper.buildAiReviewLiveComposerContract(
  {
    ascendant: { body: "Lagna", rashi: "Cancer", rashi_index: 4 },
    grahas: [{ body: "Moon", rashi: "Aquarius", rashi_index: 11 }],
    panchanga: {},
  },
  [],
);
const realReportEvidencePack = {
  schemaVersion: 1,
  reportRecipeId: "personal_overview",
  reportRecipeVersion: 1,
  reportTypeId: "personal_overview",
  mode: "novice",
  profileIds: ["saved-chart-107"],
  items: [
    {
      id: "calculation.basic.settings",
      kind: "calculation",
      label: "Calculation settings",
      calculationId: "calc.settings",
      value: { ayanamsa: "lahiri", house_system: "whole_sign", varga_scheme: "parashara" },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "bphs", ruleId: "bphs.lagna.general", status: "verified" }] },
    },
    {
      id: "calculation.varga.d1",
      kind: "calculation",
      label: "D1",
      calculationId: "calc.varga.D1",
      value: {
        code: "D1",
        placements: [
          { body: "Lagna", rashi: "Cancer", rashi_index: 4, nakshatra: "Pushya", pada: 2 },
          { body: "Sun", rashi: "Cancer", rashi_index: 4, nakshatra: "Ashlesha", pada: 1 },
          { body: "Moon", rashi: "Aquarius", rashi_index: 11, nakshatra: "Purva Bhadrapada", pada: 3 },
          { body: "Jupiter", rashi: "Cancer", rashi_index: 4, nakshatra: "Punarvasu", pada: 4, dignity: "exalted" },
          { body: "Saturn", rashi: "Capricorn", rashi_index: 10, nakshatra: "Uttara Ashadha", pada: 3, retrograde: true, dignity: "own" },
        ],
      },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "bphs", ruleId: "bphs.rashi.d1", status: "verified" }] },
    },
    {
      id: "calculation.panchanga",
      kind: "calculation",
      label: "Panchanga",
      calculationId: "calc.panchanga",
      value: { tithi: { name: "Ekadashi" }, vara: { name: "Wednesday" }, yoga: { name: "Siddha" }, karana: { name: "Bava" } },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "tradition", ruleId: "panchanga.tithi", status: "verified" }] },
    },
    {
      id: "calculation.vimshottari",
      kind: "calculation",
      label: "Vimshottari",
      calculationId: "calc.vimshottari",
      value: { mahadashas: [{ lord: "Moon", starts_at: "2026-01-01", ends_at: "2036-01-01" }] },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "tradition", ruleId: "vimshottari.sequence", status: "verified" }] },
    },
    {
      id: "calculation.varga.d9",
      kind: "calculation",
      label: "D9",
      calculationId: "calc.varga.D9",
      value: { code: "D9", placements: [{ body: "Lagna", rashi: "Virgo" }, { body: "Moon", rashi: "Gemini" }] },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "jyotish.classical", ruleId: "jyotish.classical.varga.D9", status: "verified" }] },
    },
    {
      id: "calculation.classical",
      kind: "calculation",
      label: "Classical checks",
      calculationId: "calc.classical",
      value: { shadbala: { status: "calculated" }, yogas: { status: "calculated" }, ashtakavarga: { status: "calculated" } },
      available: true,
      provenance: { origin: "chart_calculation", sourceRefs: [{ sourceId: "jyotish.classical", ruleId: "jyotish.classical.yogas", status: "verified" }] },
    },
  ],
  warnings: [],
  unavailableItemIds: [],
  sourceRefs: [
    { sourceId: "bphs", ruleId: "bphs.lagna.general", status: "verified" },
    { sourceId: "bphs", ruleId: "bphs.rashi.d1", status: "verified" },
    { sourceId: "tradition", ruleId: "vimshottari.sequence", status: "verified" },
    { sourceId: "jyotish.classical", ruleId: "jyotish.classical.yogas", status: "verified" },
  ],
  inputSummary: { hasPrimaryChart: true, hasRelationshipContext: false, resolvedSectionCount: 2, resolvedFactorCount: 6 },
};
const unapprovedReportEvidencePack = JSON.parse(JSON.stringify(realReportEvidencePack));
for (const ref of unapprovedReportEvidencePack.sourceRefs) ref.status = "needs_review";
for (const item of unapprovedReportEvidencePack.items) {
  for (const ref of item.provenance.sourceRefs) ref.status = "needs_review";
}
const liveComposerFromEvidencePack = helper.buildAiReviewLiveComposerFromReportEvidencePack(realReportEvidencePack);
const blockedLiveComposerFromEvidencePack = helper.buildAiReviewLiveComposerFromReportEvidencePack(unapprovedReportEvidencePack);
const qualityLab = helper.buildAiReviewQualityLabSummary();

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
assert(telegramBenchmark.statusLabels.includes("ai_review_telegram_sanitized_benchmark_stage=R1"), "Telegram benchmark must include R1 sanitized stage label.");
assert(telegramBenchmark.benchmarks.some((benchmark) => benchmark.name === "Anonymized Telegram benchmark 1"), "Anonymized benchmark 1 missing.");
assert(telegramBenchmark.benchmarks.some((benchmark) => benchmark.name === "Anonymized Telegram benchmark 2"), "Anonymized benchmark 2 missing.");
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
assert(reportsSharedSummary.stage === "P129-A", "Reports shared contract summary stage must be P129-A.");
assert(mockSharedSummary.stage === "P129-A", "Mock-review shared contract summary stage must be P129-A.");
assert(reportsSharedSummary.statusLabels.includes("ai_review_response_contract_shared_stage=P129-A"), "Shared contract labels missing P129 stage.");
assert(mockSharedSummary.statusLabels.includes("ai_review_response_contract_mock_review_surface=true"), "Mock-review shared labels missing surface flag.");
assert(reportsSharedSummary.surface === "reports", "Reports shared summary surface mismatch.");
assert(mockSharedSummary.surface === "report-mock-review", "Mock-review shared summary surface mismatch.");
assert(reportsSharedSummary.sectionCount === 5 && mockSharedSummary.sectionCount === 5, "Shared contract must expose five sections on both surfaces.");
assert(reportsSharedSummary.sectionNames.join("|") === mockSharedSummary.sectionNames.join("|"), "Shared section names drifted between surfaces.");
assert(reportsSharedSummary.sectionNames.join("|") === "Chart anchors|Rule chain|Interpretive tension|Practical next question|Caveats and gated claims", "Shared section names changed.");
assert(reportsSharedSummary.repairCoverage.generic === true && mockSharedSummary.repairCoverage.generic === true, "Shared generic repair coverage missing.");
assert(reportsSharedSummary.repairCoverage.overclaim === true && mockSharedSummary.repairCoverage.overclaim === true, "Shared overclaim repair coverage missing.");
assert(reportsSharedSummary.repairCoverage.missingQuestion === true && mockSharedSummary.repairCoverage.missingQuestion === true, "Shared missing-question repair coverage missing.");
assert(reportsSharedSummary.aggregate.sharedSource === true && mockSharedSummary.aggregate.sharedSource === true, "Shared summary must use shared source.");
assert(reportsSharedSummary.aggregate.productGateNotFinalOutput === true, "Shared summary must be product gate, not final output.");
assert(page.includes("sharedResponseContract"), "/reports must use shared response-contract summary.");
assert(mockReviewPage.includes("buildAiReviewSharedResponseContractSurfaceSummary"), "/report-mock-review must use shared response-contract helper.");
assert(mockReviewPage.includes('data-ai-review-response-contract-shared-stage="P129-A"'), "/report-mock-review must expose P129 hook.");
assert(mockReviewPage.includes("Shared response contract"), "/report-mock-review must show shared response contract copy.");
assert(calculationPromptPacket.stage === "E130-A", "Calculation prompt packet stage must be E130-A.");
assert(calculationPromptPacket.statusLabels.includes("ai_review_calculation_packet_stage=E130-A"), "Calculation prompt packet labels missing E130 stage.");
assert(calculationPromptPacket.evidenceGroups.length >= 6, "Calculation evidence packet must include at least six evidence groups.");
assert(calculationPromptPacket.aggregate.evidenceGroupCount >= 6, "Calculation evidence group aggregate must be at least six.");
assert(calculationPromptPacket.aggregate.benchmarkCaseCount >= 3, "Sanitized benchmark case aggregate must be at least three.");
assert(calculationPromptPacket.aggregate.everyBenchmarkHasFocusAccentQuestion === true, "Each sanitized benchmark must include focus, accent, and question pattern.");
assert(calculationPromptPacket.aggregate.rawExportTextCommitted === false, "Raw export text must not be committed.");
assert(calculationPromptPacket.aggregate.usesSharedResponseContract === true, "Prompt packet must use shared response contract.");
assert(calculationPromptPacket.aggregate.usesAssertionLedger === true, "Prompt packet must use assertion ledger.");
assert(calculationPromptPacket.aggregate.usesCalculationEvidence === true, "Prompt packet must use calculation evidence.");
assert(calculationPromptPacket.aggregate.usesSanitizedBenchmarks === true, "Prompt packet must use sanitized benchmarks.");
for (const groupId of ["chart_placements", "lord_relationships", "dignity_strength", "yoga_candidates", "dasha_transit_timing", "tension_flags"]) {
  assert(calculationPromptPacket.evidenceGroups.some((group) => group.id === groupId), `Missing calculation evidence group: ${groupId}`);
}
assert(calculationPromptPacket.sanitizedBenchmarkCases.length >= 3, "At least three sanitized benchmark cases required.");
assert(
  calculationPromptPacket.sanitizedBenchmarkCases.every(
    (item) => item.calculationFocus && item.interpretiveAccent && item.questionPattern && item.qualityRisk,
  ),
  "Every sanitized benchmark case must include calculation focus, accent, question pattern, and risk.",
);
const serializedBenchmarkCases = JSON.stringify(calculationPromptPacket.sanitizedBenchmarkCases);
for (const leaked of ["Haridev", "Seva", "ChatExport", "message default clearfix", "from_name", "2026-06-23", "+", "@"]) {
  assert(!serializedBenchmarkCases.includes(leaked), `Sanitized benchmark case leaked raw/private export token: ${leaked}`);
}
assert(page.includes("calculationPromptPacket"), "/reports must render calculation prompt packet.");
assert(mockReviewPage.includes("calculationPromptPacket"), "/report-mock-review must render calculation prompt packet.");
assert(mockReviewPage.includes('data-ai-review-calculation-packet-stage="E130-A"'), "/report-mock-review must expose E130 hook.");
assert(groundedDraftEvaluator.stage === "P131-A", "Grounded draft evaluator stage must be P131-A.");
assert(groundedDraftEvaluator.statusLabels.includes("ai_review_grounded_draft_evaluator_stage=P131-A"), "Grounded draft evaluator labels missing P131 stage.");
assert(groundedDraftEvaluator.fixtures.length >= 3, "Grounded draft evaluator must include at least three fixtures.");
assert(groundedDraftEvaluator.aggregate.fixtureCount >= 3, "Grounded draft fixture aggregate must be at least three.");
assert(groundedDraftEvaluator.aggregate.strongPasses === true, "Strong grounded draft fixture must pass.");
assert(groundedDraftEvaluator.aggregate.genericFails === true, "Generic draft fixture must fail.");
assert(groundedDraftEvaluator.aggregate.overclaimFails === true, "Overclaim draft fixture must fail.");
assert(groundedDraftEvaluator.aggregate.strongGroupsHitMinimumMet === true, "Strong draft must hit at least four E130 groups.");
assert(groundedDraftEvaluator.aggregate.repairsPresent === true, "Failing draft fixtures must include repair instructions.");
assert(groundedDraftEvaluator.aggregate.usesCalculationPacket === true, "Grounded evaluator must use E130 calculation packet.");
assert(groundedDraftEvaluator.aggregate.usesSharedResponseContract === true, "Grounded evaluator must use P129 shared response contract.");
const strongDraft = groundedDraftEvaluator.evaluations.find((item) => item.fixture.id === "strong_calculation_grounded_draft");
const genericDraft = groundedDraftEvaluator.evaluations.find((item) => item.fixture.id === "generic_inspirational_draft");
const overclaimDraft = groundedDraftEvaluator.evaluations.find((item) => item.fixture.id === "advanced_overclaim_draft");
assert(strongDraft?.passed === true, "Strong calculation-grounded draft must pass.");
assert(strongDraft.evidenceGroupHits.length >= 4, "Strong draft must hit at least four evidence groups.");
assert(strongDraft.practicalQuestionQuality.passed === true, "Strong draft must include a useful practical next question.");
assert(genericDraft?.passed === false, "Generic inspirational draft must fail.");
assert(genericDraft.genericLanguageFlags.length >= 1, "Generic draft must expose generic-language flags.");
assert(genericDraft.repairInstructions.length >= 1, "Generic draft must include repair instructions.");
assert(overclaimDraft?.passed === false, "Advanced overclaim draft must fail.");
assert(overclaimDraft.overclaimFlags.length >= 1, "Overclaim draft must expose overclaim flags.");
assert(overclaimDraft.repairInstructions.length >= 1, "Overclaim draft must include repair instructions.");
assert(page.includes("groundedDraftEvaluator"), "/reports must render grounded draft evaluator.");
assert(mockReviewPage.includes("groundedDraftEvaluator"), "/report-mock-review must render grounded draft evaluator.");
assert(mockReviewPage.includes('data-ai-review-grounded-draft-stage="P131-A"'), "/report-mock-review must expose P131 hook.");
assert(groundedComposer.stage === "E132-A", "Grounded composer stage must be E132-A.");
assert(groundedComposer.statusLabels.includes("ai_review_grounded_composer_stage=E132-A"), "Grounded composer labels missing E132 stage.");
assert(groundedComposer.sections.length === 5, "Grounded composer must compose exactly five sections.");
assert(groundedComposer.sections.map((section) => section.name).join("|") === "Chart anchors|Rule chain|Interpretive tension|Practical next question|Caveats and gated claims", "Grounded composer section names changed.");
assert(groundedComposer.aggregate.sectionsExact === true, "Grounded composer must mark sections exact.");
assert(groundedComposer.aggregate.draftPasses === true, "Grounded composed draft must pass evaluator.");
assert(groundedComposer.evaluation.passed === true, "Grounded composer evaluation must pass.");
assert(groundedComposer.aggregate.groupsHit === 5, "Grounded composed draft must hit exactly five evidence groups.");
assert(groundedComposer.evaluation.evidenceGroupHits.length >= 5, "Grounded composed draft must hit at least five evidence groups.");
assert(groundedComposer.aggregate.groupsHitMinimumMet === true, "Grounded composer must mark evidence group minimum met.");
assert(groundedComposer.aggregate.practicalQuestionPresent === true, "Grounded composed draft must include practical next question.");
assert(groundedComposer.aggregate.driftFixtureFails === true, "Grounded composer drift fixture must fail.");
assert(groundedComposer.driftEvaluation.passed === false, "Grounded composer drift evaluation must fail.");
assert(groundedComposer.driftEvaluation.repairInstructions.length >= 1, "Grounded composer drift fixture must include repair instructions.");
assert(groundedComposer.aggregate.usesResponseContract === true, "Grounded composer must use response contract.");
assert(groundedComposer.aggregate.usesCalculationPacket === true, "Grounded composer must use calculation packet.");
assert(groundedComposer.aggregate.usesGroundedEvaluator === true, "Grounded composer must use grounded evaluator.");
assert(page.includes("groundedComposer"), "/reports must render grounded composer.");
assert(mockReviewPage.includes("groundedComposer"), "/report-mock-review must render grounded composer.");
assert(page.includes('data-ai-review-grounded-composer-stage="E132-A"'), "/reports must expose E132 hook.");
assert(mockReviewPage.includes('data-ai-review-grounded-composer-stage="E132-A"'), "/report-mock-review must expose E132 hook.");
assert(generationBoundary.stage === "P133-A", "Generation boundary stage must be P133-A.");
assert(generationBoundary.statusLabels.includes("ai_review_generation_boundary_stage=P133-A"), "Generation boundary labels missing P133 stage.");
assert(generationBoundary.request.requiredResponseSectionsCount === 5, "Generation boundary request must require five sections.");
assert(generationBoundary.request.requiredEvidenceGroupsCount >= 5, "Generation boundary request must require at least five evidence groups.");
assert(generationBoundary.request.practicalNextQuestionRequired === true, "Generation boundary request must require practical next question.");
assert(generationBoundary.request.forbiddenOutputClasses.length >= 4, "Generation boundary must list forbidden output classes.");
assert(generationBoundary.fixtures.length >= 3, "Generation boundary must include three fixtures.");
const groundedResponse = generationBoundary.gateResults.find((item) => item.fixture.id === "offline_composed_grounded_response");
const genericResponse = generationBoundary.gateResults.find((item) => item.fixture.id === "offline_generic_weak_response");
const overclaimResponse = generationBoundary.gateResults.find((item) => item.fixture.id === "offline_overclaim_response");
assert(groundedResponse?.outcome === "accepted", "Grounded offline response must be accepted.");
assert(groundedResponse?.displayEligible === true, "Grounded offline response must be display eligible.");
assert(genericResponse?.outcome === "blocked", "Generic offline response must be blocked.");
assert(overclaimResponse?.outcome === "blocked", "Overclaim offline response must be blocked.");
assert(genericResponse?.displayEligible === false && overclaimResponse?.displayEligible === false, "Blocked fixtures must not be display eligible.");
assert(genericResponse.repairInstructions.length >= 1 && overclaimResponse.repairInstructions.length >= 1, "Blocked fixtures must include repair instructions.");
assert(generationBoundary.aggregate.groundedFixtureAccepted === true, "Generation boundary aggregate must accept grounded fixture.");
assert(generationBoundary.aggregate.genericFixtureBlocked === true, "Generation boundary aggregate must block generic fixture.");
assert(generationBoundary.aggregate.overclaimFixtureBlocked === true, "Generation boundary aggregate must block overclaim fixture.");
assert(generationBoundary.aggregate.blockedNotDisplayEligible === true, "Generation boundary aggregate must mark blocked fixtures not display eligible.");
assert(generationBoundary.aggregate.repairsPresent === true, "Generation boundary aggregate must mark repairs present.");
assert(generationBoundary.aggregate.usesGroundedComposer === true, "Generation boundary must use grounded composer.");
assert(generationBoundary.aggregate.usesGroundedEvaluator === true, "Generation boundary must use grounded evaluator.");
assert(generationBoundary.aggregate.usesCalculationPacket === true, "Generation boundary must use calculation packet.");
assert(generationBoundary.aggregate.usesResponseContract === true, "Generation boundary must use response contract.");
assert(page.includes("generationBoundary"), "/reports must render generation boundary.");
assert(mockReviewPage.includes("generationBoundary"), "/report-mock-review must render generation boundary.");
assert(page.includes('data-ai-review-generation-boundary-stage="P133-A"'), "/reports must expose P133 hook.");
assert(mockReviewPage.includes('data-ai-review-generation-boundary-stage="P133-A"'), "/report-mock-review must expose P133 hook.");
assert(audioConsultationBenchmark.stage === "E134-A", "Audio consultation benchmark stage must be E134-A.");
assert(audioConsultationBenchmark.statusLabels.includes("ai_review_audio_consultation_benchmark_stage=E134-A"), "Audio benchmark labels missing E134 stage.");
assert(audioConsultationBenchmark.cases.length === 2, "Audio benchmark must include two sanitized consultation cases.");
assert(audioConsultationBenchmark.aggregate.houseWalkthroughPresent === true, "Audio benchmark must include house walkthrough witness.");
assert(audioConsultationBenchmark.aggregate.yogaWeightingPresent === true, "Audio benchmark must include yoga weighting witness.");
assert(audioConsultationBenchmark.aggregate.reviewStructureChainPresent === true, "Audio benchmark must require review structure chain.");
assert(audioConsultationBenchmark.aggregate.rawTranscriptCommitted === false, "Audio benchmark must not commit raw transcripts.");
assert(audioConsultationBenchmark.aggregate.sourceAudioCommitted === false, "Audio benchmark must not commit source audio.");
assert(audioConsultationBenchmark.aggregate.witnessOnly === true, "Audio benchmark must be witness-only.");
assert(
  audioConsultationBenchmark.cases.every((item) => item.calculationPatterns.length >= 3 && item.reviewStructureRules.length >= 3),
  "Each audio benchmark case must include calculation patterns and review rules.",
);
assert(page.includes("audioConsultationBenchmark"), "/reports must render audio consultation benchmark.");
assert(mockReviewPage.includes("audioConsultationBenchmark"), "/report-mock-review must render audio consultation benchmark.");
assert(page.includes('data-ai-review-audio-consultation-stage="E134-A"'), "/reports must expose E134 hook.");
assert(mockReviewPage.includes('data-ai-review-audio-consultation-stage="E134-A"'), "/report-mock-review must expose E134 hook.");
assert(consultationMethodContract.stage === "P135-A", "Consultation method contract stage must be P135-A.");
assert(consultationMethodContract.pipeline.map((step) => step.name).join("|") === "ChartFacts|Evidence|ReviewSections|QualityGate", "Consultation method pipeline changed.");
assert(consultationMethodContract.aggregate.usesAudioBenchmark === true, "Consultation method must use E134 audio benchmark.");
assert(consultationMethodContract.aggregate.usesGroundedComposer === true, "Consultation method must use grounded composer.");
assert(consultationMethodContract.aggregate.usesGenerationBoundary === true, "Consultation method must use generation boundary.");
assert(consultationMethodContract.aggregate.rawTranscriptCommitted === false, "Consultation method must not commit raw transcript.");
assert(consultationMethodContract.aggregate.finalOutputClaimed === false, "Consultation method must not claim final AI output.");
assert(consultationMethodContract.gateRules.length >= 4, "Consultation method must include gate rules.");
assert(consultationMethodContract.statusLabels.includes("ai_review_consultation_method_stage=P135-A"), "Consultation method labels missing P135 stage.");
assert(consultationMethodContract.statusLabels.includes("last_verified_deploy_commit=cc86830c"), "Consultation method labels must reference the latest verified production checkpoint.");
assert(page.includes("consultationMethodContract"), "/reports must render consultation method contract.");
assert(mockReviewPage.includes("consultationMethodContract"), "/report-mock-review must render consultation method contract.");
assert(page.includes('data-ai-review-consultation-method-stage="P135-A"'), "/reports must expose P135 hook.");
assert(mockReviewPage.includes('data-ai-review-consultation-method-stage="P135-A"'), "/report-mock-review must expose P135 hook.");
assert(liveComposerContract.stage === "E136-A", "Live composer contract stage must be E136-A.");
assert(liveComposerContract.chartFacts.length >= 8, "Live composer must extract chart facts from a real chart payload.");
assert(liveComposerContract.evidenceLinks.length >= 2, "Live composer must consume approved literature/source evidence links.");
assert(liveComposerContract.gate.displayEligible === true, "Live composer with chart facts and source evidence must be display eligible.");
assert(liveComposerContract.gate.requiredAnchorsPresent === true, "Live composer must require calculation anchors.");
assert(liveComposerContract.gate.sourceEvidencePresent === true, "Live composer must require source evidence.");
assert(liveComposerContract.gate.practicalQuestionPresent === true, "Live composer must require practical next question.");
assert(liveComposerContract.gate.caveatPresent === true, "Live composer must require caveat.");
assert(liveComposerContract.aggregate.fixtureDataUsed === false, "Live composer must not depend on fixture data.");
assert(liveComposerContract.aggregate.finalOutputClaimed === false, "Live composer must not claim final AI output.");
assert(blockedLiveComposerContract.gate.displayEligible === false, "Live composer without source evidence must be blocked.");
assert(blockedLiveComposerContract.gate.failedGateNames.includes("calculation_anchors_missing"), "Live composer blocked result must name missing calculation anchors.");
assert(blockedLiveComposerContract.gate.failedGateNames.includes("source_evidence_missing"), "Live composer blocked result must name missing source evidence.");
assert(blockedLiveComposerContract.gate.failedGateNames.includes("practical_question_missing"), "Live composer blocked result must name missing practical question.");
assert(blockedLiveComposerContract.gate.failedGateNames.includes("caveat_missing"), "Live composer blocked result must name missing caveat.");
assert(liveComposerFromEvidencePack.stage === "E136-A", "Report evidence-pack live composer stage must be E136-A.");
assert(liveComposerFromEvidencePack.chartFacts.length >= 8, "Report evidence-pack adapter must extract chart facts from report evidence values.");
assert(liveComposerFromEvidencePack.chartFacts.some((fact) => fact.sourcePath.includes("reportEvidencePack.items")), "Report evidence-pack facts must keep source paths.");
assert(liveComposerFromEvidencePack.evidenceLinks.length >= 3, "Report evidence-pack adapter must convert verified source refs into approved evidence links.");
assert(liveComposerFromEvidencePack.evidenceLinks.every((link) => link.status === "approved"), "Report evidence-pack adapter must expose only approved evidence links.");
assert(liveComposerFromEvidencePack.gate.displayEligible === true, "Report evidence-pack live composer must be display eligible when chart facts and approved sources are present.");
assert(liveComposerFromEvidencePack.statusLabels.includes("ai_review_live_composer_from_report_evidence_pack=true"), "Report evidence-pack adapter label missing.");
assert(blockedLiveComposerFromEvidencePack.gate.displayEligible === false, "Report evidence-pack live composer must block unapproved source refs.");
assert(blockedLiveComposerFromEvidencePack.gate.failedGateNames.includes("source_evidence_missing"), "Report evidence-pack blocked result must name missing approved evidence.");
assert(blockedLiveComposerFromEvidencePack.statusLabels.includes("ai_review_live_composer_blocks_unapproved_report_evidence=true"), "Report evidence-pack blocked label missing.");
assert(liveComposerContract.statusLabels.includes("ai_review_live_composer_stage=E136-A"), "Live composer labels missing E136 stage.");
assert(liveComposerContract.statusLabels.includes("last_verified_deploy_commit=cc86830c"), "Live composer labels must reference the latest verified production checkpoint.");
assert(page.includes("liveComposerContract"), "/reports must render live composer contract.");
assert(mockReviewPage.includes("liveComposerContract"), "/report-mock-review must render live composer contract.");
assert(page.includes('data-ai-review-live-composer-stage="E136-A"'), "/reports must expose E136 hook.");
assert(mockReviewPage.includes('data-ai-review-live-composer-stage="E136-A"'), "/report-mock-review must expose E136 hook.");
assert(qualityLab.benchmarkParityReport?.stage === "R2", "Quality summary must expose R2 benchmark parity report.");
assert(qualityLab.statusLabels.includes("ai_review_benchmark_parity_stage=R2"), "Quality summary status labels must include R2 parity stage.");
assert(qualityLab.audioConsultationBenchmark?.stage === "E134-A", "Quality summary must expose E134 audio consultation benchmark.");
assert(qualityLab.statusLabels.includes("ai_review_audio_consultation_benchmark_stage=E134-A"), "Quality summary status labels must include E134 audio benchmark stage.");
assert(qualityLab.consultationMethodContract?.stage === "P135-A", "Quality summary must expose P135 consultation method contract.");
assert(qualityLab.statusLabels.includes("ai_review_consultation_method_stage=P135-A"), "Quality summary status labels must include P135 consultation method stage.");
assert(qualityLab.liveComposerContract?.stage === "E136-A", "Quality summary must expose E136 live composer contract.");
assert(qualityLab.statusLabels.includes("ai_review_live_composer_stage=E136-A"), "Quality summary status labels must include E136 live composer stage.");
assert(qualityLab.benchmarkParityReport.aggregate.d1RowsChecked >= 18, "Quality summary parity report must check at least 18 D1 rows.");
assert(qualityLab.benchmarkParityReport.aggregate.unsupportedAdvancedClaimsGated === true, "Quality summary parity report must gate unsupported advanced claims.");

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
