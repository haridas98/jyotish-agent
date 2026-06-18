import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const files = {
  types: readFileSync("src/astrology/reports/reportEvidenceTypes.ts", "utf8"),
  builder: readFileSync("src/astrology/reports/reportEvidenceBuilder.ts", "utf8"),
  reportsIndex: readFileSync("src/astrology/reports/index.ts", "utf8"),
  packageJson: readFileSync("package.json", "utf8"),
  page: readFileSync("src/app/reports/page.tsx", "utf8"),
};

for (const marker of [
  "ReportEvidencePack",
  "ReportEvidenceItem",
  "ReportEvidenceProvenance",
  "ReportEvidenceSourceRef",
  "ReportEvidenceBuilderInput",
  "schemaVersion: 1",
  "sourceRefs",
  "unavailableItemIds",
]) {
  assert(files.types.includes(marker), `Report evidence types missing ${marker}`);
}

for (const marker of [
  "buildReportEvidencePack",
  "resolvedRecipe.sections",
  "getRelationshipRecipe",
  "getRelationshipFactor",
  "valueForEntity",
  "valueForCalculation",
  "ruleIdsForRelationshipFactor",
  "chart_calculation",
  "relationship_recipe",
  "report_policy",
]) {
  assert(files.builder.includes(marker), `Report evidence builder missing ${marker}`);
}

for (const forbidden of [
  "buildSingleChartEvidencePack",
  "AiEvidencePack",
  "requestCodexAnalysis",
  "requestCompatibilityCodexAnalysis",
  "Спросить AI",
  "Сгенерировать AI",
  "source.pending",
  "raw evidence",
]) {
  assert(!files.builder.includes(forbidden), `Report evidence builder must not contain ${forbidden}`);
  assert(!files.types.includes(forbidden), `Report evidence types must not contain ${forbidden}`);
}

assert(files.reportsIndex.includes("./reportEvidenceBuilder"), "Reports index must export evidence builder");
assert(files.reportsIndex.includes("./reportEvidenceTypes"), "Reports index must export evidence types");
assert(files.packageJson.includes("test:report-evidence"), "package.json must expose test:report-evidence");
assert(!files.page.includes("buildReportEvidencePack"), "/reports page must not render or dump evidence pack in this stage");

console.log("Report evidence check passed.");
