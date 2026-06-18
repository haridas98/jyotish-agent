import type { RoleCategory, RoleId } from "./roleTypes";

export type RelationshipTypeId =
  | "father_child"
  | "mother_child"
  | "parent_child"
  | "elder_younger_sibling"
  | "siblings"
  | "spouses"
  | "romantic_partners"
  | "business_partners"
  | "boss_subordinate"
  | "colleagues"
  | "guru_student"
  | "friends"
  | "opponents"
  | "client_supplier"
  | "custom";

export type RelationshipTypeDefinition = {
  id: RelationshipTypeId;
  label: {
    ru: string;
    en: string;
  };
  roleA: RoleId;
  roleB: RoleId;
  category: RoleCategory;
  symmetric: boolean;
};
