import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/reports/page.tsx", "utf8");
const registry = readFileSync("src/astrology/reports/reportRecipeRegistry.ts", "utf8");
const recipeTypes = readFileSync("src/astrology/reports/reportRecipeTypes.ts", "utf8");
const resolver = readFileSync("src/astrology/reports/reportRecipeResolver.ts", "utf8");
const renderer = readFileSync("src/ui/reports/ReportRecipeRenderer.tsx", "utf8");
const astrologyIndex = readFileSync("src/astrology/index.ts", "utf8");
const productionCheck = readFileSync("scripts/production-check.mjs", "utf8");

for (const required of [
  "ReportBuilderPage",
  "listChartProfiles",
  "listChartRelationships",
  "listReportTypes",
  "getReportType",
  "resolveReportRecipe",
  "getRelationshipType",
  "ReportRecipeRenderer",
  "EntityInspector",
  "selectedRelationship",
  "activeEntityId",
  "reportTypeId",
  "birth_time_accuracy",
]) {
  assert(page.includes(required), `/reports missing required marker: ${required}`);
}

for (const required of [
  "reportRecipeDefinitions",
  "listReportRecipes",
  "getReportRecipe",
  "\"personal_overview\"",
  "\"section.chart_core\"",
  "\"section.relationship_context\"",
  "\"calc.varga.D1\"",
  "\"calc.varga.D9\"",
  "\"calc.vimshottari\"",
]) {
  assert(registry.includes(required), `Report Recipe Registry missing required marker: ${required}`);
}
assert(recipeTypes.includes("export type ReportRecipe"), "Report recipe types must export ReportRecipe");

assert(astrologyIndex.includes("./reports"), "astrology index must export reports registry");
assert(!page.includes("const reportTypes = ["), "/reports must not keep inline report type definitions");
assert(!page.includes("type ReportType ="), "/reports must not define report type aliases inline");
assert(resolver.includes("getRelationshipRecipe"), "report resolver must project relationship recipe context");
assert(renderer.includes("ReportSectionRenderer"), "report renderer must render resolved sections");

assert((page.match(/<EntityInspector/g) ?? []).length === 1, "/reports must render exactly one EntityInspector");

for (const forbidden of [
  "PrivateHistoryPage",
  "historyKind",
  "birth_chart_codex_cli",
  "current_day_transit_overview",
  "fetchAnalysisHistory",
  "requestCodexAnalysis",
  "requestCompatibilityCodexAnalysis",
  "Спросить AI",
  "source.pending",
  "Block is not registered yet",
  "Missing calculations",
  "raw evidence",
  "recipe dump",
  "raw recipe",
  "ownerUserId",
  "pairKey",
]) {
  assert(!page.includes(forbidden), `/reports contains forbidden marker: ${forbidden}`);
  assert(productionCheck.includes(forbidden) || productionCheck.includes(forbidden.replaceAll(".", "\\.")), `production-check does not guard marker: ${forbidden}`);
}

assert(productionCheck.includes("src/app/reports/page.tsx"), "production-check must scan /reports source");

for (const forbidden of ["house.1", "house.5", "house.9", "house.10", "graha.MO", "graha.SU", "calc.varga.D1", "calc.varga.D9"]) {
  assert(!page.includes(forbidden), `/reports page must not contain hardcoded factor: ${forbidden}`);
}

console.log("Reports foundation check passed.");
