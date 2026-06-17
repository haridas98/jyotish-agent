import type { CalculationId, CalculationPreset, CalculationWarning } from "@/astrology/calculations/types";

export type AiEvidenceSubject = "single_chart" | "relationship" | "period" | "event";
export type AiFactorRelevance = "primary" | "secondary" | "supporting" | "contradicting";

export type SourceRuleRef = {
  sourceId: string;
  ruleId: string;
  entityId?: string;
  status: "verified" | "pending" | "needs_review";
};

export type AiFactor = {
  entityId: string;
  calcId: CalculationId;
  value: unknown;
  relevance: AiFactorRelevance;
  reason: string;
  sourceRuleIds?: string[];
};

export type AiEvidencePack = {
  subject: AiEvidenceSubject;
  profiles: string[];
  question: string;
  calculationPreset: CalculationPreset;
  factors: AiFactor[];
  warnings: CalculationWarning[];
  sourceRules: SourceRuleRef[];
};

export type EvidenceBuilderContext = {
  profileIds: string[];
  question: string;
  preset?: CalculationPreset;
};
