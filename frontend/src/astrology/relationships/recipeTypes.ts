import type { EntityId } from "../entities";
import type { RelationshipFactorId } from "./factorTypes";
import type { RelationshipTypeId } from "./relationshipTypes";

export type RecipeWarning =
  | {
      type: "birth_time_accuracy";
      minimumAccuracy: "exact" | "approximate";
      affectedEntityIds: EntityId[];
    }
  | {
      type: "missing_source";
      ruleIds: string[];
    }
  | {
      type: "expert_only";
      entityIds: EntityId[];
    };

export type RecipeFocus = {
  primaryEntityIds: EntityId[];
  secondaryEntityIds: EntityId[];
  relationshipFactorIds: RelationshipFactorId[];
  requiredCalculationIds: string[];
  optionalCalculationIds: string[];
  ruleIds: string[];
  warnings: RecipeWarning[];
};

export type RelationshipRecipeStatus = "draft" | "needs_source" | "verified" | "disabled";
export type RelationshipUiMode = "novice" | "astrologer";

export type RelationshipRecipe = {
  id: string;
  version: number;
  relationshipTypeId: RelationshipTypeId;
  label: {
    ru: string;
    en: string;
  };
  status: RelationshipRecipeStatus;
  perspectiveAtoB: RecipeFocus;
  perspectiveBtoA: RecipeFocus;
  mutualFocus: RecipeFocus;
  visibleInModes: RelationshipUiMode[];
  sourcePolicy: {
    requireVerifiedRulesForNormalUi: boolean;
  };
};
