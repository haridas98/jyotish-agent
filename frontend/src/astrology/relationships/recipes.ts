import type { RelationshipRecipe, RelationshipType } from "./types";

const sharedBase = [
  factor("relationship.moonRelationship", "Луна показывает эмоциональный ритм и бытовую совместимость.", "primary"),
  factor("relationship.lagnaRelationship", "Лагна показывает тело, темперамент и базовый способ взаимодействия.", "primary"),
  factor("relationship.dashaOverlap", "Пересечение даш показывает, какие темы активны у обоих людей сейчас.", "secondary"),
] satisfies RelationshipRecipe["sharedFactors"];

export const relationshipRecipes: Record<RelationshipType, RelationshipRecipe> = {
  father_child: {
    id: "father_child",
    label: "Отец и ребёнок",
    profileAFactors: [
      factor("house.9", "Для ребёнка 9 дом и Сурья являются главными указателями отца.", "primary"),
      factor("graha.SU", "Сурья является естественной каракой отца, авторитета и силы рода.", "primary"),
      factor("varga.D12", "D12 уточняет родительскую линию и наследственные темы.", "secondary"),
    ],
    profileBFactors: [
      factor("house.5", "Для отца 5 дом показывает детей и продолжение рода.", "primary"),
      factor("graha.JU", "Гуру поддерживает тему детей, защиты и наставления.", "secondary"),
      factor("varga.D7", "D7 используется для темы детей и продолжения рода.", "secondary"),
    ],
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D7", "D9", "D12"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.dualDashas", "block.compare.aiEvidence"],
  },
  mother_child: {
    id: "mother_child",
    label: "Мать и ребёнок",
    profileAFactors: [
      factor("house.4", "Для ребёнка 4 дом и Чандра являются главными указателями матери.", "primary"),
      factor("graha.MO", "Чандра является каракой матери, заботы и эмоциональной опоры.", "primary"),
      factor("varga.D12", "D12 уточняет родительскую линию и наследственные темы.", "secondary"),
    ],
    profileBFactors: [
      factor("house.5", "Для матери 5 дом показывает детей и заботу через продолжение рода.", "primary"),
      factor("graha.JU", "Гуру поддерживает тему детей и защиты.", "secondary"),
      factor("varga.D7", "D7 используется для темы детей.", "secondary"),
    ],
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D7", "D9", "D12"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.dualDashas", "block.compare.aiEvidence"],
  },
  siblings: {
    id: "siblings",
    label: "Братья и сёстры",
    profileAFactors: siblingFactors(),
    profileBFactors: siblingFactors(),
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D3", "D9"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.aiEvidence"],
  },
  spouse: {
    id: "spouse",
    label: "Супруги / партнёры",
    profileAFactors: spouseFactors("graha.VE"),
    profileBFactors: spouseFactors("graha.JU"),
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D9"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.dualDashas", "block.compare.aiEvidence"],
  },
  business_partner: {
    id: "business_partner",
    label: "Бизнес-партнёры",
    profileAFactors: businessFactors(),
    profileBFactors: businessFactors(),
    sharedFactors: [...sharedBase, factor("relationship.moneyRisk", "Финансы и доверие проверяются через 2/8/11 дома и текущие даши.", "primary")],
    requiredVargas: ["D1", "D9", "D10"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.businessFactors", "block.compare.moneyRisk", "block.compare.dualDashas", "block.compare.aiEvidence"],
  },
  boss_subordinate: {
    id: "boss_subordinate",
    label: "Начальник и подчинённый",
    profileAFactors: [
      factor("house.10", "10 дом показывает работу, власть, статус и видимый результат.", "primary"),
      factor("graha.SA", "Шани показывает иерархию, обязанность, давление и дисциплину.", "primary"),
      factor("varga.D10", "D10 уточняет профессиональный статус.", "primary"),
    ],
    profileBFactors: [
      factor("house.6", "6 дом показывает служение, работу, подчинение и конфликт.", "primary"),
      factor("house.10", "10 дом показывает карьеру и общественную роль.", "primary"),
      factor("varga.D10", "D10 уточняет профессиональный статус.", "primary"),
    ],
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D10"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.dualDashas", "block.compare.aiEvidence"],
  },
  colleague: {
    id: "colleague",
    label: "Коллеги",
    profileAFactors: businessFactors(),
    profileBFactors: businessFactors(),
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D10"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.aiEvidence"],
  },
  guru_student: {
    id: "guru_student",
    label: "Гуру и ученик",
    profileAFactors: [
      factor("house.9", "9 дом показывает гуру, дхарму и высшее руководство.", "primary"),
      factor("graha.JU", "Гуру является естественной каракой учителя, знания и защиты.", "primary"),
      factor("varga.D20", "D20 помогает рассматривать духовную практику.", "secondary"),
    ],
    profileBFactors: [
      factor("house.5", "5 дом поддерживает обучение, мантру и ученичество.", "primary"),
      factor("house.9", "9 дом показывает принятие наставления.", "primary"),
      factor("varga.D20", "D20 помогает рассматривать духовную практику.", "secondary"),
    ],
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D9", "D20"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.aiEvidence"],
  },
  custom: {
    id: "custom",
    label: "Своя роль",
    profileAFactors: [],
    profileBFactors: [],
    sharedFactors: sharedBase,
    requiredVargas: ["D1", "D9"],
    requiredDashas: ["vimshottari"],
    defaultBlocks: ["block.compare.sideBySideCharts", "block.compare.roleFactors", "block.compare.aiEvidence"],
  },
};

export function getRelationshipRecipe(id: RelationshipType): RelationshipRecipe {
  return relationshipRecipes[id];
}

function factor(entityId: string, reason: string, priority: "primary" | "secondary" | "supporting") {
  return { entityId, reason, priority };
}

function siblingFactors() {
  return [
    factor("house.3", "3 дом показывает младших братьев и сестёр, усилие и смелость.", "primary"),
    factor("house.11", "11 дом может показывать старших братьев и сестёр и поддержку.", "secondary"),
    factor("varga.D3", "D3 используется для темы братьев, сестёр и силы инициативы.", "primary"),
  ];
}

function spouseFactors(extraKaraka: string) {
  return [
    factor("house.7", "7 дом является главным домом брака, союза и договорённостей.", "primary"),
    factor("varga.D9", "D9 уточняет брак, дхарму и зрелость отношений.", "primary"),
    factor(extraKaraka, "Карака уточняет качество союза и ожидания от партнёрства.", "secondary"),
  ];
}

function businessFactors() {
  return [
    factor("house.7", "7 дом показывает договоры и партнёрство.", "primary"),
    factor("house.10", "10 дом показывает дело, статус и видимый результат.", "primary"),
    factor("house.11", "11 дом показывает прибыль и сеть поддержки.", "primary"),
    factor("house.2", "2 дом показывает деньги, речь и накопленный ресурс.", "secondary"),
    factor("house.8", "8 дом показывает общий риск, скрытые проблемы и кризисы.", "secondary"),
    factor("graha.ME", "Будха важен для торговли, расчёта и коммуникации.", "secondary"),
    factor("graha.SA", "Шани важен для обязательств, задержек и структуры.", "supporting"),
  ];
}
