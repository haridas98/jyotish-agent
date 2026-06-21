import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const presets = readFileSync(new URL("../src/astrology/relationships/interactionScenarioPresets.ts", import.meta.url), "utf8");
const page = readFileSync(new URL("../src/app/interactions/page.tsx", import.meta.url), "utf8");

for (const marker of [
  "interactionScenarioPresets",
  "sibling_brother_loan",
  "Sibling or brother loan",
  "boss_subordinate_conflict",
  "Boss/subordinate conflict",
  "friend_trust",
  "Friend trust",
  "business_partner_decision",
  "Business partner decision",
  "client_supplier_pressure",
  "Client/supplier pressure",
  "opponent_conflict_handling",
  "Opponent/conflict handling",
  "relationshipTypeId",
  "context",
]) {
  assert(presets.includes(marker), `Scenario preset marker missing: ${marker}`);
}

for (const marker of [
  "interactionScenarioPresets",
  "selectedScenarioPresetId",
  "applyScenarioPreset",
  "Scenario presets",
  "Practical question presets",
]) {
  assert(page.includes(marker), `/interactions missing scenario preset marker: ${marker}`);
}

for (const forbidden of [
  "source_report",
  "field_results",
  "expected",
  "actual",
  "sources_present",
  "seal_witness_case",
  "--ack-diff-open",
  "authority",
  "authoritative",
]) {
  assert(!presets.includes(forbidden), `Preset payload must not expose ${forbidden}`);
  assert(!page.includes(forbidden), `/interactions scenario UI must not expose ${forbidden}`);
}

for (const networkMarker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!presets.includes(networkMarker), `Presets must not add network marker ${networkMarker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during interaction scenario stage: ${changed}`);
}

console.log("Interaction scenario presets check passed.");
