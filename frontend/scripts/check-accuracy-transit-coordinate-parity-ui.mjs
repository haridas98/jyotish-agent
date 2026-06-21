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

for (const marker of ["witness_transit_coordinate_parity", "layer_summary", "body_summary", "target_met", "tolerance_profile", "next_actions"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_transit_coordinate_parity",
  "Transit coordinate parity",
  "Lagna / graha coordinates",
  "transitCoordinateParitySummary",
  "transitCoordinateParityActions",
  "transitCoordinateParityTolerance",
  "checked_bodies",
  "matched_bodies",
  "failed_bodies",
  "missing_bodies",
  "skipped_bodies",
  "checked_fields",
  "failed_fields",
  "missing_fields",
  "skipped_fields",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing Transit coordinate parity UI marker: ${marker}`);
}

const transitCoordinateSlice = sliceBetween(panel, "const transitCoordinateParity", "const plFailedCount");
for (const marker of ["Р В Р’Вµ", "Р В Р вЂ¦", "Р В РЎвЂў", "Р В РўвЂ", "Р РЋР С“", "Р РЋРІР‚В ", "Р вЂ™Р’В·", "РїС—Р…"]) {
  assert(!transitCoordinateSlice.includes(marker), `Transit coordinate parity slice contains mojibake marker: ${marker}`);
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
  assert(!transitCoordinateSlice.includes(forbidden), `Transit coordinate parity slice must not expose ${forbidden}`);
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
    ].includes(changed),
    `Formula/calculation file changed during Transit coordinate parity UI stage: ${changed}`,
  );
}

console.log("Accuracy Transit coordinate parity UI check passed.");
