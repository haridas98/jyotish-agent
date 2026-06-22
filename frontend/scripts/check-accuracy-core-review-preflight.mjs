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
const preflightSlice = sliceBetween(panel, "Core review preflight", "JHora");
const helperSlice = sliceBetween(roadmap, "export function buildCoreReviewPreflightBlocker", "function skippedCount");

for (const marker of [
  "Core review preflight",
  "Core review progress",
  "Core review batch scan",
  "Evidence backlog",
  "coreReviewPreflightBlocker",
  "coreReviewProgress",
  "coreReviewBatchScan",
  "buildCoreReviewPreflightBlocker",
  "buildCoreReviewProgress",
  "buildCoreReviewBatchScan",
  "witness_core_parity",
  "sterlitamak-1998-04-30-1345",
  "P51-A",
  "vrindavan-1990-08-15-1024",
  "mayapur-2026-01-01-0000",
  "jhora_missing_or_blocked",
  "parashara_light_missing_or_blocked",
  "evidence/manual values are missing or blocked",
  "collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands",
  "not-reviewed witness rows",
  "source family coverage",
  "both",
  "release remains blocked",
  "real diff",
  "preflight_witness_review",
  "mark_jhora_witness_reviewed",
  "mark_parashara_light_witness_reviewed",
]) {
  assert(preflightSlice.includes(marker) || helperSlice.includes(marker) || accuracyRoute.includes(marker), `Core review preflight marker missing: ${marker}`);
}

for (const marker of [
  "coreReviewPreflightBlocker.domainKey",
  "coreReviewPreflightBlocker.notReviewedRows",
  "coreReviewPreflightBlocker.sourceFamilyCoverage",
  "coreReviewPreflightBlocker.releaseGateStatus",
  "coreReviewPreflightBlocker.safeCommandFamilies",
  "coreReviewProgress.targetCaseId",
  "coreReviewProgress.reviewedRows",
  "coreReviewProgress.remainingNotReviewedRows",
  "coreReviewProgress.comparableRows",
  "coreReviewProgress.failedRows",
  "coreReviewProgress.maxAbsDeltaArcseconds",
  "coreReviewBatchScan.stage",
  "coreReviewBatchScan.requestedCloseCount",
  "coreReviewBatchScan.scannedCandidates",
  "coreReviewBatchScan.closedRows",
  "coreReviewBatchScan.skippedRows",
  "coreReviewBatchScan.remainingNotReviewedRows",
  "coreReviewBatchScan.firstSkippedCaseId",
  "coreReviewBatchScan.lastSkippedCaseId",
  "coreReviewBatchScan.blockerLabels",
  "coreReviewBatchScan.safeCommandFamilies",
]) {
  assert(preflightSlice.includes(marker), `Core review preflight UI must render helper data: ${marker}`);
}

assert(helperSlice.includes("notReviewedRows: 20"), "Core review preflight helper must expose 20 remaining not-reviewed rows");
assert(!helperSlice.includes("notReviewedRows: 21"), "Core review preflight helper must not expose stale 21 count");
assert(!accuracyRoute.includes("21 not-reviewed witness rows"), "Accuracy route marker must not expose stale 21 count");
assert(helperSlice.includes('sourceFamilyCoverage: "both"'), "Core review preflight helper must expose both source family coverage");
assert(preflightSlice.includes("join(\" - \")"), "Core review preflight command families should render as compact joined helper data");
assert(helperSlice.includes("reviewedRows: 1"), "Core review progress helper must expose one reviewed row");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core review progress helper must expose 20 remaining rows");
assert(helperSlice.includes("comparableRows: 1"), "Core review progress helper must expose one comparable row");
assert(helperSlice.includes("failedRows: 1"), "Core review progress helper must expose one failed row");
assert(helperSlice.includes("maxAbsDeltaArcseconds: 94.064472"), "Core review progress helper must expose max delta");
assert(helperSlice.includes('stage: "P51-A"'), "Core review batch scan helper must expose P51-A stage");
assert(helperSlice.includes("requestedCloseCount: 5"), "Core review batch scan helper must expose requested close count 5");
assert(helperSlice.includes("scannedCandidates: 20"), "Core review batch scan helper must expose 20 scanned candidates");
assert(helperSlice.includes("closedRows: 0"), "Core review batch scan helper must expose 0 closed rows");
assert(helperSlice.includes("skippedRows: 20"), "Core review batch scan helper must expose 20 skipped rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core review batch scan helper must expose 20 remaining rows");
assert(helperSlice.includes('firstSkippedCaseId: "vrindavan-1990-08-15-1024"'), "Core review batch scan helper must expose first skipped case");
assert(helperSlice.includes('lastSkippedCaseId: "mayapur-2026-01-01-0000"'), "Core review batch scan helper must expose last skipped case");
assert(helperSlice.includes('"jhora_missing_or_blocked"'), "Core review batch scan helper must expose JHora blocker label");
assert(helperSlice.includes('"parashara_light_missing_or_blocked"'), "Core review batch scan helper must expose Parashara Light blocker label");
assert(helperSlice.includes("evidence/manual values are missing or blocked"), "Core review batch scan helper must explain evidence blocker");
assert(helperSlice.includes("collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands"), "Core review batch scan helper must gate mark commands behind evidence collection");
assert(!helperSlice.includes("blocked until explicit review commands run"), "Core review batch scan helper must not retain stale mark-command wording");
assert(!preflightSlice.includes("blocked until explicit review commands run"), "Core review batch scan UI must not retain stale mark-command wording");

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
  "C:/Users",
  "/Users/",
  "/home/",
  ".env",
  "complete",
  "ready for release",
  "verified parity",
  "accepted parity",
  "JHora parity done",
  "Parashara Light parity done",
  "parity success",
]) {
  assert(!preflightSlice.includes(forbidden), `Core review preflight slice must not expose or imply ${forbidden}`);
  assert(!helperSlice.includes(forbidden), `Core review preflight helper must not expose or imply ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!preflightSlice.includes(marker), `Core review preflight must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only core review preflight stage: ${changed}`);
  assert(!changed.startsWith("deploy/"), `Deploy file changed during frontend-only core review preflight stage: ${changed}`);
  assert(!changed.startsWith(".github/"), `Workflow file changed during frontend-only core review preflight stage: ${changed}`);
  assert(!changed.startsWith(".tmp/"), `Artifact file changed during frontend-only core review preflight stage: ${changed}`);
}

console.log("Accuracy core review preflight check passed.");
