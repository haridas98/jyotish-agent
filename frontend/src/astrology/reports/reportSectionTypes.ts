import type { LocalizedText } from "./reportTypeTypes";

export type ReportSectionId =
  | "section.chart_core"
  | "section.relationship_context"
  | "section.warnings"
  | "section.sources";

export type ReportSectionKind =
  | "entity_group"
  | "calculation_group"
  | "relationship_context"
  | "warning_group"
  | "source_group";

export type ReportSectionDefinition = {
  id: ReportSectionId;
  label: LocalizedText;
  kind: ReportSectionKind;
  defaultExpanded: boolean;
  userToggleable: boolean;
};
