import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/compatibility/page.tsx", "utf8");
const scope = readFileSync("src/astrology/compatibility/compatibilityScope.ts", "utf8");
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
