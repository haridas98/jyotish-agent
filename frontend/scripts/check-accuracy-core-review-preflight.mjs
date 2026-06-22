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
  "Core evidence attachment gate",
  "Core evidence attachment work orders",
  "Core evidence attachment handoff",
  "Core evidence operator packets",
  "Core evidence operator packet QA",
  "Core evidence operator packet attachment readiness",
  "Core evidence external intake contract",
  "operator attachment manifest",
  "operator packet status",
  "operator packet QA status",
  "attachment readiness status",
  "external intake status",
  "Evidence backlog",
  "coreReviewPreflightBlocker",
  "coreReviewProgress",
  "coreReviewBatchScan",
  "coreEvidenceBacklog",
  "coreEvidenceIntakePlan",
  "coreEvidencePipeline",
  "coreEvidenceReadiness",
  "coreEvidenceAttachmentGate",
  "coreEvidenceAttachmentWorkOrders",
  "coreEvidenceAttachmentHandoff",
  "coreEvidenceOperatorPackets",
  "coreEvidenceOperatorPacketQa",
  "coreEvidenceOperatorPacketAttachmentReadiness",
  "coreEvidenceExternalIntakeContract",
  "buildCoreReviewPreflightBlocker",
  "buildCoreReviewProgress",
  "buildCoreReviewBatchScan",
  "buildCoreEvidenceBacklog",
  "buildCoreEvidenceIntakePlan",
  "buildCoreEvidencePipeline",
  "buildCoreEvidenceReadiness",
  "buildCoreEvidenceAttachmentGate",
  "buildCoreEvidenceAttachmentWorkOrders",
  "buildCoreEvidenceAttachmentHandoff",
  "buildCoreEvidenceOperatorPackets",
  "buildCoreEvidenceOperatorPacketQa",
  "buildCoreEvidenceOperatorPacketAttachmentReadiness",
  "buildCoreEvidenceExternalIntakeContract",
  "witness_core_parity",
  "sterlitamak-1998-04-30-1345",
  "P51-A",
  "P53-A",
  "P55-A",
  "P57-A",
  "P59-A",
  "P61-A",
  "P63-A",
  "P65-A",
  "P67-A",
  "P69-A",
  "P71-A",
  "jyotish-core-evidence-backlog-v1",
  "jyotish-core-evidence-intake-plan-v1",
  "jyotish-core-evidence-readiness-preflight-v1",
  "jyotish-core-evidence-attachment-gate-v1",
  "jyotish-core-evidence-attachment-work-orders-v1",
  "jyotish-core-evidence-attachment-handoff-v1",
  "jyotish-core-evidence-operator-packets-v1",
  "jyotish-core-evidence-operator-packet-qa-v1",
  "jyotish-core-evidence-operator-packet-attachment-readiness-v1",
  "jyotish-core-evidence-external-intake-contract-v1",
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
  "blocked_no_attached_evidence",
  "pending_not_attached",
  "blocked_pending_attachments",
  "blocked_pending_operator_evidence",
  "blocked_pending_operator_packet_evidence",
  "blocked_pending_operator_packet_qa",
  "blocked_pending_external_evidence_attachment",
  "blocked_pending_external_evidence_intake",
  "ready_to_attach=false",
  "ready_to_mark=false",
  "evidence_collected=false",
  "evidence_uploaded=false",
  "evidence_attached=false",
  "not_attached",
  "not_started",
  "Evidence must be attached before mark commands are attempted",
  "work orders are labels only and do not collect evidence",
  "handoff rows are labels only and do not collect evidence",
  "operator packets are labels only and do not collect or attach evidence",
  "operator packets are labels only",
  "external evidence has not been attached",
  "external evidence has not been collected, uploaded, or attached",
  "readiness rows are labels only",
  "intake rows are labels only",
  "collection/upload/mark commands are not executed",
  "mark commands remain blocked",
  "mark commands are not executed",
  "Evidence must be collected and attached before mark commands are attempted",
  "collect_jhora_screenshot",
  "attach_parashara_light_manual_values",
  "request_jhora_screenshot_or_packet",
  "request_parashara_light_manual_values_or_packet",
  "receive_external_evidence_from_human",
  "rerun_preflight_witness_review",
  "rerun_evidence_attachment_gate",
  "evidence/manual values are missing or blocked",
  "collect/attach missing JHora screenshots and Parashara Light evidence/manual values before running mark commands",
  "not-reviewed witness rows",
  "source family coverage",
  "both",
  "release remains blocked",
  "real diff",
  "preflight_witness_review",
  "build_witness_core_evidence_attachment_gate_report",
  "build_witness_core_evidence_attachment_work_orders_report",
  "build_witness_core_evidence_attachment_handoff_report",
  "build_witness_core_evidence_operator_packets_report",
  "build_witness_core_evidence_operator_packet_qa_report",
  "build_witness_core_evidence_operator_packet_attachment_readiness_report",
  "build_witness_core_evidence_external_intake_contract_report",
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
  "coreEvidenceAttachmentGate.stage",
  "coreEvidenceAttachmentGate.schemaVersion",
  "coreEvidenceAttachmentGate.attachmentRows",
  "coreEvidenceAttachmentGate.operatorAttachmentManifestRows",
  "coreEvidenceAttachmentGate.readyToMarkRows",
  "coreEvidenceAttachmentGate.blockedRows",
  "coreEvidenceAttachmentGate.missingAttachmentSlots",
  "coreEvidenceAttachmentGate.attachedEvidenceFiles",
  "coreEvidenceAttachmentGate.attachedEvidenceFamilyCount",
  "coreEvidenceAttachmentGate.jhoraAttachedCount",
  "coreEvidenceAttachmentGate.parasharaLightAttachedCount",
  "coreEvidenceAttachmentGate.jhoraMissingCount",
  "coreEvidenceAttachmentGate.parasharaLightMissingCount",
  "coreEvidenceAttachmentGate.remainingNotReviewedRows",
  "coreEvidenceAttachmentGate.selectedCaseIds",
  "coreEvidenceAttachmentGate.p57EvidenceSlotStatus",
  "coreEvidenceAttachmentGate.attachmentSlotStatus",
  "coreEvidenceAttachmentGate.readyToMarkLabel",
  "coreEvidenceAttachmentGate.attachmentGateStatus",
  "coreEvidenceAttachmentGate.safeNextActions",
  "coreEvidenceAttachmentGate.safeValidationCommandFamilies",
  "coreEvidenceAttachmentGate.operatorNote",
  "coreEvidenceAttachmentWorkOrders.stage",
  "coreEvidenceAttachmentWorkOrders.schemaVersion",
  "coreEvidenceAttachmentWorkOrders.workOrderRows",
  "coreEvidenceAttachmentWorkOrders.pendingWorkOrderCount",
  "coreEvidenceAttachmentWorkOrders.pendingJhoraWorkOrderCount",
  "coreEvidenceAttachmentWorkOrders.pendingParasharaLightWorkOrderCount",
  "coreEvidenceAttachmentWorkOrders.blockedCaseCount",
  "coreEvidenceAttachmentWorkOrders.readyToMarkRows",
  "coreEvidenceAttachmentWorkOrders.remainingNotReviewedRows",
  "coreEvidenceAttachmentWorkOrders.selectedCaseIds",
  "coreEvidenceAttachmentWorkOrders.workOrderStatus",
  "coreEvidenceAttachmentWorkOrders.caseWorkOrderStatus",
  "coreEvidenceAttachmentWorkOrders.readyToMarkLabel",
  "coreEvidenceAttachmentWorkOrders.safeValidationCommandFamilies",
  "coreEvidenceAttachmentWorkOrders.operatorNote",
  "coreEvidenceAttachmentHandoff.stage",
  "coreEvidenceAttachmentHandoff.schemaVersion",
  "coreEvidenceAttachmentHandoff.caseHandoffRows",
  "coreEvidenceAttachmentHandoff.handoffWorkOrderRows",
  "coreEvidenceAttachmentHandoff.pendingHandoffCount",
  "coreEvidenceAttachmentHandoff.pendingJhoraHandoffCount",
  "coreEvidenceAttachmentHandoff.pendingParasharaLightHandoffCount",
  "coreEvidenceAttachmentHandoff.blockedCaseCount",
  "coreEvidenceAttachmentHandoff.readyToMarkRows",
  "coreEvidenceAttachmentHandoff.remainingNotReviewedRows",
  "coreEvidenceAttachmentHandoff.selectedCaseIds",
  "coreEvidenceAttachmentHandoff.handoffStatus",
  "coreEvidenceAttachmentHandoff.caseWorkOrderStatus",
  "coreEvidenceAttachmentHandoff.readyToMarkLabel",
  "coreEvidenceAttachmentHandoff.safeValidationCommandFamilies",
  "coreEvidenceAttachmentHandoff.operatorNote",
  "coreEvidenceOperatorPackets.stage",
  "coreEvidenceOperatorPackets.schemaVersion",
  "coreEvidenceOperatorPackets.operatorPacketRows",
  "coreEvidenceOperatorPackets.operatorAttachmentSlotRows",
  "coreEvidenceOperatorPackets.pendingOperatorPacketCount",
  "coreEvidenceOperatorPackets.pendingOperatorAttachmentSlotCount",
  "coreEvidenceOperatorPackets.pendingJhoraAttachmentSlotCount",
  "coreEvidenceOperatorPackets.pendingParasharaLightAttachmentSlotCount",
  "coreEvidenceOperatorPackets.blockedPacketCount",
  "coreEvidenceOperatorPackets.readyToMarkRows",
  "coreEvidenceOperatorPackets.remainingNotReviewedRows",
  "coreEvidenceOperatorPackets.selectedCaseIds",
  "coreEvidenceOperatorPackets.packetStatus",
  "coreEvidenceOperatorPackets.handoffStatus",
  "coreEvidenceOperatorPackets.caseWorkOrderStatus",
  "coreEvidenceOperatorPackets.evidenceFileStatus",
  "coreEvidenceOperatorPackets.readyToMarkLabel",
  "coreEvidenceOperatorPackets.safeValidationCommandFamilies",
  "coreEvidenceOperatorPackets.operatorNote",
  "coreEvidenceOperatorPacketQa.stage",
  "coreEvidenceOperatorPacketQa.schemaVersion",
  "coreEvidenceOperatorPacketQa.operatorPacketQaRows",
  "coreEvidenceOperatorPacketQa.attachmentSlotQaRows",
  "coreEvidenceOperatorPacketQa.blockedPacketQaCount",
  "coreEvidenceOperatorPacketQa.pendingAttachmentSlotQaCount",
  "coreEvidenceOperatorPacketQa.pendingJhoraAttachmentSlotQaCount",
  "coreEvidenceOperatorPacketQa.pendingParasharaLightAttachmentSlotQaCount",
  "coreEvidenceOperatorPacketQa.readyToMarkRows",
  "coreEvidenceOperatorPacketQa.remainingNotReviewedRows",
  "coreEvidenceOperatorPacketQa.selectedCaseIds",
  "coreEvidenceOperatorPacketQa.qaStatus",
  "coreEvidenceOperatorPacketQa.packetStatus",
  "coreEvidenceOperatorPacketQa.attachmentSlotStatus",
  "coreEvidenceOperatorPacketQa.readyToMarkLabel",
  "coreEvidenceOperatorPacketQa.safeValidationCommandFamilies",
  "coreEvidenceOperatorPacketQa.operatorNote",
  "coreEvidenceOperatorPacketAttachmentReadiness.stage",
  "coreEvidenceOperatorPacketAttachmentReadiness.schemaVersion",
  "coreEvidenceOperatorPacketAttachmentReadiness.caseAttachmentReadinessRows",
  "coreEvidenceOperatorPacketAttachmentReadiness.attachmentReadinessSlotRows",
  "coreEvidenceOperatorPacketAttachmentReadiness.blockedCaseAttachmentCount",
  "coreEvidenceOperatorPacketAttachmentReadiness.pendingExternalEvidenceAttachmentCount",
  "coreEvidenceOperatorPacketAttachmentReadiness.pendingJhoraExternalAttachmentCount",
  "coreEvidenceOperatorPacketAttachmentReadiness.pendingParasharaLightExternalAttachmentCount",
  "coreEvidenceOperatorPacketAttachmentReadiness.readyToAttachRows",
  "coreEvidenceOperatorPacketAttachmentReadiness.readyToMarkRows",
  "coreEvidenceOperatorPacketAttachmentReadiness.remainingNotReviewedRows",
  "coreEvidenceOperatorPacketAttachmentReadiness.selectedCaseIds",
  "coreEvidenceOperatorPacketAttachmentReadiness.slotFamilies",
  "coreEvidenceOperatorPacketAttachmentReadiness.readinessStatus",
  "coreEvidenceOperatorPacketAttachmentReadiness.qaStatus",
  "coreEvidenceOperatorPacketAttachmentReadiness.packetStatus",
  "coreEvidenceOperatorPacketAttachmentReadiness.attachmentSlotStatus",
  "coreEvidenceOperatorPacketAttachmentReadiness.readyToAttachLabel",
  "coreEvidenceOperatorPacketAttachmentReadiness.readyToMarkLabel",
  "coreEvidenceOperatorPacketAttachmentReadiness.safeValidationCommandFamilies",
  "coreEvidenceOperatorPacketAttachmentReadiness.operatorNote",
  "coreEvidenceExternalIntakeContract.stage",
  "coreEvidenceExternalIntakeContract.schemaVersion",
  "coreEvidenceExternalIntakeContract.caseIntakeContractRows",
  "coreEvidenceExternalIntakeContract.attachmentIntakeSlotRows",
  "coreEvidenceExternalIntakeContract.pendingExternalEvidenceIntakeCount",
  "coreEvidenceExternalIntakeContract.pendingJhoraExternalIntakeCount",
  "coreEvidenceExternalIntakeContract.pendingParasharaLightExternalIntakeCount",
  "coreEvidenceExternalIntakeContract.evidenceCollectedCount",
  "coreEvidenceExternalIntakeContract.evidenceUploadedCount",
  "coreEvidenceExternalIntakeContract.evidenceAttachedCount",
  "coreEvidenceExternalIntakeContract.readyToAttachRows",
  "coreEvidenceExternalIntakeContract.readyToMarkRows",
  "coreEvidenceExternalIntakeContract.remainingNotReviewedRows",
  "coreEvidenceExternalIntakeContract.selectedCaseIds",
  "coreEvidenceExternalIntakeContract.slotFamilies",
  "coreEvidenceExternalIntakeContract.intakeStatus",
  "coreEvidenceExternalIntakeContract.readinessStatus",
  "coreEvidenceExternalIntakeContract.qaStatus",
  "coreEvidenceExternalIntakeContract.packetStatus",
  "coreEvidenceExternalIntakeContract.evidenceFileStatus",
  "coreEvidenceExternalIntakeContract.evidenceCollectionStatus",
  "coreEvidenceExternalIntakeContract.evidenceUploadStatus",
  "coreEvidenceExternalIntakeContract.evidenceAttachmentStatus",
  "coreEvidenceExternalIntakeContract.readyToAttachLabel",
  "coreEvidenceExternalIntakeContract.readyToMarkLabel",
  "coreEvidenceExternalIntakeContract.evidenceCollectedLabel",
  "coreEvidenceExternalIntakeContract.evidenceUploadedLabel",
  "coreEvidenceExternalIntakeContract.evidenceAttachedLabel",
  "coreEvidenceExternalIntakeContract.safeIntakeLabels",
  "coreEvidenceExternalIntakeContract.safeValidationCommandFamilies",
  "coreEvidenceExternalIntakeContract.operatorNote",
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
assert(!helperSlice.includes('latestStage: "P57-A"'), "Core evidence pipeline helper must not retain stale P57 latest stage");
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
assert(!helperSlice.includes('latestStage: "P59-A"'), "Core evidence pipeline helper must not retain stale P59 latest stage");
assert(!helperSlice.includes('latestStage: "P61-A"'), "Core evidence pipeline helper must not retain stale P61 latest stage");
assert(!helperSlice.includes('latestStage: "P63-A"'), "Core evidence pipeline helper must not retain stale P63 latest stage");
assert(!helperSlice.includes('latestStage: "P65-A"'), "Core evidence pipeline helper must not retain stale P65 latest stage");
assert(!helperSlice.includes('latestStage: "P67-A"'), "Core evidence pipeline helper must not retain stale P67 latest stage");
assert(!helperSlice.includes('latestStage: "P69-A"'), "Core evidence pipeline helper must not retain stale P69 latest stage");
assert(helperSlice.includes('latestStage: "P71-A"'), "Core evidence pipeline helper must expose latest P71 stage");
assert(helperSlice.includes('"P59 attachment gate"'), "Core evidence pipeline helper must expose P59 stage sequence");
assert(helperSlice.includes('"P61 work orders"'), "Core evidence pipeline helper must expose P61 stage sequence");
assert(helperSlice.includes('"P63 handoff"'), "Core evidence pipeline helper must expose P63 stage sequence");
assert(helperSlice.includes('"P65 operator packets"'), "Core evidence pipeline helper must expose P65 stage sequence");
assert(helperSlice.includes('"P67 QA preflight"'), "Core evidence pipeline helper must expose P67 stage sequence");
assert(helperSlice.includes('"P69 attachment readiness"'), "Core evidence pipeline helper must expose P69 stage sequence");
assert(helperSlice.includes('"P71 external intake contract"'), "Core evidence pipeline helper must expose P71 stage sequence");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-attachment-gate-v1"'), "Core evidence attachment helper must expose schema version");
assert(helperSlice.includes('stage: "P59-A"'), "Core evidence attachment helper must expose P59-A stage");
assert(helperSlice.includes("attachmentRows: 5"), "Core evidence attachment helper must expose 5 attachment rows");
assert(helperSlice.includes("operatorAttachmentManifestRows: 5"), "Core evidence attachment helper must expose 5 operator attachment rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence attachment helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("blockedRows: 5"), "Core evidence attachment helper must expose 5 blocked rows");
assert(helperSlice.includes("missingAttachmentSlots: 10"), "Core evidence attachment helper must expose 10 missing attachment slots");
assert(helperSlice.includes("attachedEvidenceFiles: 0"), "Core evidence attachment helper must expose 0 attached evidence files");
assert(helperSlice.includes("attachedEvidenceFamilyCount: 0"), "Core evidence attachment helper must expose 0 attached evidence families");
assert(helperSlice.includes("jhoraAttachedCount: 0"), "Core evidence attachment helper must expose 0 JHora attached rows");
assert(helperSlice.includes("parasharaLightAttachedCount: 0"), "Core evidence attachment helper must expose 0 Parashara Light attached rows");
assert(helperSlice.includes("jhoraMissingCount: 5"), "Core evidence attachment helper must expose 5 JHora missing rows");
assert(helperSlice.includes("parasharaLightMissingCount: 5"), "Core evidence attachment helper must expose 5 Parashara Light missing rows");
assert(helperSlice.includes('attachmentGateStatus: "blocked_no_attached_evidence"'), "Core evidence attachment helper must expose blocked attachment status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence attachment helper must expose false ready-to-mark label");
assert(helperSlice.includes('jhora_screenshot_or_packet: "not_attached"'), "Core evidence attachment helper must expose not-attached JHora slot");
assert(helperSlice.includes('parashara_light_manual_values_or_packet: "not_attached"'), "Core evidence attachment helper must expose not-attached Parashara Light slot");
assert(helperSlice.includes('"rerun_evidence_attachment_gate"'), "Core evidence attachment helper must expose rerun attachment gate action");
assert(helperSlice.includes('"build_witness_core_evidence_attachment_gate_report"'), "Core evidence attachment helper must expose attachment gate validation command");
assert(helperSlice.includes("Evidence must be attached before mark commands are attempted"), "Core evidence attachment helper must expose attachment operator note");
assert(preflightSlice.includes("P59 attachment gate"), "Core evidence pipeline UI must render P59 stage");
assert(preflightSlice.includes("operator attachment manifest"), "Core evidence attachment UI must expose operator attachment manifest");
assert(accuracyRoute.includes("P59-A"), "Accuracy route marker must expose P59 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-attachment-gate-v1"), "Accuracy route marker must expose P59 schema");
assert(accuracyRoute.includes("5 attachment rows"), "Accuracy route marker must expose attachment row count");
assert(accuracyRoute.includes("5 operator attachment manifest rows"), "Accuracy route marker must expose operator attachment row count");
assert(accuracyRoute.includes("10 missing attachment slots"), "Accuracy route marker must expose missing attachment slots");
assert(accuracyRoute.includes("0 attached evidence files"), "Accuracy route marker must expose attached evidence file count");
assert(accuracyRoute.includes("0 attached evidence family count"), "Accuracy route marker must expose attached evidence family count");
assert(accuracyRoute.includes("0 JHora attached"), "Accuracy route marker must expose JHora attached count");
assert(accuracyRoute.includes("0 Parashara Light attached"), "Accuracy route marker must expose Parashara Light attached count");
assert(accuracyRoute.includes("not_attached"), "Accuracy route marker must expose not-attached slot status");
assert(accuracyRoute.includes("blocked_no_attached_evidence"), "Accuracy route marker must expose blocked attachment status");
assert(accuracyRoute.includes("rerun_evidence_attachment_gate"), "Accuracy route marker must expose rerun attachment gate action");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_gate_report"), "Accuracy route marker must expose attachment validation command");
assert(accuracyRoute.includes("Evidence must be attached before mark commands are attempted"), "Accuracy route marker must expose attachment operator note");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-attachment-work-orders-v1"'), "Core evidence work orders helper must expose schema version");
assert(helperSlice.includes('stage: "P61-A"'), "Core evidence work orders helper must expose P61-A stage");
assert(helperSlice.includes("workOrderRows: 10"), "Core evidence work orders helper must expose 10 work-order rows");
assert(helperSlice.includes("pendingWorkOrderCount: 10"), "Core evidence work orders helper must expose 10 pending work orders");
assert(helperSlice.includes("pendingJhoraWorkOrderCount: 5"), "Core evidence work orders helper must expose 5 pending JHora work orders");
assert(helperSlice.includes("pendingParasharaLightWorkOrderCount: 5"), "Core evidence work orders helper must expose 5 pending Parashara Light work orders");
assert(helperSlice.includes("blockedCaseCount: 5"), "Core evidence work orders helper must expose 5 blocked cases");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence work orders helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence work orders helper must expose 20 remaining rows");
assert(helperSlice.includes('workOrderStatus: "pending_not_attached"'), "Core evidence work orders helper must expose pending work-order status");
assert(helperSlice.includes('caseWorkOrderStatus: "blocked_pending_attachments"'), "Core evidence work orders helper must expose blocked case work-order status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence work orders helper must expose false ready-to-mark label");
assert(helperSlice.includes('"build_witness_core_evidence_attachment_work_orders_report"'), "Core evidence work orders helper must expose work-order validation command");
assert(helperSlice.includes("work orders are labels only and do not collect evidence"), "Core evidence work orders helper must expose labels-only operator note");
assert(preflightSlice.includes("P61 work orders"), "Core evidence pipeline UI must render P61 stage");
assert(preflightSlice.includes("Core evidence attachment work orders"), "Core evidence work orders UI must render its heading");
assert(accuracyRoute.includes("P61-A"), "Accuracy route marker must expose P61 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-attachment-work-orders-v1"), "Accuracy route marker must expose P61 schema");
assert(accuracyRoute.includes("10 work-order rows"), "Accuracy route marker must expose work-order row count");
assert(accuracyRoute.includes("10 pending work orders"), "Accuracy route marker must expose pending work-order count");
assert(accuracyRoute.includes("5 pending JHora"), "Accuracy route marker must expose pending JHora count");
assert(accuracyRoute.includes("5 pending Parashara Light"), "Accuracy route marker must expose pending Parashara Light count");
assert(accuracyRoute.includes("5 blocked cases"), "Accuracy route marker must expose blocked case count");
assert(accuracyRoute.includes("pending_not_attached"), "Accuracy route marker must expose pending work-order status");
assert(accuracyRoute.includes("blocked_pending_attachments"), "Accuracy route marker must expose blocked case work-order status");
assert(accuracyRoute.includes("work orders are labels only and do not collect evidence"), "Accuracy route marker must expose labels-only operator note");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_work_orders_report"), "Accuracy route marker must expose work-order validation command");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-attachment-handoff-v1"'), "Core evidence handoff helper must expose schema version");
assert(helperSlice.includes('stage: "P63-A"'), "Core evidence handoff helper must expose P63-A stage");
assert(helperSlice.includes("caseHandoffRows: 5"), "Core evidence handoff helper must expose 5 case handoff rows");
assert(helperSlice.includes("handoffWorkOrderRows: 10"), "Core evidence handoff helper must expose 10 handoff work-order rows");
assert(helperSlice.includes("pendingHandoffCount: 10"), "Core evidence handoff helper must expose 10 pending handoff rows");
assert(helperSlice.includes("pendingJhoraHandoffCount: 5"), "Core evidence handoff helper must expose 5 pending JHora handoff rows");
assert(helperSlice.includes("pendingParasharaLightHandoffCount: 5"), "Core evidence handoff helper must expose 5 pending Parashara Light handoff rows");
assert(helperSlice.includes("blockedCaseCount: 5"), "Core evidence handoff helper must expose 5 blocked cases");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence handoff helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence handoff helper must expose 20 remaining rows");
assert(helperSlice.includes('handoffStatus: "blocked_pending_operator_evidence"'), "Core evidence handoff helper must expose blocked handoff status");
assert(helperSlice.includes('caseWorkOrderStatus: "blocked_pending_attachments"'), "Core evidence handoff helper must expose blocked case work-order status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence handoff helper must expose false ready-to-mark label");
assert(helperSlice.includes('"build_witness_core_evidence_attachment_handoff_report"'), "Core evidence handoff helper must expose handoff validation command");
assert(helperSlice.includes("handoff rows are labels only and do not collect evidence"), "Core evidence handoff helper must expose labels-only operator note");
assert(helperSlice.includes("external evidence has not been attached"), "Core evidence handoff helper must expose external evidence blocker");
assert(preflightSlice.includes("P63 handoff"), "Core evidence pipeline UI must render P63 stage");
assert(preflightSlice.includes("Core evidence attachment handoff"), "Core evidence handoff UI must render its heading");
assert(accuracyRoute.includes("P63-A"), "Accuracy route marker must expose P63 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-attachment-handoff-v1"), "Accuracy route marker must expose P63 schema");
assert(accuracyRoute.includes("5 case handoff rows"), "Accuracy route marker must expose case handoff row count");
assert(accuracyRoute.includes("10 handoff work-order rows"), "Accuracy route marker must expose handoff work-order row count");
assert(accuracyRoute.includes("10 pending handoff"), "Accuracy route marker must expose pending handoff count");
assert(accuracyRoute.includes("5 pending JHora handoff"), "Accuracy route marker must expose pending JHora handoff count");
assert(accuracyRoute.includes("5 pending Parashara Light handoff"), "Accuracy route marker must expose pending Parashara Light handoff count");
assert(accuracyRoute.includes("blocked_pending_operator_evidence"), "Accuracy route marker must expose blocked handoff status");
assert(accuracyRoute.includes("handoff rows are labels only and do not collect evidence"), "Accuracy route marker must expose labels-only handoff note");
assert(accuracyRoute.includes("external evidence has not been attached"), "Accuracy route marker must expose external evidence blocker");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_handoff_report"), "Accuracy route marker must expose handoff validation command");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-operator-packets-v1"'), "Core evidence operator packets helper must expose schema version");
assert(helperSlice.includes('stage: "P65-A"'), "Core evidence operator packets helper must expose P65-A stage");
assert(helperSlice.includes("operatorPacketRows: 5"), "Core evidence operator packets helper must expose 5 operator packet rows");
assert(helperSlice.includes("operatorAttachmentSlotRows: 10"), "Core evidence operator packets helper must expose 10 operator attachment slot rows");
assert(helperSlice.includes("pendingOperatorPacketCount: 5"), "Core evidence operator packets helper must expose 5 pending operator packets");
assert(helperSlice.includes("pendingOperatorAttachmentSlotCount: 10"), "Core evidence operator packets helper must expose 10 pending operator attachment slots");
assert(helperSlice.includes("pendingJhoraAttachmentSlotCount: 5"), "Core evidence operator packets helper must expose 5 pending JHora attachment slots");
assert(helperSlice.includes("pendingParasharaLightAttachmentSlotCount: 5"), "Core evidence operator packets helper must expose 5 pending Parashara Light attachment slots");
assert(helperSlice.includes("blockedPacketCount: 5"), "Core evidence operator packets helper must expose 5 blocked packets");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence operator packets helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence operator packets helper must expose 20 remaining rows");
assert(helperSlice.includes('packetStatus: "blocked_pending_operator_packet_evidence"'), "Core evidence operator packets helper must expose blocked packet status");
assert(helperSlice.includes('handoffStatus: "blocked_pending_operator_evidence"'), "Core evidence operator packets helper must expose blocked handoff status");
assert(helperSlice.includes('caseWorkOrderStatus: "blocked_pending_attachments"'), "Core evidence operator packets helper must expose blocked case work-order status");
assert(helperSlice.includes('evidenceFileStatus: "not_attached"'), "Core evidence operator packets helper must expose not-attached evidence file status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence operator packets helper must expose false ready-to-mark label");
assert(helperSlice.includes('"build_witness_core_evidence_operator_packets_report"'), "Core evidence operator packets helper must expose operator packet validation command");
assert(helperSlice.includes("operator packets are labels only and do not collect or attach evidence"), "Core evidence operator packets helper must expose labels-only operator note");
assert(helperSlice.includes("external evidence has not been attached"), "Core evidence operator packets helper must expose external evidence blocker");
assert(preflightSlice.includes("P65 operator packets"), "Core evidence pipeline UI must render P65 stage");
assert(preflightSlice.includes("Core evidence operator packets"), "Core evidence operator packets UI must render its heading");
assert(accuracyRoute.includes("P65-A"), "Accuracy route marker must expose P65 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-operator-packets-v1"), "Accuracy route marker must expose P65 schema");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-operator-packet-qa-v1"'), "Core evidence operator packet QA helper must expose schema version");
assert(helperSlice.includes('stage: "P67-A"'), "Core evidence operator packet QA helper must expose P67-A stage");
assert(helperSlice.includes("operatorPacketQaRows: 5"), "Core evidence operator packet QA helper must expose 5 operator packet QA rows");
assert(helperSlice.includes("attachmentSlotQaRows: 10"), "Core evidence operator packet QA helper must expose 10 attachment slot QA rows");
assert(helperSlice.includes("blockedPacketQaCount: 5"), "Core evidence operator packet QA helper must expose 5 blocked packet QA rows");
assert(helperSlice.includes("pendingAttachmentSlotQaCount: 10"), "Core evidence operator packet QA helper must expose 10 pending attachment slot QA rows");
assert(helperSlice.includes("pendingJhoraAttachmentSlotQaCount: 5"), "Core evidence operator packet QA helper must expose 5 pending JHora slot QA rows");
assert(helperSlice.includes("pendingParasharaLightAttachmentSlotQaCount: 5"), "Core evidence operator packet QA helper must expose 5 pending Parashara Light slot QA rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence operator packet QA helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence operator packet QA helper must expose 20 remaining rows");
assert(helperSlice.includes('qaStatus: "blocked_pending_operator_packet_qa"'), "Core evidence operator packet QA helper must expose blocked QA status");
assert(helperSlice.includes('packetStatus: "blocked_pending_operator_packet_evidence"'), "Core evidence operator packet QA helper must expose blocked packet status");
assert(helperSlice.includes('attachmentSlotStatus: "not_attached"'), "Core evidence operator packet QA helper must expose not-attached slot status");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence operator packet QA helper must expose false ready-to-mark label");
assert(helperSlice.includes('"build_witness_core_evidence_operator_packet_qa_report"'), "Core evidence operator packet QA helper must expose QA validation command");
assert(helperSlice.includes("operator packets are labels only"), "Core evidence operator packet QA helper must expose labels-only note");
assert(helperSlice.includes("external evidence has not been attached"), "Core evidence operator packet QA helper must expose external evidence blocker");
assert(helperSlice.includes("mark commands remain blocked"), "Core evidence operator packet QA helper must expose mark-command blocker");
assert(preflightSlice.includes("P67 QA preflight"), "Core evidence pipeline UI must render P67 stage");
assert(preflightSlice.includes("Core evidence operator packet QA"), "Core evidence operator packet QA UI must render its heading");
assert(accuracyRoute.includes("P67-A"), "Accuracy route marker must expose P67 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-operator-packet-qa-v1"), "Accuracy route marker must expose P67 schema");
assert(accuracyRoute.includes("5 operator packet QA rows"), "Accuracy route marker must expose P67 operator packet QA rows");
assert(accuracyRoute.includes("10 attachment slot QA rows"), "Accuracy route marker must expose P67 attachment slot QA rows");
assert(accuracyRoute.includes("5 blocked packet QA"), "Accuracy route marker must expose P67 blocked packet QA count");
assert(accuracyRoute.includes("10 pending attachment slot QA"), "Accuracy route marker must expose P67 pending attachment slot QA count");
assert(accuracyRoute.includes("5 pending JHora slot QA"), "Accuracy route marker must expose P67 pending JHora slot QA count");
assert(accuracyRoute.includes("5 pending Parashara Light slot QA"), "Accuracy route marker must expose P67 pending Parashara Light slot QA count");
assert(accuracyRoute.includes("0 ready-to-mark"), "Accuracy route marker must expose P67 ready-to-mark count");
assert(accuracyRoute.includes("20 remaining"), "Accuracy route marker must expose P67 remaining count");
assert(accuracyRoute.includes("blocked_pending_operator_packet_qa"), "Accuracy route marker must expose P67 QA status");
assert(accuracyRoute.includes("blocked_pending_operator_packet_evidence"), "Accuracy route marker must expose P67 packet status");
assert(accuracyRoute.includes("not_attached"), "Accuracy route marker must expose P67 not-attached status");
assert(accuracyRoute.includes("ready_to_mark=false"), "Accuracy route marker must expose P67 false ready-to-mark state");
assert(accuracyRoute.includes("operator packets are labels only"), "Accuracy route marker must expose P67 labels-only note");
assert(accuracyRoute.includes("external evidence has not been attached"), "Accuracy route marker must expose P67 external evidence blocker");
assert(accuracyRoute.includes("mark commands remain blocked"), "Accuracy route marker must expose P67 mark-command blocker");
assert(accuracyRoute.includes("build_witness_core_evidence_operator_packet_qa_report"), "Accuracy route marker must expose P67 QA command family");
assert(accuracyRoute.includes("build_witness_core_evidence_operator_packets_report"), "Accuracy route marker must expose P65 command family retained for P67");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_handoff_report"), "Accuracy route marker must expose P63 command family retained for P67");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_work_orders_report"), "Accuracy route marker must expose P61 command family retained for P67");
assert(accuracyRoute.includes("build_witness_core_evidence_attachment_gate_report"), "Accuracy route marker must expose P59 command family retained for P67");
assert(accuracyRoute.includes("preflight_witness_review"), "Accuracy route marker must expose preflight command family retained for P67");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-operator-packet-attachment-readiness-v1"'), "Core evidence operator packet attachment readiness helper must expose schema version");
assert(helperSlice.includes('stage: "P69-A"'), "Core evidence operator packet attachment readiness helper must expose P69-A stage");
assert(helperSlice.includes("caseAttachmentReadinessRows: 5"), "Core evidence operator packet attachment readiness helper must expose 5 case readiness rows");
assert(helperSlice.includes("attachmentReadinessSlotRows: 10"), "Core evidence operator packet attachment readiness helper must expose 10 slot readiness rows");
assert(helperSlice.includes("blockedCaseAttachmentCount: 5"), "Core evidence operator packet attachment readiness helper must expose 5 blocked case attachments");
assert(helperSlice.includes("pendingExternalEvidenceAttachmentCount: 10"), "Core evidence operator packet attachment readiness helper must expose 10 pending external attachments");
assert(helperSlice.includes("pendingJhoraExternalAttachmentCount: 5"), "Core evidence operator packet attachment readiness helper must expose 5 pending JHora external attachments");
assert(helperSlice.includes("pendingParasharaLightExternalAttachmentCount: 5"), "Core evidence operator packet attachment readiness helper must expose 5 pending Parashara Light external attachments");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence operator packet attachment readiness helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence operator packet attachment readiness helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence operator packet attachment readiness helper must expose 20 remaining rows");
assert(helperSlice.includes('readinessStatus: "blocked_pending_external_evidence_attachment"'), "Core evidence operator packet attachment readiness helper must expose blocked readiness status");
assert(helperSlice.includes('qaStatus: "blocked_pending_operator_packet_qa"'), "Core evidence operator packet attachment readiness helper must expose blocked QA status");
assert(helperSlice.includes('packetStatus: "blocked_pending_operator_packet_evidence"'), "Core evidence operator packet attachment readiness helper must expose blocked packet status");
assert(helperSlice.includes('attachmentSlotStatus: "not_attached"'), "Core evidence operator packet attachment readiness helper must expose not-attached status");
assert(helperSlice.includes('readyToAttachLabel: "ready_to_attach=false"'), "Core evidence operator packet attachment readiness helper must expose false ready-to-attach label");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence operator packet attachment readiness helper must expose false ready-to-mark label");
assert(helperSlice.includes('"build_witness_core_evidence_operator_packet_attachment_readiness_report"'), "Core evidence operator packet attachment readiness helper must expose P69 validation command");
assert(helperSlice.includes("readiness rows are labels only"), "Core evidence operator packet attachment readiness helper must expose labels-only note");
assert(helperSlice.includes("collection/upload/mark commands are not executed"), "Core evidence operator packet attachment readiness helper must expose non-execution note");
assert(preflightSlice.includes("P69 attachment readiness"), "Core evidence pipeline UI must render P69 stage");
assert(preflightSlice.includes("Core evidence operator packet attachment readiness"), "Core evidence operator packet attachment readiness UI must render its heading");
assert(accuracyRoute.includes("P69-A"), "Accuracy route marker must expose P69 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-operator-packet-attachment-readiness-v1"), "Accuracy route marker must expose P69 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_attachment"), "Accuracy route marker must expose P69 status");
assert(accuracyRoute.includes("5 case attachment readiness rows"), "Accuracy route marker must expose P69 case readiness rows");
assert(accuracyRoute.includes("10 attachment readiness slot rows"), "Accuracy route marker must expose P69 slot readiness rows");
assert(accuracyRoute.includes("5 blocked case attachments"), "Accuracy route marker must expose P69 blocked case attachments");
assert(accuracyRoute.includes("10 pending external evidence attachments"), "Accuracy route marker must expose P69 pending external attachments");
assert(accuracyRoute.includes("5 pending JHora external attachments"), "Accuracy route marker must expose P69 pending JHora external attachments");
assert(accuracyRoute.includes("5 pending Parashara Light external attachments"), "Accuracy route marker must expose P69 pending Parashara Light external attachments");
assert(accuracyRoute.includes("0 ready-to-attach"), "Accuracy route marker must expose P69 ready-to-attach count");
assert(accuracyRoute.includes("0 ready-to-mark"), "Accuracy route marker must expose P69 ready-to-mark count");
assert(accuracyRoute.includes("20 remaining"), "Accuracy route marker must expose P69 remaining count");
assert(accuracyRoute.includes("jhora_screenshot_or_packet, parashara_light_manual_values_or_packet"), "Accuracy route marker must expose P69 slot family order");
assert(accuracyRoute.includes("ready_to_attach=false"), "Accuracy route marker must expose P69 false ready-to-attach state");
assert(accuracyRoute.includes("ready_to_mark=false"), "Accuracy route marker must expose P69 false ready-to-mark state");
assert(accuracyRoute.includes("readiness rows are labels only"), "Accuracy route marker must expose P69 labels-only note");
assert(accuracyRoute.includes("collection/upload/mark commands are not executed"), "Accuracy route marker must expose P69 non-execution note");
assert(accuracyRoute.includes("build_witness_core_evidence_operator_packet_attachment_readiness_report"), "Accuracy route marker must expose P69 readiness command family");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-intake-contract-v1"'), "Core evidence external intake contract helper must expose schema version");
assert(helperSlice.includes('stage: "P71-A"'), "Core evidence external intake contract helper must expose P71-A stage");
assert(helperSlice.includes("caseIntakeContractRows: 5"), "Core evidence external intake contract helper must expose 5 case intake rows");
assert(helperSlice.includes("attachmentIntakeSlotRows: 10"), "Core evidence external intake contract helper must expose 10 slot intake rows");
assert(helperSlice.includes("pendingExternalEvidenceIntakeCount: 10"), "Core evidence external intake contract helper must expose 10 pending external intake slots");
assert(helperSlice.includes("pendingJhoraExternalIntakeCount: 5"), "Core evidence external intake contract helper must expose 5 pending JHora intake slots");
assert(helperSlice.includes("pendingParasharaLightExternalIntakeCount: 5"), "Core evidence external intake contract helper must expose 5 pending Parashara Light intake slots");
assert(helperSlice.includes("evidenceCollectedCount: 0"), "Core evidence external intake contract helper must expose 0 collected evidence rows");
assert(helperSlice.includes("evidenceUploadedCount: 0"), "Core evidence external intake contract helper must expose 0 uploaded evidence rows");
assert(helperSlice.includes("evidenceAttachedCount: 0"), "Core evidence external intake contract helper must expose 0 attached evidence rows");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence external intake contract helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence external intake contract helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence external intake contract helper must expose 20 remaining rows");
assert(helperSlice.includes('intakeStatus: "blocked_pending_external_evidence_intake"'), "Core evidence external intake contract helper must expose blocked intake status");
assert(helperSlice.includes('readinessStatus: "blocked_pending_external_evidence_attachment"'), "Core evidence external intake contract helper must expose blocked readiness status");
assert(helperSlice.includes('qaStatus: "blocked_pending_operator_packet_qa"'), "Core evidence external intake contract helper must expose blocked QA status");
assert(helperSlice.includes('packetStatus: "blocked_pending_operator_packet_evidence"'), "Core evidence external intake contract helper must expose blocked packet status");
assert(helperSlice.includes('evidenceFileStatus: "not_attached"'), "Core evidence external intake contract helper must expose not-attached file status");
assert(helperSlice.includes('evidenceCollectionStatus: "not_started"'), "Core evidence external intake contract helper must expose not-started collection status");
assert(helperSlice.includes('evidenceUploadStatus: "not_started"'), "Core evidence external intake contract helper must expose not-started upload status");
assert(helperSlice.includes('evidenceAttachmentStatus: "not_attached"'), "Core evidence external intake contract helper must expose not-attached attachment status");
assert(helperSlice.includes('readyToAttachLabel: "ready_to_attach=false"'), "Core evidence external intake contract helper must expose false ready-to-attach label");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence external intake contract helper must expose false ready-to-mark label");
assert(helperSlice.includes('evidenceCollectedLabel: "evidence_collected=false"'), "Core evidence external intake contract helper must expose false collected label");
assert(helperSlice.includes('evidenceUploadedLabel: "evidence_uploaded=false"'), "Core evidence external intake contract helper must expose false uploaded label");
assert(helperSlice.includes('evidenceAttachedLabel: "evidence_attached=false"'), "Core evidence external intake contract helper must expose false attached label");
assert(helperSlice.includes('"request_jhora_screenshot_or_packet"'), "Core evidence external intake contract helper must expose JHora request label");
assert(helperSlice.includes('"request_parashara_light_manual_values_or_packet"'), "Core evidence external intake contract helper must expose Parashara Light request label");
assert(helperSlice.includes('"receive_external_evidence_from_human"'), "Core evidence external intake contract helper must expose receive evidence label");
assert(helperSlice.includes('"build_witness_core_evidence_external_intake_contract_report"'), "Core evidence external intake contract helper must expose P71 validation command");
assert(helperSlice.includes("external evidence has not been collected, uploaded, or attached"), "Core evidence external intake contract helper must expose external intake blocker");
assert(helperSlice.includes("intake rows are labels only"), "Core evidence external intake contract helper must expose labels-only note");
assert(helperSlice.includes("mark commands are not executed"), "Core evidence external intake contract helper must expose mark-command blocker");
assert(preflightSlice.includes("P71 external intake contract"), "Core evidence pipeline UI must render P71 stage");
assert(preflightSlice.includes("Core evidence external intake contract"), "Core evidence external intake contract UI must render its heading");
assert(accuracyRoute.includes("P71-A"), "Accuracy route marker must expose P71 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-intake-contract-v1"), "Accuracy route marker must expose P71 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_intake"), "Accuracy route marker must expose P71 status");
assert(accuracyRoute.includes("5 case intake contract rows"), "Accuracy route marker must expose P71 case intake rows");
assert(accuracyRoute.includes("10 attachment intake slot rows"), "Accuracy route marker must expose P71 slot intake rows");
assert(accuracyRoute.includes("10 pending external evidence intake"), "Accuracy route marker must expose P71 pending external intake count");
assert(accuracyRoute.includes("5 pending JHora external intake"), "Accuracy route marker must expose P71 pending JHora intake count");
assert(accuracyRoute.includes("5 pending Parashara Light external intake"), "Accuracy route marker must expose P71 pending Parashara Light intake count");
assert(accuracyRoute.includes("0 collected"), "Accuracy route marker must expose P71 collected count");
assert(accuracyRoute.includes("0 uploaded"), "Accuracy route marker must expose P71 uploaded count");
assert(accuracyRoute.includes("0 attached"), "Accuracy route marker must expose P71 attached count");
assert(accuracyRoute.includes("0 ready-to-attach"), "Accuracy route marker must expose P71 ready-to-attach count");
assert(accuracyRoute.includes("0 ready-to-mark"), "Accuracy route marker must expose P71 ready-to-mark count");
assert(accuracyRoute.includes("20 remaining"), "Accuracy route marker must expose P71 remaining count");
assert(accuracyRoute.includes("jhora_screenshot_or_packet, parashara_light_manual_values_or_packet"), "Accuracy route marker must expose P71 slot family order");
assert(accuracyRoute.includes("not_started"), "Accuracy route marker must expose P71 not-started status");
assert(accuracyRoute.includes("evidence_collected=false"), "Accuracy route marker must expose P71 false collected state");
assert(accuracyRoute.includes("evidence_uploaded=false"), "Accuracy route marker must expose P71 false uploaded state");
assert(accuracyRoute.includes("evidence_attached=false"), "Accuracy route marker must expose P71 false attached state");
assert(accuracyRoute.includes("external evidence has not been collected, uploaded, or attached"), "Accuracy route marker must expose P71 intake blocker");
assert(accuracyRoute.includes("intake rows are labels only"), "Accuracy route marker must expose P71 labels-only note");
assert(accuracyRoute.includes("mark commands are not executed"), "Accuracy route marker must expose P71 mark-command blocker");
assert(accuracyRoute.includes("request_jhora_screenshot_or_packet"), "Accuracy route marker must expose P71 JHora request label");
assert(accuracyRoute.includes("request_parashara_light_manual_values_or_packet"), "Accuracy route marker must expose P71 Parashara Light request label");
assert(accuracyRoute.includes("receive_external_evidence_from_human"), "Accuracy route marker must expose P71 receive evidence label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_intake_contract_report"), "Accuracy route marker must expose P71 intake contract command family");
assert(accuracyRoute.includes("5 operator packet rows"), "Accuracy route marker must expose operator packet row count");
assert(accuracyRoute.includes("10 operator attachment slot rows"), "Accuracy route marker must expose operator attachment slot row count");
assert(accuracyRoute.includes("5 pending operator packets"), "Accuracy route marker must expose pending operator packet count");
assert(accuracyRoute.includes("10 pending operator attachment slots"), "Accuracy route marker must expose pending operator attachment slot count");
assert(accuracyRoute.includes("5 pending JHora attachment slots"), "Accuracy route marker must expose pending JHora attachment slot count");
assert(accuracyRoute.includes("5 pending Parashara Light attachment slots"), "Accuracy route marker must expose pending Parashara Light attachment slot count");
assert(accuracyRoute.includes("5 blocked packets"), "Accuracy route marker must expose blocked packet count");
assert(accuracyRoute.includes("blocked_pending_operator_packet_evidence"), "Accuracy route marker must expose blocked operator packet status");
assert(accuracyRoute.includes("not_attached"), "Accuracy route marker must expose not-attached file status");
assert(accuracyRoute.includes("operator packets are labels only and do not collect or attach evidence"), "Accuracy route marker must expose labels-only packet note");
assert(accuracyRoute.includes("build_witness_core_evidence_operator_packets_report"), "Accuracy route marker must expose operator packet validation command");

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
  "external evidence attached",
  "evidence collected",
  "evidence uploaded",
  "ready_to_attach=true",
  "ready_to_mark=true",
  "mark commands enabled",
  "collection executed",
  "upload executed",
  "release ready",
  "sk-",
  "OPENAI_API_KEY",
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
