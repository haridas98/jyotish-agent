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
const preflightSlice = sliceBetween(panel, "Core review preflight", "accuracy-summary-grid witness-summary-grid");
const helperSlice = sliceBetween(roadmap, "export function buildCoreReviewPreflightBlocker", "function skippedCount");

for (const marker of [
  "Core review preflight",
  "Core review progress",
  "Core review batch scan",
  "Core evidence backlog",
  "Core evidence intake plan",
  "Core evidence pipeline",
  "Core evidence readiness",
  "operator packet manifest",
  "Evidence backlog",
  "coreReviewPreflightBlocker",
  "coreReviewProgress",
  "coreReviewBatchScan",
  "coreEvidenceBacklog",
  "coreEvidenceIntakePlan",
  "coreEvidencePipeline",
  "coreEvidenceReadiness",
  "buildCoreReviewPreflightBlocker",
  "buildCoreReviewProgress",
  "buildCoreReviewBatchScan",
  "buildCoreEvidenceBacklog",
  "buildCoreEvidenceIntakePlan",
  "buildCoreEvidencePipeline",
  "buildCoreEvidenceReadiness",
  "witness_core_parity",
  "sterlitamak-1998-04-30-1345",
  "P51-A",
  "P53-A",
  "P55-A",
  "P57-A",
  "jyotish-core-evidence-backlog-v1",
  "jyotish-core-evidence-intake-plan-v1",
  "jyotish-core-evidence-readiness-preflight-v1",
  "vrindavan-1990-08-15-1024",
  "delhi-india-1947-08-15-000001",
  "mayapur-2001-02-03-0910",
  "new-york-2026-03-08-0155",
  "new-york-2026-11-01-0130",
  "mayapur-2026-01-01-0000",
  "jhora_missing_or_blocked",
  "parashara_light_missing_or_blocked",
  "jhora_screenshot_or_packet",
  "parashara_light_manual_values_or_packet",
  "missing",
  "blocked_missing_evidence",
  "ready_to_mark=false",
  "Evidence must be collected and attached before mark commands are attempted",
  "collect_jhora_screenshot",
  "attach_parashara_light_manual_values",
  "rerun_preflight_witness_review",
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
  "coreEvidenceBacklog.stage",
  "coreEvidenceBacklog.schemaVersion",
  "coreEvidenceBacklog.backlogRows",
  "coreEvidenceBacklog.blockedRows",
  "coreEvidenceBacklog.readyToMarkRows",
  "coreEvidenceBacklog.remainingNotReviewedRows",
  "coreEvidenceBacklog.jhoraEvidenceBacklog",
  "coreEvidenceBacklog.parasharaLightEvidenceBacklog",
  "coreEvidenceBacklog.firstBacklogCaseId",
  "coreEvidenceBacklog.lastBacklogCaseId",
  "coreEvidenceBacklog.nextActions",
  "coreEvidenceIntakePlan.stage",
  "coreEvidenceIntakePlan.schemaVersion",
  "coreEvidenceIntakePlan.intakeRows",
  "coreEvidenceIntakePlan.readyToMarkRows",
  "coreEvidenceIntakePlan.evidenceFilesCommitted",
  "coreEvidenceIntakePlan.remainingNotReviewedRows",
  "coreEvidenceIntakePlan.selectedCaseIds",
  "coreEvidenceIntakePlan.evidenceSlotStatus",
  "coreEvidenceIntakePlan.safeNextActions",
  "coreEvidenceIntakePlan.safeValidationCommandFamilies",
  "coreEvidencePipeline.latestStage",
  "coreEvidencePipeline.backlogSummary",
  "coreEvidencePipeline.intakeSummary",
  "coreEvidencePipeline.readinessSummary",
  "coreEvidencePipeline.operatorNote",
  "coreEvidenceReadiness.stage",
  "coreEvidenceReadiness.schemaVersion",
  "coreEvidenceReadiness.readinessRows",
  "coreEvidenceReadiness.operatorPacketRows",
  "coreEvidenceReadiness.readyToMarkRows",
  "coreEvidenceReadiness.blockedRows",
  "coreEvidenceReadiness.missingEvidenceSlots",
  "coreEvidenceReadiness.jhoraMissingCount",
  "coreEvidenceReadiness.parasharaLightMissingCount",
  "coreEvidenceReadiness.remainingNotReviewedRows",
  "coreEvidenceReadiness.selectedCaseIds",
  "coreEvidenceReadiness.evidenceSlotStatus",
  "coreEvidenceReadiness.readyToMarkLabel",
  "coreEvidenceReadiness.readinessStatus",
  "coreEvidenceReadiness.safeNextActions",
  "coreEvidenceReadiness.safeValidationCommandFamilies",
  "coreEvidenceReadiness.operatorNote",
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
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-backlog-v1"'), "Core evidence backlog helper must expose schema version");
assert(helperSlice.includes('stage: "P53-A"'), "Core evidence backlog helper must expose P53-A stage");
assert(helperSlice.includes("backlogRows: 20"), "Core evidence backlog helper must expose 20 backlog rows");
assert(helperSlice.includes("blockedRows: 20"), "Core evidence backlog helper must expose 20 blocked rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence backlog helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence backlog helper must expose 20 remaining rows");
assert(helperSlice.includes("jhoraEvidenceBacklog: 20"), "Core evidence backlog helper must expose 20 JHora evidence rows");
assert(helperSlice.includes("parasharaLightEvidenceBacklog: 20"), "Core evidence backlog helper must expose 20 Parashara Light evidence rows");
assert(helperSlice.includes('firstBacklogCaseId: "vrindavan-1990-08-15-1024"'), "Core evidence backlog helper must expose first backlog case");
assert(helperSlice.includes('lastBacklogCaseId: "mayapur-2026-01-01-0000"'), "Core evidence backlog helper must expose last backlog case");
assert(helperSlice.includes('"collect_jhora_screenshot"'), "Core evidence backlog helper must expose JHora evidence action");
assert(helperSlice.includes('"attach_parashara_light_manual_values"'), "Core evidence backlog helper must expose Parashara Light evidence action");
assert(helperSlice.includes('"rerun_preflight_witness_review"'), "Core evidence backlog helper must expose rerun preflight action");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-intake-plan-v1"'), "Core evidence intake helper must expose schema version");
assert(helperSlice.includes('stage: "P55-A"'), "Core evidence intake helper must expose P55-A stage");
assert(helperSlice.includes("intakeRows: 5"), "Core evidence intake helper must expose 5 intake rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence intake helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("evidenceFilesCommitted: 0"), "Core evidence intake helper must expose 0 committed evidence files");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence intake helper must expose 20 remaining rows");
assert(helperSlice.includes('"delhi-india-1947-08-15-000001"'), "Core evidence intake helper must expose second selected case");
assert(helperSlice.includes('"mayapur-2001-02-03-0910"'), "Core evidence intake helper must expose third selected case");
assert(helperSlice.includes('"new-york-2026-03-08-0155"'), "Core evidence intake helper must expose fourth selected case");
assert(helperSlice.includes('"new-york-2026-11-01-0130"'), "Core evidence intake helper must expose fifth selected case");
assert(helperSlice.includes('jhora_screenshot_or_packet: "missing"'), "Core evidence intake helper must expose missing JHora slot");
assert(helperSlice.includes('parashara_light_manual_values_or_packet: "missing"'), "Core evidence intake helper must expose missing Parashara Light slot");
assert(accuracyRoute.includes("jyotish-core-evidence-backlog-v1"), "Accuracy route marker must expose P53 backlog schema");
assert(accuracyRoute.includes("jyotish-core-evidence-intake-plan-v1"), "Accuracy route marker must expose P55 intake schema");
assert(accuracyRoute.includes("evidence files committed 0"), "Accuracy route marker must expose committed evidence file count");
assert(accuracyRoute.includes("ready-to-mark 0"), "Accuracy route marker must expose ready-to-mark count");
assert(helperSlice.includes('latestStage: "P57-A"'), "Core evidence pipeline helper must expose latest P57 stage");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-readiness-preflight-v1"'), "Core evidence readiness helper must expose schema version");
assert(helperSlice.includes('stage: "P57-A"'), "Core evidence readiness helper must expose P57-A stage");
assert(helperSlice.includes("readinessRows: 5"), "Core evidence readiness helper must expose 5 readiness rows");
assert(helperSlice.includes("operatorPacketRows: 5"), "Core evidence readiness helper must expose 5 operator packet rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence readiness helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("blockedRows: 5"), "Core evidence readiness helper must expose 5 blocked rows");
assert(helperSlice.includes("missingEvidenceSlots: 10"), "Core evidence readiness helper must expose 10 missing evidence slots");
assert(helperSlice.includes("jhoraMissingCount: 5"), "Core evidence readiness helper must expose 5 JHora missing rows");
assert(helperSlice.includes("parasharaLightMissingCount: 5"), "Core evidence readiness helper must expose 5 Parashara Light missing rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence readiness helper must expose 20 remaining rows");
assert(helperSlice.includes('readinessStatus: "blocked_missing_evidence"'), "Core evidence readiness helper must expose blocked missing evidence status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence readiness helper must expose false ready-to-mark label");
assert(helperSlice.includes("Evidence must be collected and attached before mark commands are attempted"), "Core evidence readiness helper must expose blocked operator note");
assert(preflightSlice.includes("P53 backlog") && preflightSlice.includes("P55 intake") && preflightSlice.includes("P57 readiness"), "Core evidence pipeline UI must render all three stages");
assert(preflightSlice.includes("operator packet manifest"), "Core evidence readiness UI must expose operator packet manifest");
assert(accuracyRoute.includes("Core evidence pipeline"), "Accuracy route marker must expose core evidence pipeline");
assert(accuracyRoute.includes("jyotish-core-evidence-readiness-preflight-v1"), "Accuracy route marker must expose P57 readiness schema");
assert(accuracyRoute.includes("5 operator packet rows"), "Accuracy route marker must expose operator packet row count");
assert(accuracyRoute.includes("10 missing evidence slots"), "Accuracy route marker must expose missing evidence slot count");
assert(accuracyRoute.includes("blocked_missing_evidence"), "Accuracy route marker must expose blocked evidence status");
assert(accuracyRoute.includes("ready_to_mark=false"), "Accuracy route marker must expose false ready-to-mark state");
assert(accuracyRoute.includes("Evidence must be collected and attached before mark commands are attempted"), "Accuracy route marker must expose blocked operator note");

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
  "evidence available",
  "release ready",
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
