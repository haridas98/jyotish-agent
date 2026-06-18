import type { CalculationId } from "../calculations";
import type { EntityId } from "../entities";
import type { RelationshipFactorId, RelationshipTypeId, RelationshipUiMode } from "../relationships";
import type { ReportFactorPriority, ResolvedReportRecipe } from "./reportRecipeTypes";
import type { ReportTypeId } from "./reportTypeTypes";

export type ReportEvidenceItemKind = "entity" | "calculation" | "relationship_factor" | "warning";

export type ReportEvidenceSourceRef = {
  sourceId: string;
  ruleId: string;
  entityId?: EntityId;
  status: "verified" | "needs_review";
};

export type ReportEvidenceProvenance = {
  origin: "report_recipe" | "relationship_recipe" | "chart_calculation" | "report_policy";
  reportRecipeId: string;
  reportRecipeVersion: number;
  reportTypeId: ReportTypeId;
  sectionId?: string;
  groupId?: string;
  relationshipTypeId?: RelationshipTypeId;
  ruleIds: string[];
  sourceRefs: ReportEvidenceSourceRef[];
};

export type ReportEvidenceItem = {
  id: string;
  kind: ReportEvidenceItemKind;
  label: string;
  priority: ReportFactorPriority | "warning";
  entityId?: EntityId;
  calculationId?: CalculationId;
  relationshipFactorId?: RelationshipFactorId;
  value: unknown;
  available: boolean;
  provenance: ReportEvidenceProvenance;
  warnings: string[];
};

export type ReportEvidencePack = {
  schemaVersion: 1;
  reportRecipeId: string;
  reportRecipeVersion: number;
  reportTypeId: ReportTypeId;
  mode: RelationshipUiMode;
  profileIds: string[];
  relationshipId?: string;
  relationshipTypeId?: RelationshipTypeId;
  items: ReportEvidenceItem[];
  warnings: string[];
  unavailableItemIds: string[];
  sourceRefs: ReportEvidenceSourceRef[];
  inputSummary: {
    hasPrimaryChart: boolean;
    hasRelationshipContext: boolean;
    resolvedSectionCount: number;
    resolvedFactorCount: number;
  };
};

export type ReportEvidenceBuilderInput = {
  resolvedRecipe: ResolvedReportRecipe;
  mode: RelationshipUiMode;
  primaryChart?: unknown;
  primaryProfileId?: string | number | null;
  selectedRelationship?: {
    id?: string | number | null;
    relationshipTypeId: RelationshipTypeId;
    chartAId?: string | number | null;
    chartBId?: string | number | null;
  } | null;
};
