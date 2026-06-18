import { readFileSync } from "node:fs";
import { join } from "node:path";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const snapshotPath = join("scripts", "__snapshots__", "report-evidence-personal-overview.json");
const snapshot = JSON.parse(readFileSync(snapshotPath, "utf8"));

assert(snapshot.schemaVersion === 1, "Snapshot schemaVersion must be 1");
assert(snapshot.reportRecipeId === "personal_overview", "Snapshot must use personal_overview");
assert(snapshot.reportTypeId === "personal_overview", "Snapshot reportTypeId mismatch");
assert(snapshot.mode === "novice", "Snapshot mode mismatch");
assert(snapshot.relationshipTypeId === "spouses", "Snapshot relationship type mismatch");

const itemIds = snapshot.itemIds;
assert(Array.isArray(itemIds) && itemIds.length === 15, "Snapshot must contain expected item IDs");
assert(itemIds.join("\n") === [...itemIds].sort().join("\n"), "Snapshot item IDs must be sorted");

for (const expected of [
  "entity.section.chart_core.personal_overview.key_points.house.1",
  "entity.section.chart_core.personal_overview.key_points.graha.MO",
  "entity.section.chart_core.personal_overview.key_points.graha.SU",
  "calculation.section.chart_core.personal_overview.calculations.calc.varga.D1",
  "calculation.section.chart_core.personal_overview.calculations.calc.varga.D9",
  "calculation.section.chart_core.personal_overview.calculations.calc.vimshottari",
  "relationship.section.relationship_context.personal_overview.relationship_context.factor.moon.relationship",
]) {
  assert(itemIds.includes(expected), `Snapshot missing item ${expected}`);
}

const sourceRefKeys = snapshot.sourceRefKeys;
assert(sourceRefKeys.join("\n") === [...sourceRefKeys].sort().join("\n"), "Snapshot source refs must be sorted");
assert(sourceRefKeys.includes("tradition:rule.relationship.spouses.mutual:"), "Snapshot must include relationship rule source ref");
assert(Array.isArray(snapshot.unavailableItemIds) && snapshot.unavailableItemIds.length === 0, "Snapshot must have no unavailable items");

console.log("Report evidence snapshot check passed.");
