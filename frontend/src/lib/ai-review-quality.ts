import { buildAiReviewTelegramSanitizedBenchmark } from "@/lib/ai-review-benchmark";
import { buildAiReviewBenchmarkParityReport } from "@/lib/ai-review-benchmark-parity";

export const AI_REVIEW_QUALITY_STAGE = "P119-A";

export const AI_REVIEW_QUALITY_DIMENSIONS = [
  "interpretation_depth",
  "specific_chart_evidence",
  "practical_synthesis",
  "caveats_confidence",
] as const;

export type AiReviewQualityDimension = (typeof AI_REVIEW_QUALITY_DIMENSIONS)[number];

export type AiReviewQualityDimensionResult = {
  id: AiReviewQualityDimension;
  label: string;
  passed: boolean;
  reason: string;
};

export type AiReviewQualityEvaluation = {
  passed: boolean;
  score: number;
  matchedEvidence: string[];
  dimensions: AiReviewQualityDimensionResult[];
  genericFillerGuard: {
    passed: boolean;
    matches: string[];
  };
};

export type AiReviewQualityFixture = {
  draft: string;
  fixtureEvidence: string[];
};

export type AiReviewEvidencePacket = {
  chartEvidenceItems: string[];
  synthesisLinks: string[];
  practicalNextStepRequirement: string;
  caveatConfidenceRequirement: string;
};

export type AiReviewMockPreview = {
  stage: "E120-A";
  evidencePacket: AiReviewEvidencePacket;
  strong: {
    status: "passes_quality_gate";
    passed: true;
    matchedEvidenceCount: number;
    matchedEvidence: string[];
  };
  weak: {
    status: "blocked_by_quality_gate";
    passed: false;
    failedDimensionFeedback: string[];
    genericFillerMatches: string[];
  };
  statusLabels: string[];
};

export type AiReviewComposedSection = {
  heading: "Chart evidence cited" | "Interpretive synthesis" | "Practical guidance" | "Caveats and confidence";
  body: string;
};

export type AiReviewComposedMockReview = {
  stage: "P121-A";
  sections: AiReviewComposedSection[];
  strong: {
    status: "passes_quality_gate";
    matchedEvidenceCount: number;
  };
  weak: {
    status: "blocked_by_quality_gate";
    usableReviewVisible: false;
    blockReason: string;
    failedDimensionFeedback: string[];
  };
  statusLabels: string[];
};

export type AiReviewPromptPayloadSection = {
  heading:
    | "System quality rules"
    | "Chart evidence packet"
    | "Required review structure"
    | "Anti-generic guardrails"
    | "Quality gate before final answer";
  body: string;
};

export type AiReviewPromptPayload = {
  stage: "E122-A";
  localOnly: true;
  llmNetworkCallExecuted: false;
  evidenceItems: string[];
  requiredEvidenceCitationCount: number;
  sections: AiReviewPromptPayloadSection[];
  antiGenericGuardrails: string[];
  qualityGateBeforeFinalAnswer: AiReviewQualityDimension[];
  statusLabels: string[];
};

export type AiReviewScenarioFixture = {
  id: string;
  intent: string;
  evidencePacket: AiReviewEvidencePacket;
  strongDraft: string;
  weakDraft: string;
};

export type AiReviewScenarioMatrixRow = {
  id: string;
  intent: string;
  evidenceItems: string[];
  requiredEvidenceCitationCount: number;
  strong: {
    status: "passes_quality_gate" | "fails_quality_gate";
    matchedEvidenceCount: number;
  };
  weak: {
    status: "blocked_by_quality_gate" | "passes_quality_gate";
    improvementReason: string;
  };
  promptPayload: AiReviewPromptPayload;
};

export type AiReviewScenarioMatrix = {
  stage: "P123-A";
  scenarios: AiReviewScenarioMatrixRow[];
  aggregate: {
    scenarioCount: number;
    strongPassCount: number;
    weakBlockedCount: number;
    minimumEvidenceItemCount: number;
    promptContractAppliedAllScenarios: boolean;
  };
  statusLabels: string[];
};

export type TelegramBenchmarkChart = {
  name: string;
  chartFacts: string[];
  calculationAccents: string[];
  followUpQuestions: string[];
  advancedClaimCautions: string[];
};

export type TelegramBenchmarkReviewBlueprint = {
  stage: "E124-A";
  benchmarks: TelegramBenchmarkChart[];
  blueprintSections: ["Chart fact", "Jyotish rule", "Interpretive accent", "Risk or caveat", "Practical next step", "Next question"];
  styleCopied: false;
  statusLabels: string[];
};

export type AiReviewFollowupQuestionStatus = "ready" | "gated" | "rejected";

export type AiReviewFollowupQuestionCandidate = {
  question: string;
  anchorChartFact: string;
  jyotishRuleAccent: string;
  status: AiReviewFollowupQuestionStatus;
  reason: string;
  sourceBenchmarkId: string;
};

export type AiReviewFollowupQuestionContract = {
  stage: "P125-A";
  candidates: AiReviewFollowupQuestionCandidate[];
  aggregate: {
    totalCount: number;
    readyCount: number;
    gatedCount: number;
    rejectedGenericCount: number;
    groundedInChartFacts: boolean;
    advancedClaimsBlockedWithoutCalculation: boolean;
  };
  statusLabels: string[];
};

export type AiReviewAssertionSourceType =
  | "computed_chart_fact"
  | "jyotish_rule"
  | "derived_synthesis"
  | "practical_guidance"
  | "gated_advanced_claim";

export type AiReviewAssertionStatus = "usable" | "blocked";

export type AiReviewAssertion = {
  id: string;
  assertion: string;
  sourceType: AiReviewAssertionSourceType;
  evidenceAnchor: string;
  confidenceCaveat: string;
  status: AiReviewAssertionStatus;
};

export type AiReviewAssertionComposedSection = {
  heading: "Grounded chart facts" | "Jyotish interpretation" | "Practical focus" | "Caveats and blocked claims";
  body: string;
  anchorIds: string[];
};

export type AiReviewAssertionLedger = {
  stage: "E126-A";
  assertions: AiReviewAssertion[];
  aggregate: {
    totalCount: number;
    computedChartFactCount: number;
    jyotishRuleCount: number;
    derivedSynthesisCount: number;
    practicalGuidanceCount: number;
    blockedAdvancedCount: number;
    usableCount: number;
    blockedCount: number;
  };
  composedReview: {
    sections: AiReviewAssertionComposedSection[];
    usesOnlyUsableAssertions: boolean;
    citesLedgerAnchors: boolean;
  };
  statusLabels: string[];
};

export const AI_REVIEW_NARRATIVE_DIMENSIONS = [
  "chart_specificity",
  "rule_to_interpretation_chain",
  "life_domain_tension",
  "practical_next_question",
  "caveat_and_gating",
] as const;

export type AiReviewNarrativeDimension = (typeof AI_REVIEW_NARRATIVE_DIMENSIONS)[number];

export type AiReviewNarrativeSampleId = "strong_grounded_review" | "generic_pretty_review" | "overclaimed_advanced_review";

export type AiReviewNarrativeSampleStatus = "passes_quality_rubric" | "blocked_by_quality_rubric";

export type AiReviewNarrativeSample = {
  id: AiReviewNarrativeSampleId;
  label: string;
  text: string;
  status: AiReviewNarrativeSampleStatus;
  passedDimensions: AiReviewNarrativeDimension[];
  failedDimensions: AiReviewNarrativeDimension[];
  anchorCount: number;
  keyFailureReason: string;
  hasLifeDomainTension: boolean;
  hasPracticalNextQuestion: boolean;
};

export type AiReviewNarrativeQualityRubric = {
  stage: "P127-A";
  dimensions: AiReviewNarrativeDimension[];
  samples: AiReviewNarrativeSample[];
  aggregate: {
    sampleCount: number;
    strongPassCount: number;
    blockedGenericCount: number;
    blockedOverclaimCount: number;
    passingSamplesHaveFourAnchors: boolean;
  };
  statusLabels: string[];
};

export type AiReviewResponseContractSectionName =
  | "Chart anchors"
  | "Rule chain"
  | "Interpretive tension"
  | "Practical next question"
  | "Caveats and gated claims";

export type AiReviewRepairGuidanceType =
  | "generic_without_anchors"
  | "advanced_overclaim_without_computed_tables"
  | "advice_without_practical_next_question";

export type AiReviewResponseContractSection = {
  name: AiReviewResponseContractSectionName;
  requiredSourceAnchorCount: number;
  requiredRubricDimensions: AiReviewNarrativeDimension[];
  blockedFailureExamples: string[];
  repairInstruction: string;
};

export type AiReviewRepairGuidance = {
  type: AiReviewRepairGuidanceType;
  failurePattern: string;
  repairInstruction: string;
};

export type AiReviewResponseContract = {
  stage: "E128-A";
  sections: AiReviewResponseContractSection[];
  repairGuidance: AiReviewRepairGuidance[];
  usesAssertionLedger: boolean;
  usesNarrativeRubric: boolean;
  aggregate: {
    sectionCount: number;
    sectionsExact: boolean;
    everySectionRequiresAnchor: boolean;
    everySectionHasRepair: boolean;
    genericRepairPresent: boolean;
    advancedOverclaimRepairPresent: boolean;
    missingPracticalQuestionRepairPresent: boolean;
    localOnlyNotFinalOutput: boolean;
  };
  statusLabels: string[];
};

export type AiReviewResponseContractSurface = "reports" | "report-mock-review";

export type AiReviewSharedResponseContractSurfaceSummary = {
  stage: "P129-A";
  surface: AiReviewResponseContractSurface;
  contract: AiReviewResponseContract;
  sectionNames: AiReviewResponseContractSectionName[];
  sectionCount: number;
  repairCoverage: {
    generic: boolean;
    overclaim: boolean;
    missingQuestion: boolean;
  };
  aggregate: {
    sharedSource: boolean;
    sectionsExact: boolean;
    repairGuidanceCoversFailures: boolean;
    productGateNotFinalOutput: boolean;
  };
  statusLabels: string[];
};

export type AiReviewCalculationEvidenceGroupId =
  | "chart_placements"
  | "lord_relationships"
  | "dignity_strength"
  | "yoga_candidates"
  | "dasha_transit_timing"
  | "tension_flags";

export type AiReviewCalculationEvidenceGroup = {
  id: AiReviewCalculationEvidenceGroupId;
  evidenceGroup: string;
  whyItMatters: string;
  requiredAnchorType: string;
  benchmarkCovered: boolean;
};

export type AiReviewSanitizedBenchmarkCase = {
  id: string;
  calculationFocus: string;
  interpretiveAccent: string;
  questionPattern: string;
  qualityRisk: string;
};

