import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function sliceBetween(source, start, end) {
  const startIndex = source.indexOf(start);
  const endIndex = source.indexOf(end, startIndex);
  assert(startIndex >= 0, `Missing slice start: ${start}`);
  assert(endIndex > startIndex, `Missing slice end: ${end}`);
  return source.slice(startIndex, endIndex);
}

const presets = readFileSync(new URL("../src/astrology/timing/timingScenarioPresets.ts", import.meta.url), "utf8");
const page = readFileSync(new URL("../src/app/transits/page.tsx", import.meta.url), "utf8");
const timingSlice = sliceBetween(page, "Timing decision presets", "Transit Workbench");

for (const marker of [
  "timingScenarioPresets",
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
  "category",
  "context",
  "planningFactors",
  "Moon state",
  "weekday",
  "tithi",
  "nakshatra",
  "transits",
]) {
  assert(presets.includes(marker), `Timing preset marker missing: ${marker}`);
}

for (const marker of [
  "timingScenarioPresets",
  "selectedTimingPresetId",
  "timingScenarioContext",
  "applyTimingScenarioPreset",
  "Timing decision presets",
  "Planning context",
]) {
  assert(page.includes(marker), `/transits missing timing preset marker: ${marker}`);
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
]) {
  assert(!presets.includes(forbidden), `Preset payload must not expose ${forbidden}`);
  assert(!timingSlice.includes(forbidden), `Timing preset UI must not expose ${forbidden}`);
}

for (const networkMarker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!timingSlice.includes(networkMarker), `Timing presets must not add network marker ${networkMarker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only timing preset stage: ${changed}`);
}

console.log("Timing scenario presets check passed.");
