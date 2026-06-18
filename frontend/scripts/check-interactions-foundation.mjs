import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const page = readFileSync("src/app/interactions/page.tsx", "utf8");
const productionCheck = readFileSync("scripts/production-check.mjs", "utf8");

for (const required of [
  "listRelationshipRecipes",
  "getRelationshipType",
  "getRelationshipFactor",
  "EntityChip",
  "EntityInspector",
  "RelationshipFactorChip",
  "perspectiveAtoB",
  "perspectiveBtoA",
  "mutualFocus",
  "mode === \"astrologer\"",
  "recipe.status !== \"draft\"",
  "recipe.status !== \"disabled\"",
  "relationshipType.symmetric",
  "activeEntityId",
  "setActiveEntityId",
  "profiles.length < 2",
]) {
  assert(page.includes(required), `/interactions missing required marker: ${required}`);
}

assert(!page.includes("relationshipRoleDefinitions"), "/interactions must not use legacy role definitions");
assert(!page.includes("relationshipRoleFor"), "/interactions must not use legacy role resolver");
assert((page.match(/<EntityInspector/g) ?? []).length === 1, "/interactions must render exactly one EntityInspector");
assert(page.includes("varga.D60") && page.includes("birth_time_accuracy"), "/interactions must keep D60 in expert/warning path");

for (const forbidden of [
  "relationship.moonRelationship",
  "relationship.goodCompatibility",
  "relationship.badCompatibility",
  "karmicConnection",
  "source.pending",
  "Block is not registered yet",
  "Missing calculations",
  "AI должен читать это",
  "Спросить AI",
  "D9 отвечает за семью",
  "D60 — карта кармы",
]) {
  assert(!page.includes(forbidden), `/interactions contains forbidden marker: ${forbidden}`);
  const escaped = forbidden.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regexEscaped = forbidden.replaceAll(".", "\\.");
  assert(
    productionCheck.includes(forbidden) || productionCheck.includes(escaped) || productionCheck.includes(regexEscaped),
    `production-check does not guard marker: ${forbidden}`,
  );
}

assert(productionCheck.includes("src/app/interactions/page.tsx"), "production-check must scan /interactions source");

console.log("Interactions foundation check passed.");
