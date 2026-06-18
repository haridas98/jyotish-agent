import type { EntityId } from "../entities";

export type ReportRecipeId = "core" | "family" | "career" | "karma";

export type ReportRecipe = {
  id: ReportRecipeId;
  label: string;
  summary: string;
  primaryEntityIds: EntityId[];
  secondaryEntityIds: EntityId[];
  calculationIds: string[];
};

export const reportRecipeDefinitions: ReportRecipe[] = [
  {
    id: "core",
    label: "\u041b\u0438\u0447\u043d\u044b\u0439 \u043e\u0431\u0437\u043e\u0440",
    summary:
      "\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043a\u0430\u0440\u0442\u0430, \u043b\u0430\u0433\u043d\u0430, \u041b\u0443\u043d\u0430, \u0421\u043e\u043b\u043d\u0446\u0435, \u0431\u0430\u0437\u043e\u0432\u044b\u0435 \u0434\u043e\u043c\u0430 \u0438 \u043e\u0441\u043d\u043e\u0432\u043d\u044b\u0435 \u0432\u0430\u0440\u0433\u0438.",
    primaryEntityIds: ["house.1", "graha.MO", "graha.SU"],
    secondaryEntityIds: ["house.5", "house.9", "house.10"],
    calculationIds: ["varga.D1", "varga.D9", "dasha.vimshottari"],
  },
  {
    id: "family",
    label: "\u0421\u0435\u043c\u044c\u044f \u0438 \u0440\u043e\u0434",
    summary:
      "\u0420\u043e\u0434\u0438\u0442\u0435\u043b\u0438, \u0434\u0435\u0442\u0438, \u0440\u043e\u0434\u043e\u0432\u0430\u044f \u043b\u0438\u043d\u0438\u044f \u0438 \u043a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0445 \u0441\u0432\u044f\u0437\u0435\u0439.",
    primaryEntityIds: ["house.4", "house.9", "varga.D12"],
    secondaryEntityIds: ["house.2", "house.5", "graha.JU"],
    calculationIds: ["varga.D1", "varga.D7", "varga.D12"],
  },
  {
    id: "career",
    label: "\u0414\u0435\u043b\u043e \u0438 \u0441\u0442\u0430\u0442\u0443\u0441",
    summary:
      "\u0414\u0435\u0441\u044f\u0442\u044b\u0439 \u0434\u043e\u043c, \u0434\u0435\u044f\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c, \u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0441\u0442\u044c, \u0440\u0430\u0431\u043e\u0442\u0430 \u0438 \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u0430\u044f \u0440\u043e\u043b\u044c.",
    primaryEntityIds: ["house.10", "varga.D10", "graha.SA"],
    secondaryEntityIds: ["house.6", "house.11", "graha.ME"],
    calculationIds: ["varga.D1", "varga.D10", "dasha.vimshottari"],
  },
  {
    id: "karma",
    label: "\u0413\u043b\u0443\u0431\u043e\u043a\u0438\u0439 \u0441\u043b\u043e\u0439",
    summary:
      "\u0422\u043e\u043d\u043a\u0438\u0435 \u0432\u0430\u0440\u0433\u0438 \u0438 \u043e\u0441\u0442\u043e\u0440\u043e\u0436\u043d\u044b\u0439 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u043d\u044b\u0439 \u043a\u043e\u043d\u0442\u0435\u043a\u0441\u0442 \u0431\u0435\u0437 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u0432\u044b\u0432\u043e\u0434\u043e\u0432.",
    primaryEntityIds: ["house.8", "house.12", "graha.SA"],
    secondaryEntityIds: ["graha.KE", "varga.D60"],
    calculationIds: ["varga.D1", "varga.D30", "varga.D60"],
  },
];

const reportRecipeMap = new Map(reportRecipeDefinitions.map((recipe) => [recipe.id, recipe]));

export function getReportRecipe(id: string): ReportRecipe | null {
  return reportRecipeMap.get(id as ReportRecipeId) ?? null;
}

export function listReportRecipes(): ReportRecipe[] {
  return reportRecipeDefinitions;
}
