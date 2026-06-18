import type { EntityId, ResolvedReportSection } from "@/astrology";
import { ReportFactorGroup } from "./ReportFactorGroup";

type ReportSectionRendererProps = {
  activeEntityId: EntityId | null;
  onEntitySelect: (entityId: EntityId) => void;
  section: ResolvedReportSection;
};

export function ReportSectionRenderer({ activeEntityId, onEntitySelect, section }: ReportSectionRendererProps) {
  return (
    <section className="interaction-layer">
      <h3>{section.label.ru}</h3>
      {section.factorGroups.map((group) => (
        <ReportFactorGroup key={group.id} group={group} activeEntityId={activeEntityId} onEntitySelect={onEntitySelect} />
      ))}
    </section>
  );
}
