import type { EntityId, ResolvedReportRecipe } from "@/astrology";
import { ReportSectionRenderer } from "./ReportSectionRenderer";
import { ReportWarningList } from "./ReportWarningList";

type ReportRecipeRendererProps = {
  activeEntityId: EntityId | null;
  onEntitySelect: (entityId: EntityId) => void;
  resolvedRecipe: ResolvedReportRecipe;
};

export function ReportRecipeRenderer({ activeEntityId, onEntitySelect, resolvedRecipe }: ReportRecipeRendererProps) {
  return (
    <>
      {resolvedRecipe.sections.map((section) => (
        <ReportSectionRenderer key={section.sectionId} section={section} activeEntityId={activeEntityId} onEntitySelect={onEntitySelect} />
      ))}
      <ReportWarningList warnings={resolvedRecipe.warnings} />
    </>
  );
}
