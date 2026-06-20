import type { AiEligibilityPack, AiReportRequest, MockAiDryRunResult } from "../sources";

export const AI_HUMAN_REVIEW_WORKSPACE_SCHEMA_VERSION = "jyotish-ai-human-review-workspace-v1" as const;

export type AiHumanReviewWorkspaceStatus = "review_ready" | "blocked";

export type AiHumanReviewCitationReviewItem = {
  evidenceItemId: string;
  labels: string[];
};

export type AiHumanReviewItem = {
  id: string;
  label: string;
  body: string;
  confidence: string;
  evidenceItemIds: string[];
  citationLabels: AiHumanReviewCitationReviewItem[];
};

export type AiHumanReviewWorkspace = {
  schemaVersion: typeof AI_HUMAN_REVIEW_WORKSPACE_SCHEMA_VERSION;
  status: AiHumanReviewWorkspaceStatus;
  provider: "mock";
  gateSummary: {
    requestSchemaVersion: number;
    responseSchemaVersion: number;
    reportTypeId: string;
    reportRecipeId: string;
  };
  evidenceSummary: {
    eligibleCount: number;
    excludedCount: number;
    blockedCount: number;
  };
  validationSummary: {
    passed: boolean;
    errors: string[];
  };
  safetyFlags: {
    offlineMockOnly: true;
    realProviderCalled: false;
    rawContentStored: false;
    safeForInternalReview: boolean;
  };
  reviewItems: AiHumanReviewItem[];
};

export function buildAiHumanReviewWorkspace(input: {
  eligibility: AiEligibilityPack;
  request: AiReportRequest;
  dryRun: MockAiDryRunResult;
}): AiHumanReviewWorkspace {
  const { eligibility, request, dryRun } = input;
  const reviewItems = dryRun.response.theses.map((thesis, index) => {
    const citationLabelsByEvidence = new Map<string, Set<string>>();

    for (const citation of thesis.citations) {
      const labels = citationLabelsByEvidence.get(citation.evidenceItemId) ?? new Set<string>();
      labels.add(citation.citationLabel);
      citationLabelsByEvidence.set(citation.evidenceItemId, labels);
    }

    return {
      id: thesis.id,
      label: `Тезис ${index + 1}`,
      body: thesis.body,
      confidence: thesis.confidence,
      evidenceItemIds: [...thesis.evidenceItemIds],
      citationLabels: [...citationLabelsByEvidence.entries()].map(([evidenceItemId, labels]) => ({
        evidenceItemId,
        labels: [...labels].sort((a, b) => a.localeCompare(b)),
      })),
    };
  });

  const validationPassed = dryRun.validation.ok;
  const hasReviewItems = reviewItems.length > 0;

  return {
    schemaVersion: AI_HUMAN_REVIEW_WORKSPACE_SCHEMA_VERSION,
    status: validationPassed && hasReviewItems ? "review_ready" : "blocked",
    provider: dryRun.response.provider,
    gateSummary: {
      requestSchemaVersion: request.schemaVersion,
      responseSchemaVersion: dryRun.response.schemaVersion,
      reportTypeId: request.reportTypeId,
      reportRecipeId: request.reportRecipeId,
    },
    evidenceSummary: {
      eligibleCount: request.items.length,
      excludedCount: request.excludedSummary.total,
      blockedCount: eligibility.summary.blockedItems,
    },
    validationSummary: {
      passed: validationPassed,
      errors: [...dryRun.validation.errors],
    },
    safetyFlags: {
      offlineMockOnly: true,
      realProviderCalled: false,
      rawContentStored: false,
      safeForInternalReview: validationPassed && hasReviewItems,
    },
    reviewItems,
  };
}
