export type RelationshipType =
  | "father_child"
  | "mother_child"
  | "siblings"
  | "spouse"
  | "business_partner"
  | "boss_subordinate"
  | "colleague"
  | "guru_student"
  | "custom";

export type RelationshipFactorDefinition = {
  entityId: string;
  reason: string;
  priority: "primary" | "secondary" | "supporting";
};

export type RelationshipRecipe = {
  id: RelationshipType;
  label: string;
  profileAFactors: RelationshipFactorDefinition[];
  profileBFactors: RelationshipFactorDefinition[];
  sharedFactors: RelationshipFactorDefinition[];
  requiredVargas: string[];
  requiredDashas: string[];
  defaultBlocks: string[];
};
