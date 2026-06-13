export type RelationshipRoleDefinition = {
  key: string;
  label: string;
  focus: string;
  houses: number[];
  vargas: string[];
  promptHint: string;
};

export const relationshipRoleDefinitions: RelationshipRoleDefinition[] = [
  {
    key: "partner",
    label: "Партнёр",
    focus: "брак, договорённости, близость",
    houses: [1, 7, 2, 8, 12],
    vargas: ["D1", "D9", "D7", "D12"],
    promptHint: "читать как совместимость пары: 7 дом, Шукра/Мангала, D9, семейные ценности и текущие даши",
  },
  {
    key: "father",
    label: "Отец",
    focus: "род, наставление, авторитет",
    houses: [1, 9, 10, 4],
    vargas: ["D1", "D9", "D12", "D60"],
    promptHint: "читать как связь с отцом: 9 дом, Солнце, дхарма, авторитет, родовая поддержка",
  },
  {
    key: "mother",
    label: "Мать",
    focus: "забота, дом, эмоциональная опора",
    houses: [1, 4, 9, 12],
    vargas: ["D1", "D9", "D12", "D60"],
    promptHint: "читать как связь с матерью: 4 дом, Луна, эмоциональная опора, дом и родовая линия",
  },
  {
    key: "sibling",
    label: "Брат/сестра",
    focus: "поддержка, соперничество, коммуникация",
    houses: [1, 3, 11, 6],
    vargas: ["D1", "D3", "D9"],
    promptHint: "читать как взаимодействие с братом или сестрой: 3 дом, инициатива, поддержка, конкуренция",
  },
  {
    key: "brother",
    label: "Брат",
    focus: "инициатива, защита, соперничество и поддержка",
    houses: [1, 3, 11, 6],
    vargas: ["D1", "D3", "D9"],
    promptHint: "читать как взаимодействие с братом: 3 дом, Марс, инициатива, соперничество, защита и поддержка",
  },
  {
    key: "sister",
    label: "Сестра",
    focus: "эмоциональная связь, поддержка и бытовая коммуникация",
    houses: [1, 3, 11, 4],
    vargas: ["D1", "D3", "D9"],
    promptHint: "читать как взаимодействие с сестрой: 3 дом, Луна/Венера, эмоциональная связь, поддержка и бытовая коммуникация",
  },
  {
    key: "boss",
    label: "Руководитель",
    focus: "карьера, власть, ответственность",
    houses: [1, 10, 6, 9],
    vargas: ["D1", "D10", "D9"],
    promptHint: "читать как рабочую иерархию: 10 дом, 6 дом, статус, обязанности и границы",
  },
  {
    key: "subordinate",
    label: "Подчинённый",
    focus: "делегирование, служение, рабочая динамика",
    houses: [1, 6, 10, 11],
    vargas: ["D1", "D10", "D9"],
    promptHint: "читать как управление и сотрудничество: 6 дом служения, 10 дом роли, 11 дом результата",
  },
  {
    key: "opponent",
    label: "Оппонент",
    focus: "конфликты, долги, скрытые напряжения",
    houses: [1, 6, 7, 8],
    vargas: ["D1", "D6", "D10", "D60"],
    promptHint: "читать как конфликтное взаимодействие: 6 дом споров, 7 дом открытого противостояния, 8 дом кризисов",
  },
  {
    key: "other",
    label: "Другая роль",
    focus: "общая динамика контакта",
    houses: [1, 7],
    vargas: ["D1", "D9"],
    promptHint: "читать как общий ракурс взаимодействия: лагна, 7 дом, Луна, текущие даши и контекст вопроса",
  },
];

export function relationshipRoleFor(key: string | null | undefined): RelationshipRoleDefinition {
  return relationshipRoleDefinitions.find((role) => role.key === key) ?? relationshipRoleDefinitions[relationshipRoleDefinitions.length - 1];
}
