import type { RelationshipUiMode } from "../relationships";

export type ReportTypeId = "personal_overview";

export type ReportSubjectKind = "single_chart" | "relationship" | "period";

export type ReportContextRequirement = "forbidden" | "optional" | "required";

export type ReportChartSelection = "one_required" | "two_required";

export type ReportTypeStatus = "draft" | "active" | "disabled";

export type LocalizedText = {
  ru: string;
  en: string;
};

export type ReportTypeDefinition = {
  id: ReportTypeId;
  label: LocalizedText;
  shortDescription: LocalizedText;
  subjectKind: ReportSubjectKind;
  chartSelection: ReportChartSelection;
  relationshipContext: ReportContextRequirement;
  periodContext: ReportContextRequirement;
  visibleInModes: RelationshipUiMode[];
  status: ReportTypeStatus;
};
