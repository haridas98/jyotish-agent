import type { RoleDefinition, RoleId } from "./roleTypes";

export const roleDefinitions: RoleDefinition[] = [
  role("self", "Я", "Self", "custom", false),
  role("father", "Отец", "Father", "family", true),
  role("mother", "Мать", "Mother", "family", true),
  role("parent", "Родитель", "Parent", "family", true),
  role("child", "Ребенок", "Child", "family", true),
  role("elder_sibling", "Старший брат или сестра", "Elder sibling", "family", true),
  role("younger_sibling", "Младший брат или сестра", "Younger sibling", "family", true),
  role("sibling", "Брат или сестра", "Sibling", "family", false),
  role("spouse", "Супруг", "Spouse", "romantic", false),
  role("romantic_partner", "Романтический партнер", "Romantic partner", "romantic", false),
  role("business_partner", "Бизнес-партнер", "Business partner", "business", false),
  role("boss", "Руководитель", "Boss", "work", true),
  role("subordinate", "Подчиненный", "Subordinate", "work", true),
  role("colleague", "Коллега", "Colleague", "work", false),
  role("guru", "Гуру", "Guru", "education", true),
  role("student", "Ученик", "Student", "education", true),
  role("friend", "Друг", "Friend", "social", false),
  role("opponent", "Оппонент", "Opponent", "conflict", false),
  role("client", "Клиент", "Client", "business", true),
  role("supplier", "Поставщик", "Supplier", "business", true),
  role("custom", "Своя роль", "Custom", "custom", true),
];

const roleMap = new Map(roleDefinitions.map((definition) => [definition.id, definition]));

export function getRole(id: RoleId): RoleDefinition | null {
  return roleMap.get(id) ?? null;
}

export function listRoles(): RoleDefinition[] {
  return roleDefinitions;
}

function role(id: RoleId, ru: string, en: string, category: RoleDefinition["category"], directional: boolean): RoleDefinition {
  return {
    id,
    label: { ru, en },
    category,
    directional,
  };
}
