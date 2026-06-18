import { getEntity, registerCoreEntities, type EntityId } from "../entities";
import { getRelationshipFactor, listRelationshipFactors } from "./factorRegistry";
import type { RelationshipFactorId } from "./factorTypes";
import { getRelationshipType, listRelationshipTypes } from "./relationshipTypeRegistry";
import { listRelationshipRecipes } from "./recipeRegistry";
import type { RecipeFocus, RelationshipRecipe } from "./recipeTypes";
import { getRole } from "./roleRegistry";

const registeredCalculationIds = new Set([
  "varga.D1",
  "varga.D2",
  "varga.D3",
  "varga.D4",
  "varga.D7",
  "varga.D9",
  "varga.D10",
  "varga.D12",
  "varga.D16",
  "varga.D20",
  "varga.D24",
  "varga.D27",
  "varga.D30",
  "varga.D40",
  "varga.D45",
  "varga.D60",
  "dasha.vimshottari",
  "transits.current",
]);

export type RelationshipValidationResult = {
  ok: boolean;
  errors: string[];
};

export function validateRelationshipRegistry(): RelationshipValidationResult {
  const errors: string[] = [];
  errors.push(...duplicateErrors("relationship type", listRelationshipTypes().map((item) => item.id)));
  errors.push(...duplicateErrors("relationship factor", listRelationshipFactors().map((item) => item.id)));
  errors.push(...duplicateErrors("relationship recipe", listRelationshipRecipes().map((item) => item.id)));

  for (const relationshipType of listRelationshipTypes()) {
    if (!getRole(relationshipType.roleA)) errors.push(`relationship ${relationshipType.id} has unknown roleA ${relationshipType.roleA}`);
    if (!getRole(relationshipType.roleB)) errors.push(`relationship ${relationshipType.id} has unknown roleB ${relationshipType.roleB}`);
  }

  for (const factor of listRelationshipFactors()) {
    for (const calculationId of factor.requiredCalculationIds) {
      if (!registeredCalculationIds.has(calculationId)) errors.push(`factor ${factor.id} uses unknown calculation ${calculationId}`);
    }
  }

  for (const recipe of listRelationshipRecipes()) {
    errors.push(...validateRelationshipRecipe(recipe).errors);
  }

  return { ok: errors.length === 0, errors };
}

export function validateRelationshipRecipe(recipe: RelationshipRecipe): RelationshipValidationResult {
  registerCoreEntities();

  const errors: string[] = [];
  const relationshipType = getRelationshipType(recipe.relationshipTypeId);
  if (!relationshipType) {
    errors.push(`recipe ${recipe.id} uses unknown relationshipTypeId ${recipe.relationshipTypeId}`);
  } else {
    if (!getRole(relationshipType.roleA)) errors.push(`recipe ${recipe.id} relationship roleA is unknown`);
    if (!getRole(relationshipType.roleB)) errors.push(`recipe ${recipe.id} relationship roleB is unknown`);
  }

  for (const [name, focus] of Object.entries({
    perspectiveAtoB: recipe.perspectiveAtoB,
    perspectiveBtoA: recipe.perspectiveBtoA,
    mutualFocus: recipe.mutualFocus,
  })) {
    errors.push(...validateFocus(recipe.id, name, focus));
  }

  if (!relationshipType?.symmetric && sameFocus(recipe.perspectiveAtoB, recipe.perspectiveBtoA)) {
    errors.push(`recipe ${recipe.id} asymmetric relationship must have distinct directed perspectives`);
  }

  if (recipe.status === "draft" && recipe.visibleInModes.includes("novice")) {
    errors.push(`recipe ${recipe.id} draft recipe is normal-ui-visible`);
  }

  if (recipe.status === "verified") {
    const warnings = collectWarnings(recipe);
    const hasMissingSource = warnings.some((warning) => warning.type === "missing_source");
    if (hasMissingSource) errors.push(`recipe ${recipe.id} verified recipe has missing source`);
    if (recipe.sourcePolicy.requireVerifiedRulesForNormalUi && collectRuleIds(recipe).length === 0) {
      errors.push(`recipe ${recipe.id} verified recipe has no source-backed rules`);
    }
  }

  const pendingMarker = ["source", "pending"].join(".");
  if (JSON.stringify(recipe).includes(pendingMarker)) errors.push(`recipe ${recipe.id} contains forbidden pending source marker`);
  if (hasLongInterpretiveText(recipe)) errors.push(`recipe ${recipe.id} contains long interpretive text`);

  return { ok: errors.length === 0, errors };
}

