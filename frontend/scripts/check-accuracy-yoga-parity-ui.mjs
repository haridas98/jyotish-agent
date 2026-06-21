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

const api = readFileSync(new URL("../src/lib/api.ts", import.meta.url), "utf8");
const page = readFileSync(new URL("../src/app/page.tsx", import.meta.url), "utf8");
const panel = sliceBetween(page, "function AccuracyReportPanel", "export default function Home");

for (const marker of ["witness_yoga_parity", "layer_summary", "yoga_summary", "target_met", "next_actions"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_yoga_parity",
  "Yoga parity",
  "Active yogas",
  "yogaParitySummary",
  "yogaParityActions",
  "checked_yogas",
  "failed_yogas",
  "missing_yogas",
  "skipped_yogas",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing Yoga parity UI marker: ${marker}`);
}

const yogaSlice = sliceBetween(panel, "const yogaParity", "const plFailedCount");
for (const marker of ["Р Вµ", "Р Р…", "Р С•", "Р Т‘", "РЎРѓ", "РЎвЂ ", "Р’В·", "пїЅ"]) {
  assert(!yogaSlice.includes(marker), `Yoga parity slice contains mojibake marker: ${marker}`);
}

for (const forbidden of [
  "field_results",
  "expected",
  "actual",
  "source_report",
  "sources_present",
  "authority",
  "authoritative",
  "seal_witness_case",
  "mark_",
  "--ack-diff-open",
]) {
  assert(!panel.includes(forbidden), `AccuracyReportPanel must not expose ${forbidden}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(
    ![
      "backend/apps/calculations/classical.py",
      "backend/apps/calculations/chart.py",
      "backend/apps/calculations/ephemeris.py",
      "backend/apps/calculations/math.py",
      "backend/apps/calculations/panchanga.py",
      "backend/apps/calculations/vimshottari.py",
      "backend/apps/calculations/dasha_systems.py",
      "backend/apps/calculations/vargas.py",
      "backend/apps/calculations/accuracy.py",
    ].includes(changed),
    `Formula/calculation file changed during Yoga parity UI stage: ${changed}`,
  );
}

console.log("Accuracy Yoga parity UI check passed.");
