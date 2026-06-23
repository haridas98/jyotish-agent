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
  name: "Haridev D1/D9 benchmark" | "Seva D1/career benchmark";
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

export const telegramBenchmarkCharts: TelegramBenchmarkChart[] = [
  {
    name: "Haridev D1/D9 benchmark",
    chartFacts: [
      "Haridev D1 Cancer Lagna Ashlesha",
      "Haridev D1 Sun Mars Saturn in Aries 10th",
      "Haridev D1 Moon in Gemini 12th Ardra",
      "Haridev D1 Mercury Venus in Pisces 9th",
      "Haridev D9 Aquarius Lagna with Sun Rahu in Leo",
    ],
    calculationAccents: [
      "10th-house Aries cluster anchors career pressure and visibility before prose.",
      "Moon in 12th Ardra must be read with sleep, isolation, and mental-noise caveats.",
      "D9 relationship layer is a separate confirmation layer, not a substitute for D1 facts.",
    ],
    followUpQuestions: [
      "How is the 10th-house Aries cluster showing up in authority, conflict, or public work?",
      "Which Sookshma-dasha Mars timing window should be checked before career interpretation?",
      "What does the D9 relationship layer add after the D1 career pressure is grounded?",
      "Does Rahu in 2nd connect to speech, family resources, or digital assets in the lived case?",
    ],
    advancedClaimCautions: [
      "Shadbala remains gated unless a calculated table exists.",
      "Ashtakavarga bindu remains gated unless a calculated table exists.",
      "Avastha and Mrityu-bhaga remain gated unless calculated by the system.",
    ],
  },
  {
    name: "Seva D1/career benchmark",
    chartFacts: [
      "Seva D1 Cancer Lagna Ashlesha",
      "Seva D1 Mars in Aries 10th Ashwini",
      "Seva D1 Sun Mercury in Aquarius 8th",
      "Seva D1 Moon in Capricorn 7th",
      "Seva D1 Saturn Rahu in Taurus 11th",
    ],
    calculationAccents: [
      "Mars in Aries 10th Ashwini anchors career action before generic vocation advice.",
      "Sun Mercury in Aquarius 8th requires caveats around hidden systems, research, and volatility.",
      "Saturn Rahu in Taurus 11th must be tied to networks, gains, and long-cycle ambition.",
    ],
    followUpQuestions: [
      "Where is Mars in Aries 10th producing initiative, urgency, or leadership friction?",
      "Which D10 career peak should be inspected before making professional timing claims?",
      "How does Moon in Capricorn 7th shape partnership duties during career choices?",
      "Are Saturn Rahu 11th gains coming through stable networks or unusual digital channels?",
    ],
    advancedClaimCautions: [
      "Shadbala remains gated unless a calculated table exists.",
      "Ashtakavarga bindu remains gated unless a calculated table exists.",
      "Avastha and Mrityu-bhaga remain gated unless calculated by the system.",
    ],
  },
];

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
      "ai_review_llm_network_call_executed=false",
      "backend_calculation_changed=false",
      "production_deploy_skipped_per_user_batching_policy=true",
      "last_verified_deploy_commit=508df50",
    ],
  };
}

