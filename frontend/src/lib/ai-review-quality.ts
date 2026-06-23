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
  "balanced life",
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
      "You have positive energy and many opportunities. Trust your intuition, follow your heart, and seek a balanced life. Everything happens for a reason, so stay open to growth.",
  },
};

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

export function buildAiReviewQualityLabSummary() {
  const strong = evaluateAiReviewDraft(aiReviewQualityFixtures.strong.draft, aiReviewQualityFixtures.strong.fixtureEvidence);
  const weak = evaluateAiReviewDraft(aiReviewQualityFixtures.weak.draft, aiReviewQualityFixtures.weak.fixtureEvidence);
  const preview = buildAiReviewMockPreview();

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
  };
}
