export type RelationshipFactorId =
  | "factor.overlay.planets_a_to_b"
  | "factor.overlay.planets_b_to_a"
  | "factor.overlay.houses_a_to_b"
  | "factor.overlay.houses_b_to_a"
  | "factor.moon.relationship"
  | "factor.lagna.relationship"
  | "factor.mutual.aspects"
  | "factor.dasha.overlap"
  | "factor.transit.context";

export type RelationshipFactorStatus = "implemented" | "planned" | "disabled";

export type RelationshipFactorDefinition = {
  id: RelationshipFactorId;
  label: {
    ru: string;
    en: string;
  };
  requiredCalculationIds: string[];
  status: RelationshipFactorStatus;
};
