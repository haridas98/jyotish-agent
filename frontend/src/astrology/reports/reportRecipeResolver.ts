import { getRelationshipRecipe, type RelationshipRecipe, type RelationshipTypeId, type RelationshipUiMode } from "../relationships";
import { getReportRecipe } from "./reportRecipeRegistry";
import type {
  ReportCondition,
  ReportFactorRef,
  ReportRelationshipContextFactor,
  ResolvedReportFactor,
  ResolvedReportFactorGroup,
  ResolvedReportRecipe,
  UnavailableReportFactor,
} from "./reportRecipeTypes";
import type { ReportTypeId } from "./reportTypeTypes";
import { getReportSection } from "./reportSectionRegistry";
import { isVisibleInMode } from "./reportModePolicy";

type SelectedRelationshipContext = {
  relationshipTypeId: RelationshipTypeId;
  deleted?: boolean;
} | null;

export type ResolveReportRecipeInput = {
  reportTypeId: ReportTypeId;
  mode: RelationshipUiMode;
  primaryBirthTimeAccuracy?: string | null;
  selectedRelationship?: SelectedRelationshipContext;
  availableCalculations?: string[];
};

function conditionMet(condition: ReportCondition, input: ResolveReportRecipeInput): boolean {
  if (condition.type === "mode") return condition.allowed === input.mode;
  if (condition.type === "relationship_selected") return condition.required ? Boolean(input.selectedRelationship && !input.selectedRelationship.deleted) : true;
  if (condition.type === "calculation_available") return input.availableCalculations?.includes(condition.calculationId) ?? true;
  if (condition.type === "birth_time_accuracy") {
    if (condition.minimum === "exact") return input.primaryBirthTimeAccuracy === "exact";
    return input.primaryBirthTimeAccuracy === "exact" || input.primaryBirthTimeAccuracy === "approximate";
  }
  return true;
}

function factorVisible(factor: ReportFactorRef, input: ResolveReportRecipeInput): boolean {
  if (!isVisibleInMode(factor.visibleInModes, input.mode)) return false;
  if (factor.kind === "relationship_context") return true;
  return (factor.conditions ?? []).every((condition) => conditionMet(condition, input));
}

function calculationUnavailable(factor: ReportFactorRef, input: ResolveReportRecipeInput): UnavailableReportFactor | null {
  if (factor.kind !== "calculation") return null;
  if (!input.availableCalculations) return null;
  if (input.availableCalculations.includes(factor.calculationId)) return null;
  return { factorId: factor.calculationId, reason: "calculation_unavailable" };
}

function relationshipProjection(
  factor: ReportRelationshipContextFactor,
  input: ResolveReportRecipeInput,
): { factors: ResolvedReportFactor[]; recipe: RelationshipRecipe | null } {
  if (!input.selectedRelationship || input.selectedRelationship.deleted) return { factors: [], recipe: null };
  const recipe = getRelationshipRecipe(input.selectedRelationship.relationshipTypeId);
  if (!recipe) return { factors: [], recipe: null };

  const projectedFactorIds =
    factor.recipeProjection === "mutual_only"
      ? recipe.mutualFocus.relationshipFactorIds
      : factor.recipeProjection === "perspective_layers"
        ? [
            ...recipe.perspectiveAtoB.relationshipFactorIds,
            ...recipe.perspectiveBtoA.relationshipFactorIds,
            ...recipe.mutualFocus.relationshipFactorIds,
          ]
        : recipe.mutualFocus.relationshipFactorIds.slice(0, 3);

  return {
    recipe,
    factors: Array.from(new Set(projectedFactorIds)).map((relationshipFactorId) => ({
      kind: "relationship_factor",
      relationshipFactorId,
      priority: "secondary",
      visibleInModes: factor.visibleInModes,
    })),
  };
}

export function resolveReportRecipe(input: ResolveReportRecipeInput): ResolvedReportRecipe {
  const recipe = getReportRecipe(input.reportTypeId) ?? getReportRecipe("personal_overview");
  if (!recipe) throw new Error(`Report recipe not found: ${input.reportTypeId}`);

  const unavailableFactors: UnavailableReportFactor[] = [];
  const sections = recipe.sections
    .filter((section) => isVisibleInMode(section.visibleInModes, input.mode))
    .sort((a, b) => a.order - b.order)
    .map((section) => {
      const sectionDefinition = getReportSection(section.sectionId);
      const factorGroups: ResolvedReportFactorGroup[] = section.factorGroups
        .filter((group) => isVisibleInMode(group.visibleInModes, input.mode))
        .map((group) => {
          const resolvedFactors: ResolvedReportFactor[] = [];
          let relationshipContextFound = false;

          for (const factor of group.factors) {
            const unavailable = calculationUnavailable(factor, input);
            if (unavailable) unavailableFactors.push(unavailable);
            if (!factorVisible(factor, input) || unavailable) continue;
            if (factor.kind === "relationship_context") {
              const projection = relationshipProjection(factor, input);
              relationshipContextFound = true;
              resolvedFactors.push(...projection.factors);
            } else {
              resolvedFactors.push(factor);
            }
          }

          return {
            ...group,
            factors: resolvedFactors,
            emptyState:
              relationshipContextFound && resolvedFactors.length === 0
                ? {
                    ru: "\u0421\u0432\u044f\u0437\u044c \u043d\u0435 \u0432\u044b\u0431\u0440\u0430\u043d\u0430. \u041e\u0442\u0447\u0451\u0442 \u0431\u0443\u0434\u0435\u0442 \u0441\u0442\u0440\u043e\u0438\u0442\u044c\u0441\u044f \u0442\u043e\u043b\u044c\u043a\u043e \u0432\u043e\u043a\u0440\u0443\u0433 \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u043a\u0430\u0440\u0442\u044b.",
                    en: "No relationship selected. The report will be built around the primary chart only.",
                  }
                : undefined,
          };
        });

      return {
        ...section,
        label: sectionDefinition?.label ?? { ru: section.sectionId, en: section.sectionId },
        factorGroups,
      };
    });

  return {
    recipeId: recipe.id,
    recipeVersion: recipe.version,
    reportTypeId: recipe.reportTypeId,
    label: recipe.label,
    shortDescription: recipe.shortDescription,
    sections,
    warnings: recipe.warnings.filter((warning) => isVisibleInMode(warning.visibleInModes, input.mode)),
    unavailableFactors,
  };
}
