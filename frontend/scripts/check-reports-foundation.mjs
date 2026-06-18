import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/reports/page.tsx", "utf8");
const registry = readFileSync("src/astrology/reports/reportRecipeRegistry.ts", "utf8");
const astrologyIndex = readFileSync("src/astrology/index.ts", "utf8");
const productionCheck = readFileSync("scripts/production-check.mjs", "utf8");

for (const required of [
  "ReportBuilderPage",
  "listChartProfiles",
  "listChartRelationships",
  "listReportRecipes",
  "getReportRecipe",
  "type ReportRecipe",
  "listRelationshipRecipes",
  "getRelationshipType",
  "getRelationshipFactor",
  "EntityChip",
  "EntityInspector",
  "ReportRecipePreview",
  "selectedRelationship",
  "selectedRecipe",
  "activeEntityId",
  "reportTypeId",
  "mode === \"astrologer\"",
  "birth_time_accuracy",
]) {
  assert(page.includes(required), `/reports missing required marker: ${required}`);
}

for (const required of [
  "export type ReportRecipe",
  "reportRecipeDefinitions",
  "listReportRecipes",
  "getReportRecipe",
  "\"core\"",
  "\"family\"",
  "\"career\"",
  "\"karma\"",
  "\"varga.D60\"",
]) {
  assert(registry.includes(required), `Report Recipe Registry missing required marker: ${required}`);
}

assert(astrologyIndex.includes("./reports"), "astrology index must export reports registry");
assert(!page.includes("const reportTypes"), "/reports must not keep inline report type definitions");
assert(!page.includes("type ReportType"), "/reports must import report recipe types from registry");

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
]) {
  assert(!page.includes(forbidden), `/reports contains forbidden marker: ${forbidden}`);
  assert(productionCheck.includes(forbidden) || productionCheck.includes(forbidden.replaceAll(".", "\\.")), `production-check does not guard marker: ${forbidden}`);
}

assert(productionCheck.includes("src/app/reports/page.tsx"), "production-check must scan /reports source");

console.log("Reports foundation check passed.");
