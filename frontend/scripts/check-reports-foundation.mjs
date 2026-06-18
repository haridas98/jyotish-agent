import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/reports/page.tsx", "utf8");
const productionCheck = readFileSync("scripts/production-check.mjs", "utf8");

for (const required of [
  "ReportBuilderPage",
  "listChartProfiles",
  "listChartRelationships",
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
  "varga.D60",
  "birth_time_accuracy",
]) {
  assert(page.includes(required), `/reports missing required marker: ${required}`);
}

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
