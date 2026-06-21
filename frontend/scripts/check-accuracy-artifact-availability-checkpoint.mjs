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
const checkpointSlice = sliceBetween(panel, "Artifact availability checkpoint", "JHora");
const helperSlice = sliceBetween(roadmap, "export function buildArtifactAvailabilityCheckpoint", "function skippedCount");

for (const marker of [
  "Artifact availability checkpoint",
  "artifactAvailabilityCheckpoint",
  "buildArtifactAvailabilityCheckpoint",
  "environment artifact availability",
  "total witness domains",
  "available/review rows",
  "missing reports",
  "collect reports",
  "review witness rows",
  "release gate: blocked",
  "command smoke matrix: ready",
  "local dev can show 19/19/0",
  "production can show 19/19/0",
  "committed artifact availability is aligned",
  "release remains blocked by review witness rows",
]) {
  assert(checkpointSlice.includes(marker) || helperSlice.includes(marker) || accuracyRoute.includes(marker), `Artifact availability checkpoint marker missing: ${marker}`);
}

for (const marker of [
  "artifactAvailabilityCheckpoint.totals.domainCount",
  "artifactAvailabilityCheckpoint.totals.availableReviewRows",
  "artifactAvailabilityCheckpoint.totals.missingReports",
  "artifactAvailabilityCheckpoint.totals.collectReports",
  "artifactAvailabilityCheckpoint.releaseGateStatus",
  "artifactAvailabilityCheckpoint.commandSmokeMatrixStatus",
]) {
  assert(checkpointSlice.includes(marker), `Artifact checkpoint counts must render from helper totals/status: ${marker}`);
}

for (const stale of ["19/17/2", "19/15/4", "19/12/7", "19/10/9", "19/7/12", "19/5/14"]) {
  assert(!page.includes(stale), `Artifact checkpoint source must not keep stale count ${stale}`);
  assert(!roadmap.includes(stale), `Artifact checkpoint helper must not keep stale count ${stale}`);
  assert(!accuracyRoute.includes(stale), `Artifact checkpoint route marker must not keep stale count ${stale}`);
}

for (const forbidden of [
  "complete",
  "ready for release",
  "verified parity",
  "accepted parity",
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
  assert(!checkpointSlice.includes(forbidden), `Artifact checkpoint slice must not expose or imply ${forbidden}`);
  assert(!helperSlice.includes(forbidden), `Artifact checkpoint helper must not expose or imply ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!checkpointSlice.includes(marker), `Artifact checkpoint must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only artifact checkpoint stage: ${changed}`);
  assert(!changed.startsWith("deploy/"), `Deploy file changed during frontend-only artifact checkpoint stage: ${changed}`);
  assert(!changed.startsWith(".github/"), `Workflow file changed during frontend-only artifact checkpoint stage: ${changed}`);
}

console.log("Accuracy artifact availability checkpoint check passed.");
