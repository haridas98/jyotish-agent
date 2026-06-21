import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const page = readFileSync(new URL("../src/app/muhurta/page.tsx", import.meta.url), "utf8");
const presets = readFileSync(new URL("../src/astrology/timing/timingScenarioPresets.ts", import.meta.url), "utf8");

assert(!page.includes("redirect"), "/muhurta must render a workspace and must not use redirect");
assert(page.includes("timingScenarioPresets"), "/muhurta must reuse timingScenarioPresets");

for (const marker of [
  "business_launch_investment_window",
  "Business launch / investment window",
  "contract_signing_window",
  "Contract or signing window",
  "lend_money_repayment_caution",
  "Lend money / repayment caution",
  "difficult_conversation",
  "Difficult conversation",
  "travel_move_planning",
  "Travel or move planning",
  "quiet_day_postpone",
  "Quiet day / postpone non-urgent action",
]) {
  assert(page.includes(marker) || presets.includes(marker), `Required timing preset marker missing: ${marker}`);
}

for (const marker of [
  "Muhurta planning",
  "Timing planning workspace",
  "Candidate windows",
  "candidateWindows",
  "decisionMode",
  "compare",
  "postpone",
  "prepare",
  "approvals",
  "documents",
  "budget/risk limit",
  "travel/logistics",
  "counterpart readiness",
  "/transits",
]) {
  assert(page.includes(marker), `/muhurta missing planning marker: ${marker}`);
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

for (const networkMarker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!page.includes(networkMarker), `/muhurta must not add network marker ${networkMarker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only muhurta stage: ${changed}`);
}

console.log("Muhurta planning page check passed.");
