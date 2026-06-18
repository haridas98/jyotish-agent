import { readFileSync } from "node:fs";
import vm from "node:vm";
import ts from "typescript";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/compatibility/page.tsx", "utf8");
const scope = readFileSync("src/astrology/compatibility/compatibilityScope.ts", "utf8");
const recipeRegistry = readFileSync("src/astrology/relationships/recipeRegistry.ts", "utf8");
const productionCheck = readFileSync("scripts/production-check.mjs", "utf8");

for (const required of [
  "compatibilityScope",
  "relationshipTypeIds",
  "\"spouses\"",
  "\"romantic_partners\"",
  "listCompatibilityRecipes",
  "listCompatibilityRelationshipTypes",
  "isCompatibilityRelationshipTypeId",
  "listChartProfiles",
  "listChartRelationships",
  "createChartRelationship",
  "updateChartRelationship",
  "deleteChartRelationship",
  "EntityChip",
  "EntityInspector",
  "RelationshipFactorChip",
  "perspectiveAtoB",
  "perspectiveBtoA",
  "mutualFocus",
  "mode === \"astrologer\"",
  "varga.D60",
  "birth_time_accuracy",
]) {
  assert(page.includes(required) || scope.includes(required), `/compatibility missing required marker: ${required}`);
}

assert(scope.includes("validateCompatibilityScope"), "compatibility scope must expose validation");
assert(recipeRegistry.includes('"romantic_partners"'), "romantic_partners must have its own relationship recipe");
assert(recipeRegistry.includes('spouseFocus("a_to_b"'), "spouse recipe must call spouseFocus for A to B direction");
assert(recipeRegistry.includes('spouseFocus("b_to_a"'), "spouse recipe must call spouseFocus for B to A direction");
assert(recipeRegistry.includes('direction === "b_to_a"'), "spouseFocus must switch overlay factors by direction");
assert(recipeRegistry.includes('"factor.overlay.houses_b_to_a"'), "B to A recipes must include houses_b_to_a");
assert(recipeRegistry.includes('"factor.overlay.planets_b_to_a"'), "B to A recipes must include planets_b_to_a");
assertDirectedRecipeFactors(recipeRegistry, "spouses");
assertDirectedRecipeFactors(recipeRegistry, "romantic_partners");
assert(!scope.includes("father_child"), "compatibility scope must not include father_child");
assert(!scope.includes("business_partners"), "compatibility scope must not include business_partners");
assert(!scope.includes("boss_subordinate"), "compatibility scope must not include boss_subordinate");
assert((page.match(/<EntityInspector/g) ?? []).length === 1, "/compatibility must render exactly one EntityInspector");

for (const forbidden of [
  "PrivateHistoryPage",
  "historyKind",
  "compatibility_codex_cli",
  "fetchCompatibilityCalculation",
  "requestCompatibilityCodexAnalysis",
  "Спросить AI",
  "Высокая совместимость",
  "Низкая совместимость",
  "Идеальная пара",
  "Совместимость:\\s*100%",
  "28 из 36",
  "Aṣṭakūṭa",
  "Guna Milan",
  "score",
  "source.pending",
  "Block is not registered yet",
  "Missing calculations",
  "relationship.moonRelationship",
  "ownerUserId",
  "pairKey",
  "recipe dump",
  "raw evidence",
]) {
  assert(!page.includes(forbidden), `/compatibility contains forbidden marker: ${forbidden}`);
}

for (const marker of [
  "src/app/compatibility/page.tsx",
  "Высокая совместимость",
  "Низкая совместимость",
  "Идеальная пара",
  "Совместимость:\\s*100%",
  "ownerUserId",
  "pairKey",
  "raw evidence",
]) {
  assert(productionCheck.includes(marker), `production-check missing compatibility marker: ${marker}`);
}

console.log("Compatibility foundation check passed.");

function assertDirectedRecipeFactors(source, recipeId) {
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
  }).outputText;
  const sandbox = { exports: {}, module: { exports: {} } };
  sandbox.exports = sandbox.module.exports;
  vm.runInNewContext(output, sandbox, { filename: "recipeRegistry.ts" });
  const recipes = sandbox.module.exports.relationshipRecipeDefinitions ?? sandbox.exports.relationshipRecipeDefinitions;
  const recipe = recipes.find((item) => item.id === recipeId);
  assert(recipe, `${recipeId} recipe must exist`);
  assertDirection(recipe.perspectiveAtoB.relationshipFactorIds, "A→B", ["factor.overlay.houses_a_to_b", "factor.overlay.planets_a_to_b"], [
    "factor.overlay.houses_b_to_a",
    "factor.overlay.planets_b_to_a",
  ]);
  assertDirection(recipe.perspectiveBtoA.relationshipFactorIds, "B→A", ["factor.overlay.houses_b_to_a", "factor.overlay.planets_b_to_a"], [
    "factor.overlay.houses_a_to_b",
    "factor.overlay.planets_a_to_b",
  ]);
}

function assertDirection(actual, label, required, forbidden) {
  for (const factor of required) {
    assert(actual.includes(factor), `${label} must include ${factor}`);
  }
  for (const factor of forbidden) {
    assert(!actual.includes(factor), `${label} must not include ${factor}`);
  }
}
