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
const roadmapSlice = sliceBetween(panel, "Parity roadmap", "JHora");
const subtitleMatch = roadmapSlice.match(/<p>\s*JH\/PL launch ledger\s*<\/p>/);
assert(Boolean(subtitleMatch), "Parity roadmap subtitle must render exactly JH/PL launch ledger in its own paragraph");
assert(
  !roadmapSlice.includes("JH/PL launch ledger ·") && !roadmapSlice.includes("JH/PL launch ledger:"),
  "Parity roadmap subtitle must not include counters or suffix text",
);
assert(roadmapSlice.includes("integrated:") && roadmapSlice.includes("ready:"), "Parity roadmap counters must render separately from subtitle");

for (const marker of [
  "buildParityFiniteScopeCheckpoint",
  "P109-A",
  "bounded_parity_scope=true",
  "parity_roadmap_total_items=19",
  "parity_roadmap_pending_or_blocked_count=",
  "next_concrete_evidence_gate=human_provided_external_receipt_manifests",
  "parity_success_claimed=false",
  "release_ready=false",
  "release_gate_status=blocked",
]) {
  assert(roadmap.includes(marker) || roadmapSlice.includes(marker), `Finite-scope parity checkpoint marker missing: ${marker}`);
}

assert(roadmapSlice.includes("Finite JH/PL scope"), "Parity roadmap must show a product-facing finite-scope label.");
assert(roadmapSlice.includes("next evidence gate"), "Parity roadmap must show the next concrete evidence gate.");

for (const marker of [
  "Parity roadmap",
  "JH/PL launch ledger",
  "parityRoadmapItems",
  "buildParityRoadmapRows",
  "Core parity",
  "Varga parity",
  "Dasha parity",
  "Panchanga parity",
  "Ashtakavarga parity",
  "Strengths parity",
  "Yoga parity",
  "Special points parity",
  "Argala parity",
  "Avastha parity",
  "Drishti parity",
  "Transit coordinate parity",
  "Compatibility parity",
  "Muhurta parity",
  "Tithi Pravesha parity",
  "Tajaka parity",
  "Prashna parity",
  "Jaimini karaka parity",
  "Jaimini varga parity",
  "ready",
  "review",
  "waiting",
]) {
  assert(roadmap.includes(marker) || panel.includes(marker), `Parity roadmap marker missing: ${marker}`);
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
  "verified parity",
  "accepted parity",
  "JHora parity done",
  "Parashara Light parity done",
  "parity success",
  "release ready",
  "external notification sent",
  "ticket created",
  "upload executed",
]) {
  assert(!roadmapSlice.includes(forbidden), `Parity roadmap slice must not expose ${forbidden}`);
}

for (const marker of ["fetch(", "axios", "XMLHttpRequest"]) {
  assert(!roadmapSlice.includes(marker), `Parity roadmap must not add network call marker ${marker}`);
}

const changedFiles = execFileSync("git", ["diff", "--name-only"], { encoding: "utf8" })
  .split(/\r?\n/)
  .filter(Boolean);
for (const changed of changedFiles) {
  assert(!changed.startsWith("backend/"), `Backend file changed during frontend-only parity roadmap stage: ${changed}`);
}

console.log("Accuracy parity roadmap UI check passed.");
