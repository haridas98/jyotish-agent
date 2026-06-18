import { readFileSync } from "node:fs";

const files = {
  roleTypes: "src/astrology/relationships/roleTypes.ts",
  relationshipTypes: "src/astrology/relationships/relationshipTypes.ts",
  factorTypes: "src/astrology/relationships/factorTypes.ts",
  recipeTypes: "src/astrology/relationships/recipeTypes.ts",
  roleRegistry: "src/astrology/relationships/roleRegistry.ts",
  relationshipTypeRegistry: "src/astrology/relationships/relationshipTypeRegistry.ts",
  factorRegistry: "src/astrology/relationships/factorRegistry.ts",
  recipeRegistry: "src/astrology/relationships/recipeRegistry.ts",
  validation: "src/astrology/relationships/validation.ts",
  index: "src/astrology/relationships/index.ts",
};

const source = {};
const failures = [];

function assert(condition, message) {
  if (!condition) failures.push(message);
}

for (const [key, path] of Object.entries(files)) {
  try {
    source[key] = readFileSync(path, "utf8");
  } catch {
    failures.push(`Missing file: ${path}`);
    source[key] = "";
  }
}

const all = Object.values(source).join("\n");

for (const role of ["father", "mother", "child", "spouse", "business_partner", "boss", "subordinate", "guru", "student", "opponent", "custom"]) {
  assert(all.includes(`"${role}"`), `Missing role: ${role}`);
}

for (const relationship of ["father_child", "mother_child", "siblings", "spouses", "business_partners", "boss_subordinate", "guru_student", "opponents", "custom"]) {
  assert(all.includes(`"${relationship}"`), `Missing relationship type or recipe: ${relationship}`);
}

assert(source.roleTypes.includes("export type RoleId"), "RoleId type missing");
assert(source.relationshipTypes.includes("export type RelationshipTypeId"), "RelationshipTypeId type missing");
assert(source.factorTypes.includes("export type RelationshipFactorId"), "RelationshipFactorId type missing");
assert(source.recipeTypes.includes("export type RelationshipRecipe"), "RelationshipRecipe type missing");

for (const factorId of [
  "factor.overlay.planets_a_to_b",
  "factor.overlay.planets_b_to_a",
  "factor.overlay.houses_a_to_b",
  "factor.overlay.houses_b_to_a",
  "factor.moon.relationship",
  "factor.lagna.relationship",
  "factor.mutual.aspects",
  "factor.dasha.overlap",
  "factor.transit.context",
]) {
  assert(all.includes(`"${factorId}"`), `Missing factor: ${factorId}`);
}

assert(source.recipeTypes.includes("perspectiveAtoB"), "Recipe must support perspectiveAtoB");
assert(source.recipeTypes.includes("perspectiveBtoA"), "Recipe must support perspectiveBtoA");
assert(source.recipeTypes.includes("mutualFocus"), "Recipe must support mutualFocus");
assert(source.recipeRegistry.includes("perspectiveAtoB") && source.recipeRegistry.includes("perspectiveBtoA"), "Recipes must use directed perspectives");

assert(!/requiredCalculationIds:\s*\[[^\]]*D60/.test(source.recipeRegistry), "D60 must not be required");
assert(!/primaryEntityIds:\s*\[[^\]]*varga\.D60/.test(source.recipeRegistry), "D60 must not be primary");
assert(source.recipeRegistry.includes('type: "birth_time_accuracy"') && source.recipeRegistry.includes('"varga.D60"'), "D60 must have a birth-time warning when used");
assert(!/spouses[\s\S]{0,900}varga\.D60/.test(source.recipeRegistry), "D60 must not be automatically added to spouse recipe");
assert(!/business_partners[\s\S]{0,900}varga\.D9/.test(source.recipeRegistry), "D9 must not be automatically added to business recipe");

assert(source.validation.includes("validateRelationshipRecipe"), "validateRelationshipRecipe missing");
assert(source.validation.includes("validateRelationshipRegistry"), "validateRelationshipRegistry missing");
assert(source.validation.includes("duplicate"), "Validation must check duplicate IDs");
assert(source.validation.includes("getEntity"), "Validation must check entity registry");
assert(source.validation.includes("getRelationshipFactor"), "Validation must check factor registry");
assert(source.validation.includes("D60"), "Validation must enforce D60 restrictions");
assert(source.validation.includes("sourcePolicy"), "Validation must check source status policy");

for (const forbidden of [
  "source.pending",
  "relationship.goodCompatibility",
  "relationship.badCompatibility",
  "relationship.karmicConnection",
  "relationship.moonRelationship",
  "D9 — универсальная карта",
  "D60 — карта кармы",
]) {
  assert(!all.includes(forbidden), `Forbidden marker found: ${forbidden}`);
}

assert(source.index.includes("./roleRegistry"), "index must export role registry");
assert(source.index.includes("./recipeRegistry"), "index must export recipe registry");

if (failures.length) {
  console.error("Relationship foundation check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Relationship foundation check passed.");
