import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/muhurta/page.tsx", import.meta.url), "utf8");
const timingPresets = readFileSync(new URL("../src/astrology/timing/timingScenarioPresets.ts", import.meta.url), "utf8");

for (const marker of [
  "muhurtaActionPresets",
  "selectedActionPresetId",
  "selectedActionPreset",
  "Action presets",
  "Selected action",
  "Action decision brief",
  "Practical next step",
  "Risk/attention point",
  "Missing action context",
]) {
  assert(page.includes(marker), `/muhurta action preset marker missing: ${marker}`);
}

for (const [id, label] of [
  ["project_start", "Project start"],
  ["contract_signing", "Contract signing"],
  ["investment_review", "Investment review"],
  ["important_meeting", "Important meeting"],
  ["travel_start", "Travel start"],
  ["product_launch", "Product launch"],
]) {
  assert(page.includes(id), `Muhurta action preset id missing: ${id}`);
  assert(page.includes(label), `Muhurta action preset label missing: ${label}`);
}

for (const marker of [
  "planningBrief",
  "candidateWindows",
  "planningContext",
  "decisionMode",
  "actionDecisionBrief",
  "nextStep",
  "attention",
]) {
  assert(page.includes(marker), `/muhurta action brief must use local planning marker: ${marker}`);
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
  "guaranteed auspiciousness",
  "guaranteed profit",
  "legal advice",
  "financial guarantee",
  "certain outcome",
  "В·",
  "Â·",
  "Ð",
  "�",
]) {
  assert(!page.includes(forbidden), `/muhurta action UI must not expose ${forbidden}`);
  assert(!timingPresets.includes(forbidden), `Timing presets must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest", "localStorage", "sessionStorage", "navigator.clipboard"]) {
  assert(!page.includes(marker), `/muhurta must not use browser/network marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only muhurta action preset stage: ${changed}`);
}

console.log("Muhurta action presets check passed.");
