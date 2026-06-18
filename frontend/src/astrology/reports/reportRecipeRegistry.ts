import type { ReportRecipe, ReportRecipeStatus } from "./reportRecipeTypes";
import type { ReportTypeId } from "./reportTypeTypes";

const activeStatus: ReportRecipeStatus = "needs_source";

export const reportRecipeDefinitions: ReportRecipe[] = [
  {
    id: "personal_overview",
    version: 1,
    reportTypeId: "personal_overview",
    label: {
      ru: "\u041b\u0438\u0447\u043d\u044b\u0439 \u043e\u0431\u0437\u043e\u0440",
      en: "Personal overview",
    },
    shortDescription: {
      ru: "\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0430, \u043b\u0430\u0433\u043d\u0430, \u041b\u0443\u043d\u0430, \u0421\u043e\u043b\u043d\u0446\u0435, \u0431\u0430\u0437\u043e\u0432\u044b\u0435 \u0434\u043e\u043c\u0430 \u0438 \u043e\u0441\u043d\u043e\u0432\u043d\u044b\u0435 \u0432\u0430\u0440\u0433\u0438.",
      en: "Main chart, Lagna, Moon, Sun, basic houses, and essential vargas.",
    },
    status: activeStatus,
    sections: [
      {
        sectionId: "section.chart_core",
        order: 10,
        required: true,
        visibleInModes: ["novice", "astrologer"],
        factorGroups: [
          {
            id: "personal_overview.key_points",
            label: { ru: "\u0413\u043b\u0430\u0432\u043d\u044b\u0435 \u0442\u043e\u0447\u043a\u0438", en: "Key points" },
            visibleInModes: ["novice", "astrologer"],
            defaultExpanded: true,
            factors: [
              { kind: "entity", entityId: "house.1", priority: "primary", visibleInModes: ["novice", "astrologer"] },
              { kind: "entity", entityId: "graha.MO", priority: "primary", visibleInModes: ["novice", "astrologer"] },
              { kind: "entity", entityId: "graha.SU", priority: "primary", visibleInModes: ["novice", "astrologer"] },
            ],
          },
          {
            id: "personal_overview.additional_houses",
            label: { ru: "\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e", en: "Additional" },
            visibleInModes: ["novice", "astrologer"],
            defaultExpanded: true,
            factors: [
              { kind: "entity", entityId: "house.5", priority: "secondary", visibleInModes: ["novice", "astrologer"] },
              { kind: "entity", entityId: "house.9", priority: "secondary", visibleInModes: ["novice", "astrologer"] },
              { kind: "entity", entityId: "house.10", priority: "secondary", visibleInModes: ["novice", "astrologer"] },
            ],
          },
          {
            id: "personal_overview.calculations",
            label: { ru: "\u0420\u0430\u0441\u0447\u0451\u0442\u044b", en: "Calculations" },
            visibleInModes: ["novice", "astrologer"],
            defaultExpanded: true,
            factors: [
              { kind: "calculation", calculationId: "calc.varga.D1", priority: "primary", required: true, visibleInModes: ["novice", "astrologer"] },
              { kind: "calculation", calculationId: "calc.varga.D9", priority: "secondary", required: false, visibleInModes: ["novice", "astrologer"] },
              { kind: "calculation", calculationId: "calc.vimshottari", priority: "secondary", required: false, visibleInModes: ["novice", "astrologer"] },
            ],
          },
        ],
      },
      {
        sectionId: "section.relationship_context",
        order: 20,
        required: false,
        visibleInModes: ["novice", "astrologer"],
        factorGroups: [
          {
            id: "personal_overview.relationship_context",
            label: { ru: "\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 \u0441\u0432\u044f\u0437\u0438", en: "Relationship context" },
            visibleInModes: ["novice", "astrologer"],
            defaultExpanded: true,
            factors: [
              {
                kind: "relationship_context",
                source: "selected_saved_relationship",
                recipeProjection: "summary",
                required: false,
                visibleInModes: ["novice", "astrologer"],
              },
            ],
          },
        ],
      },
    ],
    warnings: [
      {
        type: "birth_time_accuracy",
        label: {
          ru: "\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0442\u043e\u0447\u043d\u043e\u0441\u0442\u044c \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f \u043f\u0435\u0440\u0435\u0434 \u0442\u043e\u043d\u043a\u0438\u043c\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430\u043c\u0438.",
          en: "Check birth time accuracy before using subtle sections.",
        },
        visibleInModes: ["astrologer"],
      },
    ],
    sourcePolicy: {
      requireVerifiedRulesForGeneratedInterpretation: true,
    },
  },
];

const reportRecipeMap = new Map(reportRecipeDefinitions.map((recipe) => [recipe.id, recipe]));

export function getReportRecipe(id: string): ReportRecipe | null {
  return reportRecipeMap.get(id as ReportTypeId) ?? null;
}

export function listReportRecipes(): ReportRecipe[] {
  return reportRecipeDefinitions.filter((recipe) => recipe.status !== "draft" && recipe.status !== "disabled");
}
