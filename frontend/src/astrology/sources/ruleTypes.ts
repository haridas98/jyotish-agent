import type { CalculationId } from "../calculations";
import type { EntityId } from "../entities";
import type { PassageId } from "./passageTypes";

export type RuleId = string;

export type RuleCondition =
  | {
      type: "entity_present";
      entityId: EntityId;
    }
  | {
      type: "graha_in_house";
      grahaId: EntityId;
      houseId: EntityId;
    }
  | {
      type: "graha_in_rashi";
      grahaId: EntityId;
      rashiId: EntityId;
    }
  | {
      type: "calculation_available";
      calculationId: CalculationId;
    }
  | {
      type: "birth_time_accuracy";
      minimum: "exact" | "approximate";
    };

export type RuleDefinition = {
  id: RuleId;
  label: {
    ru: string;
    en: string;
  };
  domain: "graha" | "house" | "rashi" | "nakshatra" | "varga" | "dasha" | "yoga" | "relationship" | "strength" | "transit";
  appliesToEntityIds: EntityId[];
  requiredCalculationIds: CalculationId[];
  conditions: RuleCondition[];
  passageIds: PassageId[];
  status: "draft" | "needs_source" | "verified" | "disputed" | "disabled";
  interpretationPolicy: "direct" | "conditional" | "context_only";
  notes?: string;
};
