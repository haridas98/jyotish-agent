import { getRelationshipFactor, type RelationshipFactorId } from "@/astrology";

export function RelationshipFactorChip({ factorId }: { factorId: RelationshipFactorId }) {
  const factor = getRelationshipFactor(factorId);
  return <span className="relationship-factor-chip">{factor?.label.ru ?? factor?.label.en ?? "Фактор"}</span>;
}
