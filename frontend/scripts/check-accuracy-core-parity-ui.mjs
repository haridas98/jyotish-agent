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

for (const marker of ["witness_core_parity", "target_met", "next_actions", "tolerance_profile"]) {
  assert(api.includes(marker), `WitnessSummary type missing ${marker}`);
}

for (const marker of [
  "witness_core_parity",
  "target_met",
  "Core parity",
  "Сверка ядра",
  "passed_count",
  "failed_count",
  "comparable_count",
  "target_reviewed_count",
  "next_actions",
  "coreParityActions",
]) {
  assert(panel.includes(marker), `AccuracyReportPanel missing core parity UI marker: ${marker}`);
}

for (const marker of ["РЎ", "Рџ", "РІ", "Рћ", "Рљ", "В·", "�"]) {
  assert(!panel.includes(marker), `AccuracyReportPanel contains mojibake marker: ${marker}`);
}

for (const forbidden of [
  "field_results",
  "expected",
  "actual",
  "source_report",
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
  assert(!changed.startsWith("backend/"), `Backend/calculation file changed during UI-only stage: ${changed}`);
}

console.log("Accuracy core parity UI check passed.");
