import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/interactions/page.tsx", import.meta.url), "utf8");
const presets = readFileSync(new URL("../src/astrology/relationships/interactionScenarioPresets.ts", import.meta.url), "utf8");

assert(page.includes("interactionScenarioPresets"), "/interactions must keep using interactionScenarioPresets");

for (const marker of [
  "Decision brief",
  "interactionDecisionBrief",
  "briefReadiness",
  "Missing profiles",
  "Choose pair",
  "Add context",
  "Ready to review",
  "Next step",
  "Selected scenario",
  "Relationship type",
  "Direction mode",
  "Profile A",
  "Profile B",
  "Current note",
]) {
  assert(page.includes(marker), `/interactions decision brief marker missing: ${marker}`);
}

for (const marker of [
  "Sibling or brother loan",
  "Boss/subordinate conflict",
  "Friend trust",
  "Business partner decision",
  "Client/supplier pressure",
  "Opponent/conflict handling",
]) {
  assert(presets.includes(marker), `Scenario preset label missing: ${marker}`);
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
  "pending calculations",
]) {
  assert(!page.includes(forbidden), `/interactions must not expose ${forbidden}`);
  assert(!presets.includes(forbidden), `Interaction presets must not expose ${forbidden}`);
}

for (const marker of ["axios", "XMLHttpRequest", "localStorage", "sessionStorage", "navigator.clipboard"]) {
  assert(!page.includes(marker), `/interactions must not use browser/network marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only interaction brief stage: ${changed}`);
}

console.log("Interaction decision brief check passed.");