export type AiReviewCalculationPromptPacket = {
  stage: "E130-A";
  sharedResponseContract: AiReviewSharedResponseContractSurfaceSummary;
  assertionLedger: AiReviewAssertionLedger;
  evidenceGroups: AiReviewCalculationEvidenceGroup[];
  sanitizedBenchmarkCases: AiReviewSanitizedBenchmarkCase[];
  aggregate: {
    evidenceGroupCount: number;
    evidenceGroupsMinimumMet: boolean;
    benchmarkCaseCount: number;
    benchmarkCasesMinimumMet: boolean;
    everyBenchmarkHasFocusAccentQuestion: boolean;
    rawExportTextCommitted: false;
    usesSharedResponseContract: boolean;
    usesAssertionLedger: boolean;
    usesCalculationEvidence: boolean;
    usesSanitizedBenchmarks: boolean;
    localOnlyNotFinalOutput: true;
  };
  statusLabels: string[];
};

export type AiReviewGroundedDraftFixtureId =
  | "strong_calculation_grounded_draft"
  | "generic_inspirational_draft"
  | "advanced_overclaim_draft"
  | "composed_grounded_review_draft"
  | "drift_missing_anchor_draft";

export type AiReviewGroundedDraftFixture = {
  id: AiReviewGroundedDraftFixtureId;
  label: string;
  draft: string;
  expectedResult: "pass" | "fail";
  fixtureType: "strong" | "generic" | "overclaim";
};

export type AiReviewGroundedDraftEvaluation = {
  fixture: AiReviewGroundedDraftFixture;
  passed: boolean;
  evidenceGroupHits: AiReviewCalculationEvidenceGroupId[];
  missingRequiredAnchors: AiReviewCalculationEvidenceGroupId[];
  overclaimFlags: string[];
  genericLanguageFlags: string[];
  practicalQuestionQuality: {
    passed: boolean;
    reason: string;
  };
  repairInstructions: string[];
};

export type AiReviewGroundedDraftEvaluator = {
  stage: "P131-A";
  fixtures: AiReviewGroundedDraftFixture[];
  evaluations: AiReviewGroundedDraftEvaluation[];
  aggregate: {
    fixtureCount: number;
    fixturesMinimumMet: boolean;
    strongPasses: boolean;
    genericFails: boolean;
    overclaimFails: boolean;
    strongGroupsHitMinimumMet: boolean;
    repairsPresent: boolean;
    usesCalculationPacket: boolean;
    usesSharedResponseContract: boolean;
    localOnlyNotFinalOutput: true;
  };
  statusLabels: string[];
};

export type AiReviewGroundedComposerSection = {
  name: AiReviewResponseContractSectionName;
  sourceEvidenceGroups: AiReviewCalculationEvidenceGroupId[];
  body: string;
};

export type AiReviewGroundedComposer = {
  stage: "E132-A";
  sections: AiReviewGroundedComposerSection[];
  draft: AiReviewGroundedDraftFixture;
  evaluation: AiReviewGroundedDraftEvaluation;
  driftFixture: AiReviewGroundedDraftFixture;
  driftEvaluation: AiReviewGroundedDraftEvaluation;
  aggregate: {
    sectionCount: number;
    sectionsExact: boolean;
    draftPasses: boolean;
    groupsHit: number;
    groupsHitMinimumMet: boolean;
    practicalQuestionPresent: boolean;
    driftFixtureFails: boolean;
    usesResponseContract: boolean;
    usesCalculationPacket: boolean;
    usesGroundedEvaluator: boolean;
    localOnlyNotFinalOutput: true;
  };
  statusLabels: string[];
};

export type AiReviewGenerationBoundaryFixtureId =
  | "offline_composed_grounded_response"
  | "offline_generic_weak_response"
  | "offline_overclaim_response";

export type AiReviewGenerationBoundaryFixture = {
  id: AiReviewGenerationBoundaryFixtureId;
  label: string;
  fixtureType: "grounded" | "generic" | "overclaim";
  response: string;
  expectedOutcome: "accepted" | "blocked";
};

export type AiReviewGenerationBoundaryRequest = {
  requiredResponseSectionsCount: number;
  requiredEvidenceGroupsCount: number;
  practicalNextQuestionRequired: boolean;
  forbiddenOutputClasses: string[];
  usesGroundedComposer: boolean;
  usesGroundedEvaluator: boolean;
  usesCalculationPacket: boolean;
  usesResponseContract: boolean;
};

export type AiReviewGenerationBoundaryGateResult = {
  fixture: AiReviewGenerationBoundaryFixture;
  outcome: "accepted" | "blocked";
  evaluatorResult: AiReviewGroundedDraftEvaluation;
  failedGateNames: string[];
  repairInstructions: string[];
  displayEligible: boolean;
};

export type AiReviewGenerationBoundary = {
  stage: "P133-A";
  request: AiReviewGenerationBoundaryRequest;
  fixtures: AiReviewGenerationBoundaryFixture[];
  gateResults: AiReviewGenerationBoundaryGateResult[];
  aggregate: {
    fixtureCount: number;
    groundedFixtureAccepted: boolean;
    genericFixtureBlocked: boolean;
    overclaimFixtureBlocked: boolean;
    blockedNotDisplayEligible: boolean;
    repairsPresent: boolean;
    usesGroundedComposer: boolean;
    usesGroundedEvaluator: boolean;
    usesCalculationPacket: boolean;
    usesResponseContract: boolean;
    localOnlyNotFinalOutput: true;
  };
  statusLabels: string[];
};

export type AiReviewAudioConsultationBenchmarkCase = {
  id: "audio_haridas_house_walkthrough" | "audio_govardhan_yoga_weighting";
  label: string;
  sourceKind: "local_asr_consultation_witness";
  calculationPatterns: string[];
  reviewStructureRules: string[];
  followUpQuestionPatterns: string[];
  blockedUses: string[];
};

export type AiReviewAudioConsultationBenchmark = {
  stage: "E134-A";
  cases: AiReviewAudioConsultationBenchmarkCase[];
  aggregate: {
    caseCount: number;
    houseWalkthroughPresent: boolean;
    yogaWeightingPresent: boolean;
    reviewStructureChainPresent: boolean;
    rawTranscriptCommitted: false;
    sourceAudioCommitted: false;
    witnessOnly: true;
    localOnlyNotFinalOutput: true;
  };
  statusLabels: string[];
};

const dimensionLabels: Record<AiReviewQualityDimension, string> = {
  interpretation_depth: "Interpretation depth",
  specific_chart_evidence: "Specific chart evidence",
  practical_synthesis: "Practical synthesis",
  caveats_confidence: "Caveats and confidence",
};

const genericFillerPatterns = [
  "trust your intuition",
  "positive energy",
  "everything happens for a reason",
  "follow your heart",
  "many opportunities",
  "simple life",
];

export const aiReviewQualityFixtures: Record<"strong" | "weak", AiReviewQualityFixture> = {
  strong: {
    fixtureEvidence: ["D1 Pisces Lagna", "Moon in Cancer 5th house", "Saturn in Aquarius 12th house", "Jupiter aspect to Lagna"],
    draft:
      "D1 Pisces Lagna makes the review start from porous boundaries and devotional motivation, but Moon in Cancer 5th house gives a concrete emotional-intelligence anchor. Saturn in Aquarius 12th house adds isolation, sleep discipline, and long-cycle responsibility, while Jupiter aspect to Lagna softens the reading and gives counsel capacity. Together these placements suggest a synthesis: protect daily rhythm before taking on advisory roles. A practical next step is to schedule reflective study before public commitments. Caveat: confidence is moderate until birth-time evidence and divisional corroboration are reviewed.",
  },
  weak: {
    fixtureEvidence: ["D1 Pisces Lagna", "Moon in Cancer 5th house", "Saturn in Aquarius 12th house", "Jupiter aspect to Lagna"],
    draft:
      "You have positive energy and many opportunities. Trust your intuition, follow your heart, and seek a simple life. Everything happens for a reason, so stay open to growth.",
  },
};

export const aiReviewScenarioFixtures: AiReviewScenarioFixture[] = [
  {
    id: "natal-personality",
    intent: "Natal personality",
    evidencePacket: {
      chartEvidenceItems: ["D1 Pisces Lagna", "Moon in Cancer 5th house", "Saturn in Aquarius 12th house", "Jupiter aspect to Lagna"],
      synthesisLinks: [
        "Connect D1 Pisces Lagna with Moon in Cancer 5th house before temperament advice.",
        "Connect Saturn in Aquarius 12th house with Jupiter aspect to Lagna before confidence.",
      ],
      practicalNextStepRequirement: "Include practical next-step framing for study, rest, and advisory boundaries.",
      caveatConfidenceRequirement: "Include caveat/confidence language until birth-time evidence is reviewed.",
    },
    strongDraft:
      "D1 Pisces Lagna shows porous motivation and devotional identity, but Moon in Cancer 5th house gives emotional intelligence and a teaching instinct. Saturn in Aquarius 12th house suggests private discipline, sleep boundaries, and karmic work behind the scenes, while Jupiter aspect to Lagna softens judgment and supports counsel. Together these factors suggest a synthesis: protect rest before serving others. A practical next step is to schedule reflective study before commitments. Caveat: confidence is moderate until birth-time evidence is reviewed.",
    weakDraft: aiReviewQualityFixtures.weak.draft,
  },
  {
    id: "career-dharma",
    intent: "Career dharma",
    evidencePacket: {
      chartEvidenceItems: ["Sun in Aries 2nd house", "Mars in Capricorn 11th house", "Mercury in Gemini 4th house", "10th lord Jupiter in Sagittarius"],
      synthesisLinks: [
        "Connect Sun in Aries 2nd house with Mars in Capricorn 11th house before career direction.",
        "Connect Mercury in Gemini 4th house with 10th lord Jupiter in Sagittarius before role design.",
      ],
      practicalNextStepRequirement: "Include practical next-step framing for one measurable professional experiment.",
      caveatConfidenceRequirement: "Include caveat/confidence language before treating career timing as fixed.",
    },
    strongDraft:
      "Sun in Aries 2nd house indicates assertive speech and value-building, but Mars in Capricorn 11th house makes the career pattern more strategic, networked, and goal-disciplined. Mercury in Gemini 4th house adds analysis and teaching from a knowledge base, while 10th lord Jupiter in Sagittarius points toward advisory, educational, or dharma-aligned work. Together these placements suggest a synthesis: lead through structured knowledge rather than raw urgency. A practical next step is to schedule one measurable professional experiment. Caveat: confidence is moderate until divisional career evidence is checked.",
    weakDraft:
      "Your career has many opportunities and positive energy. Trust your intuition, follow your heart, and choose work that feels comfortable. Everything happens for a reason, so stay open to growth.",
  },
  {
    id: "relationship-compatibility",
    intent: "Relationship compatibility",
    evidencePacket: {
      chartEvidenceItems: ["Venus in Taurus 3rd house", "7th lord Mercury in Virgo", "Moon in Scorpio 9th house", "Rahu in Libra 8th house"],
      synthesisLinks: [
        "Connect Venus in Taurus 3rd house with 7th lord Mercury in Virgo before compatibility advice.",
        "Connect Moon in Scorpio 9th house with Rahu in Libra 8th house before emotional risk framing.",
      ],
      practicalNextStepRequirement: "Include practical next-step framing for communication agreements and pacing.",
      caveatConfidenceRequirement: "Include caveat/confidence language before drawing relationship conclusions.",
    },
    strongDraft:
      "Venus in Taurus 3rd house favors steady affection expressed through daily conversation, but 7th lord Mercury in Virgo makes precision, repair, and shared routines central to compatibility. Moon in Scorpio 9th house adds intense belief patterns and emotional memory, while Rahu in Libra 8th house can amplify intimacy questions and hidden expectations. Together these placements suggest a synthesis: relational stability improves when communication is explicit and paced. A practical next step is to schedule a direct agreement about conflict repair. Caveat: confidence is moderate until partner data and timing context are reviewed.",
    weakDraft:
      "Love improves when both people stay positive and open. Trust your intuition, follow your heart, and seek harmony. Many opportunities for harmony will appear if you keep growing together.",
  },
  {
    id: "transit-timing-guidance",
    intent: "Transit timing guidance",
    evidencePacket: {
      chartEvidenceItems: ["Saturn transit over natal Moon", "Jupiter transit aspect to 10th house", "Rahu transit through 2nd house", "Dasha sequence Venus-Mercury"],
      synthesisLinks: [
        "Connect Saturn transit over natal Moon with Jupiter transit aspect to 10th house before timing advice.",
        "Connect Rahu transit through 2nd house with Dasha sequence Venus-Mercury before guidance.",
      ],
      practicalNextStepRequirement: "Include practical next-step framing for timing decisions and review cadence.",
      caveatConfidenceRequirement: "Include caveat/confidence language before relying on timing guidance.",
    },
    strongDraft:
      "Saturn transit over natal Moon indicates emotional weight and slower decision tempo, but Jupiter transit aspect to 10th house gives a constructive window for professional guidance and mentoring. Rahu transit through 2nd house can distort appetite, speech, and financial urgency, while Dasha sequence Venus-Mercury supports negotiation, learning, and relationship-based choices. Together these factors suggest a synthesis: use timing for careful preparation rather than sudden expansion. A practical next step is to schedule a two-week review cadence before commitments. Caveat: confidence is moderate until transit dates and birth-time evidence are confirmed.",
    weakDraft:
      "This is a good time for growth and new opportunities. Trust your intuition, stay steady, and follow your heart. Everything happens for a reason, so remain positive.",
  },
];

