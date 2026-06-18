import type { RuleDefinition, RuleId } from "./ruleTypes";

export const ruleDefinitions: RuleDefinition[] = [
  {
    id: "bphs.house.1",
    label: { ru: "Лагна как основа карты", en: "Lagna as chart foundation" },
    domain: "house",
    appliesToEntityIds: ["house.1"],
    requiredCalculationIds: ["calc.varga.D1"],
    conditions: [{ type: "entity_present", entityId: "house.1" }],
    passageIds: ["passage.bphs.lagna.general"],
    status: "verified",
    interpretationPolicy: "conditional",
  },
  {
    id: "bphs.house.5",
    label: { ru: "Пятый дом как слой детей и разума", en: "Fifth house as children and intelligence layer" },
    domain: "house",
    appliesToEntityIds: ["house.5"],
    requiredCalculationIds: ["calc.varga.D1"],
    conditions: [{ type: "entity_present", entityId: "house.5" }],
    passageIds: [],
    status: "needs_source",
    interpretationPolicy: "context_only",
  },
  {
    id: "bphs.house.9",
    label: { ru: "Девятый дом как дхарма и благословение", en: "Ninth house as dharma and blessing" },
    domain: "house",
    appliesToEntityIds: ["house.9"],
    requiredCalculationIds: ["calc.varga.D1"],
    conditions: [{ type: "entity_present", entityId: "house.9" }],
    passageIds: [],
    status: "needs_source",
    interpretationPolicy: "context_only",
  },
  {
    id: "bphs.house.10",
    label: { ru: "Десятый дом как действие и статус", en: "Tenth house as action and status" },
    domain: "house",
    appliesToEntityIds: ["house.10"],
    requiredCalculationIds: ["calc.varga.D1"],
    conditions: [{ type: "entity_present", entityId: "house.10" }],
    passageIds: [],
    status: "needs_source",
    interpretationPolicy: "context_only",
  },
  {
    id: "bphs.graha.mo",
    label: { ru: "Луна как ум и восприятие", en: "Moon as mind and perception" },
    domain: "graha",
    appliesToEntityIds: ["graha.MO"],
    requiredCalculationIds: ["calc.planetPositions", "calc.nakshatras"],
    conditions: [{ type: "entity_present", entityId: "graha.MO" }],
    passageIds: ["passage.bphs.moon.general"],
    status: "verified",
    interpretationPolicy: "conditional",
  },
  {
    id: "bphs.graha.su",
    label: { ru: "Солнце как атма и власть", en: "Sun as atma and authority" },
    domain: "graha",
    appliesToEntityIds: ["graha.SU"],
    requiredCalculationIds: ["calc.planetPositions"],
    conditions: [{ type: "entity_present", entityId: "graha.SU" }],
    passageIds: ["passage.bphs.sun.general"],
    status: "verified",
    interpretationPolicy: "conditional",
  },
  {
    id: "jyotish.classical.varga.D1",
    label: { ru: "D1 Раши как базовая варга", en: "D1 Rashi as the base varga" },
    domain: "varga",
    appliesToEntityIds: ["varga.D1"],
    requiredCalculationIds: ["calc.varga.D1"],
    conditions: [{ type: "calculation_available", calculationId: "calc.varga.D1" }],
    passageIds: ["passage.bphs.varga.sixteen.names", "passage.bphs.varga.uses"],
    status: "verified",
    interpretationPolicy: "context_only",
  },
  {
    id: "jyotish.classical.varga.D9",
    label: { ru: "D9 Навамша как существенная варга", en: "D9 Navamsha as an essential varga" },
    domain: "varga",
    appliesToEntityIds: ["varga.D9"],
    requiredCalculationIds: ["calc.varga.D9"],
    conditions: [{ type: "calculation_available", calculationId: "calc.varga.D9" }],
    passageIds: ["passage.bphs.varga.sixteen.names", "passage.bphs.varga.uses"],
    status: "verified",
    interpretationPolicy: "context_only",
  },
  {
    id: "vimshottari.sequence",
    label: { ru: "Последовательность Вимшоттари", en: "Vimshottari sequence" },
    domain: "dasha",
    appliesToEntityIds: [],
    requiredCalculationIds: ["calc.vimshottari"],
    conditions: [{ type: "calculation_available", calculationId: "calc.vimshottari" }],
    passageIds: ["passage.vimshottari.sequence.general"],
    status: "verified",
    interpretationPolicy: "context_only",
  },
];

const ruleMap = new Map(ruleDefinitions.map((rule) => [rule.id, rule]));

export function getRule(id: RuleId): RuleDefinition | null {
  return ruleMap.get(id) ?? null;
}

export function listRules(): RuleDefinition[] {
  return ruleDefinitions.filter((rule) => rule.status !== "disabled");
}
