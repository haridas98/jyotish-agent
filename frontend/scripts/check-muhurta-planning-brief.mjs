import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/muhurta/page.tsx", import.meta.url), "utf8");
const presets = readFileSync(new URL("../src/astrology/timing/timingScenarioPresets.ts", import.meta.url), "utf8");

assert(page.includes("timingScenarioPresets"), "/muhurta must keep using timingScenarioPresets");

for (const marker of [
  "Planning brief",
  "planningBrief",
  "readinessStatus",
  "Ready to compare",
  "Needs details",
  "Prepare first",
  "Selected scenario",
  "Decision mode",
  "Candidate window brief",
  "candidate_1",
  "candidate_2",
  "candidate_3",
  "Checked constraints",
  "Open constraints",
]) {
  assert(page.includes(marker), `/muhurta planning brief marker missing: ${marker}`);
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
  "pending calculations",
]) {
  assert(!page.includes(forbidden), `/muhurta must not expose ${forbidden}`);
  assert(!presets.includes(forbidden), `Timing presets must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest", "localStorage", "sessionStorage", "navigator.clipboard"]) {
  assert(!page.includes(marker), `/muhurta must not use browser/network marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only muhurta brief stage: ${changed}`);
}

console.log("Muhurta planning brief check passed.");