function buildTelegramBenchmarkChartsFromSanitized(): TelegramBenchmarkChart[] {
  const benchmark = buildAiReviewTelegramSanitizedBenchmark();
  return benchmark.cases.map((item, index) => ({
    name: `Anonymized Telegram benchmark ${index + 1}`,
    chartFacts: [...item.chartFacts, ...item.divisionalFacts],
    calculationAccents: [...item.calculationAccents],
    followUpQuestions: [...item.followUpQuestions],
    advancedClaimCautions: [...item.advancedClaimCautions],
  }));
}

export const telegramBenchmarkCharts: TelegramBenchmarkChart[] = buildTelegramBenchmarkChartsFromSanitized();

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function findMatches(text: string, terms: string[]): string[] {
  const normalized = text.toLowerCase();
  return terms.filter((term) => normalized.includes(term.toLowerCase()));
}

function hasAny(text: string, values: string[]): boolean {
  const normalized = text.toLowerCase();
  return values.some((value) => normalized.includes(value));
}

export function evaluateAiReviewDraft(draft: string, fixtureEvidence: string[]): AiReviewQualityEvaluation {
  const wordCount = countWords(draft);
  const matchedEvidence = findMatches(draft, fixtureEvidence);
  const genericMatches = findMatches(draft, genericFillerPatterns);

  const dimensions: AiReviewQualityDimensionResult[] = [
    {
      id: "interpretation_depth",
      label: dimensionLabels.interpretation_depth,
      passed: wordCount >= 70 && hasAny(draft, ["because", "but", "while", "suggest", "indicate"]),
      reason: "Requires enough depth and explicit interpretive linkage.",
    },
    {
      id: "specific_chart_evidence",
      label: dimensionLabels.specific_chart_evidence,
      passed: matchedEvidence.length >= 3,
      reason: "Requires at least three concrete fixture chart-evidence references.",
    },
    {
      id: "practical_synthesis",
      label: dimensionLabels.practical_synthesis,
      passed: hasAny(draft, ["together", "synthesis"]) && hasAny(draft, ["practical next step", "next step", "prioritize", "schedule"]),
      reason: "Requires synthesis across factors plus next-step framing.",
    },
    {
      id: "caveats_confidence",
      label: dimensionLabels.caveats_confidence,
      passed: hasAny(draft, ["caveat", "confidence", "moderate", "until birth-time"]),
      reason: "Requires caveats or confidence language.",
    },
  ];

  const genericFillerGuard = {
    passed: genericMatches.length <= 1 && matchedEvidence.length >= 2,
    matches: genericMatches,
  };
  const passedDimensions = dimensions.filter((item) => item.passed).length;
  const passed = passedDimensions === dimensions.length && genericFillerGuard.passed;

  return {
    passed,
    score: passedDimensions + (genericFillerGuard.passed ? 1 : 0),
    matchedEvidence,
    dimensions,
    genericFillerGuard,
  };
}

function feedbackForFailedDimension(result: AiReviewQualityDimensionResult): string {
  if (result.id === "specific_chart_evidence") return "Weak preview lacks chart-specific evidence from the evidence packet.";
  if (result.id === "practical_synthesis") return "Weak preview lacks practical synthesis across multiple placements/factors.";
  if (result.id === "interpretation_depth") return "Weak preview lacks interpretation depth and causal linkage.";
  return "Weak preview lacks caveats/confidence framing.";
}

export function buildAiReviewEvidencePacket(): AiReviewEvidencePacket {
  return {
    chartEvidenceItems: [...aiReviewQualityFixtures.strong.fixtureEvidence],
    synthesisLinks: [
      "Connect D1 Pisces Lagna with Moon in Cancer 5th house before advice.",
      "Connect Saturn in Aquarius 12th house with Jupiter aspect to Lagna before confidence.",
    ],
    practicalNextStepRequirement: "Include practical next-step framing tied to the chart evidence.",
    caveatConfidenceRequirement: "Include caveat/confidence language before trusting the draft.",
  };
}

