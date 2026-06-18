export type RoleId =
  | "self"
  | "father"
  | "mother"
  | "parent"
  | "child"
  | "elder_sibling"
  | "younger_sibling"
  | "sibling"
  | "spouse"
  | "romantic_partner"
  | "business_partner"
  | "boss"
  | "subordinate"
  | "colleague"
  | "guru"
  | "student"
  | "friend"
  | "opponent"
  | "client"
  | "supplier"
  | "custom";

export type RoleCategory = "family" | "romantic" | "business" | "work" | "education" | "social" | "conflict" | "custom";

export type RoleDefinition = {
  id: RoleId;
  label: {
    ru: string;
    en: string;
    sa?: string;
  };
  category: RoleCategory;
  directional: boolean;
};
