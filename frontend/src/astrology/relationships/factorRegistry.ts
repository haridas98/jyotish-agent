import type { RelationshipFactorDefinition, RelationshipFactorId } from "./factorTypes";

export const relationshipFactorDefinitions: RelationshipFactorDefinition[] = [
  factor("factor.overlay.planets_a_to_b", "Планеты A в карте B", "Planets A over B", ["varga.D1"], "planned"),
  factor("factor.overlay.planets_b_to_a", "Планеты B в карте A", "Planets B over A", ["varga.D1"], "planned"),
  factor("factor.overlay.houses_a_to_b", "Дома A относительно B", "Houses A over B", ["varga.D1"], "planned"),
  factor("factor.overlay.houses_b_to_a", "Дома B относительно A", "Houses B over A", ["varga.D1"], "planned"),
  factor("factor.moon.relationship", "Связь Лун", "Moon relationship", ["varga.D1"], "planned"),
  factor("factor.lagna.relationship", "Связь Лагн", "Lagna relationship", ["varga.D1"], "planned"),
  factor("factor.mutual.aspects", "Взаимные аспекты", "Mutual aspects", ["varga.D1"], "planned"),
  factor("factor.dasha.overlap", "Пересечение даш", "Dasha overlap", ["dasha.vimshottari"], "planned"),
  factor("factor.transit.context", "Транзитный контекст", "Transit context", ["transits.current"], "planned"),
];

const factorMap = new Map(relationshipFactorDefinitions.map((definition) => [definition.id, definition]));

export function getRelationshipFactor(id: RelationshipFactorId): RelationshipFactorDefinition | null {
  return factorMap.get(id) ?? null;
}

export function listRelationshipFactors(): RelationshipFactorDefinition[] {
  return relationshipFactorDefinitions;
}

function factor(
  id: RelationshipFactorId,
  ru: string,
  en: string,
  requiredCalculationIds: string[],
  status: RelationshipFactorDefinition["status"],
): RelationshipFactorDefinition {
  return {
    id,
    label: { ru, en },
    requiredCalculationIds,
    status,
  };
}
