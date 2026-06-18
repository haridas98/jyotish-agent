import { registerExistingChartCalculationModules } from "../calculations";
import { hasCalculationModule } from "../calculations/registry";
import { registerCoreEntities, getEntity } from "../entities";
import { listRelationshipRecipes } from "../relationships";
import { validateD60Factor } from "./reportAccuracyPolicy";
import { reportRecipeDefinitions } from "./reportRecipeRegistry";
import type { ReportCalculationFactor, ReportFactorRef, ReportRecipe } from "./reportRecipeTypes";
import { reportSectionDefinitions } from "./reportSectionRegistry";
import { reportTypeDefinitions } from "./reportTypeRegistry";

const allowedRelationshipProjections = new Set(["summary", "perspective_layers", "mutual_only"]);

function duplicateValues(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

function factorKey(factor: ReportFactorRef): string {
  if (factor.kind === "entity") return `entity:${factor.entityId}`;
  if (factor.kind === "calculation") return `calculation:${factor.calculationId}`;
  return `relationship_context:${factor.source}:${factor.recipeProjection}`;
}

export function validateReportTypeRegistry(): string[] {
  const errors: string[] = [];
  const ids = reportTypeDefinitions.map((definition) => definition.id);
  for (const id of duplicateValues(ids)) errors.push(`Duplicate report type id: ${id}`);
  for (const definition of reportTypeDefinitions) {
    if (!definition.label.ru || !definition.label.en) errors.push(`Report type ${definition.id} needs labels`);
    if (definition.status === "active" && !definition.visibleInModes.length) errors.push(`Report type ${definition.id} must be visible in a mode`);
  }
  return errors;
}

export function validateReportSectionRegistry(): string[] {
  const errors: string[] = [];
  const ids = reportSectionDefinitions.map((definition) => definition.id);
  for (const id of duplicateValues(ids)) errors.push(`Duplicate report section id: ${id}`);
  for (const definition of reportSectionDefinitions) {
    if (!definition.label.ru || !definition.label.en) errors.push(`Report section ${definition.id} needs labels`);
  }
  return errors;
}

export function validateReportRecipe(recipe: ReportRecipe): string[] {
  registerCoreEntities();
  registerExistingChartCalculationModules();

  const errors: string[] = [];
  const reportTypeIds = new Set(reportTypeDefinitions.map((definition) => definition.id));
  const sectionIds = new Set(reportSectionDefinitions.map((definition) => definition.id));
  const sectionOrders = recipe.sections.map((section) => String(section.order));

  if (!reportTypeIds.has(recipe.reportTypeId)) errors.push(`Recipe ${recipe.id} references unknown report type ${recipe.reportTypeId}`);
  for (const duplicateOrder of duplicateValues(sectionOrders)) errors.push(`Recipe ${recipe.id} has duplicate section order ${duplicateOrder}`);

  for (const section of recipe.sections) {
    if (!sectionIds.has(section.sectionId)) errors.push(`Recipe ${recipe.id} references unknown section ${section.sectionId}`);
    const sectionFactors = section.factorGroups.flatMap((group) => group.factors);
    if (section.required && sectionFactors.length > 0 && sectionFactors.every((factor) => "priority" in factor && factor.priority === "optional")) {
      errors.push(`Required section ${section.sectionId} cannot contain only optional factors`);
    }
    for (const group of section.factorGroups) {
      const keys = group.factors.map(factorKey);
      for (const duplicateKey of duplicateValues(keys)) errors.push(`Group ${group.id} has duplicate factor ${duplicateKey}`);

      const primaryKeys = new Set(group.factors.filter((factor) => "priority" in factor && factor.priority === "primary").map(factorKey));
      const secondaryKeys = new Set(group.factors.filter((factor) => "priority" in factor && factor.priority === "secondary").map(factorKey));
      for (const primaryKey of primaryKeys) {
        if (secondaryKeys.has(primaryKey)) errors.push(`Group ${group.id} has factor as primary and secondary: ${primaryKey}`);
      }

      for (const factor of group.factors) {
        if (factor.kind === "entity" && !getEntity(factor.entityId)) errors.push(`Unknown entity factor: ${factor.entityId}`);
        if (factor.kind === "calculation") {
          if (!hasCalculationModule(factor.calculationId)) errors.push(`Unknown calculation factor: ${factor.calculationId}`);
          errors.push(...validateD60Factor(factor as ReportCalculationFactor));
        }
        if (factor.kind === "relationship_context" && !allowedRelationshipProjections.has(factor.recipeProjection)) {
          errors.push(`Unsupported relationship projection: ${factor.recipeProjection}`);
        }
      }
    }
  }

  const serialized = JSON.stringify(recipe);
  const forbiddenMarkers = ["source" + ".pending", "AI prompt", "interpretation", "chartId", "relationshipId"];
  for (const forbidden of forbiddenMarkers) {
    if (serialized.includes(forbidden)) errors.push(`Recipe ${recipe.id} contains forbidden marker ${forbidden}`);
  }

  return errors;
}

export function validateReportRecipeRegistry(): string[] {
  const errors: string[] = [];
  const ids = reportRecipeDefinitions.map((recipe) => recipe.id);
  for (const id of duplicateValues(ids)) errors.push(`Duplicate report recipe id: ${id}`);

  const activeReportTypeIds = reportTypeDefinitions.filter((definition) => definition.status === "active").map((definition) => definition.id);
  for (const reportTypeId of activeReportTypeIds) {
    if (!reportRecipeDefinitions.some((recipe) => recipe.reportTypeId === reportTypeId && recipe.status !== "disabled")) {
      errors.push(`Active report type ${reportTypeId} has no recipe`);
    }
  }

  for (const recipe of reportRecipeDefinitions) errors.push(...validateReportRecipe(recipe));

  // Keep a runtime dependency on the relationship registry without copying its recipe content.
  if (!listRelationshipRecipes().length) errors.push("Relationship Recipe Registry is unavailable");

  return errors;
}
