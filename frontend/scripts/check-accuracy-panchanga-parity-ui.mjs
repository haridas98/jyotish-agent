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

for (const marker of ["witness_panchanga_parity", "field_summary", "target_met", "next_actions"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_panchanga_parity",
  "Panchanga parity",
  "Tithi / Vara / Yoga",
  "panchangaParitySummary",
  "panchangaParityActions",
  "field_summary",
  "checked_fields",
  "not_comparable_count",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing panchanga parity UI marker: ${marker}`);
}

for (const marker of ["Рµ", "РЅ", "Рѕ", "Рґ", "СЃ", "С†", "В·", "�"]) {
  assert(!panel.includes(marker), `AccuracyReportPanel contains mojibake marker: ${marker}`);
}

for (const forbidden of [
  "field_results",
  "expected",
  "actual",
  "source_report",
  "sources_present",
  "authority",
  "authoritative",
  "longitude",
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
      "backend/apps/calculations/panchanga.py",
      "backend/apps/calculations/chart.py",
      "backend/apps/calculations/vimshottari.py",
      "backend/apps/calculations/dasha_systems.py",
      "backend/apps/calculations/vargas.py",
      "backend/apps/calculations/ephemeris.py",
      "backend/apps/calculations/math.py",
    ].includes(changed),
    `Formula/calculation file changed during panchanga parity UI stage: ${changed}`,
  );
}

console.log("Accuracy panchanga parity UI check passed.");
