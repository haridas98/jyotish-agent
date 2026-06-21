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
const accuracyRoute = readFileSync(new URL("../src/app/accuracy/page.tsx", import.meta.url), "utf8");
const panel = sliceBetween(page, "function AccuracyReportPanel", "export default function Home");
const runbookSlice = sliceBetween(panel, "Collection plan snapshot runbook", "JHora");
const runbookHelperSlice = sliceBetween(roadmap, "export function buildCollectionPlanSnapshotRunbook", "function skippedCount");

for (const marker of [
  "Collection plan snapshot runbook",
  "witness-parity-collection-plan.v1",
  "build_witness_parity_collection_plan_report --output <report-json>",
  "dry-run plan",
  "does not collect or generate reports",
  "collectionPlanRunbook",
  "buildCollectionPlanSnapshotRunbook",
]) {
  assert(runbookSlice.includes(marker) || runbookHelperSlice.includes(marker) || accuracyRoute.includes(marker), `Collection plan runbook marker missing: ${marker}`);
}

for (const marker of [
  "collectionPlanRunbook.totals.domainCount",
  "collectionPlanRunbook.totals.collectReports",
  "collectionPlanRunbook.totals.reviewRows",
  "collectionPlanRunbook.totals.readyDemo",
  "collectionPlanRunbook.releaseGateStatus",
]) {
  assert(runbookSlice.includes(marker), `Collection plan counts must render from helper totals: ${marker}`);
}

for (const marker of [
  "rows.length",
  "releaseGateActionSummary.totals.collectReports",
  "releaseGateActionSummary.totals.reviewRows",
  "releaseGateActionSummary.totals.readyDemo",
]) {
  assert(runbookHelperSlice.includes(marker), `Collection plan helper must derive counts from existing rows/summary: ${marker}`);
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
  assert(!runbookSlice.includes(forbidden), `Collection plan runbook slice must not expose ${forbidden}`);
  assert(!runbookHelperSlice.includes(forbidden), `Collection plan runbook helper must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!runbookSlice.includes(marker), `Collection plan runbook must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only collection plan runbook stage: ${changed}`);
  assert(!changed.startsWith("deploy/"), `Deploy file changed during frontend-only collection plan runbook stage: ${changed}`);
  assert(!changed.startsWith(".github/"), `Workflow file changed during frontend-only collection plan runbook stage: ${changed}`);
}

console.log("Accuracy collection plan runbook check passed.");
