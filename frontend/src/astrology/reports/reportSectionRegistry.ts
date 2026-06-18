import type { ReportSectionDefinition, ReportSectionId } from "./reportSectionTypes";

export const reportSectionDefinitions: ReportSectionDefinition[] = [
  {
    id: "section.chart_core",
    label: { ru: "\u041a\u0430\u0440\u0442\u0430", en: "Chart" },
    kind: "entity_group",
    defaultExpanded: true,
    userToggleable: false,
  },
  {
    id: "section.relationship_context",
    label: { ru: "\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 \u0441\u0432\u044f\u0437\u0438", en: "Relationship context" },
    kind: "relationship_context",
    defaultExpanded: true,
    userToggleable: true,
  },
  {
    id: "section.warnings",
    label: { ru: "\u041f\u0440\u0435\u0434\u0443\u043f\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u044f", en: "Warnings" },
    kind: "warning_group",
    defaultExpanded: true,
    userToggleable: false,
  },
  {
    id: "section.sources",
    label: { ru: "\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0438", en: "Sources" },
    kind: "source_group",
    defaultExpanded: false,
    userToggleable: true,
  },
];

const sectionMap = new Map(reportSectionDefinitions.map((definition) => [definition.id, definition]));

export function getReportSection(id: string): ReportSectionDefinition | null {
  return sectionMap.get(id as ReportSectionId) ?? null;
}

export function listReportSections(): ReportSectionDefinition[] {
  return reportSectionDefinitions;
}
