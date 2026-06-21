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

for (const marker of ["witness_jaimini_varga_parity", "varga_summary", "field_summary", "readiness_summary", "actual_missing", "target_met", "next_actions"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_jaimini_varga_parity",
  "Jaimini varga parity",
  "D5/D6/D8/D11 readiness",
  "jaiminiVargaParitySummary",
  "jaiminiVargaParityActions",
  "checked_vargas",
  "failed_vargas",
  "missing_vargas",
  "skipped_vargas",
  "checked_fields",
  "failed_fields",
  "missing_fields",
  "skipped_fields",
  "jaiminiVargaParityReadinessMissing",
  "compared",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing Jaimini varga parity UI marker: ${marker}`);
}

const jaiminiVargaSlice = sliceBetween(panel, "const jaiminiVargaParity", "const hasOpenAccuracyItems");
for (const marker of ["Рµ", "РЅ", "Рѕ", "Рґ", "СЃ", "С†", "В·", "�"]) {
  assert(!jaiminiVargaSlice.includes(marker), `Jaimini varga parity slice contains mojibake marker: ${marker}`);
}

for (const forbidden of [
  "field_results",
  '"expected"',
  '"actual"',
  "sources_present",
  "source_report",
  "authority",
  "authoritative",
  "seal_witness_case",
  "mark_",
  "--ack-diff-open",
]) {
  assert(!jaiminiVargaSlice.includes(forbidden), `Jaimini varga parity slice must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!jaiminiVargaSlice.includes(marker), `Jaimini varga parity slice must not add network call marker ${marker}`);
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
      "backend/apps/calculations/witness_jaimini_varga_parity.py",
      "backend/apps/calculations/management/commands/build_witness_jaimini_varga_parity_report.py",
    ].includes(changed),
    `Formula/workflow/report implementation file changed during Jaimini varga parity UI stage: ${changed}`,
  );
}

console.log("Accuracy Jaimini varga parity UI check passed.");
