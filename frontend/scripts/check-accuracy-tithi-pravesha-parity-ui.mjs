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

for (const marker of ["witness_tithi_pravesha_parity", "layer_summary", "field_summary", "target_met", "tolerance_profile", "next_actions"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_tithi_pravesha_parity",
  "Tithi Pravesha parity",
  "Annual return rows",
  "tithiPraveshaParitySummary",
  "tithiPraveshaParityActions",
  "checked_fields",
  "failed_fields",
  "missing_fields",
  "skipped_fields",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing Tithi Pravesha parity UI marker: ${marker}`);
}

const tithiSlice = sliceBetween(panel, "const tithiPraveshaParity", "const plFailedCount");
for (const marker of ["Р Вµ", "Р Р…", "Р С•", "Р Т‘", "РЎРѓ", "РЎвЂ ", "Р’В·", "пїЅ"]) {
  assert(!tithiSlice.includes(marker), `Tithi Pravesha parity slice contains mojibake marker: ${marker}`);
}

for (const forbidden of [
  "field_results",
  "expected",
  "actual",
  "sources_present",
  "source_report",
  "authority",
  "authoritative",
  "seal_witness_case",
  "mark_",
  "--ack-diff-open",
]) {
  assert(!tithiSlice.includes(forbidden), `Tithi Pravesha parity slice must not expose ${forbidden}`);
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
      "backend/apps/calculations/graha_drishti.py",
      "backend/apps/calculations/rashi_drishti.py",
      "backend/apps/calculations/transit_coordinates.py",
      "backend/apps/calculations/workflows.py",
      "backend/apps/calculations/witness_tithi_pravesha_parity.py",
    ].includes(changed),
    `Formula/workflow/report implementation file changed during Tithi Pravesha parity UI stage: ${changed}`,
  );
}

console.log("Accuracy Tithi Pravesha parity UI check passed.");
