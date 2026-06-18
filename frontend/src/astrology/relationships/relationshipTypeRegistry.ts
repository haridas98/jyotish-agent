import type { RelationshipTypeDefinition, RelationshipTypeId } from "./relationshipTypes";

export const relationshipTypeDefinitions: RelationshipTypeDefinition[] = [
  relationship("father_child", "Отец и ребенок", "Father and child", "father", "child", "family", false),
  relationship("mother_child", "Мать и ребенок", "Mother and child", "mother", "child", "family", false),
  relationship("parent_child", "Родитель и ребенок", "Parent and child", "parent", "child", "family", false),
  relationship("elder_younger_sibling", "Старший и младший", "Elder and younger sibling", "elder_sibling", "younger_sibling", "family", false),
  relationship("siblings", "Братья и сестры", "Siblings", "sibling", "sibling", "family", true),
  relationship("spouses", "Супруги", "Spouses", "spouse", "spouse", "romantic", true),
  relationship("romantic_partners", "Романтические партнеры", "Romantic partners", "romantic_partner", "romantic_partner", "romantic", true),
  relationship("business_partners", "Бизнес-партнеры", "Business partners", "business_partner", "business_partner", "business", true),
  relationship("boss_subordinate", "Руководитель и подчиненный", "Boss and subordinate", "boss", "subordinate", "work", false),
  relationship("colleagues", "Коллеги", "Colleagues", "colleague", "colleague", "work", true),
  relationship("guru_student", "Гуру и ученик", "Guru and student", "guru", "student", "education", false),
  relationship("friends", "Друзья", "Friends", "friend", "friend", "social", true),
  relationship("opponents", "Оппоненты", "Opponents", "opponent", "opponent", "conflict", true),
  relationship("client_supplier", "Клиент и поставщик", "Client and supplier", "client", "supplier", "business", false),
  relationship("custom", "Своя связь", "Custom relationship", "custom", "custom", "custom", false),
];

const relationshipTypeMap = new Map(relationshipTypeDefinitions.map((definition) => [definition.id, definition]));

export function getRelationshipType(id: RelationshipTypeId): RelationshipTypeDefinition | null {
  return relationshipTypeMap.get(id) ?? null;
}

export function listRelationshipTypes(): RelationshipTypeDefinition[] {
  return relationshipTypeDefinitions;
}

function relationship(
  id: RelationshipTypeId,
  ru: string,
  en: string,
  roleA: RelationshipTypeDefinition["roleA"],
  roleB: RelationshipTypeDefinition["roleB"],
  category: RelationshipTypeDefinition["category"],
  symmetric: boolean,
): RelationshipTypeDefinition {
  return {
    id,
    label: { ru, en },
    roleA,
    roleB,
    category,
    symmetric,
  };
}
