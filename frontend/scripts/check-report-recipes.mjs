import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const files = {
  typeTypes: readFileSync("src/astrology/reports/reportTypeTypes.ts", "utf8"),
  sectionTypes: readFileSync("src/astrology/reports/reportSectionTypes.ts", "utf8"),
  recipeTypes: readFileSync("src/astrology/reports/reportRecipeTypes.ts", "utf8"),
  typeRegistry: readFileSync("src/astrology/reports/reportTypeRegistry.ts", "utf8"),
  sectionRegistry: readFileSync("src/astrology/reports/reportSectionRegistry.ts", "utf8"),
  recipeRegistry: readFileSync("src/astrology/reports/reportRecipeRegistry.ts", "utf8"),
  resolver: readFileSync("src/astrology/reports/reportRecipeResolver.ts", "utf8"),
  validation: readFileSync("src/astrology/reports/reportRecipeValidation.ts", "utf8"),
  renderer: readFileSync("src/ui/reports/ReportRecipeRenderer.tsx", "utf8"),
  sectionRenderer: readFileSync("src/ui/reports/ReportSectionRenderer.tsx", "utf8"),
  factorGroup: readFileSync("src/ui/reports/ReportFactorGroup.tsx", "utf8"),
  page: readFileSync("src/app/reports/page.tsx", "utf8"),
  packageJson: readFileSync("package.json", "utf8"),
  inventory: readFileSync("../docs/report_constructor_inventory.md", "utf8"),
};

for (const [name, content] of Object.entries(files)) {
  assert(content.trim().length > 0, `${name} must not be empty`);
}

for (const marker of [
  "ReportTypeDefinition",
  "ReportTypeId = \"personal_overview\"",
  "chartSelection",
  "relationshipContext",
  "periodContext",
]) {
  assert(files.typeTypes.includes(marker), `Report type types missing ${marker}`);
}

for (const marker of ["ReportSectionDefinition", "section.chart_core", "section.relationship_context"]) {
  assert(files.sectionTypes.includes(marker) || files.sectionRegistry.includes(marker), `Report section foundation missing ${marker}`);
}

for (const marker of [
  "ReportEntityFactor",
  "ReportCalculationFactor",
  "ReportRelationshipContextFactor",
  "ReportFactorGroup",
  "ReportRecipeSection",
  "ResolvedReportRecipe",
]) {
  assert(files.recipeTypes.includes(marker), `Report recipe types missing ${marker}`);
}

assert(files.typeRegistry.includes("personal_overview"), "Report Type Registry must define personal_overview");
assert(!files.typeRegistry.includes("\"family\""), "Report Type Registry must not expose old family scaffold");
assert(!files.typeRegistry.includes("\"career\""), "Report Type Registry must not expose old career scaffold");
assert(!files.typeRegistry.includes("\"karma\""), "Report Type Registry must not expose old karma scaffold");

for (const marker of [
  "house.1",
  "graha.MO",
  "graha.SU",
  "house.5",
  "house.9",
  "house.10",
  "calc.varga.D1",
  "calc.varga.D9",
  "calc.vimshottari",
  "selected_saved_relationship",
]) {
  assert(files.recipeRegistry.includes(marker), `personal_overview recipe missing ${marker}`);
}

assert(!files.recipeRegistry.includes("calc.varga.D60"), "personal_overview must not include D60");
assert(files.recipeRegistry.includes("needs_source"), "Recipe must not be marked verified at this stage");
assert(files.resolver.includes("getRelationshipRecipe"), "Resolver must reference Relationship Recipe Registry");
assert(files.resolver.includes("relationshipProjection"), "Resolver must project saved relationship context");
assert(files.validation.includes("validateReportTypeRegistry"), "Validation must include report type registry");
assert(files.validation.includes("validateReportSectionRegistry"), "Validation must include report section registry");
assert(files.validation.includes("validateReportRecipeRegistry"), "Validation must include report recipe registry");
assert(files.validation.includes("validateD60Factor"), "Validation must enforce D60 policy");

for (const marker of ["ReportRecipeRenderer", "ReportSectionRenderer", "ReportFactorGroup", "EntityChip", "CalculationChip", "RelationshipFactorChip"]) {
  assert(
    files.renderer.includes(marker) || files.sectionRenderer.includes(marker) || files.factorGroup.includes(marker),
    `Renderer stack missing ${marker}`,
  );
}

for (const forbidden of ["house.1", "house.5", "house.9", "house.10", "graha.MO", "graha.SU", "calc.varga.D1", "calc.varga.D9", "calc.vimshottari"]) {
  assert(!files.page.includes(forbidden), `/reports page must not contain hardcoded report factor ${forbidden}`);
}

assert(files.page.includes("resolveReportRecipe"), "/reports page must call resolver");
assert(files.page.includes("<ReportRecipeRenderer"), "/reports page must use ReportRecipeRenderer");
assert((files.page.match(/<EntityInspector/g) ?? []).length === 1, "/reports must render exactly one EntityInspector");
assert(files.packageJson.includes("test:report-recipes"), "package.json must expose test:report-recipes");

for (const forbidden of ["source.pending", "AI prompt", "interpretation text", "chart IDs", "relationship IDs"]) {
  assert(!files.recipeRegistry.includes(forbidden), `Recipe Registry contains forbidden marker: ${forbidden}`);
}

console.log("Report recipes check passed.");
