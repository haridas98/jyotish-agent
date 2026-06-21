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
  "coreReviewPreflightBlocker",
  "buildCoreReviewPreflightBlocker",
  "witness_core_parity",
  "not-reviewed witness rows",
  "source family coverage",
  "both",
  "release remains blocked",
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
]) {
  assert(preflightSlice.includes(marker), `Core review preflight UI must render helper data: ${marker}`);
}

assert(helperSlice.includes("notReviewedRows: 21"), "Core review preflight helper must expose 21 not-reviewed rows");
assert(helperSlice.includes('sourceFamilyCoverage: "both"'), "Core review preflight helper must expose both source family coverage");
assert(preflightSlice.includes("join(\" - \")"), "Core review preflight command families should render as compact joined helper data");

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
