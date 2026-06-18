import { readFileSync } from "node:fs";
import { join } from "node:path";

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const snapshotPath = join("scripts", "__snapshots__", "ai-contract-personal-overview-dry-run.json");
const snapshot = JSON.parse(readFileSync(snapshotPath, "utf8"));

assert(snapshot.request.schemaVersion === 1, "Request snapshot schemaVersion must be 1");
assert(snapshot.request.reportRecipeId === "personal_overview", "Request snapshot must use personal_overview");
assert(snapshot.request.reportTypeId === "personal_overview", "Request snapshot reportTypeId mismatch");
assert(snapshot.request.mode === "novice", "Request snapshot mode mismatch");

const itemIds = snapshot.request.eligibleItemIds;
assert(Array.isArray(itemIds) && itemIds.length === 6, "Request snapshot must include only verified eligible items");
assert(itemIds.join("\n") === [...itemIds].sort().join("\n"), "Eligible item IDs must be sorted");
assert(!itemIds.some((id) => id.includes("house.5") || id.includes("house.9") || id.includes("house.10")), "Needs-source houses must not become eligible request items");
assert(!itemIds.some((id) => id.includes("relationship.")), "Relationship factors must not become eligible until citations are verified");

const citationChainKeys = snapshot.request.citationChainKeys;
assert(Array.isArray(citationChainKeys) && citationChainKeys.length === 8, "Request snapshot must include expected citation chains");
assert(citationChainKeys.join("\n") === [...citationChainKeys].sort().join("\n"), "Citation chains must be sorted");
assert(citationChainKeys.every((key) => key.endsWith(":source.bphs")), "Pilot citation chains must point to source.bphs");

assert(snapshot.request.excludedSummary.total === 9, "Excluded summary total mismatch");
assert(snapshot.request.excludedSummary.byReason.needs_source === 8, "Needs-source excluded count mismatch");
assert(snapshot.request.excludedSummary.byReason.unsupported === 1, "Unsupported excluded count mismatch");
assert(!("excludedItems" in snapshot.request), "Snapshot request must not contain excluded item bodies");

assert(snapshot.response.schemaVersion === 1, "Response snapshot schemaVersion must be 1");
assert(snapshot.response.provider === "mock", "Response snapshot provider must be mock");
assert(snapshot.response.thesisCount === itemIds.length, "Mock response must create one thesis per eligible item");
assert(snapshot.response.firstThesisEvidenceItemIds[0] === itemIds[0], "First thesis must reference the first request item");
assert(snapshot.response.firstThesisCitationKeys.length === 2, "First thesis must carry citation chains");

console.log("AI contract dry-run snapshot check passed.");
