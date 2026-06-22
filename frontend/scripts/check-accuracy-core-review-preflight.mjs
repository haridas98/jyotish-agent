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
  "Core evidence external receipt gate",
  "Core evidence external receipt manifest templates",
  "Core evidence external receipt manifest preflight",
  "Core evidence external receipt manifest acceptance gate",
  "Core evidence external receipt manifest decision queue",
  "Core evidence external receipt manifest decision audit",
  "Core evidence external receipt manifest decision audit work orders",
  "Core evidence external receipt manifest decision audit work-order readiness",
  "Core evidence external receipt manifest decision audit operator handoff smoke matrix",
  "Core evidence external receipt manifest decision audit operator handoff safe-validation transcript",
  "Core evidence external receipt manifest decision audit operator handoff safe-validation result audit",
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
  "coreEvidenceExternalReceiptGate",
  "coreEvidenceExternalReceiptManifestTemplates",
  "coreEvidenceExternalReceiptManifestPreflight",
  "coreEvidenceExternalReceiptManifestAcceptanceGate",
  "coreEvidenceExternalReceiptManifestDecisionQueue",
  "coreEvidenceExternalReceiptManifestDecisionAudit",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationTranscript",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationResultAudit",
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
  "buildCoreEvidenceExternalReceiptGate",
  "buildCoreEvidenceExternalReceiptManifestTemplates",
  "buildCoreEvidenceExternalReceiptManifestPreflight",
  "buildCoreEvidenceExternalReceiptManifestAcceptanceGate",
  "buildCoreEvidenceExternalReceiptManifestDecisionQueue",
  "buildCoreEvidenceExternalReceiptManifestDecisionAudit",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditWorkOrders",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationTranscript",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationResultLedger",
  "buildCoreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationResultAudit",
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
  "P73-A",
  "P75-A",
  "P77-A",
  "P79-A",
  "P81-A",
  "P83-A",
  "P85-A",
  "P87-A",
  "P89-A",
  "P91-A",
  "P93-A",
  "P95-A",
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
  "jyotish-core-evidence-external-receipt-gate-v1",
  "jyotish-core-evidence-external-receipt-manifest-templates-v1",
  "jyotish-core-evidence-external-receipt-manifest-preflight-v1",
  "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-orders-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-order-readiness-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-transcript-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-ledger-v1",
  "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-v1",
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
  "blocked_pending_external_evidence_receipts",
  "blocked_pending_external_evidence_receipt_manifests",
  "blocked_pending_external_evidence_receipt_manifest_preflight",
  "blocked_pending_external_evidence_receipt_manifest_acceptance",
  "blocked_pending_external_evidence_receipt_manifest_decision",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger",
  "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit",
  "command_smoke_matrix_status=blocked_pending_external_evidence_and_operator_handoff",
  "safe_validation_transcript_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript",
  "safe_validation_command_status=blocked_pending_external_evidence_and_operator_handoff",
  "safe_validation_command_execution_status=not_executed",
  "safe_validation_result_ledger_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger",
  "safe_validation_result_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit",
  "safe_validation_result_execution_status=not_executed",
  "safe_validation_result_record_status=not_recorded",
  "safe_validation_result_acceptance_status=not_accepted",
  "safe_validation_result_failure_status=not_failed",
  "safe_validation_result_audit_execution_status=not_executed",
  "safe_validation_result_audit_record_status=not_recorded",
  "safe_validation_result_audit_pass_status=not_passed",
  "safe_validation_result_audit_failure_status=not_failed",
  "safe_validation_only=true",
  "safe_validation_result_ledger_only=true",
  "safe_validation_result_audit_only=true",
  "no_command_execution_performed=true",
  "no_safe_validation_result_recorded=true",
  "no_safe_validation_result_accepted=true",
  "no_safe_validation_result_failed=true",
  "no_safe_validation_result_audit_performed=true",
  "no_safe_validation_result_audit_passed=true",
  "no_safe_validation_result_audit_failed=true",
  "ready_to_attach=false",
  "ready_to_mark=false",
  "evidence_collected=false",
  "evidence_uploaded=false",
  "evidence_attached=false",
  "evidence_received_count=0",
  "evidence_validated_count=0",
  "receipt_manifest_received_count=0",
  "receipt_manifest_accepted_count=0",
  "receipt_manifest_rejected_count=0",
  "evidence_file_recorded_count=0",
  "evidence_hash_recorded_count=0",
  "preflight_status=blocked_pending_external_evidence_receipt_manifest_preflight",
  "acceptance_gate_status=blocked_pending_external_evidence_receipt_manifest_acceptance",
  "receipt_manifest_status=not_received",
  "receipt_manifest_acceptance_status=not_started",
  "receipt_manifest_rejection_status=not_started",
  "no_raw_values_in_manifest=true",
  "no_private_paths_in_manifest=true",
  "no_secrets_in_manifest=true",
  "decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision",
  "decision_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit",
  "decision_audit_record_status=not_started",
  "decision_audited_count=0",
  "decision_audit_passed_count=0",
  "decision_audit_failed_count=0",
  "no_evidence_file_recorded=true",
  "no_evidence_hash_recorded=true",
  "no_upload_executed=true",
  "no_attachment_executed=true",
  "no_mark_command_executed=true",
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
  "template rows are labels only",
  "collection/upload/mark commands are not executed",
  "mark commands remain blocked",
  "mark commands are not executed",
  "Evidence must be collected and attached before mark commands are attempted",
  "collect_jhora_screenshot",
  "attach_parashara_light_manual_values",
  "request_jhora_screenshot_or_packet",
  "request_parashara_light_manual_values_or_packet",
  "receive_external_evidence_from_human",
  "await_jhora_screenshot_or_packet_receipt",
  "await_parashara_light_manual_values_or_packet_receipt",
  "await_jhora_receipt_manifest",
  "await_parashara_light_receipt_manifest",
  "await_jhora_receipt_manifest_preflight",
  "await_parashara_light_receipt_manifest_preflight",
  "await_jhora_receipt_manifest_acceptance",
  "await_parashara_light_receipt_manifest_acceptance",
  "await_jhora_receipt_manifest_decision_audit",
  "await_parashara_light_receipt_manifest_decision_audit",
  "audit_external_evidence_receipt_manifest_decision_after_human_review",
  "defer_external_evidence_receipt_manifest_decision_audit",
  "rerun_external_receipt_manifest_decision_audit_report",
  "rerun_external_receipt_manifest_decision_queue_report",
  "record_external_evidence_receipt_manifest",
  "record_external_evidence_receipt_manifest_after_human_review",
  "rerun_external_receipt_manifest_acceptance_gate_report",
  "rerun_external_receipt_manifest_preflight_report",
  "rerun_external_receipt_manifest_templates_report",
  "rerun_external_receipt_gate_report",
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
  "build_witness_core_evidence_external_receipt_gate_report",
  "build_witness_core_evidence_external_receipt_manifest_templates_report",
  "build_witness_core_evidence_external_receipt_manifest_preflight_report",
  "build_witness_core_evidence_external_receipt_manifest_acceptance_gate_report",
  "build_witness_core_evidence_external_receipt_manifest_decision_queue_report",
  "build_witness_core_evidence_external_receipt_manifest_decision_audit_report",
  "mark_jhora_witness_reviewed",
  "mark_parashara_light_witness_reviewed",
  "case_id",
  "evidence_family",
  "external_tool_label",
  "human_receipt_timestamp_utc",
  "redacted_receipt_manifest_id",
  "operator_receipt_note_label",
  "expected_receipt_manifest_label",
  "operator_preflight_note_label",
  "operator_acceptance_note_label",
  "operator_decision_label",
  "operator_decision_audit_label",
  "required_human_receipt_timestamp_utc",
  "required_human_decision_timestamp_utc",
  "required_human_decision_audit_timestamp_utc",
  "no_raw_values_in_manifest",
  "no_private_paths_in_manifest",
  "no_secrets_in_manifest",
  "require_human_receipt_timestamp_utc",
  "require_human_decision_timestamp_utc",
  "require_human_decision_audit_timestamp_utc",
  "require_redacted_receipt_manifest_id",
  "require_operator_acceptance_note_label",
  "require_operator_decision_label",
  "require_operator_decision_audit_label",
  "require_accept_or_reject_or_defer_label",
  "require_no_raw_values_in_manifest",
  "require_no_private_paths_in_manifest",
  "require_no_secrets_in_manifest",
  "require_no_evidence_file_recorded_before_acceptance",
  "require_no_evidence_hash_recorded_before_acceptance",
  "block_upload_until_manifest_accepted",
  "block_attachment_until_manifest_accepted",
  "block_mark_until_manifest_accepted",
  "block_upload_until_manifest_decision_audited",
  "block_attachment_until_manifest_decision_audited",
  "block_mark_until_manifest_decision_audited",
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
  "coreEvidenceExternalReceiptGate.stage",
  "coreEvidenceExternalReceiptGate.schemaVersion",
  "coreEvidenceExternalReceiptGate.caseReceiptGateRows",
  "coreEvidenceExternalReceiptGate.attachmentReceiptSlotRows",
  "coreEvidenceExternalReceiptGate.pendingExternalEvidenceReceiptCount",
  "coreEvidenceExternalReceiptGate.pendingJhoraReceiptCount",
  "coreEvidenceExternalReceiptGate.pendingParasharaLightReceiptCount",
  "coreEvidenceExternalReceiptGate.evidenceReceivedCount",
  "coreEvidenceExternalReceiptGate.evidenceValidatedCount",
  "coreEvidenceExternalReceiptGate.evidenceUploadedCount",
  "coreEvidenceExternalReceiptGate.evidenceAttachedCount",
  "coreEvidenceExternalReceiptGate.readyToAttachRows",
  "coreEvidenceExternalReceiptGate.readyToMarkRows",
  "coreEvidenceExternalReceiptGate.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptGate.selectedCaseIds",
  "coreEvidenceExternalReceiptGate.slotFamilies",
  "coreEvidenceExternalReceiptGate.receiptGateStatus",
  "coreEvidenceExternalReceiptGate.intakeStatus",
  "coreEvidenceExternalReceiptGate.readinessStatus",
  "coreEvidenceExternalReceiptGate.evidenceReceiptStatus",
  "coreEvidenceExternalReceiptGate.evidenceValidationStatus",
  "coreEvidenceExternalReceiptGate.evidenceFileStatus",
  "coreEvidenceExternalReceiptGate.evidenceUploadStatus",
  "coreEvidenceExternalReceiptGate.evidenceAttachmentStatus",
  "coreEvidenceExternalReceiptGate.readyToAttachLabel",
  "coreEvidenceExternalReceiptGate.readyToMarkLabel",
  "coreEvidenceExternalReceiptGate.evidenceReceivedLabel",
  "coreEvidenceExternalReceiptGate.evidenceValidatedLabel",
  "coreEvidenceExternalReceiptGate.evidenceUploadedLabel",
  "coreEvidenceExternalReceiptGate.evidenceAttachedLabel",
  "coreEvidenceExternalReceiptGate.paritySuccessClaimedLabel",
  "coreEvidenceExternalReceiptGate.releaseReadyClaimedLabel",
  "coreEvidenceExternalReceiptGate.safeReceiptLabels",
  "coreEvidenceExternalReceiptGate.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptGate.operatorNote",
  "coreEvidenceExternalReceiptManifestTemplates.stage",
  "coreEvidenceExternalReceiptManifestTemplates.schemaVersion",
  "coreEvidenceExternalReceiptManifestTemplates.caseReceiptManifestTemplateRows",
  "coreEvidenceExternalReceiptManifestTemplates.attachmentReceiptManifestTemplateRows",
  "coreEvidenceExternalReceiptManifestTemplates.pendingExternalEvidenceReceiptManifestCount",
  "coreEvidenceExternalReceiptManifestTemplates.pendingJhoraReceiptManifestCount",
  "coreEvidenceExternalReceiptManifestTemplates.pendingParasharaLightReceiptManifestCount",
  "coreEvidenceExternalReceiptManifestTemplates.receiptManifestReceivedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceReceivedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceValidatedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceFileRecordedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceHashRecordedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceUploadedCount",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceAttachedCount",
  "coreEvidenceExternalReceiptManifestTemplates.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestTemplates.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestTemplates.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestTemplates.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestTemplates.slotFamilies",
  "coreEvidenceExternalReceiptManifestTemplates.receiptManifestTemplateStatus",
  "coreEvidenceExternalReceiptManifestTemplates.receiptGateStatus",
  "coreEvidenceExternalReceiptManifestTemplates.intakeStatus",
  "coreEvidenceExternalReceiptManifestTemplates.readinessStatus",
  "coreEvidenceExternalReceiptManifestTemplates.receiptManifestStatus",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceValidationStatus",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceFileStatus",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceHashStatus",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceUploadStatus",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceAttachmentStatus",
  "coreEvidenceExternalReceiptManifestTemplates.readyToAttachLabel",
  "coreEvidenceExternalReceiptManifestTemplates.readyToMarkLabel",
  "coreEvidenceExternalReceiptManifestTemplates.receiptManifestReceivedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceReceivedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceValidatedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceFileRecordedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceHashRecordedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceUploadedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.evidenceAttachedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.paritySuccessClaimedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.releaseReadyClaimedLabel",
  "coreEvidenceExternalReceiptManifestTemplates.safeManifestTemplateLabels",
  "coreEvidenceExternalReceiptManifestTemplates.safeRequiredManifestFields",
  "coreEvidenceExternalReceiptManifestTemplates.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestTemplates.operatorNote",
  "coreEvidenceExternalReceiptManifestPreflight.stage",
  "coreEvidenceExternalReceiptManifestPreflight.schemaVersion",
  "coreEvidenceExternalReceiptManifestPreflight.status",
  "coreEvidenceExternalReceiptManifestPreflight.upstreamTemplateSchemaVersion",
  "coreEvidenceExternalReceiptManifestPreflight.upstreamTemplateStage",
  "coreEvidenceExternalReceiptManifestPreflight.upstreamTemplateStatus",
  "coreEvidenceExternalReceiptManifestPreflight.caseReceiptManifestPreflightRows",
  "coreEvidenceExternalReceiptManifestPreflight.attachmentReceiptManifestPreflightRows",
  "coreEvidenceExternalReceiptManifestPreflight.pendingExternalEvidenceReceiptManifestPreflightCount",
  "coreEvidenceExternalReceiptManifestPreflight.pendingJhoraReceiptManifestPreflightCount",
  "coreEvidenceExternalReceiptManifestPreflight.pendingParasharaLightReceiptManifestPreflightCount",
  "coreEvidenceExternalReceiptManifestPreflight.receiptManifestReceivedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceReceivedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceValidatedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceFileRecordedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceHashRecordedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceUploadedCount",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceAttachedCount",
  "coreEvidenceExternalReceiptManifestPreflight.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestPreflight.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestPreflight.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestPreflight.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestPreflight.slotFamilies",
  "coreEvidenceExternalReceiptManifestPreflight.receiptManifestPreflightStatus",
  "coreEvidenceExternalReceiptManifestPreflight.receiptManifestTemplateStatus",
  "coreEvidenceExternalReceiptManifestPreflight.receiptGateStatus",
  "coreEvidenceExternalReceiptManifestPreflight.intakeStatus",
  "coreEvidenceExternalReceiptManifestPreflight.readinessStatus",
  "coreEvidenceExternalReceiptManifestPreflight.preflightStatusLabel",
  "coreEvidenceExternalReceiptManifestPreflight.receiptManifestReceivedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceReceivedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceValidatedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceFileRecordedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceHashRecordedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceUploadedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.evidenceAttachedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.readyToAttachLabel",
  "coreEvidenceExternalReceiptManifestPreflight.readyToMarkLabel",
  "coreEvidenceExternalReceiptManifestPreflight.paritySuccessClaimedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.releaseReadyClaimedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.noRawValuesInManifestLabel",
  "coreEvidenceExternalReceiptManifestPreflight.noPrivatePathsInManifestLabel",
  "coreEvidenceExternalReceiptManifestPreflight.noSecretsInManifestLabel",
  "coreEvidenceExternalReceiptManifestPreflight.noEvidenceFileRecordedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.noEvidenceHashRecordedLabel",
  "coreEvidenceExternalReceiptManifestPreflight.safePreflightLabels",
  "coreEvidenceExternalReceiptManifestPreflight.safePreflightFields",
  "coreEvidenceExternalReceiptManifestPreflight.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestPreflight.operatorNote",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.stage",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.schemaVersion",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.status",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamPreflightSchemaVersion",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamPreflightStage",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamPreflightStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamTemplateSchemaVersion",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamTemplateStage",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.upstreamTemplateStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.caseReceiptManifestAcceptanceGateRows",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.attachmentReceiptManifestAcceptanceGateRows",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.pendingExternalEvidenceReceiptManifestAcceptanceCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.pendingJhoraReceiptManifestAcceptanceCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.pendingParasharaLightReceiptManifestAcceptanceCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestReceivedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestAcceptedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestRejectedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceReceivedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceValidatedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceFileRecordedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceHashRecordedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceUploadedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.evidenceAttachedCount",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.slotFamilies",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestAcceptanceStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestPreflightStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestTemplateStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptGateStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.intakeStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.readinessStatus",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.acceptanceGateStatusLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestStatusLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestAcceptanceStatusLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestRejectionStatusLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestAcceptedLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.receiptManifestRejectedLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.noUploadExecutedLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.noAttachmentExecutedLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.noMarkCommandExecutedLabel",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.safeAcceptanceLabels",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.safeAcceptanceFields",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.acceptanceCriteriaLabels",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestAcceptanceGate.operatorNote",
  "coreEvidenceExternalReceiptManifestDecisionAudit.stage",
  "coreEvidenceExternalReceiptManifestDecisionAudit.schemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAudit.status",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamDecisionQueueSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamDecisionQueueStage",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamDecisionQueueStatus",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamAcceptanceGateSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamAcceptanceGateStage",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamAcceptanceGateStatus",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamPreflightSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamPreflightStage",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamPreflightStatus",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamTemplateSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamTemplateStage",
  "coreEvidenceExternalReceiptManifestDecisionAudit.upstreamTemplateStatus",
  "coreEvidenceExternalReceiptManifestDecisionAudit.caseReceiptManifestDecisionAuditRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.attachmentReceiptManifestDecisionAuditRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.pendingExternalEvidenceReceiptManifestDecisionAuditCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.pendingJhoraReceiptManifestDecisionAuditCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.pendingParasharaLightReceiptManifestDecisionAuditCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionQueueRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionRecordedCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditedCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditPassedCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditFailedCount",
  "coreEvidenceExternalReceiptManifestDecisionAudit.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestDecisionAudit.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestDecisionAudit.slotFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAudit.receiptGateStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.intakeStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.readinessStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionQueueStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.receiptManifestStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditRecordStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionRecordedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditPassedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditFailedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.readyToAttachLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.readyToMarkLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.paritySuccessClaimedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.releaseReadyClaimedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noRawValuesInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noPrivatePathsInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noSecretsInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noEvidenceFileRecordedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noEvidenceHashRecordedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noUploadExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noAttachmentExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.noMarkCommandExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAudit.safeDecisionAuditLabels",
  "coreEvidenceExternalReceiptManifestDecisionAudit.safeDecisionAuditFields",
  "coreEvidenceExternalReceiptManifestDecisionAudit.decisionAuditCriteriaLabels",
  "coreEvidenceExternalReceiptManifestDecisionAudit.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAudit.operatorNote",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.stage",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.schemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.status",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.upstreamDecisionAuditSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.upstreamDecisionAuditStage",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.upstreamDecisionAuditStatus",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.caseDecisionAuditWorkOrderRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.attachmentDecisionAuditWorkOrderRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.pendingExternalEvidenceDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.pendingJhoraDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.pendingParasharaLightDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditWorkOrderReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditWorkOrderBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionRecordedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditPassedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditFailedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.slotFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditWorkOrderStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionQueueStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.receiptGateStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.intakeStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.readinessStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.receiptManifestStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditRecordStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.workOrderDeliveryStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.humanDecisionAuditStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noRawValuesInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noPrivatePathsInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noSecretsInManifestLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noEvidenceFileRecordedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noEvidenceHashRecordedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noUploadExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noAttachmentExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noMarkCommandExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noAcceptExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noRejectExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noDeferExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noExternalNotificationSentLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.noExternalTicketCreatedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.safeDecisionAuditWorkOrderLabels",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.safeDecisionAuditWorkOrderFields",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.decisionAuditWorkOrderCriteriaLabels",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrders.operatorNote",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.stage",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.schemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.status",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditWorkOrdersSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditWorkOrdersStage",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditWorkOrdersStatus",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditStage",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.upstreamDecisionAuditStatus",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.caseDecisionAuditWorkOrderRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.attachmentDecisionAuditWorkOrderRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorHandoffCasePacketRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorHandoffAttachmentPacketRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.pendingExternalEvidenceDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.pendingJhoraDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.pendingParasharaLightDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditWorkOrderReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditWorkOrderBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorHandoffReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorHandoffBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.workOrderDeliveryReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.workOrderDeliveryBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionRecordedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditPassedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditFailedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.selectedCaseIds",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.slotFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditWorkOrderReadinessStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditWorkOrderStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionQueueStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.receiptGateStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.intakeStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.readinessStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.receiptManifestStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.decisionAuditRecordStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.workOrderDeliveryStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorHandoffStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.humanDecisionAuditStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.noWorkOrderDeliveryExecutedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.noOperatorHandoffDeliveredLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.safeDecisionAuditWorkOrderReadinessLabels",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.safeDecisionAuditWorkOrderReadinessFields",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAuditWorkOrderReadiness.operatorNote",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.stage",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.schemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.status",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrderReadinessSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrderReadinessStage",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrderReadinessStatus",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrdersSchemaVersion",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrdersStage",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.upstreamDecisionAuditWorkOrdersStatus",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffCasePacketRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffAttachmentPacketRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffSmokeCaseRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffSmokeAttachmentRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.safeValidationCommandFamilyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.unsafeExternalActionCommandCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.commandExecutionPerformedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.commandSmokeMatrixReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.commandSmokeMatrixBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.workOrderDeliveryReadyCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.workOrderDeliveryBlockedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.pendingExternalEvidenceDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.pendingJhoraDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.pendingParasharaLightDecisionAuditWorkOrderCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.decisionRecordedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.decisionAuditedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.decisionAuditPassedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.decisionAuditFailedCount",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.readyToAttachRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.readyToMarkRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.remainingNotReviewedRows",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorHandoffSmokeMatrixStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.commandSmokeMatrixStatusLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.safeValidationOnlyLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.noCommandExecutionPerformedLabel",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.safeValidationCommandFamilies",
  "coreEvidenceExternalReceiptManifestDecisionAuditOperatorHandoffSmokeMatrix.operatorNote",
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
assert(!helperSlice.includes('latestStage: "P71-A"'), "Core evidence pipeline helper must not retain stale P71 latest stage");
assert(!helperSlice.includes('latestStage: "P73-A"'), "Core evidence pipeline helper must not retain stale P73 latest stage");
assert(!helperSlice.includes('latestStage: "P75-A"'), "Core evidence pipeline helper must not retain stale P75 latest stage");
assert(!helperSlice.includes('latestStage: "P77-A"'), "Core evidence pipeline helper must not retain stale P77 latest stage");
assert(!helperSlice.includes('latestStage: "P79-A"'), "Core evidence pipeline helper must not retain stale P79 latest stage");
assert(!helperSlice.includes('latestStage: "P81-A"'), "Core evidence pipeline helper must not retain stale P81 latest stage");
assert(!helperSlice.includes('latestStage: "P83-A"'), "Core evidence pipeline helper must not retain stale P83 latest stage");
assert(!helperSlice.includes('latestStage: "P85-A"'), "Core evidence pipeline helper must not retain stale P85 latest stage");
assert(!helperSlice.includes('latestStage: "P87-A"'), "Core evidence pipeline helper must not retain stale P87 latest stage");
assert(!helperSlice.includes('latestStage: "P89-A"'), "Core evidence pipeline helper must not retain stale P89 latest stage");
assert(!helperSlice.includes('latestStage: "P91-A"'), "Core evidence pipeline helper must not retain stale P91 latest stage");
assert(!helperSlice.includes('latestStage: "P93-A"'), "Core evidence pipeline helper must not retain stale P93 latest stage");
assert(helperSlice.includes('latestStage: "P95-A"'), "Core evidence pipeline helper must expose latest P95 stage");
assert(helperSlice.includes('"P59 attachment gate"'), "Core evidence pipeline helper must expose P59 stage sequence");
assert(helperSlice.includes('"P61 work orders"'), "Core evidence pipeline helper must expose P61 stage sequence");
assert(helperSlice.includes('"P63 handoff"'), "Core evidence pipeline helper must expose P63 stage sequence");
assert(helperSlice.includes('"P65 operator packets"'), "Core evidence pipeline helper must expose P65 stage sequence");
assert(helperSlice.includes('"P67 QA preflight"'), "Core evidence pipeline helper must expose P67 stage sequence");
assert(helperSlice.includes('"P69 attachment readiness"'), "Core evidence pipeline helper must expose P69 stage sequence");
assert(helperSlice.includes('"P71 external intake contract"'), "Core evidence pipeline helper must expose P71 stage sequence");
assert(helperSlice.includes('"P73 external receipt gate"'), "Core evidence pipeline helper must expose P73 stage sequence");
assert(helperSlice.includes('"P75 receipt manifest templates"'), "Core evidence pipeline helper must expose P75 stage sequence");
assert(helperSlice.includes('"P77 receipt manifest preflight"'), "Core evidence pipeline helper must expose P77 stage sequence");
assert(helperSlice.includes('"P79 receipt manifest acceptance gate"'), "Core evidence pipeline helper must expose P79 stage sequence");
assert(helperSlice.includes('"P81 receipt manifest decision queue"'), "Core evidence pipeline helper must expose P81 stage sequence");
assert(helperSlice.includes('"P83 receipt manifest decision audit"'), "Core evidence pipeline helper must expose P83 stage sequence");
assert(helperSlice.includes('"P85 decision audit work orders"'), "Core evidence pipeline helper must expose P85 stage sequence");
assert(helperSlice.includes('"P87 work-order readiness"'), "Core evidence pipeline helper must expose P87 stage sequence");
assert(helperSlice.includes('"P89 operator handoff smoke matrix"'), "Core evidence pipeline helper must expose P89 stage sequence");
assert(helperSlice.includes('"P91 safe-validation transcript"'), "Core evidence pipeline helper must expose P91 stage sequence");
assert(helperSlice.includes('"P93 safe-validation result ledger"'), "Core evidence pipeline helper must expose P93 stage sequence");
assert(helperSlice.includes('"P95 safe-validation result audit"'), "Core evidence pipeline helper must expose P95 stage sequence");
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
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-gate-v1"'), "Core evidence external receipt gate helper must expose schema version");
assert(helperSlice.includes('stage: "P73-A"'), "Core evidence external receipt gate helper must expose P73-A stage");
assert(helperSlice.includes("caseReceiptGateRows: 5"), "Core evidence external receipt gate helper must expose 5 case receipt rows");
assert(helperSlice.includes("attachmentReceiptSlotRows: 10"), "Core evidence external receipt gate helper must expose 10 receipt slot rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptCount: 10"), "Core evidence external receipt gate helper must expose 10 pending receipts");
assert(helperSlice.includes("pendingJhoraReceiptCount: 5"), "Core evidence external receipt gate helper must expose 5 pending JHora receipts");
assert(helperSlice.includes("pendingParasharaLightReceiptCount: 5"), "Core evidence external receipt gate helper must expose 5 pending Parashara Light receipts");
assert(helperSlice.includes("evidenceReceivedCount: 0"), "Core evidence external receipt gate helper must expose 0 received count");
assert(helperSlice.includes("evidenceValidatedCount: 0"), "Core evidence external receipt gate helper must expose 0 validated count");
assert(helperSlice.includes("evidenceUploadedCount: 0"), "Core evidence external receipt gate helper must expose 0 uploaded count");
assert(helperSlice.includes("evidenceAttachedCount: 0"), "Core evidence external receipt gate helper must expose 0 attached count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence external receipt gate helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence external receipt gate helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence external receipt gate helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptGateStatus: "blocked_pending_external_evidence_receipts"'), "Core evidence external receipt gate helper must expose blocked receipt status");
assert(helperSlice.includes('intakeStatus: "blocked_pending_external_evidence_intake"'), "Core evidence external receipt gate helper must expose blocked intake status");
assert(helperSlice.includes('readinessStatus: "blocked_pending_external_evidence_attachment"'), "Core evidence external receipt gate helper must expose blocked readiness status");
assert(helperSlice.includes('evidenceReceiptStatus: "not_received"'), "Core evidence external receipt gate helper must expose not-received status");
assert(helperSlice.includes('evidenceValidationStatus: "not_started"'), "Core evidence external receipt gate helper must expose not-started validation status");
assert(helperSlice.includes('evidenceFileStatus: "not_attached"'), "Core evidence external receipt gate helper must expose not-attached file status");
assert(helperSlice.includes('evidenceUploadStatus: "not_started"'), "Core evidence external receipt gate helper must expose not-started upload status");
assert(helperSlice.includes('evidenceAttachmentStatus: "not_attached"'), "Core evidence external receipt gate helper must expose not-attached attachment status");
assert(helperSlice.includes('readyToAttachLabel: "ready_to_attach=false"'), "Core evidence external receipt gate helper must expose false ready-to-attach label");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence external receipt gate helper must expose false ready-to-mark label");
assert(helperSlice.includes('evidenceReceivedLabel: "evidence_received_count=0"'), "Core evidence external receipt gate helper must expose zero received label");
assert(helperSlice.includes('evidenceValidatedLabel: "evidence_validated_count=0"'), "Core evidence external receipt gate helper must expose zero validated label");
assert(helperSlice.includes('paritySuccessClaimedLabel: "parity_success_claimed=false"'), "Core evidence external receipt gate helper must expose false parity-success label");
assert(helperSlice.includes('releaseReadyClaimedLabel: "release_ready_claimed=false"'), "Core evidence external receipt gate helper must expose false release-ready label");
assert(helperSlice.includes('"await_jhora_screenshot_or_packet_receipt"'), "Core evidence external receipt gate helper must expose JHora receipt label");
assert(helperSlice.includes('"await_parashara_light_manual_values_or_packet_receipt"'), "Core evidence external receipt gate helper must expose Parashara Light receipt label");
assert(helperSlice.includes('"record_external_evidence_receipt_manifest"'), "Core evidence external receipt gate helper must expose receipt manifest label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_gate_report"'), "Core evidence external receipt gate helper must expose P73 validation command");
assert(helperSlice.includes("external evidence receipts have not been received or validated"), "Core evidence external receipt gate helper must expose receipt blocker");
assert(helperSlice.includes("receipt rows are labels only"), "Core evidence external receipt gate helper must expose labels-only note");
assert(helperSlice.includes("collection/upload/attachment/mark commands are not executed"), "Core evidence external receipt gate helper must expose non-execution note");
assert(preflightSlice.includes("P73 external receipt gate"), "Core evidence pipeline UI must render P73 stage");
assert(preflightSlice.includes("Core evidence external receipt gate"), "Core evidence external receipt gate UI must render its heading");
assert(accuracyRoute.includes("P73-A"), "Accuracy route marker must expose P73 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-gate-v1"), "Accuracy route marker must expose P73 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipts"), "Accuracy route marker must expose P73 status");
assert(accuracyRoute.includes("5 case receipt gate rows"), "Accuracy route marker must expose P73 case receipt rows");
assert(accuracyRoute.includes("10 attachment receipt slot rows"), "Accuracy route marker must expose P73 receipt slot rows");
assert(accuracyRoute.includes("10 pending external evidence receipts"), "Accuracy route marker must expose P73 pending receipt count");
assert(accuracyRoute.includes("5 pending JHora receipts"), "Accuracy route marker must expose P73 pending JHora receipt count");
assert(accuracyRoute.includes("5 pending Parashara Light receipts"), "Accuracy route marker must expose P73 pending Parashara Light receipt count");
assert(accuracyRoute.includes("0 received"), "Accuracy route marker must expose P73 received count");
assert(accuracyRoute.includes("0 validated"), "Accuracy route marker must expose P73 validated count");
assert(accuracyRoute.includes("0 uploaded"), "Accuracy route marker must expose P73 uploaded count");
assert(accuracyRoute.includes("0 attached"), "Accuracy route marker must expose P73 attached count");
assert(accuracyRoute.includes("0 ready-to-attach"), "Accuracy route marker must expose P73 ready-to-attach count");
assert(accuracyRoute.includes("0 ready-to-mark"), "Accuracy route marker must expose P73 ready-to-mark count");
assert(accuracyRoute.includes("20 remaining"), "Accuracy route marker must expose P73 remaining count");
assert(accuracyRoute.includes("jhora_screenshot_or_packet, parashara_light_manual_values_or_packet"), "Accuracy route marker must expose P73 slot family order");
assert(accuracyRoute.includes("not_received"), "Accuracy route marker must expose P73 not-received status");
assert(accuracyRoute.includes("evidence_received_count=0"), "Accuracy route marker must expose P73 zero received label");
assert(accuracyRoute.includes("evidence_validated_count=0"), "Accuracy route marker must expose P73 zero validated label");
assert(accuracyRoute.includes("parity_success_claimed=false"), "Accuracy route marker must expose P73 false parity-success label");
assert(accuracyRoute.includes("release_ready_claimed=false"), "Accuracy route marker must expose P73 false release-ready label");
assert(accuracyRoute.includes("external evidence receipts have not been received or validated"), "Accuracy route marker must expose P73 receipt blocker");
assert(accuracyRoute.includes("receipt rows are labels only"), "Accuracy route marker must expose P73 labels-only note");
assert(accuracyRoute.includes("collection/upload/attachment/mark commands are not executed"), "Accuracy route marker must expose P73 non-execution note");
assert(accuracyRoute.includes("await_jhora_screenshot_or_packet_receipt"), "Accuracy route marker must expose P73 JHora receipt label");
assert(accuracyRoute.includes("await_parashara_light_manual_values_or_packet_receipt"), "Accuracy route marker must expose P73 Parashara Light receipt label");
assert(accuracyRoute.includes("record_external_evidence_receipt_manifest"), "Accuracy route marker must expose P73 receipt manifest label");
assert(accuracyRoute.includes("rerun_external_receipt_gate_report"), "Accuracy route marker must expose P73 rerun receipt label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_gate_report"), "Accuracy route marker must expose P73 receipt gate command family");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1"'), "Core evidence receipt manifest templates helper must expose schema version");
assert(helperSlice.includes('stage: "P75-A"'), "Core evidence receipt manifest templates helper must expose P75-A stage");
assert(helperSlice.includes("caseReceiptManifestTemplateRows: 5"), "Core evidence receipt manifest templates helper must expose 5 case template rows");
assert(helperSlice.includes("attachmentReceiptManifestTemplateRows: 10"), "Core evidence receipt manifest templates helper must expose 10 attachment template rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptManifestCount: 10"), "Core evidence receipt manifest templates helper must expose 10 pending manifest rows");
assert(helperSlice.includes("pendingJhoraReceiptManifestCount: 5"), "Core evidence receipt manifest templates helper must expose 5 pending JHora manifests");
assert(helperSlice.includes("pendingParasharaLightReceiptManifestCount: 5"), "Core evidence receipt manifest templates helper must expose 5 pending Parashara Light manifests");
assert(helperSlice.includes("receiptManifestReceivedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 manifest received count");
assert(helperSlice.includes("evidenceReceivedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 evidence received count");
assert(helperSlice.includes("evidenceValidatedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 validated count");
assert(helperSlice.includes("evidenceFileRecordedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 file recorded count");
assert(helperSlice.includes("evidenceHashRecordedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 hash recorded count");
assert(helperSlice.includes("evidenceUploadedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 uploaded count");
assert(helperSlice.includes("evidenceAttachedCount: 0"), "Core evidence receipt manifest templates helper must expose 0 attached count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence receipt manifest templates helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence receipt manifest templates helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence receipt manifest templates helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptManifestTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest templates helper must expose blocked template status");
assert(helperSlice.includes('receiptGateStatus: "blocked_pending_external_evidence_receipts"'), "Core evidence receipt manifest templates helper must expose blocked receipt gate status");
assert(helperSlice.includes('intakeStatus: "blocked_pending_external_evidence_intake"'), "Core evidence receipt manifest templates helper must expose blocked intake status");
assert(helperSlice.includes('readinessStatus: "blocked_pending_external_evidence_attachment"'), "Core evidence receipt manifest templates helper must expose blocked readiness status");
assert(helperSlice.includes('receiptManifestStatus: "not_received"'), "Core evidence receipt manifest templates helper must expose not-received manifest status");
assert(helperSlice.includes('evidenceValidationStatus: "not_started"'), "Core evidence receipt manifest templates helper must expose not-started validation status");
assert(helperSlice.includes('evidenceFileStatus: "not_attached"'), "Core evidence receipt manifest templates helper must expose not-attached file status");
assert(helperSlice.includes('evidenceHashStatus: "not_recorded"'), "Core evidence receipt manifest templates helper must expose not-recorded hash status");
assert(helperSlice.includes('evidenceUploadStatus: "not_started"'), "Core evidence receipt manifest templates helper must expose not-started upload status");
assert(helperSlice.includes('evidenceAttachmentStatus: "not_attached"'), "Core evidence receipt manifest templates helper must expose not-attached attachment status");
assert(helperSlice.includes('readyToAttachLabel: "ready_to_attach=false"'), "Core evidence receipt manifest templates helper must expose false ready-to-attach label");
assert(helperSlice.includes('readyToMarkLabel: "ready_to_mark=false"'), "Core evidence receipt manifest templates helper must expose false ready-to-mark label");
assert(helperSlice.includes('receiptManifestReceivedLabel: "receipt_manifest_received_count=0"'), "Core evidence receipt manifest templates helper must expose zero manifest label");
assert(helperSlice.includes('evidenceFileRecordedLabel: "evidence_file_recorded_count=0"'), "Core evidence receipt manifest templates helper must expose zero file label");
assert(helperSlice.includes('evidenceHashRecordedLabel: "evidence_hash_recorded_count=0"'), "Core evidence receipt manifest templates helper must expose zero hash label");
assert(helperSlice.includes('"await_jhora_receipt_manifest"'), "Core evidence receipt manifest templates helper must expose JHora manifest label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest"'), "Core evidence receipt manifest templates helper must expose Parashara Light manifest label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_templates_report"'), "Core evidence receipt manifest templates helper must expose rerun templates label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_templates_report"'), "Core evidence receipt manifest templates helper must expose P75 validation command");
assert(helperSlice.includes('"human_receipt_timestamp_utc"'), "Core evidence receipt manifest templates helper must expose required safe manifest fields");
assert(helperSlice.includes("template rows are labels only"), "Core evidence receipt manifest templates helper must expose labels-only note");
assert(preflightSlice.includes("P75 receipt manifest templates"), "Core evidence pipeline UI must render P75 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest templates"), "Core evidence receipt manifest templates UI must render its heading");
assert(accuracyRoute.includes("P75-A"), "Accuracy route marker must expose P75 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-templates-v1"), "Accuracy route marker must expose P75 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifests"), "Accuracy route marker must expose P75 status");
assert(accuracyRoute.includes("5 case receipt manifest template rows"), "Accuracy route marker must expose P75 case template rows");
assert(accuracyRoute.includes("10 attachment receipt manifest template rows"), "Accuracy route marker must expose P75 attachment template rows");
assert(accuracyRoute.includes("10 pending external evidence receipt manifests"), "Accuracy route marker must expose P75 pending manifest count");
assert(accuracyRoute.includes("5 pending JHora receipt manifests"), "Accuracy route marker must expose P75 pending JHora manifest count");
assert(accuracyRoute.includes("5 pending Parashara Light receipt manifests"), "Accuracy route marker must expose P75 pending Parashara Light manifest count");
assert(accuracyRoute.includes("receipt_manifest_received_count=0"), "Accuracy route marker must expose P75 zero manifest label");
assert(accuracyRoute.includes("evidence_file_recorded_count=0"), "Accuracy route marker must expose P75 zero file label");
assert(accuracyRoute.includes("evidence_hash_recorded_count=0"), "Accuracy route marker must expose P75 zero hash label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest"), "Accuracy route marker must expose P75 JHora manifest label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest"), "Accuracy route marker must expose P75 Parashara Light manifest label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_templates_report"), "Accuracy route marker must expose P75 rerun templates label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_templates_report"), "Accuracy route marker must expose P75 command family");
assert(accuracyRoute.includes("human_receipt_timestamp_utc"), "Accuracy route marker must expose P75 safe required fields");
assert(accuracyRoute.includes("template rows are labels only"), "Accuracy route marker must expose P75 labels-only note");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-preflight-v1"'), "Core evidence receipt manifest preflight helper must expose schema version");
assert(helperSlice.includes('stage: "P77-A"'), "Core evidence receipt manifest preflight helper must expose P77-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest preflight helper must expose blocked status");
assert(helperSlice.includes('upstreamTemplateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1"'), "Core evidence receipt manifest preflight helper must expose upstream schema");
assert(helperSlice.includes('upstreamTemplateStage: "P75-A"'), "Core evidence receipt manifest preflight helper must expose upstream stage");
assert(helperSlice.includes('upstreamTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest preflight helper must expose upstream status");
assert(helperSlice.includes("caseReceiptManifestPreflightRows: 5"), "Core evidence receipt manifest preflight helper must expose 5 case preflight rows");
assert(helperSlice.includes("attachmentReceiptManifestPreflightRows: 10"), "Core evidence receipt manifest preflight helper must expose 10 attachment preflight rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptManifestPreflightCount: 10"), "Core evidence receipt manifest preflight helper must expose 10 pending preflight rows");
assert(helperSlice.includes("pendingJhoraReceiptManifestPreflightCount: 5"), "Core evidence receipt manifest preflight helper must expose 5 JHora preflight rows");
assert(helperSlice.includes("pendingParasharaLightReceiptManifestPreflightCount: 5"), "Core evidence receipt manifest preflight helper must expose 5 Parashara Light preflight rows");
assert(helperSlice.includes("receiptManifestReceivedCount: 0"), "Core evidence receipt manifest preflight helper must expose 0 manifest received count");
assert(helperSlice.includes("evidenceFileRecordedCount: 0"), "Core evidence receipt manifest preflight helper must expose 0 file recorded count");
assert(helperSlice.includes("evidenceHashRecordedCount: 0"), "Core evidence receipt manifest preflight helper must expose 0 hash recorded count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence receipt manifest preflight helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence receipt manifest preflight helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence receipt manifest preflight helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptManifestPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest preflight helper must expose preflight status");
assert(helperSlice.includes('receiptManifestTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest preflight helper must expose upstream template status");
assert(helperSlice.includes('receiptGateStatus: "blocked_pending_external_evidence_receipts"'), "Core evidence receipt manifest preflight helper must expose receipt gate status");
assert(helperSlice.includes('intakeStatus: "blocked_pending_external_evidence_intake"'), "Core evidence receipt manifest preflight helper must expose intake status");
assert(helperSlice.includes('readinessStatus: "blocked_pending_external_evidence_attachment"'), "Core evidence receipt manifest preflight helper must expose attachment readiness status");
assert(helperSlice.includes('preflightStatusLabel: "preflight_status=blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest preflight helper must expose preflight status label");
assert(helperSlice.includes('noRawValuesInManifestLabel: "no_raw_values_in_manifest=true"'), "Core evidence receipt manifest preflight helper must expose no raw values label");
assert(helperSlice.includes('noPrivatePathsInManifestLabel: "no_private_paths_in_manifest=true"'), "Core evidence receipt manifest preflight helper must expose no private paths label");
assert(helperSlice.includes('noSecretsInManifestLabel: "no_secrets_in_manifest=true"'), "Core evidence receipt manifest preflight helper must expose no secrets label");
assert(helperSlice.includes('noEvidenceFileRecordedLabel: "no_evidence_file_recorded=true"'), "Core evidence receipt manifest preflight helper must expose no evidence file label");
assert(helperSlice.includes('noEvidenceHashRecordedLabel: "no_evidence_hash_recorded=true"'), "Core evidence receipt manifest preflight helper must expose no evidence hash label");
assert(helperSlice.includes('"await_jhora_receipt_manifest_preflight"'), "Core evidence receipt manifest preflight helper must expose JHora preflight label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest_preflight"'), "Core evidence receipt manifest preflight helper must expose Parashara Light preflight label");
assert(helperSlice.includes('"record_external_evidence_receipt_manifest_after_human_review"'), "Core evidence receipt manifest preflight helper must expose human-review record label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_preflight_report"'), "Core evidence receipt manifest preflight helper must expose rerun preflight label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_preflight_report"'), "Core evidence receipt manifest preflight helper must expose P77 validation command");
assert(helperSlice.includes('"redacted_receipt_manifest_id"'), "Core evidence receipt manifest preflight helper must expose redacted manifest id field");
assert(helperSlice.includes('"operator_preflight_note_label"'), "Core evidence receipt manifest preflight helper must expose operator note field");
assert(helperSlice.includes('"required_human_receipt_timestamp_utc"'), "Core evidence receipt manifest preflight helper must expose timestamp field");
assert(helperSlice.includes("external receipt manifest preflight is blocked"), "Core evidence receipt manifest preflight helper must expose blocked preflight note");
assert(preflightSlice.includes("P77 receipt manifest preflight"), "Core evidence pipeline UI must render P77 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest preflight"), "Core evidence receipt manifest preflight UI must render its heading");
assert(accuracyRoute.includes("P77-A"), "Accuracy route marker must expose P77 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-preflight-v1"), "Accuracy route marker must expose P77 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_preflight"), "Accuracy route marker must expose P77 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-templates-v1"), "Accuracy route marker must expose P77 upstream schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifests"), "Accuracy route marker must expose P77 upstream status");
assert(accuracyRoute.includes("case_receipt_manifest_preflight_rows=5"), "Accuracy route marker must expose P77 case preflight count");
assert(accuracyRoute.includes("attachment_receipt_manifest_preflight_rows=10"), "Accuracy route marker must expose P77 attachment preflight count");
assert(accuracyRoute.includes("pending_external_evidence_receipt_manifest_preflight_count=10"), "Accuracy route marker must expose P77 pending preflight count");
assert(accuracyRoute.includes("pending_jhora_receipt_manifest_preflight_count=5"), "Accuracy route marker must expose P77 pending JHora count");
assert(accuracyRoute.includes("pending_parashara_light_receipt_manifest_preflight_count=5"), "Accuracy route marker must expose P77 pending Parashara Light count");
assert(accuracyRoute.includes("receipt_manifest_received_count=0"), "Accuracy route marker must expose P77 zero manifest received count");
assert(accuracyRoute.includes("evidence_file_recorded_count=0"), "Accuracy route marker must expose P77 zero file count");
assert(accuracyRoute.includes("evidence_hash_recorded_count=0"), "Accuracy route marker must expose P77 zero hash count");
assert(accuracyRoute.includes("ready_to_attach_count=0"), "Accuracy route marker must expose P77 zero ready-to-attach count");
assert(accuracyRoute.includes("ready_to_mark_count=0"), "Accuracy route marker must expose P77 zero ready-to-mark count");
assert(accuracyRoute.includes("remaining_not_reviewed_count=20"), "Accuracy route marker must expose P77 remaining count");
assert(accuracyRoute.includes("expected_receipt_manifest_label"), "Accuracy route marker must expose P77 expected label field");
assert(accuracyRoute.includes("redacted_receipt_manifest_id"), "Accuracy route marker must expose P77 redacted id field");
assert(accuracyRoute.includes("operator_preflight_note_label"), "Accuracy route marker must expose P77 operator note field");
assert(accuracyRoute.includes("required_human_receipt_timestamp_utc"), "Accuracy route marker must expose P77 timestamp field");
assert(accuracyRoute.includes("no_raw_values_in_manifest=true"), "Accuracy route marker must expose P77 no raw values label");
assert(accuracyRoute.includes("no_private_paths_in_manifest=true"), "Accuracy route marker must expose P77 no private path label");
assert(accuracyRoute.includes("no_secrets_in_manifest=true"), "Accuracy route marker must expose P77 no secrets label");
assert(accuracyRoute.includes("no_evidence_file_recorded=true"), "Accuracy route marker must expose P77 no evidence file label");
assert(accuracyRoute.includes("no_evidence_hash_recorded=true"), "Accuracy route marker must expose P77 no evidence hash label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest_preflight"), "Accuracy route marker must expose P77 JHora preflight label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest_preflight"), "Accuracy route marker must expose P77 Parashara Light preflight label");
assert(accuracyRoute.includes("record_external_evidence_receipt_manifest_after_human_review"), "Accuracy route marker must expose P77 human review record label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_preflight_report"), "Accuracy route marker must expose P77 rerun preflight label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_preflight_report"), "Accuracy route marker must expose P77 command family");
assert(accuracyRoute.includes("blocked human/operator preflight"), "Accuracy route marker must expose P77 blocked operator copy");
assert(accuracyRoute.includes("labels-only handoff"), "Accuracy route marker must expose P77 labels-only copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"'), "Core evidence receipt manifest acceptance helper must expose schema version");
assert(helperSlice.includes('stage: "P79-A"'), "Core evidence receipt manifest acceptance helper must expose P79-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_acceptance"'), "Core evidence receipt manifest acceptance helper must expose blocked status");
assert(helperSlice.includes('upstreamPreflightSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-preflight-v1"'), "Core evidence receipt manifest acceptance helper must expose upstream P77 schema");
assert(helperSlice.includes('upstreamPreflightStage: "P77-A"'), "Core evidence receipt manifest acceptance helper must expose upstream P77 stage");
assert(helperSlice.includes('upstreamPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest acceptance helper must expose upstream P77 status");
assert(helperSlice.includes('upstreamTemplateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1"'), "Core evidence receipt manifest acceptance helper must expose upstream P75 schema");
assert(helperSlice.includes('upstreamTemplateStage: "P75-A"'), "Core evidence receipt manifest acceptance helper must expose upstream P75 stage");
assert(helperSlice.includes('upstreamTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest acceptance helper must expose upstream P75 status");
assert(helperSlice.includes("caseReceiptManifestAcceptanceGateRows: 5"), "Core evidence receipt manifest acceptance helper must expose 5 case rows");
assert(helperSlice.includes("attachmentReceiptManifestAcceptanceGateRows: 10"), "Core evidence receipt manifest acceptance helper must expose 10 attachment rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptManifestAcceptanceCount: 10"), "Core evidence receipt manifest acceptance helper must expose 10 pending acceptance rows");
assert(helperSlice.includes("pendingJhoraReceiptManifestAcceptanceCount: 5"), "Core evidence receipt manifest acceptance helper must expose 5 JHora acceptance rows");
assert(helperSlice.includes("pendingParasharaLightReceiptManifestAcceptanceCount: 5"), "Core evidence receipt manifest acceptance helper must expose 5 Parashara Light acceptance rows");
assert(helperSlice.includes("receiptManifestAcceptedCount: 0"), "Core evidence receipt manifest acceptance helper must expose 0 accepted count");
assert(helperSlice.includes("receiptManifestRejectedCount: 0"), "Core evidence receipt manifest acceptance helper must expose 0 rejected count");
assert(helperSlice.includes("evidenceFileRecordedCount: 0"), "Core evidence receipt manifest acceptance helper must expose 0 file recorded count");
assert(helperSlice.includes("evidenceHashRecordedCount: 0"), "Core evidence receipt manifest acceptance helper must expose 0 hash recorded count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence receipt manifest acceptance helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence receipt manifest acceptance helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence receipt manifest acceptance helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptManifestAcceptanceStatus: "blocked_pending_external_evidence_receipt_manifest_acceptance"'), "Core evidence receipt manifest acceptance helper must expose acceptance status");
assert(helperSlice.includes('receiptManifestPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest acceptance helper must expose P77 preflight status");
assert(helperSlice.includes('receiptManifestStatusLabel: "receipt_manifest_status=not_received"'), "Core evidence receipt manifest acceptance helper must expose not-received label");
assert(helperSlice.includes('receiptManifestAcceptanceStatusLabel: "receipt_manifest_acceptance_status=not_started"'), "Core evidence receipt manifest acceptance helper must expose not-started acceptance label");
assert(helperSlice.includes('receiptManifestRejectionStatusLabel: "receipt_manifest_rejection_status=not_started"'), "Core evidence receipt manifest acceptance helper must expose not-started rejection label");
assert(helperSlice.includes('noUploadExecutedLabel: "no_upload_executed=true"'), "Core evidence receipt manifest acceptance helper must expose no upload label");
assert(helperSlice.includes('noAttachmentExecutedLabel: "no_attachment_executed=true"'), "Core evidence receipt manifest acceptance helper must expose no attachment label");
assert(helperSlice.includes('noMarkCommandExecutedLabel: "no_mark_command_executed=true"'), "Core evidence receipt manifest acceptance helper must expose no mark label");
assert(helperSlice.includes('"await_jhora_receipt_manifest_acceptance"'), "Core evidence receipt manifest acceptance helper must expose JHora acceptance label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest_acceptance"'), "Core evidence receipt manifest acceptance helper must expose Parashara Light acceptance label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_acceptance_gate_report"'), "Core evidence receipt manifest acceptance helper must expose rerun acceptance label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_acceptance_gate_report"'), "Core evidence receipt manifest acceptance helper must expose P79 command family");
assert(helperSlice.includes('"operator_acceptance_note_label"'), "Core evidence receipt manifest acceptance helper must expose operator acceptance note field");
assert(helperSlice.includes('"require_human_receipt_timestamp_utc"'), "Core evidence receipt manifest acceptance helper must expose human timestamp criterion");
assert(helperSlice.includes('"block_upload_until_manifest_accepted"'), "Core evidence receipt manifest acceptance helper must expose upload block criterion");
assert(helperSlice.includes('"block_attachment_until_manifest_accepted"'), "Core evidence receipt manifest acceptance helper must expose attachment block criterion");
assert(helperSlice.includes('"block_mark_until_manifest_accepted"'), "Core evidence receipt manifest acceptance helper must expose mark block criterion");
assert(preflightSlice.includes("P79 receipt manifest acceptance gate"), "Core evidence pipeline UI must render P79 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest acceptance gate"), "Core evidence receipt manifest acceptance UI must render its heading");
assert(accuracyRoute.includes("P79-A"), "Accuracy route marker must expose P79 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"), "Accuracy route marker must expose P79 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_acceptance"), "Accuracy route marker must expose P79 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-preflight-v1"), "Accuracy route marker must expose P79 upstream P77 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_preflight"), "Accuracy route marker must expose P79 upstream P77 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-templates-v1"), "Accuracy route marker must expose P79 upstream P75 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifests"), "Accuracy route marker must expose P79 upstream P75 status");
assert(accuracyRoute.includes("case_receipt_manifest_acceptance_gate_rows=5"), "Accuracy route marker must expose P79 case count");
assert(accuracyRoute.includes("attachment_receipt_manifest_acceptance_gate_rows=10"), "Accuracy route marker must expose P79 attachment count");
assert(accuracyRoute.includes("pending_external_evidence_receipt_manifest_acceptance_count=10"), "Accuracy route marker must expose P79 pending acceptance count");
assert(accuracyRoute.includes("pending_jhora_receipt_manifest_acceptance_count=5"), "Accuracy route marker must expose P79 pending JHora count");
assert(accuracyRoute.includes("pending_parashara_light_receipt_manifest_acceptance_count=5"), "Accuracy route marker must expose P79 pending Parashara Light count");
assert(accuracyRoute.includes("receipt_manifest_accepted_count=0"), "Accuracy route marker must expose P79 accepted zero count");
assert(accuracyRoute.includes("receipt_manifest_rejected_count=0"), "Accuracy route marker must expose P79 rejected zero count");
assert(accuracyRoute.includes("evidence_file_recorded_count=0"), "Accuracy route marker must expose P79 zero file count");
assert(accuracyRoute.includes("evidence_hash_recorded_count=0"), "Accuracy route marker must expose P79 zero hash count");
assert(accuracyRoute.includes("ready_to_attach_count=0"), "Accuracy route marker must expose P79 zero ready-to-attach count");
assert(accuracyRoute.includes("ready_to_mark_count=0"), "Accuracy route marker must expose P79 zero ready-to-mark count");
assert(accuracyRoute.includes("remaining_not_reviewed_count=20"), "Accuracy route marker must expose P79 remaining count");
assert(accuracyRoute.includes("operator_acceptance_note_label"), "Accuracy route marker must expose P79 operator acceptance field");
assert(accuracyRoute.includes("acceptance_gate_status=blocked_pending_external_evidence_receipt_manifest_acceptance"), "Accuracy route marker must expose P79 acceptance status label");
assert(accuracyRoute.includes("receipt_manifest_status=not_received"), "Accuracy route marker must expose P79 not-received status");
assert(accuracyRoute.includes("receipt_manifest_acceptance_status=not_started"), "Accuracy route marker must expose P79 not-started acceptance status");
assert(accuracyRoute.includes("receipt_manifest_rejection_status=not_started"), "Accuracy route marker must expose P79 not-started rejection status");
assert(accuracyRoute.includes("no_upload_executed=true"), "Accuracy route marker must expose P79 no-upload label");
assert(accuracyRoute.includes("no_attachment_executed=true"), "Accuracy route marker must expose P79 no-attachment label");
assert(accuracyRoute.includes("no_mark_command_executed=true"), "Accuracy route marker must expose P79 no-mark label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest_acceptance"), "Accuracy route marker must expose P79 JHora acceptance label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest_acceptance"), "Accuracy route marker must expose P79 Parashara Light acceptance label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_acceptance_gate_report"), "Accuracy route marker must expose P79 rerun acceptance label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_acceptance_gate_report"), "Accuracy route marker must expose P79 command family");
assert(accuracyRoute.includes("require_human_receipt_timestamp_utc"), "Accuracy route marker must expose P79 timestamp criterion");
assert(accuracyRoute.includes("require_redacted_receipt_manifest_id"), "Accuracy route marker must expose P79 redacted id criterion");
assert(accuracyRoute.includes("require_operator_acceptance_note_label"), "Accuracy route marker must expose P79 note criterion");
assert(accuracyRoute.includes("require_no_raw_values_in_manifest"), "Accuracy route marker must expose P79 no raw values criterion");
assert(accuracyRoute.includes("require_no_private_paths_in_manifest"), "Accuracy route marker must expose P79 no private paths criterion");
assert(accuracyRoute.includes("require_no_secrets_in_manifest"), "Accuracy route marker must expose P79 no secrets criterion");
assert(accuracyRoute.includes("require_no_evidence_file_recorded_before_acceptance"), "Accuracy route marker must expose P79 no file criterion");
assert(accuracyRoute.includes("require_no_evidence_hash_recorded_before_acceptance"), "Accuracy route marker must expose P79 no hash criterion");
assert(accuracyRoute.includes("block_upload_until_manifest_accepted"), "Accuracy route marker must expose P79 upload block criterion");
assert(accuracyRoute.includes("block_attachment_until_manifest_accepted"), "Accuracy route marker must expose P79 attachment block criterion");
assert(accuracyRoute.includes("block_mark_until_manifest_accepted"), "Accuracy route marker must expose P79 mark block criterion");
assert(accuracyRoute.includes("blocked acceptance gate for future human-submitted receipt manifests"), "Accuracy route marker must expose P79 blocked acceptance copy");
assert(accuracyRoute.includes("no manifest has been received, accepted, rejected, uploaded, attached, or marked"), "Accuracy route marker must expose P79 negative status copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1"'), "Core evidence receipt manifest decision helper must expose schema version");
assert(helperSlice.includes('stage: "P81-A"'), "Core evidence receipt manifest decision helper must expose P81-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose blocked status");
assert(helperSlice.includes('upstreamAcceptanceGateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"'), "Core evidence receipt manifest decision helper must expose upstream P79 schema");
assert(helperSlice.includes('upstreamAcceptanceGateStage: "P79-A"'), "Core evidence receipt manifest decision helper must expose upstream P79 stage");
assert(helperSlice.includes('upstreamAcceptanceGateStatus: "blocked_pending_external_evidence_receipt_manifest_acceptance"'), "Core evidence receipt manifest decision helper must expose upstream P79 status");
assert(helperSlice.includes('upstreamPreflightSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-preflight-v1"'), "Core evidence receipt manifest decision helper must expose upstream P77 schema");
assert(helperSlice.includes('upstreamPreflightStage: "P77-A"'), "Core evidence receipt manifest decision helper must expose upstream P77 stage");
assert(helperSlice.includes('upstreamPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest decision helper must expose upstream P77 status");
assert(helperSlice.includes('upstreamTemplateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1"'), "Core evidence receipt manifest decision helper must expose upstream P75 schema");
assert(helperSlice.includes('upstreamTemplateStage: "P75-A"'), "Core evidence receipt manifest decision helper must expose upstream P75 stage");
assert(helperSlice.includes('upstreamTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest decision helper must expose upstream P75 status");
assert(helperSlice.includes("caseReceiptManifestDecisionQueueRows: 5"), "Core evidence receipt manifest decision helper must expose 5 case rows");
assert(helperSlice.includes("attachmentReceiptManifestDecisionQueueRows: 10"), "Core evidence receipt manifest decision helper must expose 10 attachment rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptManifestDecisionCount: 10"), "Core evidence receipt manifest decision helper must expose 10 pending decision rows");
assert(helperSlice.includes("pendingJhoraReceiptManifestDecisionCount: 5"), "Core evidence receipt manifest decision helper must expose 5 JHora decision rows");
assert(helperSlice.includes("pendingParasharaLightReceiptManifestDecisionCount: 5"), "Core evidence receipt manifest decision helper must expose 5 Parashara Light decision rows");
assert(helperSlice.includes("receiptManifestDeferredCount: 0"), "Core evidence receipt manifest decision helper must expose 0 deferred count");
assert(helperSlice.includes("decisionRecordedCount: 0"), "Core evidence receipt manifest decision helper must expose 0 decision-recorded count");
assert(helperSlice.includes("evidenceFileRecordedCount: 0"), "Core evidence receipt manifest decision helper must expose 0 file recorded count");
assert(helperSlice.includes("evidenceHashRecordedCount: 0"), "Core evidence receipt manifest decision helper must expose 0 hash recorded count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence receipt manifest decision helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence receipt manifest decision helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence receipt manifest decision helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptManifestDecisionStatus: "blocked_pending_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose decision status");
assert(helperSlice.includes('receiptManifestAcceptanceStatus: "blocked_pending_external_evidence_receipt_manifest_acceptance"'), "Core evidence receipt manifest decision helper must expose P79 acceptance status");
assert(helperSlice.includes('receiptManifestPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest decision helper must expose P77 preflight status");
assert(helperSlice.includes('decisionQueueStatusLabel: "decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose decision queue label");
assert(helperSlice.includes('receiptManifestStatusLabel: "receipt_manifest_status=not_received"'), "Core evidence receipt manifest decision helper must expose not-received label");
assert(helperSlice.includes('receiptManifestAcceptanceStatusLabel: "receipt_manifest_acceptance_status=not_started"'), "Core evidence receipt manifest decision helper must expose not-started acceptance label");
assert(helperSlice.includes('receiptManifestRejectionStatusLabel: "receipt_manifest_rejection_status=not_started"'), "Core evidence receipt manifest decision helper must expose not-started rejection label");
assert(helperSlice.includes('receiptManifestDeferStatusLabel: "receipt_manifest_defer_status=not_started"'), "Core evidence receipt manifest decision helper must expose not-started defer label");
assert(helperSlice.includes('decisionRecordStatusLabel: "decision_record_status=not_started"'), "Core evidence receipt manifest decision helper must expose not-started decision record label");
assert(helperSlice.includes('noUploadExecutedLabel: "no_upload_executed=true"'), "Core evidence receipt manifest decision helper must expose no upload label");
assert(helperSlice.includes('noAttachmentExecutedLabel: "no_attachment_executed=true"'), "Core evidence receipt manifest decision helper must expose no attachment label");
assert(helperSlice.includes('noMarkCommandExecutedLabel: "no_mark_command_executed=true"'), "Core evidence receipt manifest decision helper must expose no mark label");
assert(helperSlice.includes('"await_jhora_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose JHora decision label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose Parashara Light decision label");
assert(helperSlice.includes('"record_external_evidence_receipt_manifest_decision_after_human_review"'), "Core evidence receipt manifest decision helper must expose human review decision label");
assert(helperSlice.includes('"defer_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision helper must expose defer label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_decision_queue_report"'), "Core evidence receipt manifest decision helper must expose rerun decision label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_decision_queue_report"'), "Core evidence receipt manifest decision helper must expose P81 command family");
assert(helperSlice.includes('"operator_decision_label"'), "Core evidence receipt manifest decision helper must expose operator decision field");
assert(helperSlice.includes('"require_human_decision_timestamp_utc"'), "Core evidence receipt manifest decision helper must expose human decision timestamp criterion");
assert(helperSlice.includes('"require_operator_decision_label"'), "Core evidence receipt manifest decision helper must expose operator decision criterion");
assert(helperSlice.includes('"require_accept_or_reject_or_defer_label"'), "Core evidence receipt manifest decision helper must expose accept/reject/defer criterion");
assert(helperSlice.includes('"block_upload_until_manifest_decision_recorded"'), "Core evidence receipt manifest decision helper must expose upload block criterion");
assert(helperSlice.includes('"block_attachment_until_manifest_decision_recorded"'), "Core evidence receipt manifest decision helper must expose attachment block criterion");
assert(helperSlice.includes('"block_mark_until_manifest_decision_recorded"'), "Core evidence receipt manifest decision helper must expose mark block criterion");
assert(preflightSlice.includes("P81 receipt manifest decision queue"), "Core evidence pipeline UI must render P81 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision queue"), "Core evidence receipt manifest decision UI must render its heading");
assert(accuracyRoute.includes("P81-A"), "Accuracy route marker must expose P81 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-queue-v1"), "Accuracy route marker must expose P81 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision"), "Accuracy route marker must expose P81 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"), "Accuracy route marker must expose P81 upstream P79 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_acceptance"), "Accuracy route marker must expose P81 upstream P79 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-preflight-v1"), "Accuracy route marker must expose P81 upstream P77 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_preflight"), "Accuracy route marker must expose P81 upstream P77 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-templates-v1"), "Accuracy route marker must expose P81 upstream P75 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifests"), "Accuracy route marker must expose P81 upstream P75 status");
assert(accuracyRoute.includes("case_receipt_manifest_decision_queue_rows=5"), "Accuracy route marker must expose P81 case count");
assert(accuracyRoute.includes("attachment_receipt_manifest_decision_queue_rows=10"), "Accuracy route marker must expose P81 attachment count");
assert(accuracyRoute.includes("pending_external_evidence_receipt_manifest_decision_count=10"), "Accuracy route marker must expose P81 pending decision count");
assert(accuracyRoute.includes("pending_jhora_receipt_manifest_decision_count=5"), "Accuracy route marker must expose P81 pending JHora count");
assert(accuracyRoute.includes("pending_parashara_light_receipt_manifest_decision_count=5"), "Accuracy route marker must expose P81 pending Parashara Light count");
assert(accuracyRoute.includes("receipt_manifest_deferred_count=0"), "Accuracy route marker must expose P81 deferred zero count");
assert(accuracyRoute.includes("decision_recorded_count=0"), "Accuracy route marker must expose P81 decision-recorded zero count");
assert(accuracyRoute.includes("evidence_file_recorded_count=0"), "Accuracy route marker must expose P81 zero file count");
assert(accuracyRoute.includes("evidence_hash_recorded_count=0"), "Accuracy route marker must expose P81 zero hash count");
assert(accuracyRoute.includes("ready_to_attach_count=0"), "Accuracy route marker must expose P81 zero ready-to-attach count");
assert(accuracyRoute.includes("ready_to_mark_count=0"), "Accuracy route marker must expose P81 zero ready-to-mark count");
assert(accuracyRoute.includes("remaining_not_reviewed_count=20"), "Accuracy route marker must expose P81 remaining count");
assert(accuracyRoute.includes("operator_decision_label"), "Accuracy route marker must expose P81 operator decision field");
assert(accuracyRoute.includes("decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision"), "Accuracy route marker must expose P81 decision status label");
assert(accuracyRoute.includes("receipt_manifest_status=not_received"), "Accuracy route marker must expose P81 not-received status");
assert(accuracyRoute.includes("receipt_manifest_acceptance_status=not_started"), "Accuracy route marker must expose P81 not-started acceptance status");
assert(accuracyRoute.includes("receipt_manifest_rejection_status=not_started"), "Accuracy route marker must expose P81 not-started rejection status");
assert(accuracyRoute.includes("receipt_manifest_defer_status=not_started"), "Accuracy route marker must expose P81 not-started defer status");
assert(accuracyRoute.includes("decision_record_status=not_started"), "Accuracy route marker must expose P81 not-started decision record status");
assert(accuracyRoute.includes("no_upload_executed=true"), "Accuracy route marker must expose P81 no-upload label");
assert(accuracyRoute.includes("no_attachment_executed=true"), "Accuracy route marker must expose P81 no-attachment label");
assert(accuracyRoute.includes("no_mark_command_executed=true"), "Accuracy route marker must expose P81 no-mark label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest_decision"), "Accuracy route marker must expose P81 JHora decision label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest_decision"), "Accuracy route marker must expose P81 Parashara Light decision label");
assert(accuracyRoute.includes("record_external_evidence_receipt_manifest_decision_after_human_review"), "Accuracy route marker must expose P81 human review decision label");
assert(accuracyRoute.includes("defer_external_evidence_receipt_manifest_decision"), "Accuracy route marker must expose P81 defer decision label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_decision_queue_report"), "Accuracy route marker must expose P81 rerun decision label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_decision_queue_report"), "Accuracy route marker must expose P81 command family");
assert(accuracyRoute.includes("require_human_decision_timestamp_utc"), "Accuracy route marker must expose P81 timestamp criterion");
assert(accuracyRoute.includes("require_redacted_receipt_manifest_id"), "Accuracy route marker must expose P81 redacted id criterion");
assert(accuracyRoute.includes("require_operator_decision_label"), "Accuracy route marker must expose P81 decision label criterion");
assert(accuracyRoute.includes("require_accept_or_reject_or_defer_label"), "Accuracy route marker must expose P81 accept/reject/defer criterion");
assert(accuracyRoute.includes("require_no_raw_values_in_manifest"), "Accuracy route marker must expose P81 no raw values criterion");
assert(accuracyRoute.includes("require_no_private_paths_in_manifest"), "Accuracy route marker must expose P81 no private paths criterion");
assert(accuracyRoute.includes("require_no_secrets_in_manifest"), "Accuracy route marker must expose P81 no secrets criterion");
assert(accuracyRoute.includes("require_no_evidence_file_recorded_before_decision"), "Accuracy route marker must expose P81 no file criterion");
assert(accuracyRoute.includes("require_no_evidence_hash_recorded_before_decision"), "Accuracy route marker must expose P81 no hash criterion");
assert(accuracyRoute.includes("block_upload_until_manifest_decision_recorded"), "Accuracy route marker must expose P81 upload block criterion");
assert(accuracyRoute.includes("block_attachment_until_manifest_decision_recorded"), "Accuracy route marker must expose P81 attachment block criterion");
assert(accuracyRoute.includes("block_mark_until_manifest_decision_recorded"), "Accuracy route marker must expose P81 mark block criterion");
assert(accuracyRoute.includes("blocked decision queue for future human-submitted receipt manifest decisions"), "Accuracy route marker must expose P81 blocked decision copy");
assert(accuracyRoute.includes("no manifest has been received, accepted, rejected, deferred, decision-recorded, uploaded, attached, or marked"), "Accuracy route marker must expose P81 negative status copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1"'), "Core evidence receipt manifest decision audit helper must expose schema version");
assert(helperSlice.includes('stage: "P83-A"'), "Core evidence receipt manifest decision audit helper must expose P83-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose blocked status");
assert(helperSlice.includes('upstreamDecisionQueueSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1"'), "Core evidence receipt manifest decision audit helper must expose upstream P81 schema");
assert(helperSlice.includes('upstreamDecisionQueueStage: "P81-A"'), "Core evidence receipt manifest decision audit helper must expose upstream P81 stage");
assert(helperSlice.includes('upstreamDecisionQueueStatus: "blocked_pending_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision audit helper must expose upstream P81 status");
assert(helperSlice.includes('upstreamAcceptanceGateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"'), "Core evidence receipt manifest decision audit helper must expose upstream P79 schema");
assert(helperSlice.includes('upstreamAcceptanceGateStage: "P79-A"'), "Core evidence receipt manifest decision audit helper must expose upstream P79 stage");
assert(helperSlice.includes('upstreamAcceptanceGateStatus: "blocked_pending_external_evidence_receipt_manifest_acceptance"'), "Core evidence receipt manifest decision audit helper must expose upstream P79 status");
assert(helperSlice.includes('upstreamPreflightSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-preflight-v1"'), "Core evidence receipt manifest decision audit helper must expose upstream P77 schema");
assert(helperSlice.includes('upstreamPreflightStage: "P77-A"'), "Core evidence receipt manifest decision audit helper must expose upstream P77 stage");
assert(helperSlice.includes('upstreamPreflightStatus: "blocked_pending_external_evidence_receipt_manifest_preflight"'), "Core evidence receipt manifest decision audit helper must expose upstream P77 status");
assert(helperSlice.includes('upstreamTemplateSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-templates-v1"'), "Core evidence receipt manifest decision audit helper must expose upstream P75 schema");
assert(helperSlice.includes('upstreamTemplateStage: "P75-A"'), "Core evidence receipt manifest decision audit helper must expose upstream P75 stage");
assert(helperSlice.includes('upstreamTemplateStatus: "blocked_pending_external_evidence_receipt_manifests"'), "Core evidence receipt manifest decision audit helper must expose upstream P75 status");
assert(helperSlice.includes("caseReceiptManifestDecisionAuditRows: 5"), "Core evidence receipt manifest decision audit helper must expose 5 case rows");
assert(helperSlice.includes("attachmentReceiptManifestDecisionAuditRows: 10"), "Core evidence receipt manifest decision audit helper must expose 10 attachment rows");
assert(helperSlice.includes("pendingExternalEvidenceReceiptManifestDecisionAuditCount: 10"), "Core evidence receipt manifest decision audit helper must expose 10 pending audit rows");
assert(helperSlice.includes("pendingJhoraReceiptManifestDecisionAuditCount: 5"), "Core evidence receipt manifest decision audit helper must expose 5 JHora audit rows");
assert(helperSlice.includes("pendingParasharaLightReceiptManifestDecisionAuditCount: 5"), "Core evidence receipt manifest decision audit helper must expose 5 Parashara Light audit rows");
assert(helperSlice.includes("decisionQueueRows: 10"), "Core evidence receipt manifest decision audit helper must expose 10 decision queue rows");
assert(helperSlice.includes("decisionAuditReadyCount: 0"), "Core evidence receipt manifest decision audit helper must expose 0 audit-ready count");
assert(helperSlice.includes("decisionAuditBlockedCount: 10"), "Core evidence receipt manifest decision audit helper must expose 10 audit-blocked count");
assert(helperSlice.includes("decisionRecordedCount: 0"), "Core evidence receipt manifest decision audit helper must expose 0 decision-recorded count");
assert(helperSlice.includes("decisionAuditedCount: 0"), "Core evidence receipt manifest decision audit helper must expose 0 decision-audited count");
assert(helperSlice.includes("decisionAuditPassedCount: 0"), "Core evidence receipt manifest decision audit helper must expose 0 decision-audit-passed count");
assert(helperSlice.includes("decisionAuditFailedCount: 0"), "Core evidence receipt manifest decision audit helper must expose 0 decision-audit-failed count");
assert(helperSlice.includes("readyToAttachRows: 0"), "Core evidence receipt manifest decision audit helper must expose 0 ready-to-attach rows");
assert(helperSlice.includes("readyToMarkRows: 0"), "Core evidence receipt manifest decision audit helper must expose 0 ready-to-mark rows");
assert(helperSlice.includes("remainingNotReviewedRows: 20"), "Core evidence receipt manifest decision audit helper must expose 20 remaining rows");
assert(helperSlice.includes('receiptGateStatusLabel: "external_receipt_gate_status=blocked_pending_external_evidence_receipts"'), "Core evidence receipt manifest decision audit helper must expose receipt gate label");
assert(helperSlice.includes('intakeStatusLabel: "external_intake_status=blocked_pending_external_evidence_intake"'), "Core evidence receipt manifest decision audit helper must expose intake label");
assert(helperSlice.includes('readinessStatusLabel: "attachment_readiness_status=blocked_pending_external_evidence_attachment"'), "Core evidence receipt manifest decision audit helper must expose readiness label");
assert(helperSlice.includes('decisionQueueStatusLabel: "decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision"'), "Core evidence receipt manifest decision audit helper must expose decision queue label");
assert(helperSlice.includes('decisionAuditStatusLabel: "decision_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose decision audit label");
assert(helperSlice.includes('receiptManifestStatusLabel: "receipt_manifest_status=not_received"'), "Core evidence receipt manifest decision audit helper must expose not-received label");
assert(helperSlice.includes('decisionAuditRecordStatusLabel: "decision_audit_record_status=not_started"'), "Core evidence receipt manifest decision audit helper must expose not-started audit record label");
assert(helperSlice.includes('noRawValuesInManifestLabel: "no_raw_values_in_manifest=true"'), "Core evidence receipt manifest decision audit helper must expose no raw values label");
assert(helperSlice.includes('noPrivatePathsInManifestLabel: "no_private_paths_in_manifest=true"'), "Core evidence receipt manifest decision audit helper must expose no private paths label");
assert(helperSlice.includes('noSecretsInManifestLabel: "no_secrets_in_manifest=true"'), "Core evidence receipt manifest decision audit helper must expose no secrets label");
assert(helperSlice.includes('noEvidenceFileRecordedLabel: "no_evidence_file_recorded=true"'), "Core evidence receipt manifest decision audit helper must expose no file label");
assert(helperSlice.includes('noEvidenceHashRecordedLabel: "no_evidence_hash_recorded=true"'), "Core evidence receipt manifest decision audit helper must expose no hash label");
assert(helperSlice.includes('noUploadExecutedLabel: "no_upload_executed=true"'), "Core evidence receipt manifest decision audit helper must expose no upload label");
assert(helperSlice.includes('noAttachmentExecutedLabel: "no_attachment_executed=true"'), "Core evidence receipt manifest decision audit helper must expose no attachment label");
assert(helperSlice.includes('noMarkCommandExecutedLabel: "no_mark_command_executed=true"'), "Core evidence receipt manifest decision audit helper must expose no mark label");
assert(helperSlice.includes('"await_jhora_receipt_manifest_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose JHora audit label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose Parashara Light audit label");
assert(helperSlice.includes('"audit_external_evidence_receipt_manifest_decision_after_human_review"'), "Core evidence receipt manifest decision audit helper must expose human review audit label");
assert(helperSlice.includes('"defer_external_evidence_receipt_manifest_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose defer audit label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_decision_audit_report"'), "Core evidence receipt manifest decision audit helper must expose rerun audit label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_decision_audit_report"'), "Core evidence receipt manifest decision audit helper must expose P83 command family");
assert(helperSlice.includes('"operator_decision_audit_label"'), "Core evidence receipt manifest decision audit helper must expose operator audit field");
assert(helperSlice.includes('"require_human_decision_audit_timestamp_utc"'), "Core evidence receipt manifest decision audit helper must expose human audit timestamp criterion");
assert(helperSlice.includes('"require_operator_decision_audit_label"'), "Core evidence receipt manifest decision audit helper must expose operator audit criterion");
assert(helperSlice.includes('"require_no_evidence_file_recorded_before_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose no file audit criterion");
assert(helperSlice.includes('"require_no_evidence_hash_recorded_before_decision_audit"'), "Core evidence receipt manifest decision audit helper must expose no hash audit criterion");
assert(helperSlice.includes('"block_upload_until_manifest_decision_audited"'), "Core evidence receipt manifest decision audit helper must expose upload audit block criterion");
assert(helperSlice.includes('"block_attachment_until_manifest_decision_audited"'), "Core evidence receipt manifest decision audit helper must expose attachment audit block criterion");
assert(helperSlice.includes('"block_mark_until_manifest_decision_audited"'), "Core evidence receipt manifest decision audit helper must expose mark audit block criterion");
assert(preflightSlice.includes("P83 receipt manifest decision audit"), "Core evidence pipeline UI must render P83 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit"), "Core evidence receipt manifest decision audit UI must render its heading");
assert(accuracyRoute.includes("P83-A"), "Accuracy route marker must expose P83 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-v1"), "Accuracy route marker must expose P83 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit"), "Accuracy route marker must expose P83 status");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-queue-v1"), "Accuracy route marker must expose P83 upstream P81 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision"), "Accuracy route marker must expose P83 upstream P81 status");
assert(accuracyRoute.includes("case_receipt_manifest_decision_audit_rows=5"), "Accuracy route marker must expose P83 case count");
assert(accuracyRoute.includes("attachment_receipt_manifest_decision_audit_rows=10"), "Accuracy route marker must expose P83 attachment count");
assert(accuracyRoute.includes("pending_external_evidence_receipt_manifest_decision_audit_count=10"), "Accuracy route marker must expose P83 pending audit count");
assert(accuracyRoute.includes("pending_jhora_receipt_manifest_decision_audit_count=5"), "Accuracy route marker must expose P83 pending JHora audit count");
assert(accuracyRoute.includes("pending_parashara_light_receipt_manifest_decision_audit_count=5"), "Accuracy route marker must expose P83 pending Parashara Light audit count");
assert(accuracyRoute.includes("decision_queue_rows=10"), "Accuracy route marker must expose P83 decision queue count");
assert(accuracyRoute.includes("decision_audit_ready_count=0"), "Accuracy route marker must expose P83 audit-ready zero count");
assert(accuracyRoute.includes("decision_audit_blocked_count=10"), "Accuracy route marker must expose P83 audit-blocked count");
assert(accuracyRoute.includes("decision_recorded_count=0"), "Accuracy route marker must expose P83 decision-recorded zero count");
assert(accuracyRoute.includes("decision_audited_count=0"), "Accuracy route marker must expose P83 decision-audited zero count");
assert(accuracyRoute.includes("decision_audit_passed_count=0"), "Accuracy route marker must expose P83 decision-audit-passed zero count");
assert(accuracyRoute.includes("decision_audit_failed_count=0"), "Accuracy route marker must expose P83 decision-audit-failed zero count");
assert(accuracyRoute.includes("ready_to_attach_count=0"), "Accuracy route marker must expose P83 zero ready-to-attach count");
assert(accuracyRoute.includes("ready_to_mark_count=0"), "Accuracy route marker must expose P83 zero ready-to-mark count");
assert(accuracyRoute.includes("remaining_not_reviewed_count=20"), "Accuracy route marker must expose P83 remaining count");
assert(accuracyRoute.includes("external_receipt_gate_status=blocked_pending_external_evidence_receipts"), "Accuracy route marker must expose P83 receipt gate label");
assert(accuracyRoute.includes("external_intake_status=blocked_pending_external_evidence_intake"), "Accuracy route marker must expose P83 intake label");
assert(accuracyRoute.includes("attachment_readiness_status=blocked_pending_external_evidence_attachment"), "Accuracy route marker must expose P83 readiness label");
assert(accuracyRoute.includes("decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision"), "Accuracy route marker must expose P83 decision queue label");
assert(accuracyRoute.includes("decision_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit"), "Accuracy route marker must expose P83 decision audit label");
assert(accuracyRoute.includes("receipt_manifest_status=not_received"), "Accuracy route marker must expose P83 not-received status");
assert(accuracyRoute.includes("decision_audit_record_status=not_started"), "Accuracy route marker must expose P83 not-started audit record status");
assert(accuracyRoute.includes("no_raw_values_in_manifest=true"), "Accuracy route marker must expose P83 no raw values label");
assert(accuracyRoute.includes("no_private_paths_in_manifest=true"), "Accuracy route marker must expose P83 no private paths label");
assert(accuracyRoute.includes("no_secrets_in_manifest=true"), "Accuracy route marker must expose P83 no secrets label");
assert(accuracyRoute.includes("no_evidence_file_recorded=true"), "Accuracy route marker must expose P83 no file label");
assert(accuracyRoute.includes("no_evidence_hash_recorded=true"), "Accuracy route marker must expose P83 no hash label");
assert(accuracyRoute.includes("no_upload_executed=true"), "Accuracy route marker must expose P83 no-upload label");
assert(accuracyRoute.includes("no_attachment_executed=true"), "Accuracy route marker must expose P83 no-attachment label");
assert(accuracyRoute.includes("no_mark_command_executed=true"), "Accuracy route marker must expose P83 no-mark label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest_decision_audit"), "Accuracy route marker must expose P83 JHora audit label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest_decision_audit"), "Accuracy route marker must expose P83 Parashara Light audit label");
assert(accuracyRoute.includes("audit_external_evidence_receipt_manifest_decision_after_human_review"), "Accuracy route marker must expose P83 human review audit label");
assert(accuracyRoute.includes("defer_external_evidence_receipt_manifest_decision_audit"), "Accuracy route marker must expose P83 defer audit label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_decision_audit_report"), "Accuracy route marker must expose P83 rerun audit label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_decision_audit_report"), "Accuracy route marker must expose P83 command family");
assert(accuracyRoute.includes("operator_decision_audit_label"), "Accuracy route marker must expose P83 operator audit field");
assert(accuracyRoute.includes("required_human_decision_audit_timestamp_utc"), "Accuracy route marker must expose P83 human audit timestamp field");
assert(accuracyRoute.includes("require_human_decision_audit_timestamp_utc"), "Accuracy route marker must expose P83 audit timestamp criterion");
assert(accuracyRoute.includes("require_operator_decision_audit_label"), "Accuracy route marker must expose P83 operator audit criterion");
assert(accuracyRoute.includes("require_no_evidence_file_recorded_before_decision_audit"), "Accuracy route marker must expose P83 no file audit criterion");
assert(accuracyRoute.includes("require_no_evidence_hash_recorded_before_decision_audit"), "Accuracy route marker must expose P83 no hash audit criterion");
assert(accuracyRoute.includes("block_upload_until_manifest_decision_audited"), "Accuracy route marker must expose P83 upload block criterion");
assert(accuracyRoute.includes("block_attachment_until_manifest_decision_audited"), "Accuracy route marker must expose P83 attachment block criterion");
assert(accuracyRoute.includes("block_mark_until_manifest_decision_audited"), "Accuracy route marker must expose P83 mark block criterion");
assert(accuracyRoute.includes("blocked decision audit gate for future human-submitted receipt manifest decisions"), "Accuracy route marker must expose P83 blocked audit copy");
assert(accuracyRoute.includes("no manifest decision has been recorded or audited"), "Accuracy route marker must expose P83 negative audit copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-orders-v1"'), "Core evidence decision audit work orders helper must expose P85 schema");
assert(helperSlice.includes('stage: "P85-A"'), "Core evidence decision audit work orders helper must expose P85-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"'), "Core evidence decision audit work orders helper must expose blocked work-order status");
assert(helperSlice.includes('upstreamDecisionAuditSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1"'), "Core evidence decision audit work orders helper must expose upstream P83 schema");
assert(helperSlice.includes('upstreamDecisionAuditStage: "P83-A"'), "Core evidence decision audit work orders helper must expose upstream P83 stage");
assert(helperSlice.includes('upstreamDecisionAuditStatus: "blocked_pending_external_evidence_receipt_manifest_decision_audit"'), "Core evidence decision audit work orders helper must expose upstream P83 status");
assert(helperSlice.includes("caseDecisionAuditWorkOrderRows: 5"), "Core evidence decision audit work orders helper must expose 5 case rows");
assert(helperSlice.includes("attachmentDecisionAuditWorkOrderRows: 10"), "Core evidence decision audit work orders helper must expose 10 attachment rows");
assert(helperSlice.includes("pendingExternalEvidenceDecisionAuditWorkOrderCount: 10"), "Core evidence decision audit work orders helper must expose 10 pending work orders");
assert(helperSlice.includes("pendingJhoraDecisionAuditWorkOrderCount: 5"), "Core evidence decision audit work orders helper must expose 5 JHora work orders");
assert(helperSlice.includes("pendingParasharaLightDecisionAuditWorkOrderCount: 5"), "Core evidence decision audit work orders helper must expose 5 Parashara Light work orders");
assert(helperSlice.includes("decisionAuditWorkOrderReadyCount: 0"), "Core evidence decision audit work orders helper must expose 0 ready work orders");
assert(helperSlice.includes("decisionAuditWorkOrderBlockedCount: 10"), "Core evidence decision audit work orders helper must expose 10 blocked work orders");
assert(helperSlice.includes("decisionAuditReadyCount: 0"), "Core evidence decision audit work orders helper must expose 0 audit-ready count");
assert(helperSlice.includes("decisionAuditBlockedCount: 10"), "Core evidence decision audit work orders helper must expose 10 audit-blocked count");
assert(helperSlice.includes("decisionRecordedCount: 0"), "Core evidence decision audit work orders helper must expose 0 decision-recorded count");
assert(helperSlice.includes("decisionAuditedCount: 0"), "Core evidence decision audit work orders helper must expose 0 decision-audited count");
assert(helperSlice.includes("decisionAuditPassedCount: 0"), "Core evidence decision audit work orders helper must expose 0 decision-audit-passed count");
assert(helperSlice.includes("decisionAuditFailedCount: 0"), "Core evidence decision audit work orders helper must expose 0 decision-audit-failed count");
assert(helperSlice.includes('decisionAuditWorkOrderStatusLabel: "decision_audit_work_order_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"'), "Core evidence decision audit work orders helper must expose work-order status label");
assert(helperSlice.includes('workOrderDeliveryStatusLabel: "work_order_delivery_status=not_delivered"'), "Core evidence decision audit work orders helper must expose delivery status label");
assert(helperSlice.includes('humanDecisionAuditStatusLabel: "human_decision_audit_status=not_started"'), "Core evidence decision audit work orders helper must expose human audit status label");
assert(helperSlice.includes('noAcceptExecutedLabel: "no_accept_executed=true"'), "Core evidence decision audit work orders helper must expose no-accept label");
assert(helperSlice.includes('noRejectExecutedLabel: "no_reject_executed=true"'), "Core evidence decision audit work orders helper must expose no-reject label");
assert(helperSlice.includes('noDeferExecutedLabel: "no_defer_executed=true"'), "Core evidence decision audit work orders helper must expose no-defer label");
assert(helperSlice.includes('noExternalNotificationSentLabel: "no_external_notification_sent=true"'), "Core evidence decision audit work orders helper must expose no-notification label");
assert(helperSlice.includes('noExternalTicketCreatedLabel: "no_external_ticket_created=true"'), "Core evidence decision audit work orders helper must expose no-ticket label");
assert(helperSlice.includes('"await_jhora_receipt_manifest_decision_audit_work_order"'), "Core evidence decision audit work orders helper must expose JHora work-order label");
assert(helperSlice.includes('"await_parashara_light_receipt_manifest_decision_audit_work_order"'), "Core evidence decision audit work orders helper must expose Parashara Light work-order label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_decision_audit_work_orders_report"'), "Core evidence decision audit work orders helper must expose rerun work-orders label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_decision_audit_work_orders_report"'), "Core evidence decision audit work orders helper must expose P85 command family");
assert(preflightSlice.includes("P85 decision audit work orders"), "Core evidence pipeline UI must render P85 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit work orders"), "Core evidence decision audit work orders UI must render its heading");
assert(accuracyRoute.includes("P85-A"), "Accuracy route marker must expose P85 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-work-orders-v1"), "Accuracy route marker must expose P85 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"), "Accuracy route marker must expose P85 status");
assert(accuracyRoute.includes("case_decision_audit_work_order_rows=5"), "Accuracy route marker must expose P85 case count");
assert(accuracyRoute.includes("attachment_decision_audit_work_order_rows=10"), "Accuracy route marker must expose P85 attachment count");
assert(accuracyRoute.includes("pending_external_evidence_decision_audit_work_order_count=10"), "Accuracy route marker must expose P85 pending work-order count");
assert(accuracyRoute.includes("pending_jhora_decision_audit_work_order_count=5"), "Accuracy route marker must expose P85 pending JHora count");
assert(accuracyRoute.includes("pending_parashara_light_decision_audit_work_order_count=5"), "Accuracy route marker must expose P85 pending Parashara Light count");
assert(accuracyRoute.includes("decision_audit_work_order_ready_count=0"), "Accuracy route marker must expose P85 ready work-order zero count");
assert(accuracyRoute.includes("decision_audit_work_order_blocked_count=10"), "Accuracy route marker must expose P85 blocked work-order count");
assert(accuracyRoute.includes("decision_audit_work_order_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"), "Accuracy route marker must expose P85 work-order status label");
assert(accuracyRoute.includes("work_order_delivery_status=not_delivered"), "Accuracy route marker must expose P85 delivery status");
assert(accuracyRoute.includes("human_decision_audit_status=not_started"), "Accuracy route marker must expose P85 human audit status");
assert(accuracyRoute.includes("no_accept_executed=true"), "Accuracy route marker must expose P85 no-accept label");
assert(accuracyRoute.includes("no_reject_executed=true"), "Accuracy route marker must expose P85 no-reject label");
assert(accuracyRoute.includes("no_defer_executed=true"), "Accuracy route marker must expose P85 no-defer label");
assert(accuracyRoute.includes("no_external_notification_sent=true"), "Accuracy route marker must expose P85 no-notification label");
assert(accuracyRoute.includes("no_external_ticket_created=true"), "Accuracy route marker must expose P85 no-ticket label");
assert(accuracyRoute.includes("await_jhora_receipt_manifest_decision_audit_work_order"), "Accuracy route marker must expose P85 JHora work-order label");
assert(accuracyRoute.includes("await_parashara_light_receipt_manifest_decision_audit_work_order"), "Accuracy route marker must expose P85 Parashara Light work-order label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_decision_audit_work_orders_report"), "Accuracy route marker must expose P85 rerun label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_decision_audit_work_orders_report"), "Accuracy route marker must expose P85 command family");
assert(accuracyRoute.includes("blocked internal decision-audit work-order handoff"), "Accuracy route marker must expose P85 blocked work-order copy");
assert(accuracyRoute.includes("no work orders have been delivered to external systems"), "Accuracy route marker must expose P85 negative delivery copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-order-readiness-v1"'), "Core evidence decision audit work-order readiness helper must expose P87 schema");
assert(helperSlice.includes('stage: "P87-A"'), "Core evidence decision audit work-order readiness helper must expose P87-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"'), "Core evidence decision audit work-order readiness helper must expose blocked readiness status");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrdersSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-orders-v1"'), "Core evidence decision audit work-order readiness helper must expose upstream P85 schema");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrdersStage: "P85-A"'), "Core evidence decision audit work-order readiness helper must expose upstream P85 stage");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrdersStatus: "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"'), "Core evidence decision audit work-order readiness helper must expose upstream P85 status");
assert(helperSlice.includes("operatorHandoffCasePacketRows: 5"), "Core evidence decision audit work-order readiness helper must expose 5 handoff case packets");
assert(helperSlice.includes("operatorHandoffAttachmentPacketRows: 10"), "Core evidence decision audit work-order readiness helper must expose 10 handoff attachment packets");
assert(helperSlice.includes("operatorHandoffReadyCount: 0"), "Core evidence decision audit work-order readiness helper must expose 0 handoff-ready count");
assert(helperSlice.includes("operatorHandoffBlockedCount: 10"), "Core evidence decision audit work-order readiness helper must expose 10 handoff-blocked count");
assert(helperSlice.includes("workOrderDeliveryReadyCount: 0"), "Core evidence decision audit work-order readiness helper must expose 0 delivery-ready count");
assert(helperSlice.includes("workOrderDeliveryBlockedCount: 10"), "Core evidence decision audit work-order readiness helper must expose 10 delivery-blocked count");
assert(helperSlice.includes('decisionAuditWorkOrderReadinessStatusLabel: "decision_audit_work_order_readiness_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"'), "Core evidence decision audit work-order readiness helper must expose readiness status label");
assert(helperSlice.includes('operatorHandoffStatusLabel: "operator_handoff_status=not_delivered"'), "Core evidence decision audit work-order readiness helper must expose operator handoff status label");
assert(helperSlice.includes('noWorkOrderDeliveryExecutedLabel: "no_work_order_delivery_executed=true"'), "Core evidence decision audit work-order readiness helper must expose no-delivery label");
assert(helperSlice.includes('noOperatorHandoffDeliveredLabel: "no_operator_handoff_delivered=true"'), "Core evidence decision audit work-order readiness helper must expose no-handoff label");
assert(helperSlice.includes('"prepare_operator_handoff_readiness_packet"'), "Core evidence decision audit work-order readiness helper must expose prepare handoff label");
assert(helperSlice.includes('"build_witness_core_evidence_external_receipt_manifest_decision_audit_work_order_readiness_report"'), "Core evidence decision audit work-order readiness helper must expose P87 command family");
assert(preflightSlice.includes("P87 work-order readiness"), "Core evidence pipeline UI must render P87 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit work-order readiness"), "Core evidence decision audit work-order readiness UI must render its heading");
assert(accuracyRoute.includes("P87-A"), "Accuracy route marker must expose P87 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-work-order-readiness-v1"), "Accuracy route marker must expose P87 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"), "Accuracy route marker must expose P87 status");
assert(accuracyRoute.includes("operator_handoff_case_packet_rows=5"), "Accuracy route marker must expose P87 handoff case packet count");
assert(accuracyRoute.includes("operator_handoff_attachment_packet_rows=10"), "Accuracy route marker must expose P87 handoff attachment packet count");
assert(accuracyRoute.includes("operator_handoff_ready_count=0"), "Accuracy route marker must expose P87 handoff-ready zero count");
assert(accuracyRoute.includes("operator_handoff_blocked_count=10"), "Accuracy route marker must expose P87 handoff-blocked count");
assert(accuracyRoute.includes("work_order_delivery_ready_count=0"), "Accuracy route marker must expose P87 delivery-ready zero count");
assert(accuracyRoute.includes("work_order_delivery_blocked_count=10"), "Accuracy route marker must expose P87 delivery-blocked count");
assert(accuracyRoute.includes("decision_audit_work_order_readiness_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"), "Accuracy route marker must expose P87 readiness status label");
assert(accuracyRoute.includes("operator_handoff_status=not_delivered"), "Accuracy route marker must expose P87 operator handoff status label");
assert(accuracyRoute.includes("no_work_order_delivery_executed=true"), "Accuracy route marker must expose P87 no-delivery label");
assert(accuracyRoute.includes("no_operator_handoff_delivered=true"), "Accuracy route marker must expose P87 no-handoff label");
assert(accuracyRoute.includes("prepare_operator_handoff_readiness_packet"), "Accuracy route marker must expose P87 prepare handoff label");
assert(accuracyRoute.includes("build_witness_core_evidence_external_receipt_manifest_decision_audit_work_order_readiness_report"), "Accuracy route marker must expose P87 command family");
assert(accuracyRoute.includes("blocked operator handoff readiness packet"), "Accuracy route marker must expose P87 blocked readiness copy");
assert(accuracyRoute.includes("no operator handoff has been delivered"), "Accuracy route marker must expose P87 negative handoff copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-v1"'), "Core evidence operator handoff smoke matrix helper must expose P89 schema");
assert(helperSlice.includes('stage: "P89-A"'), "Core evidence operator handoff smoke matrix helper must expose P89-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"'), "Core evidence operator handoff smoke matrix helper must expose blocked smoke status");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrderReadinessSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-order-readiness-v1"'), "Core evidence operator handoff smoke matrix helper must expose upstream P87 schema");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrderReadinessStage: "P87-A"'), "Core evidence operator handoff smoke matrix helper must expose upstream P87 stage");
assert(helperSlice.includes('upstreamDecisionAuditWorkOrderReadinessStatus: "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"'), "Core evidence operator handoff smoke matrix helper must expose upstream P87 status");
assert(helperSlice.includes("operatorHandoffSmokeCaseRows: 5"), "Core evidence operator handoff smoke matrix helper must expose 5 smoke case rows");
assert(helperSlice.includes("operatorHandoffSmokeAttachmentRows: 10"), "Core evidence operator handoff smoke matrix helper must expose 10 smoke attachment rows");
assert(helperSlice.includes("safeValidationCommandFamilyCount: 4"), "Core evidence operator handoff smoke matrix helper must expose 4 safe validation families");
assert(helperSlice.includes("unsafeExternalActionCommandCount: 0"), "Core evidence operator handoff smoke matrix helper must expose 0 unsafe external action commands");
assert(helperSlice.includes("commandExecutionPerformedCount: 0"), "Core evidence operator handoff smoke matrix helper must expose 0 command executions");
assert(helperSlice.includes("commandSmokeMatrixReadyCount: 0"), "Core evidence operator handoff smoke matrix helper must expose 0 smoke ready rows");
assert(helperSlice.includes("commandSmokeMatrixBlockedCount: 10"), "Core evidence operator handoff smoke matrix helper must expose 10 smoke blocked rows");
assert(helperSlice.includes('operatorHandoffSmokeMatrixStatusLabel: "operator_handoff_smoke_matrix_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"'), "Core evidence operator handoff smoke matrix helper must expose smoke matrix status label");
assert(helperSlice.includes('commandSmokeMatrixStatusLabel: "command_smoke_matrix_status=blocked_pending_external_evidence_and_operator_handoff"'), "Core evidence operator handoff smoke matrix helper must expose blocked command smoke label");
assert(helperSlice.includes('safeValidationOnlyLabel: "safe_validation_only=true"'), "Core evidence operator handoff smoke matrix helper must expose validation-only label");
assert(helperSlice.includes('noCommandExecutionPerformedLabel: "no_command_execution_performed=true"'), "Core evidence operator handoff smoke matrix helper must expose no command execution label");
assert(helperSlice.includes('"validate_manifest_shape"'), "Core evidence operator handoff smoke matrix helper must expose manifest shape validation label");
assert(helperSlice.includes('"validate_operator_handoff_readiness"'), "Core evidence operator handoff smoke matrix helper must expose handoff readiness validation label");
assert(helperSlice.includes('"validate_no_external_action"'), "Core evidence operator handoff smoke matrix helper must expose no external action validation label");
assert(helperSlice.includes('"validate_release_gate_blocked"'), "Core evidence operator handoff smoke matrix helper must expose release blocked validation label");
assert(preflightSlice.includes("P89 operator handoff smoke matrix"), "Core evidence pipeline UI must render P89 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit operator handoff smoke matrix"), "Core evidence operator handoff smoke matrix UI must render its heading");
assert(accuracyRoute.includes("P89-A"), "Accuracy route marker must expose P89 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-v1"), "Accuracy route marker must expose P89 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"), "Accuracy route marker must expose P89 status");
assert(accuracyRoute.includes("operator_handoff_smoke_case_rows=5"), "Accuracy route marker must expose P89 smoke case row count");
assert(accuracyRoute.includes("operator_handoff_smoke_attachment_rows=10"), "Accuracy route marker must expose P89 smoke attachment row count");
assert(accuracyRoute.includes("safe_validation_command_family_count=4"), "Accuracy route marker must expose P89 safe validation family count");
assert(accuracyRoute.includes("unsafe_external_action_command_count=0"), "Accuracy route marker must expose P89 unsafe action zero count");
assert(accuracyRoute.includes("command_execution_performed_count=0"), "Accuracy route marker must expose P89 no command execution count");
assert(accuracyRoute.includes("command_smoke_matrix_ready_count=0"), "Accuracy route marker must expose P89 matrix-ready zero count");
assert(accuracyRoute.includes("command_smoke_matrix_blocked_count=10"), "Accuracy route marker must expose P89 matrix-blocked count");
assert(accuracyRoute.includes("operator_handoff_smoke_matrix_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"), "Accuracy route marker must expose P89 smoke matrix status label");
assert(accuracyRoute.includes("command_smoke_matrix_status=blocked_pending_external_evidence_and_operator_handoff"), "Accuracy route marker must expose P89 command smoke status label");
assert(accuracyRoute.includes("safe_validation_only=true"), "Accuracy route marker must expose P89 validation-only label");
assert(accuracyRoute.includes("no_command_execution_performed=true"), "Accuracy route marker must expose P89 no command execution label");
assert(accuracyRoute.includes("validate_manifest_shape"), "Accuracy route marker must expose P89 manifest shape validation label");
assert(accuracyRoute.includes("validate_operator_handoff_readiness"), "Accuracy route marker must expose P89 handoff readiness validation label");
assert(accuracyRoute.includes("validate_no_external_action"), "Accuracy route marker must expose P89 no external action validation label");
assert(accuracyRoute.includes("validate_release_gate_blocked"), "Accuracy route marker must expose P89 release blocked validation label");
assert(accuracyRoute.includes("blocked safe command-smoke matrix"), "Accuracy route marker must expose P89 blocked smoke matrix copy");
assert(accuracyRoute.includes("no validation commands have been executed"), "Accuracy route marker must expose P89 negative command execution copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-transcript-v1"'), "Core evidence safe-validation transcript helper must expose P91 schema");
assert(helperSlice.includes('stage: "P91-A"'), "Core evidence safe-validation transcript helper must expose P91-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript"'), "Core evidence safe-validation transcript helper must expose blocked transcript status");
assert(helperSlice.includes('upstreamOperatorHandoffSmokeMatrixSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-v1"'), "Core evidence safe-validation transcript helper must expose upstream P89 schema");
assert(helperSlice.includes('upstreamOperatorHandoffSmokeMatrixStage: "P89-A"'), "Core evidence safe-validation transcript helper must expose upstream P89 stage");
assert(helperSlice.includes("safeValidationTranscriptCaseRows: 5"), "Core evidence safe-validation transcript helper must expose 5 transcript case rows");
assert(helperSlice.includes("safeValidationTranscriptAttachmentRows: 10"), "Core evidence safe-validation transcript helper must expose 10 transcript attachment rows");
assert(helperSlice.includes("safeValidationTranscriptCommandRows: 40"), "Core evidence safe-validation transcript helper must expose 40 transcript command rows");
assert(helperSlice.includes("safeValidationCommandExecutionPerformedCount: 0"), "Core evidence safe-validation transcript helper must expose 0 safe command executions");
assert(helperSlice.includes("safeValidationCommandReadyCount: 0"), "Core evidence safe-validation transcript helper must expose 0 safe command ready rows");
assert(helperSlice.includes("safeValidationCommandBlockedCount: 40"), "Core evidence safe-validation transcript helper must expose 40 safe command blocked rows");
assert(helperSlice.includes('safeValidationTranscriptStatusLabel: "safe_validation_transcript_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript"'), "Core evidence safe-validation transcript helper must expose transcript status label");
assert(helperSlice.includes('safeValidationCommandStatusLabel: "safe_validation_command_status=blocked_pending_external_evidence_and_operator_handoff"'), "Core evidence safe-validation transcript helper must expose safe command status label");
assert(helperSlice.includes('safeValidationCommandExecutionStatusLabel: "safe_validation_command_execution_status=not_executed"'), "Core evidence safe-validation transcript helper must expose not-executed label");
assert(helperSlice.includes('"rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report"'), "Core evidence safe-validation transcript helper must expose P91 rerun label");
assert(preflightSlice.includes("P91 safe-validation transcript"), "Core evidence pipeline UI must render P91 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit operator handoff safe-validation transcript"), "Core evidence safe-validation transcript UI must render its heading");
assert(accuracyRoute.includes("P91-A"), "Accuracy route marker must expose P91 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-transcript-v1"), "Accuracy route marker must expose P91 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript"), "Accuracy route marker must expose P91 status");
assert(accuracyRoute.includes("safe_validation_transcript_case_rows=5"), "Accuracy route marker must expose P91 transcript case count");
assert(accuracyRoute.includes("safe_validation_transcript_attachment_rows=10"), "Accuracy route marker must expose P91 transcript attachment count");
assert(accuracyRoute.includes("safe_validation_transcript_command_rows=40"), "Accuracy route marker must expose P91 transcript command count");
assert(accuracyRoute.includes("safe_validation_command_execution_performed_count=0"), "Accuracy route marker must expose P91 no safe command execution count");
assert(accuracyRoute.includes("safe_validation_command_ready_count=0"), "Accuracy route marker must expose P91 safe command ready zero count");
assert(accuracyRoute.includes("safe_validation_command_blocked_count=40"), "Accuracy route marker must expose P91 safe command blocked count");
assert(accuracyRoute.includes("safe_validation_transcript_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript"), "Accuracy route marker must expose P91 transcript status label");
assert(accuracyRoute.includes("safe_validation_command_status=blocked_pending_external_evidence_and_operator_handoff"), "Accuracy route marker must expose P91 safe command status label");
assert(accuracyRoute.includes("safe_validation_command_execution_status=not_executed"), "Accuracy route marker must expose P91 not-executed label");
assert(accuracyRoute.includes("rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report"), "Accuracy route marker must expose P91 rerun label");
assert(accuracyRoute.includes("blocked safe-validation transcript bundle"), "Accuracy route marker must expose P91 blocked transcript copy");
assert(accuracyRoute.includes("no safe validation commands have been executed"), "Accuracy route marker must expose P91 negative command execution copy");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-ledger-v1"'), "Core evidence safe-validation result ledger helper must expose P93 schema");
assert(helperSlice.includes('stage: "P93-A"'), "Core evidence safe-validation result ledger helper must expose P93-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger"'), "Core evidence safe-validation result ledger helper must expose blocked result ledger status");
assert(helperSlice.includes('upstreamSafeValidationTranscriptSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-transcript-v1"'), "Core evidence safe-validation result ledger helper must expose upstream P91 schema");
assert(helperSlice.includes('upstreamSafeValidationTranscriptStage: "P91-A"'), "Core evidence safe-validation result ledger helper must expose upstream P91 stage");
assert(helperSlice.includes("safeValidationResultLedgerRows: 40"), "Core evidence safe-validation result ledger helper must expose 40 ledger rows");
assert(helperSlice.includes("safeValidationResultRecordedCount: 0"), "Core evidence safe-validation result ledger helper must expose 0 recorded results");
assert(helperSlice.includes("safeValidationResultAcceptedCount: 0"), "Core evidence safe-validation result ledger helper must expose 0 accepted results");
assert(helperSlice.includes("safeValidationResultFailedCount: 0"), "Core evidence safe-validation result ledger helper must expose 0 failed results");
assert(helperSlice.includes("safeValidationResultBlockedCount: 40"), "Core evidence safe-validation result ledger helper must expose 40 blocked results");
assert(helperSlice.includes('safeValidationResultLedgerStatusLabel: "safe_validation_result_ledger_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger"'), "Core evidence safe-validation result ledger helper must expose result ledger status label");
assert(helperSlice.includes('safeValidationResultExecutionStatusLabel: "safe_validation_result_execution_status=not_executed"'), "Core evidence safe-validation result ledger helper must expose result execution status label");
assert(helperSlice.includes('safeValidationResultRecordStatusLabel: "safe_validation_result_record_status=not_recorded"'), "Core evidence safe-validation result ledger helper must expose result record status label");
assert(helperSlice.includes('safeValidationResultAcceptanceStatusLabel: "safe_validation_result_acceptance_status=not_accepted"'), "Core evidence safe-validation result ledger helper must expose result acceptance status label");
assert(helperSlice.includes('safeValidationResultFailureStatusLabel: "safe_validation_result_failure_status=not_failed"'), "Core evidence safe-validation result ledger helper must expose result failure status label");
assert(helperSlice.includes('safeValidationResultLedgerOnlyLabel: "safe_validation_result_ledger_only=true"'), "Core evidence safe-validation result ledger helper must expose ledger-only label");
assert(helperSlice.includes('noSafeValidationResultRecordedLabel: "no_safe_validation_result_recorded=true"'), "Core evidence safe-validation result ledger helper must expose no recorded result label");
assert(helperSlice.includes('noSafeValidationResultAcceptedLabel: "no_safe_validation_result_accepted=true"'), "Core evidence safe-validation result ledger helper must expose no accepted result label");
assert(helperSlice.includes('noSafeValidationResultFailedLabel: "no_safe_validation_result_failed=true"'), "Core evidence safe-validation result ledger helper must expose no failed result label");
assert(helperSlice.includes("validate_manifest_shape_blocked_result_label_only"), "Core evidence safe-validation result ledger helper must expose manifest shape result label");
assert(helperSlice.includes("validate_operator_handoff_readiness_blocked_result_label_only"), "Core evidence safe-validation result ledger helper must expose handoff readiness result label");
assert(helperSlice.includes("validate_no_external_action_blocked_result_label_only"), "Core evidence safe-validation result ledger helper must expose no external action result label");
assert(helperSlice.includes("validate_release_gate_blocked_blocked_result_label_only"), "Core evidence safe-validation result ledger helper must expose release blocked result label");
assert(preflightSlice.includes("P93 safe-validation result ledger"), "Core evidence pipeline UI must render P93 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit operator handoff safe-validation result ledger"), "Core evidence safe-validation result ledger UI must render its heading");
assert(accuracyRoute.includes("P93-A"), "Accuracy route marker must expose P93 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-ledger-v1"), "Accuracy route marker must expose P93 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger"), "Accuracy route marker must expose P93 status");
assert(accuracyRoute.includes("safe_validation_result_ledger_rows=40"), "Accuracy route marker must expose P93 result ledger count");
assert(accuracyRoute.includes("safe_validation_result_recorded_count=0"), "Accuracy route marker must expose P93 no recorded results count");
assert(accuracyRoute.includes("safe_validation_result_accepted_count=0"), "Accuracy route marker must expose P93 no accepted results count");
assert(accuracyRoute.includes("safe_validation_result_failed_count=0"), "Accuracy route marker must expose P93 no failed results count");
assert(accuracyRoute.includes("safe_validation_result_blocked_count=40"), "Accuracy route marker must expose P93 blocked result count");
assert(accuracyRoute.includes("safe_validation_result_ledger_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger"), "Accuracy route marker must expose P93 ledger status label");
assert(accuracyRoute.includes("safe_validation_result_execution_status=not_executed"), "Accuracy route marker must expose P93 result not-executed label");
assert(accuracyRoute.includes("safe_validation_result_record_status=not_recorded"), "Accuracy route marker must expose P93 result not-recorded label");
assert(accuracyRoute.includes("safe_validation_result_acceptance_status=not_accepted"), "Accuracy route marker must expose P93 result not-accepted label");
assert(accuracyRoute.includes("safe_validation_result_failure_status=not_failed"), "Accuracy route marker must expose P93 result not-failed label");
assert(accuracyRoute.includes("safe_validation_result_ledger_only=true"), "Accuracy route marker must expose P93 ledger-only label");
assert(accuracyRoute.includes("no_safe_validation_result_recorded=true"), "Accuracy route marker must expose P93 no result recorded label");
assert(accuracyRoute.includes("no_safe_validation_result_accepted=true"), "Accuracy route marker must expose P93 no result accepted label");
assert(accuracyRoute.includes("no_safe_validation_result_failed=true"), "Accuracy route marker must expose P93 no result failed label");
assert(accuracyRoute.includes("validate_manifest_shape_blocked_result_label_only"), "Accuracy route marker must expose P93 manifest shape blocked result label");
assert(accuracyRoute.includes("validate_operator_handoff_readiness_blocked_result_label_only"), "Accuracy route marker must expose P93 handoff readiness blocked result label");
assert(accuracyRoute.includes("validate_no_external_action_blocked_result_label_only"), "Accuracy route marker must expose P93 no external action blocked result label");
assert(accuracyRoute.includes("validate_release_gate_blocked_blocked_result_label_only"), "Accuracy route marker must expose P93 release blocked result label");
assert(accuracyRoute.includes("blocked safe-validation result ledger"), "Accuracy route marker must expose P93 blocked result ledger copy");
assert(accuracyRoute.includes("no safe-validation result has been recorded, accepted, or failed"), "Accuracy route marker must expose P93 negative result copy");
assert(!helperSlice.includes('latestStage: "P93-A"'), "Core evidence pipeline helper must not retain stale P93 latest stage");
assert(helperSlice.includes('latestStage: "P95-A"'), "Core evidence pipeline helper must expose latest P95 stage");
assert(helperSlice.includes('"P95 safe-validation result audit"'), "Core evidence pipeline helper must expose P95 stage sequence");
assert(helperSlice.includes('schemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-v1"'), "Core evidence safe-validation result audit helper must expose P95 schema");
assert(helperSlice.includes('stage: "P95-A"'), "Core evidence safe-validation result audit helper must expose P95-A stage");
assert(helperSlice.includes('status: "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit"'), "Core evidence safe-validation result audit helper must expose blocked result audit status");
assert(helperSlice.includes('upstreamSafeValidationResultLedgerSchemaVersion: "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-ledger-v1"'), "Core evidence safe-validation result audit helper must expose upstream P93 schema");
assert(helperSlice.includes('upstreamSafeValidationResultLedgerStage: "P93-A"'), "Core evidence safe-validation result audit helper must expose upstream P93 stage");
assert(helperSlice.includes("safeValidationResultAuditRows: 40"), "Core evidence safe-validation result audit helper must expose 40 audit rows");
assert(helperSlice.includes("safeValidationResultAuditPerformedCount: 0"), "Core evidence safe-validation result audit helper must expose 0 performed audits");
assert(helperSlice.includes("safeValidationResultAuditPassedCount: 0"), "Core evidence safe-validation result audit helper must expose 0 passed audits");
assert(helperSlice.includes("safeValidationResultAuditFailedCount: 0"), "Core evidence safe-validation result audit helper must expose 0 failed audits");
assert(helperSlice.includes("safeValidationResultAuditBlockedCount: 40"), "Core evidence safe-validation result audit helper must expose 40 blocked audits");
assert(helperSlice.includes('safeValidationResultAuditStatusLabel: "safe_validation_result_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit"'), "Core evidence safe-validation result audit helper must expose result audit status label");
assert(helperSlice.includes('safeValidationResultAuditExecutionStatusLabel: "safe_validation_result_audit_execution_status=not_executed"'), "Core evidence safe-validation result audit helper must expose result audit execution status label");
assert(helperSlice.includes('safeValidationResultAuditRecordStatusLabel: "safe_validation_result_audit_record_status=not_recorded"'), "Core evidence safe-validation result audit helper must expose result audit record status label");
assert(helperSlice.includes('safeValidationResultAuditPassStatusLabel: "safe_validation_result_audit_pass_status=not_passed"'), "Core evidence safe-validation result audit helper must expose result audit pass status label");
assert(helperSlice.includes('safeValidationResultAuditFailureStatusLabel: "safe_validation_result_audit_failure_status=not_failed"'), "Core evidence safe-validation result audit helper must expose result audit failure status label");
assert(helperSlice.includes('safeValidationResultAuditOnlyLabel: "safe_validation_result_audit_only=true"'), "Core evidence safe-validation result audit helper must expose result-audit-only label");
assert(helperSlice.includes('noSafeValidationResultAuditPerformedLabel: "no_safe_validation_result_audit_performed=true"'), "Core evidence safe-validation result audit helper must expose no audit performed label");
assert(helperSlice.includes('noSafeValidationResultAuditPassedLabel: "no_safe_validation_result_audit_passed=true"'), "Core evidence safe-validation result audit helper must expose no audit passed label");
assert(helperSlice.includes('noSafeValidationResultAuditFailedLabel: "no_safe_validation_result_audit_failed=true"'), "Core evidence safe-validation result audit helper must expose no audit failed label");
assert(helperSlice.includes("audit_manifest_shape_blocked_label_only"), "Core evidence safe-validation result audit helper must expose manifest shape audit label");
assert(helperSlice.includes("audit_operator_handoff_readiness_blocked_label_only"), "Core evidence safe-validation result audit helper must expose handoff readiness audit label");
assert(helperSlice.includes("audit_no_external_action_blocked_label_only"), "Core evidence safe-validation result audit helper must expose no external action audit label");
assert(helperSlice.includes("audit_release_gate_blocked_label_only"), "Core evidence safe-validation result audit helper must expose release blocked audit label");
assert(preflightSlice.includes("P95 safe-validation result audit"), "Core evidence pipeline UI must render P95 stage");
assert(preflightSlice.includes("Core evidence external receipt manifest decision audit operator handoff safe-validation result audit"), "Core evidence safe-validation result audit UI must render its heading");
assert(accuracyRoute.includes("P95-A"), "Accuracy route marker must expose P95 stage");
assert(accuracyRoute.includes("jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-v1"), "Accuracy route marker must expose P95 schema");
assert(accuracyRoute.includes("blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit"), "Accuracy route marker must expose P95 status");
assert(accuracyRoute.includes("safe_validation_result_audit_rows=40"), "Accuracy route marker must expose P95 result audit row count");
assert(accuracyRoute.includes("safe_validation_result_audit_performed_count=0"), "Accuracy route marker must expose P95 no performed audits count");
assert(accuracyRoute.includes("safe_validation_result_audit_passed_count=0"), "Accuracy route marker must expose P95 no passed audits count");
assert(accuracyRoute.includes("safe_validation_result_audit_failed_count=0"), "Accuracy route marker must expose P95 no failed audits count");
assert(accuracyRoute.includes("safe_validation_result_audit_blocked_count=40"), "Accuracy route marker must expose P95 blocked audit count");
assert(accuracyRoute.includes("safe_validation_result_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit"), "Accuracy route marker must expose P95 audit status label");
assert(accuracyRoute.includes("safe_validation_result_audit_execution_status=not_executed"), "Accuracy route marker must expose P95 audit not-executed label");
assert(accuracyRoute.includes("safe_validation_result_audit_record_status=not_recorded"), "Accuracy route marker must expose P95 audit not-recorded label");
assert(accuracyRoute.includes("safe_validation_result_audit_pass_status=not_passed"), "Accuracy route marker must expose P95 audit not-passed label");
assert(accuracyRoute.includes("safe_validation_result_audit_failure_status=not_failed"), "Accuracy route marker must expose P95 audit not-failed label");
assert(accuracyRoute.includes("safe_validation_result_audit_only=true"), "Accuracy route marker must expose P95 result-audit-only label");
assert(accuracyRoute.includes("no_safe_validation_result_audit_performed=true"), "Accuracy route marker must expose P95 no audit performed label");
assert(accuracyRoute.includes("no_safe_validation_result_audit_passed=true"), "Accuracy route marker must expose P95 no audit passed label");
assert(accuracyRoute.includes("no_safe_validation_result_audit_failed=true"), "Accuracy route marker must expose P95 no audit failed label");
assert(accuracyRoute.includes("audit_manifest_shape_blocked_label_only"), "Accuracy route marker must expose P95 manifest shape audit label");
assert(accuracyRoute.includes("audit_operator_handoff_readiness_blocked_label_only"), "Accuracy route marker must expose P95 handoff readiness audit label");
assert(accuracyRoute.includes("audit_no_external_action_blocked_label_only"), "Accuracy route marker must expose P95 no external action audit label");
assert(accuracyRoute.includes("audit_release_gate_blocked_label_only"), "Accuracy route marker must expose P95 release blocked audit label");
assert(accuracyRoute.includes("blocked safe-validation result audit"), "Accuracy route marker must expose P95 blocked audit copy");
assert(accuracyRoute.includes("no safe-validation result audit has been performed, passed, or failed"), "Accuracy route marker must expose P95 negative audit copy");
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
  "raw expected",
  "raw actual",
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
  "done",
  "ready for release",
  "verified parity",
  "accepted parity",
  "JHora parity done",
  "Parashara Light parity done",
  "parity success",
  "evidence available",
  "external evidence received",
  "external evidence validated",
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
