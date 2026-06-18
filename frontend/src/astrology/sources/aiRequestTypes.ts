import type { AiEligibilityExclusionReason, AiEligibilityPack } from "./aiEligibilityTypes";

export type AiRequestCitationChain = {
  ruleId: string;
  passageId: string;
  sourceId: string;
  citationLabel: string;
};

export type AiReportRequestItem = {
  evidenceItemId: string;
  label: string;
  kind: AiEligibilityPack["eligibleItems"][number]["kind"];
  entityId?: string;
  calculationId?: string;
  relationshipFactorId?: string;
  citationChains: AiRequestCitationChain[];
};

export type AiReportExcludedSummary = {
  total: number;
  byReason: Partial<Record<AiEligibilityExclusionReason, number>>;
};

export type AiReportRequest = {
  schemaVersion: 1;
  reportEvidenceSchemaVersion: AiEligibilityPack["reportEvidenceSchemaVersion"];
  reportRecipeId: string;
  reportRecipeVersion: number;
  reportTypeId: AiEligibilityPack["reportTypeId"];
  mode: AiEligibilityPack["mode"];
  eligibleItemIds: string[];
  items: AiReportRequestItem[];
  citationChains: AiRequestCitationChain[];
  excludedSummary: AiReportExcludedSummary;
};
