import type { CalculationId } from "../calculations";
import type { EntityId } from "../entities";
import type { RelationshipFactorId, RelationshipUiMode } from "../relationships";
import type { ReportSectionId } from "./reportSectionTypes";
import type { LocalizedText, ReportTypeId } from "./reportTypeTypes";

export type ReportFactorPriority = "primary" | "secondary" | "optional";

export type ReportCondition =
  | {
      type: "birth_time_accuracy";
      scope: "primary_chart" | "both_relationship_charts";
      minimum: "exact" | "approximate";
    }
  | {
      type: "mode";
      allowed: RelationshipUiMode;
    }
  | {
      type: "relationship_selected";
      required: boolean;
    }
  | {
      type: "calculation_available";
      calculationId: CalculationId;
    };

export type ReportEntityFactor = {
  kind: "entity";
  entityId: EntityId;
  priority: ReportFactorPriority;
  visibleInModes: RelationshipUiMode[];
  conditions?: ReportCondition[];
};

export type ReportCalculationFactor = {
  kind: "calculation";
  calculationId: CalculationId;
  priority: ReportFactorPriority;
  required: boolean;
  visibleInModes: RelationshipUiMode[];
  conditions?: ReportCondition[];
};

export type ReportRelationshipContextFactor = {
  kind: "relationship_context";
  source: "selected_saved_relationship";
  recipeProjection: "summary" | "perspective_layers" | "mutual_only";
  required: boolean;
  visibleInModes: RelationshipUiMode[];
};

export type ReportFactorRef =
  | ReportEntityFactor
  | ReportCalculationFactor
  | ReportRelationshipContextFactor;

export type ReportFactorGroup = {
  id: string;
  label: LocalizedText;
  factors: ReportFactorRef[];
  visibleInModes: RelationshipUiMode[];
  defaultExpanded: boolean;
};

export type ReportRecipeSection = {
  sectionId: ReportSectionId;
  order: number;
  required: boolean;
  factorGroups: ReportFactorGroup[];
  visibleInModes: RelationshipUiMode[];
};

export type ReportRecipeStatus = "draft" | "needs_source" | "verified" | "disabled";

export type ReportRecipeWarning = {
  type: "birth_time_accuracy" | "needs_source";
  label: LocalizedText;
  visibleInModes: RelationshipUiMode[];
};

export type ReportRecipe = {
  id: ReportTypeId;
  version: number;
  reportTypeId: ReportTypeId;
  label: LocalizedText;
  shortDescription: LocalizedText;
  status: ReportRecipeStatus;
  sections: ReportRecipeSection[];
  warnings: ReportRecipeWarning[];
  sourcePolicy: {
    requireVerifiedRulesForGeneratedInterpretation: boolean;
  };
};

export type ResolvedReportFactor =
  | ReportEntityFactor
  | ReportCalculationFactor
  | ReportRelationshipContextFactor
  | {
      kind: "relationship_factor";
      relationshipFactorId: RelationshipFactorId;
      priority: ReportFactorPriority;
      visibleInModes: RelationshipUiMode[];
    };

export type ResolvedReportFactorGroup = Omit<ReportFactorGroup, "factors"> & {
  factors: ResolvedReportFactor[];
  emptyState?: LocalizedText;
};

export type ResolvedReportSection = Omit<ReportRecipeSection, "factorGroups"> & {
  label: LocalizedText;
  factorGroups: ResolvedReportFactorGroup[];
};

export type ResolvedReportWarning = ReportRecipeWarning;

export type UnavailableReportFactor = {
  factorId: string;
  reason: "calculation_unavailable" | "condition_not_met";
};

export type ResolvedReportRecipe = {
  recipeId: string;
  recipeVersion: number;
  reportTypeId: ReportTypeId;
  label: LocalizedText;
  shortDescription: LocalizedText;
  sections: ResolvedReportSection[];
  warnings: ResolvedReportWarning[];
  unavailableFactors: UnavailableReportFactor[];
};
