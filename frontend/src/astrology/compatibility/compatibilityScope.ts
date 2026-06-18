import { getRelationshipRecipe, getRelationshipType, type RelationshipTypeId } from "@/astrology/relationships";

export const compatibilityScope = {
  relationshipTypeIds: ["spouses", "romantic_partners"] as const,
};

export type CompatibilityRelationshipTypeId = (typeof compatibilityScope.relationshipTypeIds)[number];

export function isCompatibilityRelationshipTypeId(value: string): value is CompatibilityRelationshipTypeId {
  return compatibilityScope.relationshipTypeIds.includes(value as CompatibilityRelationshipTypeId);
}

export function listCompatibilityRelationshipTypes() {
  return compatibilityScope.relationshipTypeIds
    .map((id) => getRelationshipType(id))
    .filter((item): item is NonNullable<typeof item> => Boolean(item));
}

export function listCompatibilityRecipes(mode: "novice" | "astrologer") {
  return compatibilityScope.relationshipTypeIds
    .map((id) => getRelationshipRecipe(id))
    .filter((recipe): recipe is NonNullable<typeof recipe> => {
      if (!recipe) return false;
      if (recipe.status === "disabled") return false;
      if (mode !== "astrologer" && recipe.status === "draft") return false;
      return recipe.visibleInModes.includes(mode);
    });
}

export function validateCompatibilityScope(): string[] {
  const errors: string[] = [];
  for (const id of compatibilityScope.relationshipTypeIds) {
    if (!getRelationshipType(id as RelationshipTypeId)) errors.push(`Missing relationship type: ${id}`);
    if (!getRelationshipRecipe(id)) errors.push(`Missing relationship recipe: ${id}`);
  }
  return errors;
}
