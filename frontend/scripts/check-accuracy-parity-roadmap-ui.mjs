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
const accuracyPage = readFileSync(new URL("../src/app/accuracy/page.tsx", import.meta.url), "utf8");
const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");
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
  assert(accuracyPage.includes(marker), `Rendered accuracy route finite-scope marker missing: ${marker}`);
}

assert(roadmapSlice.includes("Finite JH/PL scope"), "Parity roadmap must show a product-facing finite-scope label.");
assert(roadmapSlice.includes("next evidence gate"), "Parity roadmap must show the next concrete evidence gate.");
assert(accuracyPage.includes("Finite JH/PL scope"), "Accuracy route must expose the finite-scope label.");
assert(accuracyPage.includes("next evidence gate"), "Accuracy route must expose the next concrete evidence gate.");

for (const marker of [
  "buildParityEvidenceRequirementClarity",
  "P111-A",
  "parity_evidence_requirement_status=blocked_pending_human_provided_jh_pl_evidence",
  "jhora_evidence_required=human_provided_screenshots_or_receipt_manifests",
  "parashara_light_evidence_required=human_provided_manual_values_or_receipt_manifests",
  "no_credentials_or_files_required_now=true",
  "parity_success_claimed=false",
  "release_ready=false",
  "release_gate_status=blocked",
]) {
  assert(roadmap.includes(marker) || accuracyPage.includes(marker), `P111 evidence requirement marker missing: ${marker}`);
}

for (const copy of [
  "JHora: human-provided screenshots or receipt manifests",
  "Parashara Light: human-provided manual values or receipt manifests",
  "No credentials or files are needed now",
]) {
  assert(accuracyPage.includes(copy), `Accuracy route evidence requirement copy missing: ${copy}`);
}

for (const marker of [
  "buildParityEvidenceTemplateChecklist",
  "P113-A",
  "parity_evidence_template_status=blocked_pending_human_provided_evidence_templates",
  "evidence_template_source_family=JHora",
  "evidence_template_source_family=Parashara Light",
  "evidence_template_artifact_kind=jhora_screenshots_or_receipt_manifest",
  "evidence_template_artifact_kind=parashara_light_manual_values_or_receipt_manifest",
  "evidence_template_status=pending_human_provided_evidence",
  "no_collection_upload_or_external_delivery_executed=true",
  "no_external_action_executed=true",
  "parity_success_claimed=false",
  "release_ready=false",
  "release_gate_status=blocked",
]) {
  assert(roadmap.includes(marker) || accuracyPage.includes(marker), `P113 evidence template marker missing: ${marker}`);
}

for (const copy of [
  "Evidence template",
  "What to provide later",
  "JHora",
  "screenshots / receipt manifest",
  "Parashara Light",
  "manual values / receipt manifest",
  "pending human-provided evidence",
  "No collection, upload, or external delivery is executed by the app in this stage.",
]) {
  assert(accuracyPage.includes(copy), `Accuracy route evidence template copy missing: ${copy}`);
}

for (const marker of [
  "E114-A",
  "data-parity-evidence-template-stage=\"E114-A\"",
  "blocked: pending human evidence",
  "parity-evidence-template",
  "parity-evidence-template-grid",
  "parity-evidence-template-mobile-safe=true",
  "no_horizontal_overflow_expected=true",
  "no_external_action_executed=true",
  "parity_success_claimed=false",
  "release_ready=false",
  "release_gate_status=blocked",
]) {
  assert(accuracyPage.includes(marker) || roadmap.includes(marker), `E114 evidence template UI marker missing: ${marker}`);
}

assert(css.includes(".parity-evidence-template-grid"), "E114 evidence template grid CSS marker missing.");
assert(css.includes("@media (max-width: 640px)") && css.includes(".parity-evidence-template-grid"), "E114 evidence template must include mobile responsive CSS.");
assert(!accuracyPage.includes("<input") || !accuracyPage.includes("type=\"file\""), "E114 evidence template must not add file inputs.");
assert(!accuracyPage.includes("<form"), "E114 evidence template must not add submit forms.");

for (const marker of [
  "buildParityNextBlockerCapSummary",
  "P115-A",
  "parity_next_blocker_status=blocked_pending_human_evidence_and_witness_review",
  "internal_parity_micro_chain_capped=true",
  "no_additional_internal_parity_substage_started=true",
  "parity_success_claimed=false",
  "release_ready=false",
  "release_gate_status=blocked",
  "no_external_action_executed=true",
]) {
  assert(roadmap.includes(marker) || accuracyPage.includes(marker), `P115 next-blocker cap marker missing: ${marker}`);
}

for (const copy of [
  "Next parity blocker",
  "human-provided JHora/Parashara Light evidence and witness review",
  "Internal parity micro-chain is capped",
  "No additional internal parity substage starts before evidence/review is available",
  "Release remains blocked",
]) {
  assert(accuracyPage.includes(copy), `Accuracy route P115 next-blocker cap copy missing: ${copy}`);
}

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
