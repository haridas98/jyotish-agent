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
const releaseSlice = sliceBetween(panel, "Release gate action summary", "JHora");
const releaseHelperSlice = sliceBetween(roadmap, "export function buildReleaseGateActionSummary", "function skippedCount");

for (const marker of [
  "Release gate action summary",
  "releaseGateActionSummary",
  "buildReleaseGateActionSummary",
  "collectReports",
  "reviewRows",
  "readyDemo",
  "collect report",
  "review witness rows",
  "ready for demo",
  "command smoke matrix: ready",
]) {
  assert(releaseSlice.includes(marker) || releaseHelperSlice.includes(marker) || accuracyRoute.includes(marker), `Release gate action marker missing: ${marker}`);
}
assert(roadmap.includes("<report-json>") || accuracyRoute.includes("&lt;report-json&gt;"), "Release gate actions must use <report-json> placeholder");
assert(releaseSlice.includes("collectionHint"), "Release gate collect rows must render safe collection hints");

for (const marker of [
  "releaseGateActionSummary.totals.collectReports",
  "releaseGateActionSummary.totals.reviewRows",
  "releaseGateActionSummary.totals.readyDemo",
]) {
  assert(releaseSlice.includes(marker), `Release gate counts must render from helper totals: ${marker}`);
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
  assert(!releaseSlice.includes(forbidden), `Release gate action slice must not expose ${forbidden}`);
  assert(!releaseHelperSlice.includes(forbidden), `Release gate helper slice must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!releaseSlice.includes(marker), `Release gate action summary must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only release gate action stage: ${changed}`);
  assert(!changed.startsWith("deploy/"), `Deploy file changed during frontend-only release gate action stage: ${changed}`);
  assert(!changed.startsWith(".github/"), `Workflow file changed during frontend-only release gate action stage: ${changed}`);
}

console.log("Accuracy release gate action summary check passed.");