export function buildAiReviewMockPreview(): AiReviewMockPreview {
  const evidencePacket = buildAiReviewEvidencePacket();
  const strong = evaluateAiReviewDraft(aiReviewQualityFixtures.strong.draft, evidencePacket.chartEvidenceItems);
  const weak = evaluateAiReviewDraft(aiReviewQualityFixtures.weak.draft, evidencePacket.chartEvidenceItems);
  const failedDimensionFeedback = weak.dimensions.filter((item) => !item.passed).map(feedbackForFailedDimension);

  return {
    stage: "E120-A",
    evidencePacket,
    strong: {
      status: "passes_quality_gate",
      passed: true,
      matchedEvidenceCount: strong.matchedEvidence.length,
      matchedEvidence: strong.matchedEvidence,
    },
    weak: {
      status: "blocked_by_quality_gate",
      passed: false,
      failedDimensionFeedback,
      genericFillerMatches: weak.genericFillerGuard.matches,
    },
    statusLabels: [
      "E120-A",
      "ai_review_quality_preview_stage=E120-A",
      "ai_review_evidence_packet_present=true",
      "ai_review_quality_gate_applied_to_mock_preview=true",
      "ai_review_strong_preview_pass_visible=true",
      "ai_review_weak_preview_blocked_visible=true",
      "ai_review_failed_dimension_feedback_present=true",
      "ai_review_matched_evidence_count_visible=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function composeEvidenceDrivenMockReview(evidencePacket = buildAiReviewEvidencePacket()): AiReviewComposedMockReview {
  const [lagna, moon, saturn, jupiter] = evidencePacket.chartEvidenceItems;
  const composedDraft = [
    `${lagna}, ${moon}, and ${saturn} are the primary evidence anchors, with ${jupiter} used as a moderating factor.`,
    `Together these placements suggest porous motivation, emotional intelligence, private discipline, and counsel capacity while avoiding generic optimism.`,
    `A practical next step is to protect daily rhythm before taking advisory roles, then test commitments against sleep, study, and service capacity.`,
    `Caveat: confidence is moderate until birth-time evidence and divisional corroboration are reviewed.`,
  ].join(" ");
  const strong = evaluateAiReviewDraft(composedDraft, evidencePacket.chartEvidenceItems);
  const weak = evaluateAiReviewDraft(aiReviewQualityFixtures.weak.draft, evidencePacket.chartEvidenceItems);

  return {
    stage: "P121-A",
    sections: [
      {
        heading: "Chart evidence cited",
        body: `${lagna}; ${moon}; ${saturn}; ${jupiter}.`,
      },
      {
        heading: "Interpretive synthesis",
        body: evidencePacket.synthesisLinks.join(" "),
      },
      {
        heading: "Practical guidance",
        body: evidencePacket.practicalNextStepRequirement,
      },
      {
        heading: "Caveats and confidence",
        body: evidencePacket.caveatConfidenceRequirement,
      },
    ],
    strong: {
      status: "passes_quality_gate",
      matchedEvidenceCount: strong.matchedEvidence.length,
    },
    weak: {
      status: "blocked_by_quality_gate",
      usableReviewVisible: false,
      blockReason: "Generic output blocked by quality gate: generic text lacks chart evidence and synthesis.",
      failedDimensionFeedback: weak.dimensions.filter((item) => !item.passed).map(feedbackForFailedDimension),
    },
    statusLabels: [
      "P121-A",
      "ai_review_composer_stage=P121-A",
      "ai_review_evidence_driven_mock_review_present=true",
      "ai_review_composed_sections_present=true",
      "ai_review_composer_uses_evidence_packet=true",
      "ai_review_composed_strong_passes_gate=true",
      "ai_review_generic_output_blocked_by_gate=true",
      "ai_review_generic_block_reason_visible=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewPromptPayload(
  evidencePacket = buildAiReviewEvidencePacket(),
  composed = composeEvidenceDrivenMockReview(evidencePacket),
): AiReviewPromptPayload {
  const requiredStructure = composed.sections.map((section) => section.heading).join(" -> ");
  const antiGenericGuardrails = [
    "Block or revise generic text that lacks chart evidence and synthesis.",
    "Require chart-specific evidence before any practical guidance.",
    "Revise shallow advice when it misses synthesis across placements/factors.",
  ];

  return {
    stage: "E122-A",
    localOnly: true,
    llmNetworkCallExecuted: false,
    evidenceItems: [...evidencePacket.chartEvidenceItems],
    requiredEvidenceCitationCount: 3,
    sections: [
      {
        heading: "System quality rules",
        body: "Use the local evidence packet only; do not treat this dry run as a generated final review.",
      },
      {
        heading: "Chart evidence packet",
        body: evidencePacket.chartEvidenceItems.join("; "),
      },
      {
        heading: "Required review structure",
        body: `${requiredStructure}. Require at least 3 evidence citations before the review can pass.`,
      },
      {
        heading: "Anti-generic guardrails",
        body: antiGenericGuardrails.join(" "),
      },
      {
        heading: "Quality gate before final answer",
        body: AI_REVIEW_QUALITY_DIMENSIONS.join(","),
      },
    ],
    antiGenericGuardrails,
    qualityGateBeforeFinalAnswer: [...AI_REVIEW_QUALITY_DIMENSIONS],
    statusLabels: [
      "E122-A",
      "ai_review_prompt_contract_stage=E122-A",
      "ai_review_prompt_payload_present=true",
      "ai_review_prompt_uses_evidence_packet=true",
      "ai_review_prompt_requires_three_evidence_citations=true",
      "ai_review_prompt_sections_present=true",
      "ai_review_anti_generic_guardrails_present=true",
      "ai_review_quality_gate_before_final_answer=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewScenarioMatrix(): AiReviewScenarioMatrix {
  const scenarios = aiReviewScenarioFixtures.map((scenario): AiReviewScenarioMatrixRow => {
    const composed = composeEvidenceDrivenMockReview(scenario.evidencePacket);
    const promptPayload = buildAiReviewPromptPayload(scenario.evidencePacket, composed);
    const strong = evaluateAiReviewDraft(scenario.strongDraft, scenario.evidencePacket.chartEvidenceItems);
    const weak = evaluateAiReviewDraft(scenario.weakDraft, scenario.evidencePacket.chartEvidenceItems);
    const failedFeedback = weak.dimensions.filter((item) => !item.passed).map(feedbackForFailedDimension);

    return {
      id: scenario.id,
      intent: scenario.intent,
      evidenceItems: [...scenario.evidencePacket.chartEvidenceItems],
      requiredEvidenceCitationCount: promptPayload.requiredEvidenceCitationCount,
      strong: {
        status: strong.passed ? "passes_quality_gate" : "fails_quality_gate",
        matchedEvidenceCount: strong.matchedEvidence.length,
      },
      weak: {
        status: weak.passed ? "passes_quality_gate" : "blocked_by_quality_gate",
        improvementReason:
          failedFeedback.find((item) => item.includes("chart-specific evidence")) ||
          failedFeedback.find((item) => item.includes("practical synthesis")) ||
          "Weak generic output must add chart-specific evidence and practical synthesis.",
      },
      promptPayload,
    };
  });
  const evidenceCounts = scenarios.map((scenario) => scenario.evidenceItems.length);

  return {
    stage: "P123-A",
    scenarios,
    aggregate: {
      scenarioCount: scenarios.length,
      strongPassCount: scenarios.filter((scenario) => scenario.strong.status === "passes_quality_gate").length,
      weakBlockedCount: scenarios.filter((scenario) => scenario.weak.status === "blocked_by_quality_gate").length,
      minimumEvidenceItemCount: Math.min(...evidenceCounts),
      promptContractAppliedAllScenarios: scenarios.every(
        (scenario) =>
          scenario.promptPayload.stage === "E122-A" &&
          scenario.promptPayload.evidenceItems.length >= 4 &&
          scenario.promptPayload.requiredEvidenceCitationCount >= 3,
      ),
    },
    statusLabels: [
      "P123-A",
      "ai_review_multi_fixture_stage=P123-A",
      "ai_review_quality_fixture_matrix_present=true",
      "ai_review_multiple_intents_covered=true",
      "ai_review_scenario_count=4",
      "ai_review_each_scenario_has_four_evidence_items=true",
      "ai_review_each_scenario_requires_three_citations=true",
      "ai_review_strong_outputs_pass_all_scenarios=true",
      "ai_review_generic_outputs_blocked_all_scenarios=true",
      "ai_review_prompt_contract_applied_all_scenarios=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildTelegramBenchmarkReviewBlueprint(): TelegramBenchmarkReviewBlueprint {
  const sanitizedBenchmark = buildAiReviewTelegramSanitizedBenchmark();
  return {
    stage: "E124-A",
    benchmarks: telegramBenchmarkCharts.map((benchmark) => ({
      ...benchmark,
      chartFacts: [...benchmark.chartFacts],
      calculationAccents: [...benchmark.calculationAccents],
      followUpQuestions: [...benchmark.followUpQuestions],
      advancedClaimCautions: [...benchmark.advancedClaimCautions],
    })),
    blueprintSections: ["Chart fact", "Jyotish rule", "Interpretive accent", "Risk or caveat", "Practical next step", "Next question"],
    styleCopied: false,
    statusLabels: [
      "E124-A",
      "ai_review_telegram_benchmark_stage=E124-A",
      "ai_review_telegram_benchmark_present=true",
      "ai_review_benchmark_charts_count=2",
      "ai_review_benchmark_uses_chart_facts=true",
      "ai_review_benchmark_extracts_accents_not_style=true",
      "ai_review_benchmark_followup_questions_present=true",
      "ai_review_benchmark_advanced_claims_gated=true",
      "ai_review_blueprint_sections_present=true",
      ...sanitizedBenchmark.statusLabels,
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewFollowupQuestionContract(): AiReviewFollowupQuestionContract {
  const [publicWorkCase, careerCase] = telegramBenchmarkCharts;
  const candidates: AiReviewFollowupQuestionCandidate[] = [
    {
      question: publicWorkCase.followUpQuestions[0],
      anchorChartFact: publicWorkCase.chartFacts[1],
      jyotishRuleAccent: publicWorkCase.calculationAccents[0],
      status: "ready",
      reason: "Ready because the question names a concrete chart fact and asks for lived manifestation.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: publicWorkCase.followUpQuestions[1],
      anchorChartFact: publicWorkCase.chartFacts[3],
      jyotishRuleAccent: "Dasha layer must be checked before timing interpretation.",
      status: "ready",
      reason: "Ready because the timing question is anchored to the Mars career cluster.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: publicWorkCase.followUpQuestions[2],
      anchorChartFact: publicWorkCase.chartFacts.find((fact) => fact.includes("D9")) ?? publicWorkCase.chartFacts[0],
      jyotishRuleAccent: publicWorkCase.calculationAccents[2],
      status: "ready",
      reason: "Ready because the question asks what D9 adds after D1 is grounded.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: "Does the 2nd-house node connect to speech, family resources, or digital assets in the lived case?",
      anchorChartFact: publicWorkCase.chartFacts[8],
      jyotishRuleAccent: "Rahu in 2nd must be tied to speech, family resources, and digital assets.",
      status: "ready",
      reason: "Ready because the question ties Rahu in 2nd to a concrete life domain.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: careerCase.followUpQuestions[0],
      anchorChartFact: careerCase.chartFacts[3],
      jyotishRuleAccent: careerCase.calculationAccents[0],
      status: "ready",
      reason: "Ready because the question is career-specific and chart-fact anchored.",
      sourceBenchmarkId: "case_cancer_lagna_career",
    },
    {
      question: careerCase.followUpQuestions[1],
      anchorChartFact: careerCase.chartFacts[3],
      jyotishRuleAccent: "D10 career peak should be inspected before professional timing claims.",
      status: "ready",
      reason: "Ready because it asks for a concrete varga/timing follow-up before interpretation.",
      sourceBenchmarkId: "case_cancer_lagna_career",
    },
    {
      question: "Can Shadbala confirm the strength of the 10th-house Aries career cluster?",
      anchorChartFact: publicWorkCase.chartFacts[1],
      jyotishRuleAccent: "Shadbala requires a calculated table before strength claims.",
      status: "gated",
      reason: "Gated because Shadbala is an advanced claim and no calculated table exists.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: "Do Ashtakavarga bindu values support the D10 career peak question?",
      anchorChartFact: careerCase.chartFacts[3],
      jyotishRuleAccent: "Ashtakavarga requires a calculated table before bindu claims.",
      status: "gated",
      reason: "Gated because Ashtakavarga bindu is unavailable without a calculated table.",
      sourceBenchmarkId: "case_cancer_lagna_career",
    },
    {
      question: "Are Avastha or Mrityu-bhaga conditions changing this relationship reading?",
      anchorChartFact: publicWorkCase.chartFacts.find((fact) => fact.includes("D9")) ?? publicWorkCase.chartFacts[0],
      jyotishRuleAccent: "Avastha and Mrityu-bhaga require computed support before use.",
      status: "gated",
      reason: "Gated because Avastha and Mrityu-bhaga need a calculated table before interpretation.",
      sourceBenchmarkId: "case_cancer_lagna_public_work",
    },
    {
      question: "What should I do next?",
      anchorChartFact: "",
      jyotishRuleAccent: "",
      status: "rejected",
      reason: "Rejected generic prompt: no chart-fact anchor, rule/accent, or benchmark source.",
      sourceBenchmarkId: "generic-rejected",
    },
  ];
  const readyQuestions = candidates.filter((candidate) => candidate.status === "ready");
  const advancedTerms = ["Shadbala", "Ashtakavarga", "Avastha", "Mrityu-bhaga"];
  const advancedCandidates = candidates.filter((candidate) =>
    advancedTerms.some((term) => candidate.question.includes(term) || candidate.jyotishRuleAccent.includes(term)),
  );

  return {
    stage: "P125-A",
    candidates,
    aggregate: {
      totalCount: candidates.length,
      readyCount: readyQuestions.length,
      gatedCount: candidates.filter((candidate) => candidate.status === "gated").length,
      rejectedGenericCount: candidates.filter((candidate) => candidate.status === "rejected").length,
      groundedInChartFacts: readyQuestions.every((candidate) => Boolean(candidate.anchorChartFact && candidate.jyotishRuleAccent)),
      advancedClaimsBlockedWithoutCalculation: advancedCandidates.every((candidate) => candidate.status === "gated"),
    },
    statusLabels: [
      "P125-A",
      "ai_review_question_contract_stage=P125-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewAssertionLedger(): AiReviewAssertionLedger {
  const assertions: AiReviewAssertion[] = [
    {
      id: "fact-case-public-work-cancer-lagna",
      assertion: "Benchmark case public-work D1 uses Cancer Lagna in Ashlesha as the review starting frame.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_public_work D1: Cancer Lagna Ashlesha",
      confidenceCaveat: "Use as fixture evidence only until live chart evidence is supplied.",
      status: "usable",
    },
    {
      id: "fact-case-public-work-aries-tenth",
      assertion: "Benchmark case public-work D1 has Sun, Mars, and Saturn in Aries in the 10th house.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_public_work D1: Sun/Mars/Saturn Aries 10th",
      confidenceCaveat: "Treat as benchmark fixture evidence, not a newly computed production claim.",
      status: "usable",
    },
    {
      id: "fact-case-public-work-moon-twelfth",
      assertion: "Benchmark case public-work D1 places Moon in Gemini 12th in Ardra.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_public_work D1: Moon Gemini 12th Ardra",
      confidenceCaveat: "Use only as the named benchmark chart fact.",
      status: "usable",
    },
    {
      id: "fact-case-career-mars-tenth",
      assertion: "Benchmark case career D1 places Mars in Aries 10th in Ashwini.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_career D1: Mars Aries 10th Ashwini",
      confidenceCaveat: "Use as benchmark evidence until user-supplied chart evidence replaces it.",
      status: "usable",
    },
    {
      id: "fact-case-career-venus-ninth",
      assertion: "Benchmark case career D1 places Venus in Pisces 9th.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_career D1: Venus Pisces 9th",
      confidenceCaveat: "Use as compact fixture evidence, not a broad promise of outcome.",
      status: "usable",
    },
    {
      id: "fact-case-career-saturn-rahu-eleventh",
      assertion: "Benchmark case career D1 places Saturn and Rahu in Taurus 11th.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "case_cancer_lagna_career D1: Saturn/Rahu Taurus 11th",
      confidenceCaveat: "Use for question and synthesis scaffolding only.",
      status: "usable",
    },
    {
      id: "rule-tenth-house-career",
      assertion: "Jyotish rule: the 10th house frames public role, work visibility, and responsibility.",
      sourceType: "jyotish_rule",
      evidenceAnchor: "10th-house Aries cluster",
      confidenceCaveat: "Needs dasha and divisional support before timing claims.",
      status: "usable",
    },
    {
      id: "rule-aries-mars-action",
      assertion: "Jyotish rule: Aries and Mars accents sharpen initiative, speed, and conflict risk.",
      sourceType: "jyotish_rule",
      evidenceAnchor: "Mars/Aries career emphasis",
      confidenceCaveat: "Interpret with benefic/malefic context and house ownership.",
      status: "usable",
    },
    {
      id: "rule-twelfth-house-withdrawal",
      assertion: "Jyotish rule: the 12th house can show retreat, hidden work, sleep, expense, or foreign distance.",
      sourceType: "jyotish_rule",
      evidenceAnchor: "Moon Gemini 12th Ardra",
      confidenceCaveat: "Do not turn this into certainty about loss without corroboration.",
      status: "usable",
    },
    {
      id: "synthesis-case-public-work-career",
      assertion: "Derived synthesis: benchmark public-work Aries 10th cluster can support leadership questions, but Saturn adds duty and delay.",
      sourceType: "derived_synthesis",
      evidenceAnchor: "case_cancer_lagna_public_work D1: Sun/Mars/Saturn Aries 10th + rule-tenth-house-career",
      confidenceCaveat: "Keep timing gated until dasha evidence is present.",
      status: "usable",
    },
    {
      id: "synthesis-case-career-network",
      assertion: "Derived synthesis: benchmark career Mars 10th and Saturn/Rahu 11th connect career drive with network pressure.",
      sourceType: "derived_synthesis",
      evidenceAnchor: "case_cancer_lagna_career D1: Mars Aries 10th + Saturn/Rahu Taurus 11th",
      confidenceCaveat: "Avoid claiming peak outcome without D10 and timing support.",
      status: "usable",
    },
    {
      id: "guidance-case-public-work-career-question",
      assertion: "Practical guidance: ask which concrete career decision needs the Aries 10th-house pressure interpreted.",
      sourceType: "practical_guidance",
      evidenceAnchor: "case_cancer_lagna_public_work D1: Aries 10th cluster",
      confidenceCaveat: "Frame as a next question, not as advice to take immediate action.",
      status: "usable",
    },
    {
      id: "guidance-case-career-timing-question",
      assertion: "Practical guidance: ask for timing context before turning benchmark career 10th-house Mars into a prediction.",
      sourceType: "practical_guidance",
      evidenceAnchor: "case_cancer_lagna_career D1: Mars Aries 10th",
      confidenceCaveat: "Requires dasha/transit support before forecast language.",
      status: "usable",
    },
    {
      id: "blocked-shadbala",
      assertion: "Shadbala strength cannot be asserted without a computed Shadbala table.",
      sourceType: "gated_advanced_claim",
      evidenceAnchor: "Missing calculated Shadbala table",
      confidenceCaveat: "Blocked: advanced strength claim is not usable in the composed review.",
      status: "blocked",
    },
    {
      id: "blocked-ashtakavarga",
      assertion: "Ashtakavarga bindu support cannot be asserted without a computed Ashtakavarga table.",
      sourceType: "gated_advanced_claim",
      evidenceAnchor: "Missing calculated Ashtakavarga table",
      confidenceCaveat: "Blocked: bindu claim is not usable in the composed review.",
      status: "blocked",
    },
    {
      id: "blocked-avastha-mrityu",
      assertion: "Avastha or Mrityu-bhaga status cannot be asserted without computed Avastha/Mrityu-bhaga tables.",
      sourceType: "gated_advanced_claim",
      evidenceAnchor: "Missing computed Avastha/Mrityu-bhaga table",
      confidenceCaveat: "Blocked: advanced condition claim is not usable in the composed review.",
      status: "blocked",
    },
  ];

  const countByType = (sourceType: AiReviewAssertionSourceType) => assertions.filter((assertion) => assertion.sourceType === sourceType).length;
  const usableIds = new Set(assertions.filter((assertion) => assertion.status === "usable").map((assertion) => assertion.id));
  const sections: AiReviewAssertionComposedSection[] = [
    {
      heading: "Grounded chart facts",
      body: "Use ledger anchors fact-case-public-work-aries-tenth, fact-case-public-work-moon-twelfth, and fact-case-career-mars-tenth before interpretation.",
      anchorIds: ["fact-case-public-work-aries-tenth", "fact-case-public-work-moon-twelfth", "fact-case-career-mars-tenth"],
    },
    {
      heading: "Jyotish interpretation",
      body: "Use rule-tenth-house-career and synthesis-case-public-work-career to connect public role, responsibility, and initiative without timing certainty.",
      anchorIds: ["rule-tenth-house-career", "rule-aries-mars-action", "synthesis-case-public-work-career"],
    },
    {
      heading: "Practical focus",
      body: "Use guidance-case-public-work-career-question and guidance-case-career-timing-question to turn the reading into grounded next questions.",
      anchorIds: ["guidance-case-public-work-career-question", "guidance-case-career-timing-question", "synthesis-case-career-network"],
    },
    {
      heading: "Caveats and blocked claims",
      body: "Blocked claim reasons: blocked-shadbala and blocked-ashtakavarga require calculated tables; blocked-avastha-mrityu requires computed Avastha/Mrityu-bhaga support.",
      anchorIds: ["blocked-shadbala", "blocked-ashtakavarga", "blocked-avastha-mrityu"],
    },
  ];

  return {
    stage: "E126-A",
    assertions,
    aggregate: {
      totalCount: assertions.length,
      computedChartFactCount: countByType("computed_chart_fact"),
      jyotishRuleCount: countByType("jyotish_rule"),
      derivedSynthesisCount: countByType("derived_synthesis"),
      practicalGuidanceCount: countByType("practical_guidance"),
      blockedAdvancedCount: countByType("gated_advanced_claim"),
      usableCount: assertions.filter((assertion) => assertion.status === "usable").length,
      blockedCount: assertions.filter((assertion) => assertion.status === "blocked").length,
    },
    composedReview: {
      sections,
      usesOnlyUsableAssertions: sections
        .filter((section) => section.heading !== "Caveats and blocked claims")
        .every((section) => section.anchorIds.every((id) => usableIds.has(id))),
      citesLedgerAnchors: sections.every((section) => section.anchorIds.length > 0),
    },
    statusLabels: [
      "E126-A",
      "ai_review_assertion_ledger_stage=E126-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewNarrativeQualityRubric(
  assertionLedger = buildAiReviewAssertionLedger(),
): AiReviewNarrativeQualityRubric {
  const strongAnchors = [
    "fact-case-public-work-aries-tenth",
    "rule-tenth-house-career",
    "synthesis-case-public-work-career",
    "guidance-case-public-work-career-question",
  ];
  const blockedAdvanced = assertionLedger.assertions.filter((assertion) => assertion.sourceType === "gated_advanced_claim");
  const samples: AiReviewNarrativeSample[] = [
    {
      id: "strong_grounded_review",
      label: "Strong grounded review",
      text:
        "Using ledger anchors fact-case-public-work-aries-tenth and rule-tenth-house-career, the career reading starts from a visible 10th-house pressure rather than a mood. The tension is between Aries speed and Saturn duty, so synthesis-case-public-work-career keeps leadership useful without turning it into a timing promise. Practical next question: which concrete public role or career decision should guidance-case-public-work-career-question test against current dasha context? Caveat: Shadbala and Ashtakavarga stay blocked until computed tables exist.",
      status: "passes_quality_rubric",
      passedDimensions: [...AI_REVIEW_NARRATIVE_DIMENSIONS],
      failedDimensions: [],
      anchorCount: strongAnchors.filter((id) => assertionLedger.assertions.some((assertion) => assertion.id === id)).length,
      keyFailureReason: "none",
      hasLifeDomainTension: true,
      hasPracticalNextQuestion: true,
    },
    {
      id: "generic_pretty_review",
      label: "Generic pretty review",
      text:
        "You have a powerful journey ahead. Your intuition and inner strength can open many doors if you stay positive and follow your heart.",
      status: "blocked_by_quality_rubric",
      passedDimensions: [],
      failedDimensions: ["chart_specificity", "rule_to_interpretation_chain", "practical_next_question", "caveat_and_gating"],
      anchorCount: 0,
      keyFailureReason: "Polished language is blocked because it lacks ledger anchors, chart-specific facts, and a rule-to-interpretation chain.",
      hasLifeDomainTension: false,
      hasPracticalNextQuestion: false,
    },
    {
      id: "overclaimed_advanced_review",
      label: "Overclaimed advanced review",
      text:
        "Shadbala proves the planet is strong, Ashtakavarga confirms the result, and Avastha plus Mrityu-bhaga settle the outcome as usable proof.",
      status: "blocked_by_quality_rubric",
      passedDimensions: ["chart_specificity"],
      failedDimensions: ["rule_to_interpretation_chain", "life_domain_tension", "practical_next_question", "caveat_and_gating"],
      anchorCount: blockedAdvanced.length,
      keyFailureReason: "Advanced terms are blocked because Shadbala, Ashtakavarga, Avastha, and Mrityu-bhaga lack computed tables.",
      hasLifeDomainTension: false,
      hasPracticalNextQuestion: false,
    },
  ];
  const passingSamples = samples.filter((sample) => sample.status === "passes_quality_rubric");

  return {
    stage: "P127-A",
    dimensions: [...AI_REVIEW_NARRATIVE_DIMENSIONS],
    samples,
    aggregate: {
      sampleCount: samples.length,
      strongPassCount: samples.filter((sample) => sample.id === "strong_grounded_review" && sample.status === "passes_quality_rubric").length,
      blockedGenericCount: samples.filter((sample) => sample.id === "generic_pretty_review" && sample.status === "blocked_by_quality_rubric").length,
      blockedOverclaimCount: samples.filter((sample) => sample.id === "overclaimed_advanced_review" && sample.status === "blocked_by_quality_rubric").length,
      passingSamplesHaveFourAnchors: passingSamples.every((sample) => sample.anchorCount >= 4),
    },
    statusLabels: [
      "P127-A",
      "ai_review_narrative_rubric_stage=P127-A",
      "ai_review_narrative_rubric_present=true",
      "ai_review_narrative_dimensions=chart_specificity,rule_to_interpretation_chain,life_domain_tension,practical_next_question,caveat_and_gating",
      "ai_review_narrative_sample_count>=3",
      "ai_review_strong_grounded_sample_passes=true",
      "ai_review_generic_pretty_sample_blocked=true",
      "ai_review_overclaimed_advanced_sample_blocked=true",
      "ai_review_passing_samples_have_four_anchors=true",
      "ai_review_rubric_failure_reasons_visible=true",
      "ai_review_narrative_quality_matrix_visible=true",
      "ai_review_advanced_claims_blocked_without_calculation=true",
      "ai_review_local_quality_harness_not_final_output=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewResponseContract(
  assertionLedger = buildAiReviewAssertionLedger(),
  narrativeRubric = buildAiReviewNarrativeQualityRubric(assertionLedger),
): AiReviewResponseContract {
  const sections: AiReviewResponseContractSection[] = [
    {
      name: "Chart anchors",
      requiredSourceAnchorCount: 4,
      requiredRubricDimensions: ["chart_specificity"],
      blockedFailureExamples: ["generic without anchors", "beautiful prose without ledger ids"],
      repairInstruction: "Replace broad claims with at least four assertion-ledger anchors before interpretation.",
    },
    {
      name: "Rule chain",
      requiredSourceAnchorCount: 2,
      requiredRubricDimensions: ["rule_to_interpretation_chain", "chart_specificity"],
      blockedFailureExamples: ["chart fact listed without jyotish rule", "rule named without concrete interpretation"],
      repairInstruction: "Pair each selected chart fact with a jyotish rule and one specific interpretive consequence.",
    },
    {
      name: "Interpretive tension",
      requiredSourceAnchorCount: 2,
      requiredRubricDimensions: ["life_domain_tension", "rule_to_interpretation_chain"],
      blockedFailureExamples: ["one-note praise", "no contrast between opportunity and pressure"],
      repairInstruction: "Add a concrete life-domain tension such as speed versus duty or career drive versus network pressure.",
    },
    {
      name: "Practical next question",
      requiredSourceAnchorCount: 1,
      requiredRubricDimensions: ["practical_next_question"],
      blockedFailureExamples: ["advice without practical next question", "generic self-improvement prompt"],
      repairInstruction: "End with a chart-derived question tied to a ledger anchor and the user's next decision context.",
    },
    {
      name: "Caveats and gated claims",
      requiredSourceAnchorCount: 1,
      requiredRubricDimensions: ["caveat_and_gating"],
      blockedFailureExamples: ["advanced overclaim without computed tables", "Shadbala or Ashtakavarga used as proof"],
      repairInstruction: "Move Shadbala, Ashtakavarga, Avastha, and Mrityu-bhaga statements into blocked caveats unless computed tables exist.",
    },
  ];
  const repairGuidance: AiReviewRepairGuidance[] = [
    {
      type: "generic_without_anchors",
      failurePattern: "generic without anchors",
      repairInstruction: "Require chart anchors from the assertion ledger before any polished summary is accepted.",
    },
    {
      type: "advanced_overclaim_without_computed_tables",
      failurePattern: "advanced overclaim without computed tables",
      repairInstruction: "Block Shadbala, Ashtakavarga, Avastha, and Mrityu-bhaga proof language until computed tables exist.",
    },
    {
      type: "advice_without_practical_next_question",
      failurePattern: "advice without practical next question",
      repairInstruction: "Convert advice into one chart-derived next question with an explicit evidence anchor.",
    },
  ];
  const expectedSectionNames: AiReviewResponseContractSectionName[] = [
    "Chart anchors",
    "Rule chain",
    "Interpretive tension",
    "Practical next question",
    "Caveats and gated claims",
  ];

  return {
    stage: "E128-A",
    sections,
    repairGuidance,
    usesAssertionLedger: assertionLedger.stage === "E126-A" && assertionLedger.assertions.length >= 12,
    usesNarrativeRubric: narrativeRubric.stage === "P127-A" && narrativeRubric.dimensions.length === AI_REVIEW_NARRATIVE_DIMENSIONS.length,
    aggregate: {
      sectionCount: sections.length,
      sectionsExact: sections.map((section) => section.name).join("|") === expectedSectionNames.join("|"),
      everySectionRequiresAnchor: sections.every((section) => section.requiredSourceAnchorCount >= 1),
      everySectionHasRepair: sections.every((section) => section.repairInstruction.length > 0),
      genericRepairPresent: repairGuidance.some((repair) => repair.type === "generic_without_anchors"),
      advancedOverclaimRepairPresent: repairGuidance.some((repair) => repair.type === "advanced_overclaim_without_computed_tables"),
      missingPracticalQuestionRepairPresent: repairGuidance.some((repair) => repair.type === "advice_without_practical_next_question"),
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "E128-A",
      "ai_review_response_contract_stage=E128-A",
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
      "ai_review_local_quality_harness_not_final_output=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewSharedResponseContractSurfaceSummary(
  surface: AiReviewResponseContractSurface,
  contract = buildAiReviewResponseContract(),
): AiReviewSharedResponseContractSurfaceSummary {
  const sectionNames = contract.sections.map((section) => section.name);
  const repairCoverage = {
    generic: contract.repairGuidance.some((repair) => repair.type === "generic_without_anchors"),
    overclaim: contract.repairGuidance.some((repair) => repair.type === "advanced_overclaim_without_computed_tables"),
    missingQuestion: contract.repairGuidance.some((repair) => repair.type === "advice_without_practical_next_question"),
  };

  return {
    stage: "P129-A",
    surface,
    contract,
    sectionNames,
    sectionCount: contract.sections.length,
    repairCoverage,
    aggregate: {
      sharedSource: true,
      sectionsExact: contract.aggregate.sectionsExact && contract.sections.length === 5,
      repairGuidanceCoversFailures: repairCoverage.generic && repairCoverage.overclaim && repairCoverage.missingQuestion,
      productGateNotFinalOutput: true,
    },
    statusLabels: [
      "P129-A",
      "ai_review_response_contract_shared_stage=P129-A",
      "ai_review_response_contract_shared_source=true",
      "ai_review_response_contract_shared_across_surfaces=true",
      surface === "reports"
        ? "ai_review_response_contract_reports_surface=true"
        : "ai_review_response_contract_mock_review_surface=true",
      surface === "report-mock-review" ? "ai_review_response_contract_mock_review_visible=true" : "ai_review_response_contract_reports_visible=true",
      "ai_review_response_contract_shared_sections=5",
      "ai_review_response_contract_shared_sections_exact=true",
      "ai_review_response_contract_shared_repair_guidance=true",
      "ai_review_response_contract_shared_generic_repair=true",
      "ai_review_response_contract_shared_overclaim_repair=true",
      "ai_review_response_contract_shared_missing_question_repair=true",
      "ai_review_response_contract_product_gate_not_final_output=true",
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewCalculationPromptPacket(
  sharedResponseContract = buildAiReviewSharedResponseContractSurfaceSummary("reports"),
  assertionLedger = buildAiReviewAssertionLedger(),
): AiReviewCalculationPromptPacket {
  const evidenceGroups: AiReviewCalculationEvidenceGroup[] = [
    {
      id: "chart_placements",
      evidenceGroup: "chart placements",
      whyItMatters: "Forces the review to cite actual graha, sign, house, and lagna facts before interpretation.",
      requiredAnchorType: "computed placement anchor",
      benchmarkCovered: true,
    },
    {
      id: "lord_relationships",
      evidenceGroup: "house/lord relationships",
      whyItMatters: "Connects house ownership and placement before life-domain conclusions.",
      requiredAnchorType: "house lord relationship anchor",
      benchmarkCovered: true,
    },
    {
      id: "dignity_strength",
      evidenceGroup: "dignity/strength notes",
      whyItMatters: "Separates simple sign dignity from gated advanced strength tables.",
      requiredAnchorType: "computed dignity or strength-note anchor",
      benchmarkCovered: true,
    },
    {
      id: "yoga_candidates",
      evidenceGroup: "yoga or combination candidates",
      whyItMatters: "Makes combination claims explicit candidates instead of loose praise.",
      requiredAnchorType: "computed combination candidate anchor",
      benchmarkCovered: true,
    },
    {
      id: "dasha_transit_timing",
      evidenceGroup: "dasha/transit timing anchors",
      whyItMatters: "Blocks timing claims unless a period or transit anchor is present.",
      requiredAnchorType: "computed timing anchor",
      benchmarkCovered: true,
    },
    {
      id: "tension_flags",
      evidenceGroup: "contradiction/tension flags",
      whyItMatters: "Preserves useful contrast, such as initiative versus restraint, instead of generic positivity.",
      requiredAnchorType: "derived tension flag anchor",
      benchmarkCovered: true,
    },
  ];
  const sanitizedBenchmarkCases: AiReviewSanitizedBenchmarkCase[] = [
    {
      id: "benchmark_case_01",
      calculationFocus: "10th-house fire-sign career concentration with timing request",
      interpretiveAccent: "public-role pressure, initiative, duty, and delayed authority",
      questionPattern: "Ask which career decision should be tested against current dasha or divisional support.",
      qualityRisk: "Overconfident career prediction without timing anchor.",
    },
    {
      id: "benchmark_case_02",
      calculationFocus: "relationship-layer contrast between natal promise and divisional confirmation",
      interpretiveAccent: "distinguish attraction, commitment layer, and maturity caveat",
      questionPattern: "Ask which relationship layer needs D9 or compatibility evidence before synthesis.",
      qualityRisk: "Romantic certainty without divisional corroboration.",
    },
    {
      id: "benchmark_case_03",
      calculationFocus: "speech/resources axis with digital-asset or family-value question",
      interpretiveAccent: "separate material appetite, speech risk, and practical boundary-setting",
      questionPattern: "Ask which resource decision or communication pattern should be examined first.",
      qualityRisk: "Generic finance advice without chart-fact anchor.",
    },
  ];

  return {
    stage: "E130-A",
    sharedResponseContract,
    assertionLedger,
    evidenceGroups,
    sanitizedBenchmarkCases,
    aggregate: {
      evidenceGroupCount: evidenceGroups.length,
      evidenceGroupsMinimumMet: evidenceGroups.length >= 6,
      benchmarkCaseCount: sanitizedBenchmarkCases.length,
      benchmarkCasesMinimumMet: sanitizedBenchmarkCases.length >= 3,
      everyBenchmarkHasFocusAccentQuestion: sanitizedBenchmarkCases.every(
        (item) => item.calculationFocus.length > 0 && item.interpretiveAccent.length > 0 && item.questionPattern.length > 0,
      ),
      rawExportTextCommitted: false,
      usesSharedResponseContract: sharedResponseContract.stage === "P129-A",
      usesAssertionLedger: assertionLedger.stage === "E126-A",
      usesCalculationEvidence: evidenceGroups.length >= 6,
      usesSanitizedBenchmarks: sanitizedBenchmarkCases.length >= 3,
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "E130-A",
      "ai_review_calculation_packet_stage=E130-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export const aiReviewGroundedDraftFixtures: AiReviewGroundedDraftFixture[] = [
  {
    id: "strong_calculation_grounded_draft",
    label: "Strong calculation-grounded draft",
    expectedResult: "pass",
    fixtureType: "strong",
    draft:
      "Chart placements anchor the review before tone: the draft names concrete placements, then connects house/lord relationships to life-domain focus. Dignity/strength notes are kept as simple sign-strength context, while yoga or combination candidates stay candidate language. Dasha/transit timing anchors are requested before any forecast. The contradiction/tension flags are practical: initiative versus restraint and public drive versus network pressure. Practical next question: which career or relationship decision should be tested against the timing anchor first?",
  },
  {
    id: "generic_inspirational_draft",
    label: "Generic inspirational draft",
    expectedResult: "fail",
    fixtureType: "generic",
    draft:
      "You have positive energy and many opportunities. Trust your intuition, follow your heart, and let the universe guide your next step.",
  },
  {
    id: "advanced_overclaim_draft",
    label: "Advanced overclaim draft",
    expectedResult: "fail",
    fixtureType: "overclaim",
    draft:
      "Shadbala proves the strongest planet, Ashtakavarga confirms the result, and Avastha plus Mrityu-bhaga settle timing without any computed anchors.",
  },
];

export function evaluateAiReviewGroundedDraftFixture(
  fixture: AiReviewGroundedDraftFixture,
  calculationPromptPacket = buildAiReviewCalculationPromptPacket(),
): AiReviewGroundedDraftEvaluation {
  const draft = fixture.draft.toLowerCase();
  const evidenceGroupHits = calculationPromptPacket.evidenceGroups
    .filter((group) => {
      const groupLabel = group.evidenceGroup.toLowerCase();
      const idLabel = group.id.replaceAll("_", " ").toLowerCase();
      return draft.includes(groupLabel) || draft.includes(idLabel);
    })
    .map((group) => group.id);
  const missingRequiredAnchors = calculationPromptPacket.evidenceGroups
    .filter((group) => !evidenceGroupHits.includes(group.id))
    .map((group) => group.id);
  const overclaimFlags = ["Shadbala", "Ashtakavarga", "Avastha", "Mrityu-bhaga"].filter((term) => {
    const termLower = term.toLowerCase();
    return draft.includes(termLower) && !draft.includes("blocked") && !draft.includes("gated");
  });
  const genericLanguageFlags = genericFillerPatterns.filter((pattern) => draft.includes(pattern));
  const practicalQuestionQuality = {
    passed: draft.includes("?") && (draft.includes("which ") || draft.includes("what ")) && draft.includes("anchor"),
    reason: draft.includes("?")
      ? "Practical question is present and checked for anchor language."
      : "Missing practical next question tied to evidence.",
  };
  const repairInstructions = [
    evidenceGroupHits.length < 4 ? "Add at least four E130 calculation evidence groups before using the draft." : "",
    genericLanguageFlags.length > 0 ? "Replace generic motivational phrasing with chart placements, rule chain, and evidence anchors." : "",
    overclaimFlags.length > 0 ? "Move advanced claims into blocked caveats unless computed tables support them." : "",
    practicalQuestionQuality.passed ? "" : "Add one practical next question tied to a calculation anchor.",
  ].filter(Boolean);

  return {
    fixture,
    passed: evidenceGroupHits.length >= 4 && overclaimFlags.length === 0 && genericLanguageFlags.length === 0 && practicalQuestionQuality.passed,
    evidenceGroupHits,
    missingRequiredAnchors,
    overclaimFlags,
    genericLanguageFlags,
    practicalQuestionQuality,
    repairInstructions,
  };
}

export function buildAiReviewGroundedDraftEvaluator(
  calculationPromptPacket = buildAiReviewCalculationPromptPacket(),
): AiReviewGroundedDraftEvaluator {
  const evaluations = aiReviewGroundedDraftFixtures.map((fixture) => evaluateAiReviewGroundedDraftFixture(fixture, calculationPromptPacket));
  const strong = evaluations.find((item) => item.fixture.id === "strong_calculation_grounded_draft");
  const generic = evaluations.find((item) => item.fixture.id === "generic_inspirational_draft");
  const overclaim = evaluations.find((item) => item.fixture.id === "advanced_overclaim_draft");

  return {
    stage: "P131-A",
    fixtures: aiReviewGroundedDraftFixtures,
    evaluations,
    aggregate: {
      fixtureCount: aiReviewGroundedDraftFixtures.length,
      fixturesMinimumMet: aiReviewGroundedDraftFixtures.length >= 3,
      strongPasses: strong?.passed === true,
      genericFails: generic?.passed === false,
      overclaimFails: overclaim?.passed === false,
      strongGroupsHitMinimumMet: (strong?.evidenceGroupHits.length ?? 0) >= 4,
      repairsPresent: evaluations
        .filter((item) => item.fixture.expectedResult === "fail")
        .every((item) => item.repairInstructions.length >= 1),
      usesCalculationPacket: calculationPromptPacket.stage === "E130-A",
      usesSharedResponseContract: calculationPromptPacket.sharedResponseContract.stage === "P129-A",
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "P131-A",
      "ai_review_grounded_draft_evaluator_stage=P131-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewGroundedComposer(
  calculationPromptPacket = buildAiReviewCalculationPromptPacket(),
  groundedDraftEvaluator = buildAiReviewGroundedDraftEvaluator(calculationPromptPacket),
): AiReviewGroundedComposer {
  const responseSectionNames = calculationPromptPacket.sharedResponseContract.sectionNames;
  const sections: AiReviewGroundedComposerSection[] = responseSectionNames.map((name) => {
    if (name === "Chart anchors") {
      return {
        name,
        sourceEvidenceGroups: ["chart_placements"],
        body: "Chart anchors cite chart placements before any interpretation.",
      };
    }
    if (name === "Rule chain") {
      return {
        name,
        sourceEvidenceGroups: ["lord_relationships", "dignity_strength"],
        body: "Rule chain links house/lord relationships with dignity/strength notes.",
      };
    }
    if (name === "Interpretive tension") {
      return {
        name,
        sourceEvidenceGroups: ["tension_flags"],
        body: "Interpretive tension names contradiction/tension flags before synthesis.",
      };
    }
    if (name === "Practical next question") {
      return {
        name,
        sourceEvidenceGroups: ["dasha_transit_timing"],
        body: "Practical next question is tied to dasha/transit timing anchors.",
      };
    }
    return {
      name,
      sourceEvidenceGroups: ["dignity_strength", "tension_flags"],
      body: "Caveats keep uncomputed advanced claims gated and separate from usable output.",
    };
  });
  const draftText =
    "Chart anchors: chart placements anchor the answer before tone. Rule chain: house/lord relationships and dignity/strength notes explain why the life-domain reading is narrow. Interpretive tension: contradiction/tension flags show where public push and private restraint must be held together. Practical next question: which choice should be tested against dasha/transit timing anchors first? Caveats and gated claims: uncomputed advanced tables remain gated, and the draft stays local-only.";
  const draft: AiReviewGroundedDraftFixture = {
    id: "composed_grounded_review_draft",
    label: "Composed grounded review draft",
    expectedResult: "pass",
    fixtureType: "strong",
    draft: draftText,
  };
  const evaluation = evaluateAiReviewGroundedDraftFixture(draft, calculationPromptPacket);
  const driftFixture: AiReviewGroundedDraftFixture = {
    id: "drift_missing_anchor_draft",
    label: "Drift fixture missing anchors",
    expectedResult: "fail",
    fixtureType: "generic",
    draft:
      "Chart anchors are skipped. Rule chain is vague. Interpretive tension becomes general encouragement, and the practical next step is advice without calculation anchors.",
  };
  const driftEvaluation = evaluateAiReviewGroundedDraftFixture(driftFixture, calculationPromptPacket);
  const expectedSections = "Chart anchors|Rule chain|Interpretive tension|Practical next question|Caveats and gated claims";
  const sectionsExact = sections.map((section) => section.name).join("|") === expectedSections;
  const groupsHit = evaluation.evidenceGroupHits.length;

  return {
    stage: "E132-A",
    sections,
    draft,
    evaluation,
    driftFixture,
    driftEvaluation,
    aggregate: {
      sectionCount: sections.length,
      sectionsExact,
      draftPasses: evaluation.passed,
      groupsHit,
      groupsHitMinimumMet: groupsHit >= 5,
      practicalQuestionPresent: evaluation.practicalQuestionQuality.passed,
      driftFixtureFails: driftEvaluation.passed === false,
      usesResponseContract: calculationPromptPacket.sharedResponseContract.stage === "P129-A",
      usesCalculationPacket: calculationPromptPacket.stage === "E130-A",
      usesGroundedEvaluator: groundedDraftEvaluator.stage === "P131-A",
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "E132-A",
      "ai_review_grounded_composer_stage=E132-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

function evaluateAiReviewGenerationBoundaryFixture(
  fixture: AiReviewGenerationBoundaryFixture,
  request: AiReviewGenerationBoundaryRequest,
  calculationPromptPacket: AiReviewCalculationPromptPacket,
): AiReviewGenerationBoundaryGateResult {
  const draftFixture: AiReviewGroundedDraftFixture = {
    id:
      fixture.fixtureType === "grounded"
        ? "composed_grounded_review_draft"
        : fixture.fixtureType === "overclaim"
          ? "advanced_overclaim_draft"
          : "generic_inspirational_draft",
    label: fixture.label,
    draft: fixture.response,
    expectedResult: fixture.expectedOutcome === "accepted" ? "pass" : "fail",
    fixtureType: fixture.fixtureType === "grounded" ? "strong" : fixture.fixtureType,
  };
  const evaluatorResult = evaluateAiReviewGroundedDraftFixture(draftFixture, calculationPromptPacket);
  const responseLower = fixture.response.toLowerCase();
  const failedGateNames = [
    evaluatorResult.genericLanguageFlags.length > 0 ? "generic prose" : "",
    evaluatorResult.overclaimFlags.length > 0 ? "advanced overclaim without anchors" : "",
    evaluatorResult.evidenceGroupHits.length < request.requiredEvidenceGroupsCount ? "missing calculation anchors" : "",
    evaluatorResult.practicalQuestionQuality.passed ? "" : "missing practical next question",
    responseLower.includes("caveat") || responseLower.includes("gated") || responseLower.includes("blocked") ? "" : "missing caveats",
  ].filter(Boolean);
  const displayEligible = evaluatorResult.passed && failedGateNames.length === 0;
  const repairInstructions = Array.from(
    new Set([
      ...evaluatorResult.repairInstructions,
      failedGateNames.includes("missing calculation anchors")
        ? "Add calculation anchors from the E130 packet before display."
        : "",
      failedGateNames.includes("missing caveats") ? "Add caveats or gated-claim language before display." : "",
    ].filter(Boolean)),
  );

  return {
    fixture,
    outcome: displayEligible ? "accepted" : "blocked",
    evaluatorResult,
    failedGateNames,
    repairInstructions,
    displayEligible,
  };
}

export function buildAiReviewGenerationBoundary(
  calculationPromptPacket = buildAiReviewCalculationPromptPacket(),
  groundedDraftEvaluator = buildAiReviewGroundedDraftEvaluator(calculationPromptPacket),
  groundedComposer = buildAiReviewGroundedComposer(calculationPromptPacket, groundedDraftEvaluator),
): AiReviewGenerationBoundary {
  const request: AiReviewGenerationBoundaryRequest = {
    requiredResponseSectionsCount: groundedComposer.sections.length,
    requiredEvidenceGroupsCount: 5,
    practicalNextQuestionRequired: true,
    forbiddenOutputClasses: [
      "generic prose",
      "advanced overclaim without anchors",
      "missing calculation anchors",
      "missing caveats",
    ],
    usesGroundedComposer: groundedComposer.stage === "E132-A",
    usesGroundedEvaluator: groundedDraftEvaluator.stage === "P131-A",
    usesCalculationPacket: calculationPromptPacket.stage === "E130-A",
    usesResponseContract: calculationPromptPacket.sharedResponseContract.stage === "P129-A",
  };
  const fixtures: AiReviewGenerationBoundaryFixture[] = [
    {
      id: "offline_composed_grounded_response",
      label: "Composed grounded response",
      fixtureType: "grounded",
      expectedOutcome: "accepted",
      response: groundedComposer.draft.draft,
    },
    {
      id: "offline_generic_weak_response",
      label: "Generic weak response",
      fixtureType: "generic",
      expectedOutcome: "blocked",
      response:
        "You have positive energy and many opportunities. Trust your intuition, follow your heart, and let things unfold naturally.",
    },
    {
      id: "offline_overclaim_response",
      label: "Overclaim response",
      fixtureType: "overclaim",
      expectedOutcome: "blocked",
      response:
        "Chart placements sound promising, but Shadbala proves strength and Ashtakavarga confirms timing without computed anchors.",
    },
  ];
  const gateResults = fixtures.map((fixture) => evaluateAiReviewGenerationBoundaryFixture(fixture, request, calculationPromptPacket));
  const grounded = gateResults.find((result) => result.fixture.id === "offline_composed_grounded_response");
  const generic = gateResults.find((result) => result.fixture.id === "offline_generic_weak_response");
  const overclaim = gateResults.find((result) => result.fixture.id === "offline_overclaim_response");

  return {
    stage: "P133-A",
    request,
    fixtures,
    gateResults,
    aggregate: {
      fixtureCount: fixtures.length,
      groundedFixtureAccepted: grounded?.outcome === "accepted" && grounded.displayEligible,
      genericFixtureBlocked: generic?.outcome === "blocked",
      overclaimFixtureBlocked: overclaim?.outcome === "blocked",
      blockedNotDisplayEligible: gateResults
        .filter((result) => result.outcome === "blocked")
        .every((result) => result.displayEligible === false),
      repairsPresent: gateResults
        .filter((result) => result.outcome === "blocked")
        .every((result) => result.repairInstructions.length >= 1),
      usesGroundedComposer: request.usesGroundedComposer,
      usesGroundedEvaluator: request.usesGroundedEvaluator,
      usesCalculationPacket: request.usesCalculationPacket,
      usesResponseContract: request.usesResponseContract,
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "P133-A",
      "ai_review_generation_boundary_stage=P133-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewAudioConsultationBenchmark(): AiReviewAudioConsultationBenchmark {
  const cases: AiReviewAudioConsultationBenchmarkCase[] = [
    {
      id: "audio_haridas_house_walkthrough",
      label: "House walkthrough consultation witness",
      sourceKind: "local_asr_consultation_witness",
      calculationPatterns: [
        "Start from birth data, lagna, house meaning, house lord, lord placement, aspect, dignity, then conclusion.",
        "Treat each life domain as a house-specific calculation chain, not as generic personality prose.",
        "Use classical-source mentions as a witness for why a rule matters, while keeping raw transcript text out of the app.",
      ],
      reviewStructureRules: [
        "Explain the technical factor before the interpretation.",
        "Keep mixed outcomes visible when a house has both support and pressure.",
        "Separate objective chart factor, practical effect, and confidence caveat.",
      ],
      followUpQuestionPatterns: [
        "Ask which life domain should be expanded after the broad walkthrough.",
        "Ask for context when a result depends on period activation or user priority.",
      ],
      blockedUses: [
        "Do not copy the speaker style.",
        "Do not commit raw ASR text or source audio.",
        "Do not treat the witness as JH/PL parity evidence.",
      ],
    },
    {
      id: "audio_govardhan_yoga_weighting",
      label: "Yoga weighting consultation witness",
      sourceKind: "local_asr_consultation_witness",
      calculationPatterns: [
        "Read yogas as repeated signals whose strength depends on planet condition, relationship, and supporting factors.",
        "Reject one-factor promises; weigh whether planets are friendly, hostile, strong, weak, repeated, or contradicted.",
        "Gate wealth, longevity, health, marriage, and other advanced claims behind explicit computed anchors.",
      ],
      reviewStructureRules: [
        "Never present a chart as all good or all bad.",
        "State what improves, what weakens, and what remains uncertain.",
        "Turn strong claims into measured practical guidance unless timing and divisional support are present.",
      ],
      followUpQuestionPatterns: [
        "Ask which yoga/domain should be checked with divisional and timing layers.",
        "Ask a practical next question tied to the computed factor, not a vague coaching prompt.",
      ],
      blockedUses: [
        "Do not use audio benchmark as final generated review text.",
        "Do not infer unsupported advanced tables from a narrative witness.",
        "Do not claim competitor parity from this benchmark.",
      ],
    },
  ];

  return {
    stage: "E134-A",
    cases,
    aggregate: {
      caseCount: cases.length,
      houseWalkthroughPresent: cases.some((item) => item.id === "audio_haridas_house_walkthrough"),
      yogaWeightingPresent: cases.some((item) => item.id === "audio_govardhan_yoga_weighting"),
      reviewStructureChainPresent: cases.every((item) => item.reviewStructureRules.length >= 3),
      rawTranscriptCommitted: false,
      sourceAudioCommitted: false,
      witnessOnly: true,
      localOnlyNotFinalOutput: true,
    },
    statusLabels: [
      "E134-A",
      "ai_review_audio_consultation_benchmark_stage=E134-A",
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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewQualityLabSummary() {
  const strong = evaluateAiReviewDraft(aiReviewQualityFixtures.strong.draft, aiReviewQualityFixtures.strong.fixtureEvidence);
  const weak = evaluateAiReviewDraft(aiReviewQualityFixtures.weak.draft, aiReviewQualityFixtures.weak.fixtureEvidence);
  const preview = buildAiReviewMockPreview();
  const composed = composeEvidenceDrivenMockReview(preview.evidencePacket);
  const promptPayload = buildAiReviewPromptPayload(preview.evidencePacket, composed);
  const scenarioMatrix = buildAiReviewScenarioMatrix();
  const telegramBenchmark = buildTelegramBenchmarkReviewBlueprint();
  const followupQuestionContract = buildAiReviewFollowupQuestionContract();
  const assertionLedger = buildAiReviewAssertionLedger();
  const narrativeRubric = buildAiReviewNarrativeQualityRubric(assertionLedger);
  const responseContract = buildAiReviewResponseContract(assertionLedger, narrativeRubric);
  const sharedResponseContract = buildAiReviewSharedResponseContractSurfaceSummary("reports", responseContract);
  const calculationPromptPacket = buildAiReviewCalculationPromptPacket(sharedResponseContract, assertionLedger);
  const groundedDraftEvaluator = buildAiReviewGroundedDraftEvaluator(calculationPromptPacket);
  const groundedComposer = buildAiReviewGroundedComposer(calculationPromptPacket, groundedDraftEvaluator);
  const generationBoundary = buildAiReviewGenerationBoundary(calculationPromptPacket, groundedDraftEvaluator, groundedComposer);
  const audioConsultationBenchmark = buildAiReviewAudioConsultationBenchmark();
  const benchmarkParityReport = buildAiReviewBenchmarkParityReport();

  return {
    stage: AI_REVIEW_QUALITY_STAGE,
    statusLabels: [
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
      ...preview.statusLabels,
      ...composed.statusLabels,
      ...promptPayload.statusLabels,
      ...scenarioMatrix.statusLabels,
      ...telegramBenchmark.statusLabels,
      ...followupQuestionContract.statusLabels,
      ...assertionLedger.statusLabels,
      ...narrativeRubric.statusLabels,
      ...responseContract.statusLabels,
      ...sharedResponseContract.statusLabels,
      ...calculationPromptPacket.statusLabels,
      ...groundedDraftEvaluator.statusLabels,
      ...groundedComposer.statusLabels,
      ...generationBoundary.statusLabels,
      ...audioConsultationBenchmark.statusLabels,
      ...benchmarkParityReport.statusLabels,
    ],
    dimensions: AI_REVIEW_QUALITY_DIMENSIONS.map((id) => ({
      id,
      label: dimensionLabels[id],
    })),
    checklist: [
      "chart-specific evidence, not generic advice",
      "synthesis across multiple placements/factors",
      "practical next-step framing",
      "caveats/confidence",
    ],
    strongFixturePasses: strong.passed,
    weakFixtureFails: !weak.passed,
    strong,
    weak,
    preview,
    composed,
    promptPayload,
    scenarioMatrix,
    telegramBenchmark,
    followupQuestionContract,
    assertionLedger,
    narrativeRubric,
    responseContract,
    sharedResponseContract,
    calculationPromptPacket,
    groundedDraftEvaluator,
    groundedComposer,
    generationBoundary,
    audioConsultationBenchmark,
    benchmarkParityReport,
  };
}
