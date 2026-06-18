import type { EntityId, ResolvedReportFactorGroup } from "@/astrology";
import { EntityChip } from "@/ui/components/EntityChip";
import { CalculationChip } from "./CalculationChip";
import { RelationshipFactorChip } from "./RelationshipFactorChip";

type ReportFactorGroupProps = {
  activeEntityId: EntityId | null;
  group: ResolvedReportFactorGroup;
  onEntitySelect: (entityId: EntityId) => void;
};

export function ReportFactorGroup({ activeEntityId, group, onEntitySelect }: ReportFactorGroupProps) {
  return (
    <div className="interaction-chip-row">
      <span>{group.label.ru}</span>
      <div>
        {group.factors.length ? (
          group.factors.map((factor) => {
            if (factor.kind === "entity") {
              return <EntityChip key={factor.entityId} entityId={factor.entityId} active={activeEntityId === factor.entityId} onSelect={onEntitySelect} />;
            }
            if (factor.kind === "calculation") {
              return <CalculationChip key={factor.calculationId} calculationId={factor.calculationId} />;
            }
            if (factor.kind === "relationship_factor") {
              return <RelationshipFactorChip key={factor.relationshipFactorId} factorId={factor.relationshipFactorId} />;
            }
            return null;
          })
        ) : (
          <em>{group.emptyState?.ru ?? "не задано"}</em>
        )}
      </div>
    </div>
  );
}
