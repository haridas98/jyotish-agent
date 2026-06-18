import type { ReportTypeDefinition, ReportTypeId } from "./reportTypeTypes";

export const reportTypeDefinitions: ReportTypeDefinition[] = [
  {
    id: "personal_overview",
    label: {
      ru: "\u041b\u0438\u0447\u043d\u044b\u0439 \u043e\u0431\u0437\u043e\u0440",
      en: "Personal overview",
    },
    shortDescription: {
      ru: "\u0421\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430 \u043e\u0441\u043d\u043e\u0432\u043d\u044b\u0445 \u0444\u0430\u043a\u0442\u043e\u0440\u043e\u0432 \u043e\u0434\u043d\u043e\u0439 \u043a\u0430\u0440\u0442\u044b.",
      en: "A structure of the primary factors of one chart.",
    },
    subjectKind: "single_chart",
    chartSelection: "one_required",
    relationshipContext: "optional",
    periodContext: "optional",
    visibleInModes: ["novice", "astrologer"],
    status: "active",
  },
];

const reportTypeMap = new Map(reportTypeDefinitions.map((definition) => [definition.id, definition]));

export function getReportType(id: string): ReportTypeDefinition | null {
  return reportTypeMap.get(id as ReportTypeId) ?? null;
}

export function listReportTypes(): ReportTypeDefinition[] {
  return reportTypeDefinitions.filter((definition) => definition.status === "active");
}
