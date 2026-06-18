import type { ReportEvidenceItem, ReportEvidencePack } from "../reports";
import type { EvidenceProvenance, ProvenanceEnrichedReportEvidence } from "./provenanceResolver";

export type AiEligibilityStatus = "eligible" | "excluded" | "blocked";

export type AiEligibilityExclusionReason = "not_available" | "not_verified" | "needs_source" | "unsupported" | "partial" | "missing_citation_chain";

export type AiEligibleCitation = {
  ruleId: string;
  passageId: string;
  sourceId: string;
  citationLabel: string;
};

export type AiEligibleEvidenceItem = {
  evidenceItemId: string;
  label: string;
  kind: ReportEvidenceItem["kind"];
  entityId?: ReportEvidenceItem["entityId"];
  calculationId?: ReportEvidenceItem["calculationId"];
  relationshipFactorId?: ReportEvidenceItem["relationshipFactorId"];
  value: ReportEvidenceItem["value"];
  citations: AiEligibleCitation[];
};

export type AiExcludedEvidenceItem = {
  evidenceItemId: string;
  label: string;
  coverage: EvidenceProvenance["coverage"];
  reason: AiEligibilityExclusionReason;
};

export type AiEligibilitySummary = {
  totalItems: number;
  eligibleItems: number;
  excludedItems: number;
  blockedItems: number;
};

export type AiEligibilityPack = {
  schemaVersion: 1;
  reportEvidenceSchemaVersion: ReportEvidencePack["schemaVersion"];
  reportRecipeId: string;
  reportRecipeVersion: number;
  reportTypeId: ReportEvidencePack["reportTypeId"];
  mode: ReportEvidencePack["mode"];
  status: AiEligibilityStatus;
  eligibleItems: AiEligibleEvidenceItem[];
  excludedItems: AiExcludedEvidenceItem[];
  summary: AiEligibilitySummary;
  sourceEvidence: ProvenanceEnrichedReportEvidence;
};