function validateFocus(recipeId: string, focusName: string, focus: RecipeFocus): string[] {
  const errors: string[] = [];
  for (const entityId of [...focus.primaryEntityIds, ...focus.secondaryEntityIds]) {
    if (!getEntity(entityId)) errors.push(`recipe ${recipeId} ${focusName} uses unknown entity ${entityId}`);
  }
  for (const factorId of focus.relationshipFactorIds) {
    if (!getRelationshipFactor(factorId)) errors.push(`recipe ${recipeId} ${focusName} uses unknown factor ${factorId}`);
  }
  for (const calculationId of [...focus.requiredCalculationIds, ...focus.optionalCalculationIds]) {
    if (!registeredCalculationIds.has(calculationId)) errors.push(`recipe ${recipeId} ${focusName} uses unknown calculation ${calculationId}`);
  }

  const duplicatePrimarySecondary = focus.primaryEntityIds.filter((entityId) => focus.secondaryEntityIds.includes(entityId));
  for (const entityId of duplicatePrimarySecondary) {
    errors.push(`recipe ${recipeId} ${focusName} duplicates entity in primary and secondary: ${entityId}`);
  }

  if (focus.requiredCalculationIds.includes("varga.D60")) errors.push(`recipe ${recipeId} ${focusName} D60 cannot be required`);
  if (focus.primaryEntityIds.includes("varga.D60")) errors.push(`recipe ${recipeId} ${focusName} D60 cannot be primary`);
  if (focus.secondaryEntityIds.includes("varga.D60") || focus.optionalCalculationIds.includes("varga.D60")) {
    const hasAccuracyWarning = focus.warnings.some(
      (warning) => warning.type === "birth_time_accuracy" && warning.affectedEntityIds.includes("varga.D60"),
    );
    const hasExpertWarning = focus.warnings.some((warning) => warning.type === "expert_only" && warning.entityIds.includes("varga.D60"));
    if (!hasAccuracyWarning) errors.push(`recipe ${recipeId} ${focusName} D60 needs birth-time warning`);
    if (!hasExpertWarning) errors.push(`recipe ${recipeId} ${focusName} D60 needs expert-only warning`);
  }

  for (const factorId of focus.relationshipFactorIds) {
    const factor = getRelationshipFactor(factorId as RelationshipFactorId);
    for (const calculationId of factor?.requiredCalculationIds ?? []) {
      if (!registeredCalculationIds.has(calculationId)) errors.push(`recipe ${recipeId} ${focusName} factor ${factorId} has unknown calculation ${calculationId}`);
    }
  }

  return errors;
}

function duplicateErrors(label: string, ids: string[]): string[] {
  const seen = new Set<string>();
  const errors: string[] = [];
  for (const id of ids) {
    if (seen.has(id)) errors.push(`duplicate ${label} id: ${id}`);
    seen.add(id);
  }
  return errors;
}

function sameFocus(a: RecipeFocus, b: RecipeFocus): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

function collectWarnings(recipe: RelationshipRecipe) {
  return [...recipe.perspectiveAtoB.warnings, ...recipe.perspectiveBtoA.warnings, ...recipe.mutualFocus.warnings];
}

function collectRuleIds(recipe: RelationshipRecipe): string[] {
  return [...recipe.perspectiveAtoB.ruleIds, ...recipe.perspectiveBtoA.ruleIds, ...recipe.mutualFocus.ruleIds];
}

function hasLongInterpretiveText(recipe: RelationshipRecipe): boolean {
  const values = [recipe.label.ru, recipe.label.en];
  return values.some((value) => value.length > 90 || /несовместим|конфликтн|будут счастливы|кармическая связь/i.test(value));
}
