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

const roadmap = readFileSync(new URL("../src/lib/parity-roadmap.ts", import.meta.url), "utf8");
const page = readFileSync(new URL("../src/app/page.tsx", import.meta.url), "utf8");
const panel = sliceBetween(page, "function AccuracyReportPanel", "export default function Home");
const checklistSlice = sliceBetween(panel, "Parity collection checklist", "JHora");
const collectionHelperSlice = sliceBetween(roadmap, "const parityCollectionCommandByKey", "function skippedCount");

for (const marker of [
  "Parity collection checklist",
  "collectionChecklistTotals",
  "parityCollectionChecklistRows",
  "buildParityCollectionChecklistRows",
  "collectionHint",
  "<report-json>",
  "ready:",
  "review:",
  "waiting:",
]) {
  assert(collectionHelperSlice.includes(marker) || checklistSlice.includes(marker), `Collection checklist marker missing: ${marker}`);
}

for (const command of [
  "build_witness_core_parity_report",
  "build_witness_varga_parity_report",
  "build_witness_dasha_parity_report",
  "build_witness_panchanga_parity_report",
  "build_witness_ashtakavarga_parity_report",
  "build_witness_strengths_parity_report",
  "build_witness_yoga_parity_report",
  "build_witness_special_points_parity_report",
  "build_witness_argala_parity_report",
  "build_witness_avastha_parity_report",
  "build_witness_drishti_parity_report",
  "build_witness_transit_coordinates_parity_report",
  "build_witness_compatibility_parity_report",
  "build_witness_muhurta_parity_report",
  "build_witness_tithi_pravesha_parity_report",
  "build_witness_tajaka_parity_report",
  "build_witness_prashna_parity_report",
  "build_witness_jaimini_karaka_parity_report",
  "build_witness_jaimini_varga_parity_report",
]) {
  assert(collectionHelperSlice.includes(command), `Collection command marker missing: ${command}`);
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
  "C:\\",
  "/Users/",
  "/home/",
]) {
  assert(!checklistSlice.includes(forbidden), `Collection checklist slice must not expose ${forbidden}`);
  assert(!collectionHelperSlice.includes(forbidden), `Collection roadmap helper must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!checklistSlice.includes(marker), `Collection checklist must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only checklist stage: ${changed}`);
  assert(!changed.startsWith("deploy/"), `Deploy file changed during frontend-only checklist stage: ${changed}`);
  assert(!changed.startsWith(".github/"), `Workflow file changed during frontend-only checklist stage: ${changed}`);
}

console.log("Accuracy parity collection checklist UI check passed.");
