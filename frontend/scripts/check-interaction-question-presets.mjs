import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/interactions/page.tsx", import.meta.url), "utf8");
const scenarioPresets = readFileSync(new URL("../src/astrology/relationships/interactionScenarioPresets.ts", import.meta.url), "utf8");

for (const marker of [
  "interactionQuestionPresets",
  "selectedQuestionPresetId",
  "selectedQuestionPreset",
  "Question presets",
  "Selected question",
  "Practical next step",
  "Risk/attention point",
  "Relationship context",
]) {
  assert(page.includes(marker), `/interactions question preset marker missing: ${marker}`);
}

for (const [id, label] of [
  ["money_loan_relative", "Money/loan with sibling or relative"],
  ["boss_work_conflict", "Boss/work conflict"],
  ["friend_trust_support", "Friend trust/support"],
  ["client_business_negotiation", "Client/business negotiation"],
  ["family_boundary_conflict", "Family boundary/conflict"],
]) {
  assert(page.includes(id), `Question preset id missing: ${id}`);
  assert(page.includes(label), `Question preset label missing: ${label}`);
}

for (const marker of ["Missing profile A", "Missing profile B", "profileAName", "profileBName", "directionMode", "noteText"]) {
  assert(page.includes(marker), `Decision brief must keep local field marker: ${marker}`);
}

for (const marker of ["Sibling or brother loan", "Boss/subordinate conflict", "Friend trust"]) {
  assert(scenarioPresets.includes(marker), `Existing scenario preset missing: ${marker}`);
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
  "guaranteed correctness",
  "guaranteed auspiciousness",
  "guaranteed profit",
  "legal advice",
  "medical advice",
  "final decision",
]) {
  assert(!page.includes(forbidden), `/interactions question preset UI must not expose ${forbidden}`);
  assert(!scenarioPresets.includes(forbidden), `Interaction scenario presets must not expose ${forbidden}`);
}

for (const marker of ["axios", "XMLHttpRequest", "localStorage", "sessionStorage", "navigator.clipboard"]) {
  assert(!page.includes(marker), `/interactions must not use browser/network marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only question preset stage: ${changed}`);
}

console.log("Interaction question presets check passed.");