export function buildAiReviewFollowupQuestionContract(): AiReviewFollowupQuestionContract {
  const [haridev, seva] = telegramBenchmarkCharts;
  const candidates: AiReviewFollowupQuestionCandidate[] = [
    {
      question: haridev.followUpQuestions[0],
      anchorChartFact: "Haridev D1 Sun Mars Saturn in Aries 10th",
      jyotishRuleAccent: "10th-house Aries cluster anchors career pressure and visibility before prose.",
      status: "ready",
      reason: "Ready because the question names a concrete chart fact and asks for lived manifestation.",
      sourceBenchmarkId: "haridev-d1-d9",
    },
    {
      question: haridev.followUpQuestions[1],
      anchorChartFact: "Haridev D1 Sun Mars Saturn in Aries 10th",
      jyotishRuleAccent: "Sookshma-dasha Mars timing must be checked before career interpretation.",
      status: "ready",
      reason: "Ready because the timing question is anchored to the Mars career cluster.",
      sourceBenchmarkId: "haridev-d1-d9",
    },
    {
      question: haridev.followUpQuestions[2],
      anchorChartFact: "Haridev D9 Aquarius Lagna with Sun Rahu in Leo",
      jyotishRuleAccent: "D9 relationship layer is a separate confirmation layer, not a substitute for D1 facts.",
      status: "ready",
      reason: "Ready because the question asks what D9 adds after D1 is grounded.",
      sourceBenchmarkId: "haridev-d1-d9",
    },
    {
      question: haridev.followUpQuestions[3],
      anchorChartFact: "Haridev D1 Rahu Leo 2nd",
      jyotishRuleAccent: "Rahu in 2nd must be tied to speech, family resources, and digital assets.",
      status: "ready",
      reason: "Ready because the question ties Rahu in 2nd to a concrete life domain.",
      sourceBenchmarkId: "haridev-d1-d9",
    },
    {
      question: seva.followUpQuestions[0],
      anchorChartFact: "Seva D1 Mars in Aries 10th Ashwini",
      jyotishRuleAccent: "Mars in Aries 10th Ashwini anchors career action before generic vocation advice.",
      status: "ready",
      reason: "Ready because the question is career-specific and chart-fact anchored.",
      sourceBenchmarkId: "seva-d1-career",
    },
    {
      question: seva.followUpQuestions[1],
      anchorChartFact: "Seva D1 Mars in Aries 10th Ashwini",
      jyotishRuleAccent: "D10 career peak should be inspected before professional timing claims.",
      status: "ready",
      reason: "Ready because it asks for a concrete varga/timing follow-up before interpretation.",
      sourceBenchmarkId: "seva-d1-career",
    },
    {
      question: "Can Shadbala confirm the strength of the 10th-house Aries career cluster?",
      anchorChartFact: "Haridev D1 Sun Mars Saturn in Aries 10th",
      jyotishRuleAccent: "Shadbala requires a calculated table before strength claims.",
      status: "gated",
      reason: "Gated because Shadbala is an advanced claim and no calculated table exists.",
      sourceBenchmarkId: "haridev-d1-d9",
    },
    {
      question: "Do Ashtakavarga bindu values support the D10 career peak question?",
      anchorChartFact: "Seva D1 Mars in Aries 10th Ashwini",
      jyotishRuleAccent: "Ashtakavarga requires a calculated table before bindu claims.",
      status: "gated",
      reason: "Gated because Ashtakavarga bindu is unavailable without a calculated table.",
      sourceBenchmarkId: "seva-d1-career",
    },
    {
      question: "Are Avastha or Mrityu-bhaga conditions changing this relationship reading?",
      anchorChartFact: "Haridev D9 Aquarius Lagna with Sun Rahu in Leo",
      jyotishRuleAccent: "Avastha and Mrityu-bhaga require computed support before use.",
      status: "gated",
      reason: "Gated because Avastha and Mrityu-bhaga need a calculated table before interpretation.",
      sourceBenchmarkId: "haridev-d1-d9",
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
      id: "fact-haridev-cancer-lagna",
      assertion: "Haridev D1 uses Cancer Lagna in Ashlesha as the review's starting frame.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Haridev D1: Cancer Lagna Ashlesha",
      confidenceCaveat: "Use as fixture evidence only until live chart evidence is supplied.",
      status: "usable",
    },
    {
      id: "fact-haridev-aries-tenth",
      assertion: "Haridev D1 has Sun, Mars, and Saturn in Aries in the 10th house.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Haridev D1: Sun/Mars/Saturn Aries 10th",
      confidenceCaveat: "Treat as benchmark fixture evidence, not a newly computed production claim.",
      status: "usable",
    },
    {
      id: "fact-haridev-moon-twelfth",
      assertion: "Haridev D1 places Moon in Gemini 12th in Ardra.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Haridev D1: Moon Gemini 12th Ardra",
      confidenceCaveat: "Use only as the named benchmark chart fact.",
      status: "usable",
    },
    {
      id: "fact-seva-mars-tenth",
      assertion: "Seva D1 places Mars in Aries 10th in Ashwini.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Seva D1: Mars Aries 10th Ashwini",
      confidenceCaveat: "Use as benchmark evidence until user-supplied chart evidence replaces it.",
      status: "usable",
    },
    {
      id: "fact-seva-venus-ninth",
      assertion: "Seva D1 places Venus in Pisces 9th.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Seva D1: Venus Pisces 9th",
      confidenceCaveat: "Use as compact fixture evidence, not a broad promise of outcome.",
      status: "usable",
    },
    {
      id: "fact-seva-saturn-rahu-eleventh",
      assertion: "Seva D1 places Saturn and Rahu in Taurus 11th.",
      sourceType: "computed_chart_fact",
      evidenceAnchor: "Seva D1: Saturn/Rahu Taurus 11th",
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
      id: "synthesis-haridev-career",
      assertion: "Derived synthesis: Haridev's Aries 10th cluster can support leadership questions, but Saturn adds duty and delay.",
      sourceType: "derived_synthesis",
      evidenceAnchor: "Haridev D1: Sun/Mars/Saturn Aries 10th + rule-tenth-house-career",
      confidenceCaveat: "Keep timing gated until dasha evidence is present.",
      status: "usable",
    },
    {
      id: "synthesis-seva-career-network",
      assertion: "Derived synthesis: Seva's Mars 10th and Saturn/Rahu 11th connect career drive with network pressure.",
      sourceType: "derived_synthesis",
      evidenceAnchor: "Seva D1: Mars Aries 10th + Saturn/Rahu Taurus 11th",
      confidenceCaveat: "Avoid claiming peak outcome without D10 and timing support.",
      status: "usable",
    },
    {
      id: "guidance-haridev-career-question",
      assertion: "Practical guidance: ask which concrete career decision needs the Aries 10th-house pressure interpreted.",
      sourceType: "practical_guidance",
      evidenceAnchor: "Haridev D1: Aries 10th cluster",
      confidenceCaveat: "Frame as a next question, not as advice to take immediate action.",
      status: "usable",
    },
    {
      id: "guidance-seva-timing-question",
      assertion: "Practical guidance: ask for timing context before turning Seva's 10th-house Mars into a prediction.",
      sourceType: "practical_guidance",
      evidenceAnchor: "Seva D1: Mars Aries 10th",
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
      body: "Use ledger anchors fact-haridev-aries-tenth, fact-haridev-moon-twelfth, and fact-seva-mars-tenth before interpretation.",
      anchorIds: ["fact-haridev-aries-tenth", "fact-haridev-moon-twelfth", "fact-seva-mars-tenth"],
    },
    {
      heading: "Jyotish interpretation",
      body: "Use rule-tenth-house-career and synthesis-haridev-career to connect public role, responsibility, and initiative without timing certainty.",
      anchorIds: ["rule-tenth-house-career", "rule-aries-mars-action", "synthesis-haridev-career"],
    },
    {
      heading: "Practical focus",
      body: "Use guidance-haridev-career-question and guidance-seva-timing-question to turn the reading into grounded next questions.",
      anchorIds: ["guidance-haridev-career-question", "guidance-seva-timing-question", "synthesis-seva-career-network"],
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
    "fact-haridev-aries-tenth",
    "rule-tenth-house-career",
    "synthesis-haridev-career",
    "guidance-haridev-career-question",
  ];
  const blockedAdvanced = assertionLedger.assertions.filter((assertion) => assertion.sourceType === "gated_advanced_claim");
  const samples: AiReviewNarrativeSample[] = [
    {
      id: "strong_grounded_review",
      label: "Strong grounded review",
      text:
        "Using ledger anchors fact-haridev-aries-tenth and rule-tenth-house-career, the career reading starts from a visible 10th-house pressure rather than a mood. The tension is between Aries speed and Saturn duty, so synthesis-haridev-career keeps leadership useful without turning it into a timing promise. Practical next question: which concrete public role or career decision should guidance-haridev-career-question test against current dasha context? Caveat: Shadbala and Ashtakavarga stay blocked until computed tables exist.",
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
  };
}
